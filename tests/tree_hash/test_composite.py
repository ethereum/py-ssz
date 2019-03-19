import pytest

import ssz
from ssz.constants import (
    CHUNK_SIZE,
    EMPTY_CHUNK,
)
from ssz.hash import (
    hash_eth2,
)
from ssz.sedes import (
    ByteVector,
    Container,
    List,
    Vector,
    uint128,
)

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
        ((), EMPTY_CHUNK),
        ((A_BYTES,), A_BYTES + EMPTY_BYTES),
        ((A_BYTES, B_BYTES), A_BYTES + B_BYTES),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            hash_eth2(A_BYTES + B_BYTES + C_BYTES + EMPTY_BYTES),
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES, D_BYTES, E_BYTES),
            hash_eth2(
                hash_eth2(A_BYTES + B_BYTES + C_BYTES + D_BYTES) +
                hash_eth2(E_BYTES + 3 * EMPTY_BYTES)
            ),
        ),
    )
)
def test_vector_of_basics(serialized_uints128, result):
    sedes = Vector(len(serialized_uints128), uint128)
    int_values = tuple(ssz.decode(value, uint128) for value in serialized_uints128)
    assert ssz.hash_tree_root(int_values, sedes) == result


@pytest.mark.parametrize(
    ("serialized_uints128", "result"),
    (
        (
            (),
            hash_eth2(EMPTY_CHUNK + b"\x00".ljust(CHUNK_SIZE, b"\x00"))
        ),
        (
            (A_BYTES,),
            hash_eth2(A_BYTES + EMPTY_BYTES + b"\x01".ljust(CHUNK_SIZE, b"\x00"))
        ),
        (
            (A_BYTES, B_BYTES),
            hash_eth2(A_BYTES + B_BYTES + b"\x02".ljust(CHUNK_SIZE, b"\x00")),
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            hash_eth2(
                hash_eth2(A_BYTES + B_BYTES + C_BYTES + EMPTY_BYTES) +
                b"\x03".ljust(CHUNK_SIZE, b"\x00")
            ),
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES, D_BYTES, E_BYTES),
            hash_eth2(
                hash_eth2(
                    hash_eth2(A_BYTES + B_BYTES + C_BYTES + D_BYTES) +
                    hash_eth2(E_BYTES + 3 * EMPTY_BYTES)
                ) +
                b"\x05".ljust(CHUNK_SIZE, b"\x00")
            ),
        ),
    )
)
def test_list_of_basic(serialized_uints128, result):
    int_values = tuple(ssz.decode(value, uint128) for value in serialized_uints128)
    assert ssz.hash_tree_root(int_values, List(uint128)) == result


@pytest.mark.parametrize(
    ("bytes16_vector", "result"),
    (
        ((), EMPTY_CHUNK),
        ((A_BYTES,), A_BYTES + EMPTY_BYTES),
        (
            (A_BYTES, B_BYTES),
            hash_eth2(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            hash_eth2(
                hash_eth2(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES) +
                hash_eth2(C_BYTES + EMPTY_BYTES * 3),
            ),
        ),
    )
)
def test_vector_of_composite(bytes16_vector, result):
    sedes = Vector(len(bytes16_vector), ByteVector(16))
    assert ssz.hash_tree_root(bytes16_vector, sedes) == result


@pytest.mark.parametrize(
    ("bytes16_list", "result"),
    (
        ((), hash_eth2(EMPTY_CHUNK + b"\x00".ljust(CHUNK_SIZE, b"\x00"))),
        ((A_BYTES,), hash_eth2(A_BYTES + EMPTY_BYTES + b"\x01".ljust(CHUNK_SIZE, b"\x00"))),
        (
            (A_BYTES, B_BYTES),
            hash_eth2(
                hash_eth2(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES) +
                b"\x02".ljust(CHUNK_SIZE, b"\x00")
            ),
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            hash_eth2(
                hash_eth2(
                    hash_eth2(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES) +
                    hash_eth2(C_BYTES + EMPTY_BYTES * 3),
                ) +
                b"\x03".ljust(CHUNK_SIZE, b"\x00")
            )
        ),
    )
)
def test_list_of_composite(bytes16_list, result):
    sedes = List(bytes16)
    assert ssz.hash_tree_root(bytes16_list, sedes) == result


@pytest.mark.parametrize(
    ("bytes16_fields", "result"),
    (
        ((), EMPTY_CHUNK),
        ((A_BYTES,), A_BYTES + EMPTY_BYTES),
        (
            (A_BYTES, B_BYTES),
            hash_eth2(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES)
        ),
        (
            (A_BYTES, B_BYTES, C_BYTES),
            hash_eth2(
                hash_eth2(A_BYTES + EMPTY_BYTES + B_BYTES + EMPTY_BYTES) +
                hash_eth2(C_BYTES + EMPTY_BYTES * 3),
            ),
        ),
    )
)
def test_container(bytes16_fields, result):
    field_names = tuple(f"field{index}" for index in range(len(bytes16_fields)))
    sedes = Container(tuple(
        (field_name, bytes16) for field_name in field_names
    ))
    value = {
        field_name: field_value
        for field_name, field_value in zip(field_names, bytes16_fields)
    }
    assert ssz.hash_tree_root(value, sedes) == result
