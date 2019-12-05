from abc import abstractmethod
import io
import operator
from typing import IO, Any, Generator, Iterable, Sequence, Tuple

from eth_typing import Hash32
from eth_utils import to_tuple
from eth_utils.toolz import accumulate, concatv

from ssz import constants
from ssz.cache.utils import get_key
from ssz.constants import CHUNK_SIZE
from ssz.exceptions import DeserializationError
from ssz.sedes.base import (
    BaseBitfieldCompositeSedes,
    BaseProperCompositeSedes,
    BaseSedes,
    TSedes,
)
from ssz.typing import CacheObj, TDeserialized, TSerializable
from ssz.utils import encode_offset, merkleize, merkleize_with_cache, pack


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
    def get_hash_tree_root(self, value: TSerializable) -> Hash32:
        serialized_value = self.serialize(value)
        return merkleize(pack((serialized_value,)))

    def get_hash_tree_root_and_leaves(
        self, value: TSerializable, cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        serialized_value = self.serialize(value)
        return merkleize_with_cache(pack((serialized_value,)), cache=cache)

    def get_key(self, value: Any) -> str:
        return get_key(self, value)


def _compute_fixed_size_section_length(element_sedes: Iterable[TSedes]) -> int:
    return sum(
        sedes.get_fixed_size() if sedes.is_fixed_sized else constants.OFFSET_SIZE
        for sedes in element_sedes
    )


class BitfieldCompositeSedes(BaseBitfieldCompositeSedes[TSerializable, TDeserialized]):
    def get_key(self, value: Any) -> str:
        return get_key(self, value)


class ProperCompositeSedes(BaseProperCompositeSedes[TSerializable, TDeserialized]):
    @to_tuple
    def _get_item_sedes_pairs(
        self, value: Sequence[TSerializable]
    ) -> Generator[Tuple[TSerializable, TSedes], None, None]:
        for index, element in enumerate(value):
            yield element, self.get_element_sedes(index)

    def _validate_serializable(self, value: Any) -> None:
        ...

    def serialize(self, value: TSerializable) -> bytes:
        self._validate_serializable(value)

        if not len(value):
            return b""

        pairs = self._get_item_sedes_pairs(value)  # slow
        element_sedes = tuple(sedes for element, sedes in pairs)

        has_fixed_size_section_length_cache = hasattr(
            value, "_fixed_size_section_length_cache"
        )
        if has_fixed_size_section_length_cache:
            if value._fixed_size_section_length_cache is None:
                fixed_size_section_length = _compute_fixed_size_section_length(
                    element_sedes
                )
                value._fixed_size_section_length_cache = fixed_size_section_length
            else:
                fixed_size_section_length = value._fixed_size_section_length_cache
        else:
            fixed_size_section_length = _compute_fixed_size_section_length(
                element_sedes
            )

        variable_size_section_parts = tuple(
            sedes.serialize(item)  # slow
            for item, sedes in pairs
            if not sedes.is_fixed_sized
        )

        if variable_size_section_parts:
            offsets = tuple(
                accumulate(
                    operator.add,
                    map(len, variable_size_section_parts[:-1]),
                    fixed_size_section_length,
                )
            )
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
            raise DeserializationError(
                "Did not consume all offsets while decoding value"
            )

        return b"".join(concatv(fixed_size_section_parts, variable_size_section_parts))

    def serialize_element_for_tree(self, index: int, element: TSerializable) -> bytes:
        sedes = self.get_element_sedes(index)
        if self.is_packing:
            return sedes.serialize(element)
        else:
            return sedes.get_hash_tree_root(element)

    @property
    def element_size_in_tree(self) -> int:
        if self.is_packing:
            # note that only homogenous composites with fixed sized elements are packed
            return self.get_element_sedes(0).get_fixed_size()
        else:
            return CHUNK_SIZE

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

    def get_key(self, value: Any) -> str:
        return get_key(self, value)


class HomogeneousProperCompositeSedes(
    ProperCompositeSedes[TSerializable, TDeserialized]
):
    def __init__(self, element_sedes: TSedes, max_length: int) -> None:
        self.element_sedes = element_sedes
        if max_length < 1:
            raise ValueError(
                f"(Maximum) length of homogenous composites must be at least 1, got {max_length}"
            )
        self.max_length = max_length

    def get_sedes_id(self) -> str:
        sedes_name = self.__class__.__name__
        return f"{sedes_name}({self.element_sedes.get_sedes_id()},{self.max_length})"

    @property
    def is_packing(self) -> bool:
        return isinstance(self.element_sedes, BasicSedes)

    @property
    def chunk_count(self) -> int:
        if self.is_packing:
            element_size = self.element_sedes.get_fixed_size()
            return (element_size * self.max_length + CHUNK_SIZE - 1) // CHUNK_SIZE
        else:
            return self.max_length
