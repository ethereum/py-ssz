import pytest

from hypothesis import (
    given,
    strategies as st,
)

from ssz.constants import (
    CHUNK_SIZE,
    EMPTY_CHUNK,
    MAX_ZERO_HASHES_LAYER,
)
from ssz.hash import (
    hash_eth2,
)
from ssz.utils import (
    merkleize,
    mix_in_length,
    pack,
    pack_bytes,
    pad_zeros,
)

HALF_CHUNK_SIZE = CHUNK_SIZE // 2
A_CHUNK = b"\xaa" * CHUNK_SIZE
B_CHUNK = b"\xbb" * CHUNK_SIZE
C_CHUNK = b"\xcc" * CHUNK_SIZE
D_CHUNK = b"\xdd" * CHUNK_SIZE


@pytest.mark.parametrize(
    ("values", "packed"),
    (
        ((), (EMPTY_CHUNK,)),
        ((b"\xaa",), (pad_zeros(b"\xaa"),)),
        ((b"\xaa" * HALF_CHUNK_SIZE,), (pad_zeros(b"\xaa" * HALF_CHUNK_SIZE),)),
        ((b"\xaa" * CHUNK_SIZE,), (b"\xaa" * CHUNK_SIZE,)),
        ((b"\xaa", b"\xbb", b"\xcc"), (pad_zeros(b"\xaa\xbb\xcc"),)),
        (
            (
                b"\xaa" * HALF_CHUNK_SIZE,
                b"\xbb" * HALF_CHUNK_SIZE,
                b"\xcc" * HALF_CHUNK_SIZE,
            ),
            (
                (b"\xaa" * HALF_CHUNK_SIZE + b"\xbb" * HALF_CHUNK_SIZE),
                (pad_zeros(b"\xcc" * HALF_CHUNK_SIZE)),
            ),
        ),
    ),
)
def test_pack(values, packed):
    assert pack(values) == packed


@given(st.binary())
def test_pack_bytes(data):
    byte_data = tuple(bytes([byte]) for byte in data)
    assert pack_bytes(data) == pack(byte_data)


@pytest.mark.parametrize(
    ("chunks", "root"),
    (
        ((A_CHUNK,), A_CHUNK),
        ((A_CHUNK, B_CHUNK), hash_eth2(A_CHUNK + B_CHUNK)),
        (
            (A_CHUNK, B_CHUNK, C_CHUNK),
            hash_eth2(hash_eth2(A_CHUNK + B_CHUNK) + hash_eth2(C_CHUNK + EMPTY_CHUNK)),
        ),
        (
            (A_CHUNK, B_CHUNK, C_CHUNK, D_CHUNK),
            hash_eth2(hash_eth2(A_CHUNK + B_CHUNK) + hash_eth2(C_CHUNK + D_CHUNK)),
        ),
    ),
)
def test_merkleize(chunks, root):
    assert merkleize(chunks) == root


@pytest.mark.parametrize(
    ("limit", "success"),
    ((2**MAX_ZERO_HASHES_LAYER, True), (2**MAX_ZERO_HASHES_LAYER + 1, False)),
)
def test_merkleize_edge_case(limit, success):
    chunks = (A_CHUNK,)
    if success:
        merkleize(chunks, limit=limit)
    else:
        with pytest.raises(ValueError):
            merkleize(chunks, limit=limit)


@pytest.mark.parametrize(
    ("root", "length", "result"),
    (
        (A_CHUNK, 0, hash_eth2(A_CHUNK + b"\x00" * 32)),
        (B_CHUNK, 1, hash_eth2(B_CHUNK + b"\x01" + b"\x00" * 31)),
        (C_CHUNK, 2**256 - 1, hash_eth2(C_CHUNK + b"\xff" * 32)),
    ),
)
def test_mix_in_length(root, length, result):
    assert mix_in_length(root, length) == result
