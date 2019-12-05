from typing import IO, Any, Iterable, Sequence, Tuple

from eth_typing import Hash32
from eth_utils import to_tuple
from eth_utils.toolz import cons, sliding_window

from ssz.cache.utils import (
    get_merkle_leaves_with_cache,
    get_merkle_leaves_without_cache,
)
from ssz.constants import OFFSET_SIZE
from ssz.exceptions import DeserializationError
from ssz.hashable_list import HashableList
from ssz.hashable_structure import BaseHashableStructure
from ssz.sedes.base import BaseSedes
from ssz.sedes.basic import BasicSedes, HomogeneousProperCompositeSedes
from ssz.typing import CacheObj, TDeserialized, TSerializable
from ssz.utils import (
    merkleize,
    merkleize_with_cache,
    mix_in_length,
    pack,
    read_exact,
    s_decode_offset,
)

TSedesPairs = Tuple[Tuple[BaseSedes[TSerializable, TDeserialized], TSerializable], ...]


class List(
    HomogeneousProperCompositeSedes[Sequence[TSerializable], Tuple[TDeserialized, ...]]
):
    #
    # Size
    #
    is_fixed_sized = False

    def get_fixed_size(self):
        raise ValueError("List has no static size")

    #
    # Deserialization
    #
    def get_element_sedes(self, index) -> BaseSedes[TSerializable, TDeserialized]:
        return self.element_sedes

    def _deserialize_stream(self, stream: IO[bytes]) -> HashableList[TDeserialized]:
        elements = self._deserialize_stream_to_tuple(stream)
        return HashableList.from_iterable(elements, sedes=self)

    @to_tuple
    def _deserialize_stream_to_tuple(
        self, stream: IO[bytes]
    ) -> Iterable[TDeserialized]:
        if self.element_sedes.is_fixed_sized:
            element_size = self.element_sedes.get_fixed_size()
            data = stream.read()
            if len(data) % element_size != 0:
                raise DeserializationError(
                    f"Invalid max_length. List is comprised of a fixed size sedes "
                    f"but total serialized data is not an even multiple of the "
                    f"element size. data max_length: {len(data)}  element size: "
                    f"{element_size}"
                )
            for start_idx in range(0, len(data), element_size):
                segment = data[start_idx : start_idx + element_size]
                yield self.element_sedes.deserialize(segment)
        else:
            stream_zero_loc = stream.tell()
            try:
                first_offset = s_decode_offset(stream)
            except DeserializationError:
                if stream.tell() == stream_zero_loc:
                    # Empty list
                    return
                else:
                    raise

            num_remaining_offset_bytes = first_offset - stream.tell()
            if num_remaining_offset_bytes % OFFSET_SIZE != 0:
                raise DeserializationError(
                    f"Offset bytes was not a multiple of {OFFSET_SIZE}.  Got "
                    f"{num_remaining_offset_bytes}"
                )

            num_remaining_offsets = num_remaining_offset_bytes // OFFSET_SIZE
            tail_offsets = tuple(
                s_decode_offset(stream) for _ in range(num_remaining_offsets)
            )

            offsets = tuple(cons(first_offset, tail_offsets))

            for left_offset, right_offset in sliding_window(2, offsets):
                element_length = right_offset - left_offset
                element_data = read_exact(element_length, stream)
                yield self.element_sedes.deserialize(element_data)

            # simply reading to the end of the current stream gives us all of the final element data
            final_element_data = stream.read()
            yield self.element_sedes.deserialize(final_element_data)

    #
    # Tree hashing
    #
    def get_hash_tree_root(self, value: Iterable[TSerializable]) -> bytes:
        if isinstance(value, BaseHashableStructure) and value.sedes == self:
            return value.hash_tree_root

        if isinstance(self.element_sedes, BasicSedes):
            serialized_items = tuple(
                self.element_sedes.serialize(element) for element in value
            )
            merkle_leaves = pack(serialized_items)
        else:
            merkle_leaves = tuple(
                self.element_sedes.get_hash_tree_root(element) for element in value
            )

        return mix_in_length(
            merkleize(merkle_leaves, limit=self.chunk_count), len(value)
        )

    def get_hash_tree_root_and_leaves(
        self, value: TSerializable, cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        merkle_leaves = ()
        if isinstance(self.element_sedes, BasicSedes):
            serialized_items = tuple(
                self.element_sedes.serialize(element) for element in value
            )
            merkle_leaves = pack(serialized_items)
        else:
            has_get_hash_tree_root_and_leaves = hasattr(
                self.element_sedes, "get_hash_tree_root_and_leaves"
            )
            if has_get_hash_tree_root_and_leaves:
                merkle_leaves = get_merkle_leaves_with_cache(
                    value, self.element_sedes, cache
                )
            else:
                merkle_leaves = get_merkle_leaves_without_cache(
                    value, self.element_sedes
                )

        merkleize_result, cache = merkleize_with_cache(
            merkle_leaves, cache=cache, limit=self.chunk_count
        )
        return mix_in_length(merkleize_result, len(value)), cache

    #
    # Equality and hashing
    #
    def __hash__(self) -> int:
        return hash((hash(List), hash(self.element_sedes), self.max_length))

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, List)
            and other.element_sedes == self.element_sedes
            and other.max_length == self.max_length
        )
