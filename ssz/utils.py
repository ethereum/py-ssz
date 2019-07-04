import collections
from typing import (
    IO,
    Sequence,
    Tuple,
)

from eth_typing import (
    Hash32,
)
from eth_utils.toolz import (
    partition,
)

from ssz.constants import (
    CHUNK_SIZE,
    EMPTY_CHUNK,
    OFFSET_SIZE,
)
from ssz.exceptions import (
    DeserializationError,
)
from ssz.hash import (
    hash_eth2,
)

ZERO_BYTES32 = b'\x00' * 32
zerohashes = [ZERO_BYTES32]
for layer in range(1, 100):
    zerohashes.append(hash_eth2(zerohashes[layer - 1] + zerohashes[layer - 1]))


def get_duplicates(values):
    counts = collections.Counter(values)
    return tuple(
        item
        for item, num in counts.items()
        if num > 1
    )


def read_exact(num_bytes: int, stream: IO[bytes]) -> bytes:
    data = stream.read(num_bytes)
    if len(data) != num_bytes:
        raise DeserializationError(f"Tried to read {num_bytes}. Only got {len(data)} bytes")
    return data


def encode_offset(offset: int) -> bytes:
    return offset.to_bytes(OFFSET_SIZE, 'little')


def decode_offset(data: bytes) -> int:
    return int.from_bytes(data, 'little')


def s_decode_offset(stream: IO[bytes]) -> int:
    data = read_exact(OFFSET_SIZE, stream)
    return decode_offset(data)


def get_items_per_chunk(item_size: int) -> int:
    if item_size < 0:
        raise ValueError("Item size must be positive integer")
    elif item_size == 0:
        return 1
    elif CHUNK_SIZE % item_size != 0:
        raise ValueError("Item size must be a divisor of chunk size")
    elif item_size <= CHUNK_SIZE:
        return CHUNK_SIZE // item_size
    else:
        raise Exception("Invariant: unreachable")


def pad_zeros(value: bytes) -> bytes:
    assert len(value) < CHUNK_SIZE
    return bytes(value.ljust(CHUNK_SIZE, b"\x00"))


def to_chuncks(packed_data) -> Tuple[bytes]:
    size = len(packed_data)
    number_of_full_chunks = size // CHUNK_SIZE
    last_chunk_is_full = size % CHUNK_SIZE == 0

    full_chunks = tuple(
        packed_data[chunk_index * CHUNK_SIZE:(chunk_index + 1) * CHUNK_SIZE]
        for chunk_index in range(number_of_full_chunks)
    )
    if last_chunk_is_full:
        return full_chunks
    else:
        last_chunk = packed_data[number_of_full_chunks * CHUNK_SIZE:].ljust(CHUNK_SIZE, b"\x00")
        return full_chunks + (last_chunk,)


def pack(serialized_values: Sequence[bytes]) -> Tuple[Hash32, ...]:
    if len(serialized_values) == 0:
        return (EMPTY_CHUNK,)

    data = b''.join([value for value in serialized_values])
    return to_chuncks(data)


def pack_bytes(byte_string: bytes) -> Tuple[Hash32]:
    size = len(byte_string)
    if size == 0:
        return (EMPTY_CHUNK,)

    return to_chuncks(byte_string)


def pack_bitvector_bitlist(values) -> Tuple[Hash32]:
    as_bytearray = [0] * ((len(values) + 7) // 8)
    for i in range(len(values)):
        as_bytearray[i // 8] |= values[i] << (i % 8)
    packed = bytes(as_bytearray)
    return to_chuncks(packed)


def get_next_power_of_two(value: int) -> int:
    if value <= 0:
        return 1
    else:
        return 2**(value - 1).bit_length()


def hash_layer(child_layer: Sequence[bytes]) -> Tuple[Hash32, ...]:
    if len(child_layer) % 2 != 0:
        raise ValueError("Layer must have an even number of elements")

    child_pairs = partition(2, child_layer)
    parent_layer = tuple(
        hash_eth2(left_child + right_child)
        for left_child, right_child in child_pairs
    )
    return parent_layer


def merkleize(chunks: Sequence[Hash32], pad_for=1) -> Hash32:
    chunk_len = len(chunks)
    chunk_depth = max(chunk_len - 1, 0).bit_length()
    max_depth = max(chunk_depth, (pad_for - 1).bit_length())
    tmp_list = [None for _ in range(max_depth + 1)]

    def merge(leaf, leaf_index):
        node = leaf
        layer = 0
        while True:
            if leaf_index & (1 << layer) == 0:
                if leaf_index == chunk_len and layer < chunk_depth:
                    # Keep going if we are complementing the void to the next power of 2
                    node = hash_eth2(node + zerohashes[layer])
                else:
                    break
            else:
                node = hash_eth2(tmp_list[layer] + node)
            layer += 1
        tmp_list[layer] = node

    # Merge in leaf by leaf.
    for leaf_index in range(chunk_len):
        merge(chunks[leaf_index], leaf_index)

    # Complement with 0 if empty, or if not the right power of 2
    if 1 << chunk_depth != chunk_len:
        merge(zerohashes[0], chunk_len)

    # The next power of two may be smaller than the ultimate virtual size,
    # complement with zero-hashes at each depth.
    for layer in range(chunk_depth, max_depth):
        tmp_list[layer + 1] = hash_eth2(tmp_list[layer] + zerohashes[layer])

    return tmp_list[max_depth]


def mix_in_length(root: Hash32, length: int) -> Hash32:
    return hash_eth2(root + length.to_bytes(CHUNK_SIZE, "little"))
