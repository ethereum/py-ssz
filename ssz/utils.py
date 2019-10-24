import collections
import functools
from typing import IO, Any, Sequence, Tuple

from eth_typing import Hash32

from ssz.constants import BASE_TYPES, CHUNK_SIZE, EMPTY_CHUNK, OFFSET_SIZE, ZERO_HASHES
from ssz.exceptions import DeserializationError
from ssz.hash import hash_eth2
from ssz.typing import CacheObj


def get_duplicates(values):
    counts = collections.Counter(values)
    return tuple(item for item, num in counts.items() if num > 1)


def read_exact(num_bytes: int, stream: IO[bytes]) -> bytes:
    data = stream.read(num_bytes)
    if len(data) != num_bytes:
        raise DeserializationError(
            f"Tried to read {num_bytes}. Only got {len(data)} bytes"
        )
    return data


def encode_offset(offset: int) -> bytes:
    return offset.to_bytes(OFFSET_SIZE, "little")


def decode_offset(data: bytes) -> int:
    return int.from_bytes(data, "little")


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
    if len(value) >= CHUNK_SIZE:
        raise ValueError(
            f"The length of given value {len(value)} should be less than CHUNK_SIZE ({CHUNK_SIZE})"
        )
    return value.ljust(CHUNK_SIZE, b"\x00")


@functools.lru_cache(maxsize=2 ** 12)
def to_chunks(packed_data: bytes) -> Tuple[bytes, ...]:
    size = len(packed_data)
    number_of_full_chunks = size // CHUNK_SIZE
    last_chunk_is_full = size % CHUNK_SIZE == 0

    full_chunks = tuple(
        packed_data[chunk_index * CHUNK_SIZE : (chunk_index + 1) * CHUNK_SIZE]
        for chunk_index in range(number_of_full_chunks)
    )
    if last_chunk_is_full:
        return full_chunks
    else:
        last_chunk = pad_zeros(packed_data[number_of_full_chunks * CHUNK_SIZE :])
        return full_chunks + (last_chunk,)


@functools.lru_cache(maxsize=2 ** 12)
def pack(serialized_values: Sequence[bytes]) -> Tuple[Hash32, ...]:
    if len(serialized_values) == 0:
        return (EMPTY_CHUNK,)

    data = b"".join(serialized_values)
    return to_chunks(data)


@functools.lru_cache(maxsize=2 ** 12)
def pack_bytes(byte_string: bytes) -> Tuple[bytes, ...]:
    if len(byte_string) == 0:
        return (EMPTY_CHUNK,)

    return to_chunks(byte_string)


@functools.lru_cache(maxsize=2 ** 12)
def pack_bits(values: Sequence[bool]) -> Tuple[Hash32]:
    as_bytearray = get_serialized_bytearray(values, len(values), extra_byte=False)
    packed = bytes(as_bytearray)
    return to_chunks(packed)


def get_next_power_of_two(value: int) -> int:
    if value <= 0:
        return 1
    else:
        return 2 ** (value - 1).bit_length()


def _get_chunk_and_max_depth(
    chunks: Sequence[Hash32], limit: int, chunk_len: int
) -> Tuple[int, int]:
    chunk_depth = max(chunk_len - 1, 0).bit_length()
    max_depth = max(chunk_depth, (limit - 1).bit_length())
    if max_depth > len(ZERO_HASHES):
        raise ValueError(f"The number of layers is greater than {len(ZERO_HASHES)}")

    return chunk_depth, max_depth


def _get_merkleized_result(
    chunks: Sequence[Hash32],
    chunk_len: int,
    chunk_depth: int,
    max_depth: int,
    cache: CacheObj,
) -> Tuple[Hash32, CacheObj]:
    merkleized_result_per_layers = [None for _ in range(max_depth + 1)]

    def merge(leaf: bytes, leaf_index: int) -> None:
        node = leaf
        layer = 0
        while True:
            if leaf_index & (1 << layer) == 0:
                if leaf_index == chunk_len and layer < chunk_depth:
                    # Keep going if we are complementing the void to the next power of 2
                    key = node + ZERO_HASHES[layer]
                    if key not in cache:
                        cache[key] = hash_eth2(key)
                    node = cache[key]
                else:
                    break
            else:
                key = merkleized_result_per_layers[layer] + node
                if key not in cache:
                    cache[key] = hash_eth2(key)
                node = cache[key]
            layer += 1

        merkleized_result_per_layers[layer] = node

    # Merge in leaf by leaf.
    for leaf_index in range(chunk_len):
        merge(chunks[leaf_index], leaf_index)

    # Complement with 0 if empty, or if not the right power of 2
    if 1 << chunk_depth != chunk_len:
        merge(ZERO_HASHES[0], chunk_len)

    # The next power of two may be smaller than the ultimate virtual size,
    # complement with zero-hashes at each depth.
    for layer in range(chunk_depth, max_depth):
        key = merkleized_result_per_layers[layer] + ZERO_HASHES[layer]
        if key not in cache:
            cache[key] = hash_eth2(
                merkleized_result_per_layers[layer] + ZERO_HASHES[layer]
            )
        merkleized_result_per_layers[layer + 1] = cache[key]

    root = merkleized_result_per_layers[max_depth]

    return root, cache


def merkleize_with_cache(
    chunks: Sequence[Hash32], cache: CacheObj, limit: int = None
) -> Tuple[Hash32, CacheObj]:
    chunk_len = len(chunks)
    if limit is None:
        limit = chunk_len
    chunk_depth, max_depth = _get_chunk_and_max_depth(chunks, limit, chunk_len)

    if limit == 0:
        return ZERO_HASHES[0], cache

    return _get_merkleized_result(
        chunks=chunks,
        chunk_len=chunk_len,
        chunk_depth=chunk_depth,
        max_depth=max_depth,
        cache=cache,
    )


def merkleize(chunks: Sequence[Hash32], limit: int = None) -> Hash32:
    root, _ = merkleize_with_cache(chunks, {}, limit)
    return root


def mix_in_length(root: Hash32, length: int) -> Hash32:
    return hash_eth2(root + length.to_bytes(CHUNK_SIZE, "little"))


def get_serialized_bytearray(
    value: Sequence[bool], bit_count: int, extra_byte: bool
) -> bytearray:
    if extra_byte:
        # Serialize Bitlist
        as_bytearray = bytearray(bit_count // 8 + 1)
    else:
        # Serialize Bitvector
        as_bytearray = bytearray((bit_count + 7) // 8)

    for i in range(bit_count):
        as_bytearray[i // 8] |= value[i] << (i % 8)
    return as_bytearray


def is_immutable_field_value(value: Any) -> bool:
    return type(value) in BASE_TYPES or (
        isinstance(value, tuple)
        and (len(value) == 0 or is_immutable_field_value(value[0]))
    )
