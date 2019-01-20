import pytest

from ssz import (
    DeserializationError,
    SerializationError,
    decode,
    encode,
)
from ssz.sedes import (
    BytesN,
    bytes32,
    bytes48,
    bytes96,
)


@pytest.mark.parametrize(
    'num_bytes',
    (
        0,
        -10,
        -100,
    ),
)
def test_reject_object_with_negative_bytes(num_bytes):
    with pytest.raises(ValueError):
        BytesN(num_bytes)


def test_serialize_values():
    for num_bytes in range(1, 33):
        value = b'\x01' * num_bytes
        assert BytesN(num_bytes).serialize(value) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        (b'\x01' * 32, BytesN(16)),
        (b'\x01' * 32, BytesN(20)),
        (b'\x01' * 16, BytesN(20)),
        (b'\x01' * 16, bytes32),
        (b'\x01' * 16, bytes48),
        (b'\x01' * 16, bytes96),
        (b'\x01' * 32, BytesN(20)),
    ),
)
def test_serialize_bad_values(value, sedes):
    with pytest.raises(SerializationError):
        sedes.serialize(value)


def test_hash_deserialize_values():
    for num_bytes in range(1, 33):
        value = b'\x01' * num_bytes
        assert BytesN(num_bytes).deserialize(value) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        # Values too short
        (b'\x01' * 15, BytesN(16)),
        (b'\x01' * 16, BytesN(20)),
        (b'\x01' * 10, BytesN(20)),
        (b'\x01' * 5, BytesN(20)),
        (b'\x01' * 16, BytesN(32)),

        # Values too long
        (b'\x01' * 20, BytesN(16)),
        (b'\x01' * 25, BytesN(20)),
        (b'\x01' * 40, BytesN(32)),
    ),
)
def test_deserialize_bad_values(value, sedes):
    with pytest.raises(DeserializationError):
        sedes.deserialize(value)


def test_round_trip():
    for num_bytes in range(1, 33):
        value = b'\x01' * num_bytes
        sedes_obj = BytesN(num_bytes)
        assert sedes_obj.deserialize(sedes_obj.serialize(value)) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        (b'\x01' * 32, 'bytes32'),
        (b'\x01' * 32, bytes32),
        (b'\x01' * 48, bytes48),
        (b'\x01' * 96, bytes96),
        (b'\x01' * 32, BytesN(32)),
        (b'\x01' * 64, BytesN(64)),
    ),
)
def test_round_trip_codec(value, sedes):
    if isinstance(sedes, str):
        sedes_obj = eval(sedes)
    else:
        sedes_obj = sedes
    assert decode(encode(value, sedes), sedes_obj) == value
