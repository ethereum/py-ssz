import pytest

from ssz import (
    DeserializationError,
    SerializationError,
    decode,
    encode,
)
from ssz.sedes import (
    Hash,
    address,
    hash32,
)


@pytest.mark.parametrize(
    'num_bytes',
    (
        0,
        -10,
        -100,
    ),
)
def test_reject_hash_object_negative_bytes(num_bytes):
    with pytest.raises(ValueError):
        Hash(num_bytes)


def test_hash_serialize_values():
    for num_bytes in range(1, 33):
        value = b'\x01' * num_bytes
        assert Hash(num_bytes).serialize(value) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        (b'\x01' * 32, Hash(16)),
        (b'\x01' * 32, Hash(20)),
        (b'\x01' * 16, Hash(20)),
        (b'\x01' * 16, hash32),
        (b'\x01' * 32, Hash(20)),
    ),
)
def test_hash_serialize_bad_values(value, sedes):
    with pytest.raises(SerializationError):
        sedes.serialize(value)


def test_hash_deserialize_values():
    for num_bytes in range(1, 33):
        value = b'\x01' * num_bytes
        assert Hash(num_bytes).deserialize(value) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        # Values too short
        (b'\x01' * 15, Hash(16)),
        (b'\x01' * 16, Hash(20)),
        (b'\x01' * 10, Hash(20)),
        (b'\x01' * 5, Hash(20)),
        (b'\x01' * 16, Hash(32)),

        # Values too long
        (b'\x01' * 20, Hash(16)),
        (b'\x01' * 25, Hash(20)),
        (b'\x01' * 40, Hash(32)),
    ),
)
def test_hash_deserialize_bad_values(value, sedes):
    with pytest.raises(DeserializationError):
        sedes.deserialize(value)


def test_hash_round_trip():
    for num_bytes in range(1, 33):
        value = b'\x01' * num_bytes
        sedes_obj = Hash(num_bytes)
        assert sedes_obj.deserialize(sedes_obj.serialize(value)) == value


@pytest.mark.parametrize(
    'value',
    (
        b'\x00' * 20,
        b'\x01' * 20,
    ),
)
def test_address_round_trip(value):
    assert address.deserialize(address.serialize(value)) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        (b'\x01' * 32, 'hash32'),
        (b'\x01' * 32, hash32),
        (b'\x01' * 32, Hash(32)),
        (b'\x01' * 64, Hash(64)),
    ),
)
def test_hash_round_trip_codec(value, sedes):
    if isinstance(sedes, str):
        sedes_obj = eval(sedes)
    else:
        sedes_obj = sedes
    assert decode(encode(value, sedes), sedes_obj) == value


@pytest.mark.parametrize(
    'value',
    (
        b'\x00' * 20,
        b'\x01' * 20,
    ),
)
def test_address_round_trip_codec(value):
    assert decode(encode(value, address), address) == value
