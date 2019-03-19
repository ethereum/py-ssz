import pytest

import ssz
from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes import (
    ByteVector,
    List,
    Vector,
    byte,
    byte_list,
)


@pytest.mark.parametrize(
    "value",
    tuple(bytes([byte_value]) for byte_value in range(256)),
)
def test_byte(value):
    assert ssz.encode(value, byte) == value
    assert ssz.decode(value, byte) == value


@pytest.mark.parametrize(
    "value",
    (
        b"",
        b"\x00\x00",
    )
)
def test_byte_invalid_length(value):
    with pytest.raises(SerializationError):
        ssz.encode(value, byte)
    with pytest.raises(DeserializationError):
        ssz.decode(value, byte)


@pytest.mark.parametrize(
    "value",
    (
        b"",
        b"\x00",
        b"\x00\x01\x02\x03",
    )
)
def test_byte_list(value):
    serialized_value = ssz.encode(value, byte_list)
    assert serialized_value == ssz.encode(
        tuple(bytes([byte_value]) for byte_value in value),
        List(byte),
    )
    assert ssz.decode(serialized_value, byte_list) == value


@pytest.mark.parametrize(
    "value",
    (
        b"",
        b"\x00",
        b"\x00\x01\x02\x03",
    )
)
def test_byte_vector(value):
    byte_vector = ByteVector(len(value))
    serialized_value = ssz.encode(value, byte_vector)
    assert serialized_value == ssz.encode(
        tuple(bytes([byte_value]) for byte_value in value),
        Vector(len(value), byte),
    )
    assert ssz.decode(serialized_value, byte_vector) == value


@pytest.mark.parametrize(
    ("value", "expected_length"),
    (
        (b"", 1),
        (b"\x00", 0),
        (b"\x00", 2),
        (b"\x00\x01\x02\x03", 32),
        (b"\xff" * 64, 32),
    )
)
def test_byte_vector_invalid_length(value, expected_length):
    byte_vector = ByteVector(expected_length)
    with pytest.raises(SerializationError):
        ssz.encode(value, byte_vector)

    properly_serialized_value = ssz.encode(value, ByteVector(len(value)))
    with pytest.raises(DeserializationError):
        ssz.decode(properly_serialized_value, byte_vector)
