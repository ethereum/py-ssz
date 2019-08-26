import itertools
from typing import (
    IO,
    Any,
    Iterable,
    Sequence,
    Tuple,
)

from eth_typing import (
    Hash32,
)
from eth_utils import (
    to_tuple,
)
from eth_utils.toolz import (
    cons,
    sliding_window,
)

from ssz.cache.utils import (
    get_merkle_leaves_with_cache,
    get_merkle_leaves_without_cache,
)
from ssz.constants import (
    CHUNK_SIZE,
    OFFSET_SIZE,
)
from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes.base import (
    BaseCompositeSedes,
    BaseSedes,
    TSedes,
)
from ssz.sedes.basic import (
    BasicSedes,
    CompositeSedes,
)
from ssz.typing import (
    CacheObj,
    TDeserialized,
    TSerializable,
)
from ssz.utils import (
    merkleize,
    merkleize_with_cache,
    mix_in_length,
    pack,
    read_exact,
    s_decode_offset,
)

EMPTY_LIST_HASH_TREE_ROOT = mix_in_length(merkleize(pack(())), 0)


class EmptyList(BaseCompositeSedes[Sequence[TSerializable], Tuple[TSerializable, ...]]):
    is_fixed_sized = False
    max_length = 0

    def get_fixed_size(self):
        raise NotImplementedError("Empty list does not implement `get_fixed_size`")

    def serialize(self, value: Sequence[TSerializable]):
        if len(value):
            raise SerializationError("Cannot serialize non-empty sequence using `EmptyList` sedes")
        return b''

    def deserialize(self, data: bytes) -> Tuple[TDeserialized, ...]:
        if data:
            raise DeserializationError("Cannot deserialize non-empty bytes using `EmptyList` sedes")
        return tuple()

    def get_hash_tree_root(self, value: Sequence[TSerializable]) -> bytes:
        if len(value):
            raise ValueError("Cannot compute tree hash for non-empty value using `EmptyList` sedes")
        return EMPTY_LIST_HASH_TREE_ROOT

    def get_hash_tree_root_and_leaves(self,
                                      value: TSerializable,
                                      cache: CacheObj) -> Tuple[Hash32, CacheObj]:
        if len(value):
            raise ValueError("Cannot compute tree hash for non-empty value using `EmptyList` sedes")
        return EMPTY_LIST_HASH_TREE_ROOT

    def chunk_count(self) -> int:
        return 0

    def get_key(self, value: Any) -> bytes:
        raise NotImplementedError("Empty list does not implement `get_key`")

    def get_fixed_size_section_length(self, value: Sequence[TSerializable]):
        raise NotImplementedError("Empty list does not implement `get_fixed_size_section_length`")


empty_list = EmptyList()


TSedesPairs = Tuple[Tuple[BaseSedes[TSerializable, TDeserialized], TSerializable], ...]


class List(CompositeSedes[Sequence[TSerializable], Tuple[TDeserialized, ...]]):
    def __init__(self,
                 element_sedes: TSedes,
                 max_length: int) -> None:
        # This sedes object corresponds to each element of the iterable
        self.element_sedes = element_sedes
        self.max_length = max_length

    #
    # Size
    #
    is_fixed_sized = False

    def get_fixed_size(self):
        raise ValueError("List has no static size")

    #
    # Deserialization
    #
    def _get_item_sedes_pairs(self, value: Sequence[TSerializable]) -> TSedesPairs:
        return tuple(zip(value, itertools.repeat(self.element_sedes)))

    @to_tuple
    def _deserialize_stream(self, stream: IO[bytes]) -> Iterable[TDeserialized]:
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
                segment = data[start_idx: start_idx + element_size]
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
            tail_offsets = tuple(s_decode_offset(stream) for _ in range(num_remaining_offsets))

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
        if isinstance(self.element_sedes, BasicSedes):
            serialized_items = tuple(
                self.element_sedes.serialize(element)
                for element in value
            )
            merkle_leaves = pack(serialized_items)
        else:
            merkle_leaves = tuple(
                self.element_sedes.get_hash_tree_root(element)
                for element in value
            )

        return mix_in_length(merkleize(merkle_leaves, limit=self.chunk_count()), len(value))

    def get_hash_tree_root_and_leaves(self,
                                      value: TSerializable,
                                      cache: CacheObj) -> Tuple[Hash32, CacheObj]:
        merkle_leaves = ()
        if isinstance(self.element_sedes, BasicSedes):
            serialized_items = tuple(
                self.element_sedes.serialize(element)
                for element in value
            )
            merkle_leaves = pack(serialized_items)
        else:
            has_get_hash_tree_root_and_leaves = hasattr(
                self.element_sedes,
                'get_hash_tree_root_and_leaves',
            )
            if has_get_hash_tree_root_and_leaves:
                merkle_leaves = get_merkle_leaves_with_cache(
                    value,
                    self.element_sedes,
                    cache,
                )
            else:
                merkle_leaves = get_merkle_leaves_without_cache(value, self.element_sedes)

        merkleize_result, cache = merkleize_with_cache(
            merkle_leaves,
            cache=cache,
            limit=self.chunk_count(),
        )
        return mix_in_length(merkleize_result, len(value)), cache

    def chunk_count(self) -> int:
        if isinstance(self.element_sedes, BasicSedes):
            base_size = self.max_length * self.element_sedes.get_fixed_size()
            return (base_size + CHUNK_SIZE - 1) // CHUNK_SIZE
        else:
            return self.max_length
