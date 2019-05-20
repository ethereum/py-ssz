import itertools
from typing import (
    IO,
    Iterable,
    Sequence,
    Tuple,
    TypeVar,
)

from eth_utils import (
    to_tuple,
)
from eth_utils.toolz import (
    cons,
    partition,
    sliding_window,
)

from ssz.constants import (
    OFFSET_SIZE,
)
from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes.base import (
    BaseCompositeSedes,
    BaseSedes,
    BasicSedes,
    CompositeSedes,
)
from ssz.utils import (
    merkleize,
    mix_in_length,
    pack,
    read_exact,
    s_decode_offset,
)

TSerializable = TypeVar("TSerializable")
TDeserialized = TypeVar("TDeserialized")

EMPTY_LIST_HASH_TREE_ROOT = mix_in_length(merkleize(pack([])), 0)


class EmptyList(BaseCompositeSedes[Sequence[TSerializable], Tuple[TSerializable, ...]]):
    is_fixed_sized = False

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

    def hash_tree_root(self, value: Sequence[TSerializable]) -> bytes:
        if len(value):
            raise ValueError("Cannot compute tree hash for non-empty value using `EmptyList` sedes")
        return EMPTY_LIST_HASH_TREE_ROOT


empty_list = EmptyList()


TSedesPairs = Tuple[Tuple[BaseSedes[TSerializable, TDeserialized], TSerializable], ...]


class List(CompositeSedes[Sequence[TSerializable], Tuple[TDeserialized, ...]]):
    def __init__(self,
                 element_sedes: BaseSedes[TSerializable, TDeserialized] = None,
                 ) -> None:
        # This sedes object corresponds to each element of the iterable
        self.element_sedes = element_sedes

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
                    f"Invalid length. List is comprised of a fixed size sedes "
                    f"but total serialized data is not an even multiple of the "
                    f"element size. data length: {len(data)}  element size: "
                    f"{element_size}"
                )
            for segment in partition(element_size, data):
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
    def hash_tree_root(self, value: Iterable[TSerializable]) -> bytes:
        if len(value) == 0:
            return EMPTY_LIST_HASH_TREE_ROOT
        elif isinstance(self.element_sedes, BasicSedes):
            serialized_items = tuple(
                self.element_sedes.serialize(element)
                for element in value
            )
            length = len(serialized_items)
            merkle_leaves = pack(serialized_items)
        else:
            merkle_leaves = tuple(
                self.element_sedes.hash_tree_root(element)
                for element in value
            )
            length = len(merkle_leaves)

        return mix_in_length(merkleize(merkle_leaves), length)
