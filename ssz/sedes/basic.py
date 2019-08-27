from abc import (
    abstractmethod,
)
import io
import operator
from typing import (
    IO,
    Any,
    Iterable,
    Optional,
    Sequence,
    Tuple,
)

from eth_typing import (
    Hash32,
)
from eth_utils.toolz import (
    accumulate,
    concatv,
)

from ssz import (
    constants,
)
from ssz.cache.utils import (
    get_key,
)
from ssz.exceptions import (
    DeserializationError,
)
from ssz.sedes.base import (
    BaseCompositeSedes,
    BaseSedes,
    TSedes,
)
from ssz.typing import (
    CacheObj,
    TDeserialized,
    TSerializable,
)
from ssz.utils import (
    encode_offset,
    merkleize,
    merkleize_with_cache,
    pack,
)


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

    def get_hash_tree_root_and_leaves(self,
                                      value: TSerializable,
                                      cache: CacheObj) -> Tuple[Hash32, CacheObj]:
        serialized_value = self.serialize(value)
        return merkleize_with_cache(
            pack((serialized_value,)),
            cache=cache,
        )

    def chunk_count(self) -> int:
        return 1

    def get_key(self, value: Any) -> bytes:
        return get_key(self, value)


def _compute_fixed_size_section_length(element_sedes: Iterable[TSedes]) -> int:
    return sum(
        sedes.get_fixed_size()
        if sedes.is_fixed_sized else constants.OFFSET_SIZE
        for sedes in element_sedes
    )


class CompositeSedes(BaseCompositeSedes[TSerializable, TDeserialized]):
    @abstractmethod
    def _get_item_sedes_pairs(self,
                              value: Sequence[TSerializable],
                              ) -> Tuple[Tuple[TSerializable, TSedes], ...]:
        ...

    def get_fixed_size_section_length(
            self,
            value: Sequence[TSerializable],
            pairs: Optional[Tuple[Tuple[TSerializable, TSedes], ...]]=None) -> int:
        if pairs is None:
            pairs = self._get_item_sedes_pairs(value)
        element_sedes = tuple(sedes for element, sedes in pairs)
        return _compute_fixed_size_section_length(element_sedes)

    def _validate_serializable(self, value: Any) -> None:
        ...

    def serialize(self, value: TSerializable, fixed_size_section_length=None) -> bytes:
        self._validate_serializable(value)

        if not len(value):
            return b''

        pairs = self._get_item_sedes_pairs(value)
        if fixed_size_section_length is None:
            fixed_size_section_length = self.get_fixed_size_section_length(value, pairs=pairs)

        variable_size_section_parts = tuple(
            sedes.serialize(item)  # slow
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
            sedes.serialize(item)  # slow
            if sedes.is_fixed_sized
            else encode_offset(next(offsets_iter))
            for item, sedes in pairs
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
        ...

    def get_key(self, value: Any) -> bytes:
        return get_key(self, value)


class BasicBytesSedes(BaseSedes[TSerializable, TDeserialized]):
    def get_key(self, value: Any) -> bytes:
        return get_key(self, value)
