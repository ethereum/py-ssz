from abc import (
    ABC,
    abstractmethod,
)
import io
import operator
from typing import (
    IO,
    Any,
    Generic,
    Iterable,
    Sequence,
    Tuple,
    TypeVar,
)

from eth_utils.toolz import (
    accumulate,
    concatv,
)

from ssz import (
    constants,
)
from ssz.exceptions import (
    DeserializationError,
)
from ssz.utils import (
    encode_offset,
    merkleize,
    pack,
)

TSerializable = TypeVar("TSerializable")
TDeserialized = TypeVar("TDeserialized")


class BaseSedes(ABC, Generic[TSerializable, TDeserialized]):
    #
    # Size
    #
    @property
    @abstractmethod
    def is_fixed_sized(self) -> bool:
        pass

    @abstractmethod
    def get_fixed_size(self) -> int:
        pass

    #
    # Serialization
    #
    @abstractmethod
    def serialize(self, value: TSerializable) -> bytes:
        pass

    #
    # Deserialization
    #
    @abstractmethod
    def deserialize(self, data: bytes) -> TDeserialized:
        pass

    #
    # Tree hashing
    #
    @abstractmethod
    def get_hash_tree_root(self, value: TSerializable) -> bytes:
        pass


TSedes = BaseSedes[Any, Any]


class BasicSedes(BaseSedes[TSerializable, TDeserialized]):
    def __init__(self, size: int):
        if size <= 0:
            raise ValueError("Length must be greater than 0")

        self.size = size

    #
    # Size
    #
    is_fixed_sized = True

    def get_fixed_size(self):
        return self.size

    #
    # Tree hashing
    #
    def get_hash_tree_root(self, value: TSerializable) -> bytes:
        serialized_value = self.serialize(value)
        return merkleize(pack((serialized_value,)))


class BaseCompositeSedes(BaseSedes[TSerializable, TDeserialized]):
    pass


def _compute_fixed_size_section_length(element_sedes: Iterable[TSedes]) -> int:
    return sum(
        sedes.get_fixed_size() if sedes.is_fixed_sized else constants.OFFSET_SIZE
        for sedes in element_sedes
    )


class CompositeSedes(BaseCompositeSedes[TSerializable, TDeserialized]):
    @abstractmethod
    def _get_item_sedes_pairs(self,
                              value: Sequence[TSerializable],
                              ) -> Tuple[Tuple[TSerializable, TSedes], ...]:
        pass

    def _validate_serializable(self, value: Any) -> None:
        pass

    def serialize(self, value: TSerializable) -> bytes:
        self._validate_serializable(value)

        if not len(value):
            return b''

        pairs = self._get_item_sedes_pairs(value)
        element_sedes = tuple(sedes for element, sedes in pairs)

        fixed_size_section_length = _compute_fixed_size_section_length(element_sedes)

        variable_size_section_parts = tuple(
            sedes.serialize(item)
            for item, sedes
            in pairs
            if not sedes.is_fixed_sized
        )

        if variable_size_section_parts:
            offsets = tuple(accumulate(
                operator.add,
                map(len, variable_size_section_parts[:-1]),
                fixed_size_section_length,
            ))
        else:
            offsets = ()

        offsets_iter = iter(offsets)

        fixed_size_section_parts = tuple(
            sedes.serialize(item) if sedes.is_fixed_sized else encode_offset(next(offsets_iter))
            for item, sedes
            in pairs
        )

        try:
            next(offsets_iter)
        except StopIteration:
            pass
        else:
            raise DeserializationError("Did not consume all offsets while decoding value")

        return b"".join(concatv(
            fixed_size_section_parts,
            variable_size_section_parts,
        ))

    def deserialize(self, data: bytes) -> TDeserialized:
        stream = io.BytesIO(data)
        value = self._deserialize_stream(stream)
        extra_data = stream.read()
        if extra_data:
            raise DeserializationError(f"Got {len(extra_data)} superfluous bytes")
        return value

    @abstractmethod
    def _deserialize_stream(self, stream: IO[bytes]) -> TDeserialized:
        pass
