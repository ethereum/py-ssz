import itertools

import pytest

import ssz
from ssz.constants import CHUNK_SIZE, EMPTY_CHUNK
from ssz.hash import hash_eth2 as h
from ssz.sedes import Bitlist, Bitvector, ByteVector, Container, List, Vector, uint128
from ssz.utils import pad_zeros

bytes16 = ByteVector(16)
EMPTY_BYTES = b"\x00" * 16
A_BYTES = b"\xaa" * 16
B_BYTES = b"\xbb" * 16
C_BYTES = b"\xcc" * 16
D_BYTES = b"\xdd" * 16
E_BYTES = b"\xee" * 16


@pytest.mark.parametrize(
    ("serialized_uints128", "result"),
    (
        ((A_BYTES,), A_BYTES + EMPTY_BYTES),
        ((A_BYTES, B_BYTES), A_BYTES + B_BYTES),
        ((A_BYTES, B_BYTES, C_BYTES), h(A_BYTES + B_BYTES + C_BYTES + EMPTY_BYTES)),
        (
            (A_BYTES, B_BYTES, C_BYTES, D_BYTES, E_BYTES),
            h(h(A_BYTES + B_BYTES + C_BYTES + D_BYTES) + h(E_BYTES + 3 * EMPTY_BYTES)),
        ),
    ),
)
def test_vector_of_basics(serialized_uints128, result):
    sedes = Vector(uint128, len(serialized_uints128))
    int_values = tuple(ssz.decode(value, uint128) for value in serialized_uints128)
    assert ssz.get_hash_tree_root(int_values, sedes) == result


@pytest.mark.parametrize(
    ("serialized_uints128", "max_length", "result"),
    (
        ((), 4, h(h(EMPTY_CHUNK + EMPTY_CHUNK) + (0).to_bytes(CHUNK_SIZE, "little"))),
        (
            (A_BYTES,),
            4,
            h(
                h(A_BYTES + EMPTY_BYTES + EMPTY_CHUNK)
                + (1).to_bytes(CHUNK_SIZE, "little")
            ),
        ),
        (
            (A_BYTES, B_BYTES),
            4,
            h(h(A_BYTES + B_BYTES + EMPTY_CHUNK) + (2).to_bytes(CHUNK_SIZE, "little")),
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            4,
            h(
                h(A_BYTES + B_BYTES + C_BYTES + EMPTY_BYTES)
                + (3).to_bytes(CHUNK_SIZE, "little")
            ),
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES, D_BYTES, E_BYTES),
            8,
            h(
                h(
                    h(A_BYTES + B_BYTES + C_BYTES + D_BYTES)
                    + h(E_BYTES + 3 * EMPTY_BYTES)
                )
                + (5).to_bytes(CHUNK_SIZE, "little")
            ),
        ),
    ),
)
def test_list_of_basic(serialized_uints128, max_length, result):
    # item_length = 128 / 8 = 16
    int_values = tuple(ssz.decode(value, uint128) for value in serialized_uints128)
    assert ssz.get_hash_tree_root(int_values, List(uint128, max_length)) == result


@pytest.mark.parametrize(
    ("bytes16_vector", "result"),
    (
        ((A_BYTES,), A_BYTES + EMPTY_BYTES),
        ((A_BYTES, B_BYTES), h(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            h(
                h(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)
                + h(C_BYTES + EMPTY_BYTES * 3)
            ),
        ),
    ),
)
def test_vector_of_composite(bytes16_vector, result):
    sedes = Vector(ByteVector(16), len(bytes16_vector))
    assert ssz.get_hash_tree_root(bytes16_vector, sedes) == result


@pytest.mark.parametrize(
    ("bytes16_list", "max_length", "result"),
    (
        (
            (),
            4,
            h(
                h(h(EMPTY_CHUNK + EMPTY_CHUNK) + h(EMPTY_CHUNK + EMPTY_CHUNK))
                + (0).to_bytes(CHUNK_SIZE, "little")
            ),
        ),
        (
            (A_BYTES,),
            4,
            h(
                h(h(A_BYTES + EMPTY_BYTES + EMPTY_CHUNK) + h(EMPTY_CHUNK + EMPTY_CHUNK))
                + (1).to_bytes(CHUNK_SIZE, "little")
            ),
        ),
        (
            (A_BYTES, B_BYTES),
            4,
            h(
                h(
                    h(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)
                    + h(EMPTY_CHUNK + EMPTY_CHUNK)
                )
                + (2).to_bytes(CHUNK_SIZE, "little")
            ),
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            4,
            h(
                h(
                    h(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)
                    + h(C_BYTES + EMPTY_BYTES + EMPTY_CHUNK)
                )
                + (3).to_bytes(CHUNK_SIZE, "little")
            ),
        ),
    ),
)
def test_list_of_composite(bytes16_list, max_length, result):
    # item_length = 32
    sedes = List(bytes16, max_length)
    assert ssz.get_hash_tree_root(bytes16_list, sedes) == result


@pytest.mark.parametrize(
    ("bytes16_fields", "result"),
    (
        ((A_BYTES,), A_BYTES + EMPTY_BYTES),
        ((A_BYTES, B_BYTES), h(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            h(
                h(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)
                + h(C_BYTES + EMPTY_BYTES * 3)
            ),
        ),
    ),
)
def test_container(bytes16_fields, result):
    sedes = Container(tuple(itertools.repeat(bytes16, len(bytes16_fields))))
    assert ssz.get_hash_tree_root(bytes16_fields, sedes) == result


@pytest.mark.parametrize(
    ("size", "value", "result"),
    (
        (8, (1, 1, 0, 1, 0, 1, 0, 0), b"\x2b" + b"\x00" * 31),
        (512, ((True,) * 512), h(b"\xff" * 32 + b"\xff" * 32)),
    ),
)
def test_bitvector(size, value, result):
    foo = Bitvector(size)
    assert ssz.get_hash_tree_root(value, foo) == result


@pytest.mark.parametrize(
    ("size", "value", "result"),
    (
        (8, (1, 1, 0, 1, 0, 1, 0, 0), h(pad_zeros(b"\x2b") + pad_zeros(b"\x08"))),
        (
            512,
            tuple(1 for i in range(512)),
            h(h(b"\xff" * 32 + b"\xff" * 32) + pad_zeros(b"\x00\x02")),
        ),
    ),
)
def test_bitlist(size, value, result):
    foo = Bitlist(size)
    assert ssz.get_hash_tree_root(value, foo) == result
