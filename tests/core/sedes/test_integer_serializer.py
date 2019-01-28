import pytest

from ssz import (
    DeserializationError,
    SerializationError,
    decode,
    encode,
)
from ssz.sedes import (
    uint8,
    uint16,
    uint32,
    uint64,
)


@pytest.mark.parametrize(
    'value,sedes,expected',
    (
        (0, uint8, b'\x00'),
        (5, uint8, b'\x05'),
        (127, uint8, b'\x7f'),
        (255, uint8, b'\xff'),

        (0, uint16, b'\x00\x00'),
        (5, uint16, b'\x05\x00'),
        (127, uint16, b'\x7f\x00'),
        (256, uint16, b'\x00\x01'),
        (1024, uint16, b'\x00\x04'),
        (65535, uint16, b'\xff\xff'),

        (0, uint32, b'\x00\x00\x00\x00'),
        (5, uint32, b'\x05\x00\x00\x00'),
        (65536, uint32, b'\x00\x00\x01\x00'),
        (4294967295, uint32, b'\xff\xff\xff\xff'),

        (0, uint64, b'\x00\x00\x00\x00\x00\x00\x00\x00'),
        (18446744073709551615, uint64, b'\xff\xff\xff\xff\xff\xff\xff\xff'),
    ),
)
def test_integer_serialize_values(value, sedes, expected):
    assert sedes.serialize(value) == expected


@pytest.mark.parametrize(
    'value,sedes',
    (
        # Negative values to be serialized
        (-5, uint32),
        # Input Overflow by sedes object
        (256, uint8),
        (65536, uint16),
        (4294967296, uint32),
        (18446744073709551616, uint64),
    ),
)
def test_integer_serialize_bad_values(value, sedes):
    with pytest.raises(SerializationError):
        sedes.serialize(value)


@pytest.mark.parametrize(
    'value',
    (
        5,
        10,
        128,
        256,
    ),
)
def test_ssz_encode_integer_serialize_bad_values(value):
    with pytest.raises(TypeError):
        encode(value)


@pytest.mark.parametrize(
    'value,sedes,expected',
    (
        (b'\x05', uint8, 5),
        (b'\x05\x00', uint16, 5),
        (b'\x05\x00\x00\x00', uint32, 5),
        (b'\x7f', uint8, 127),
        (b'\xff', uint8, 255),
        (b'\xff\xff', uint16, 65535),
    ),
)
def test_integer_deserialize_values(value, sedes, expected):
    assert sedes.deserialize(value) == expected


@pytest.mark.parametrize(
    'value,sedes',
    (
        # Values too short
        (b'\x05', uint16),
        (b'\x7f', uint16),
        (b'\x05\x00', uint32),
        (b'\x05\x00\x00\x00', uint64),

        # Values too long
        (b'\x05\x00\x05', uint16),
        (b'\x7f\x00\x7f', uint16),
        (b'\x05\x00\x05\x00\x05\x00', uint32),
        (b'\x00\x00\x00\x05\x00\x00\x00\x05\x00\x00\x00\x05', uint64),
        (b'\x05\x00\x00\x00\x05\x00\x00\x00\x05\x00\x00\x00', uint64),
    ),
)
def test_integer_deserialize_bad_values(value, sedes):
    with pytest.raises(DeserializationError):
        sedes.deserialize(value)


@pytest.mark.parametrize(
    'value,sedes',
    (
        (0, uint8),
        (1, uint8),
        (0, uint16),
        (1, uint16),

        (127, uint8),
        (255, uint8),
        (127, uint16),
        (255, uint16),
    ),
)
def test_integer_round_trip(value, sedes):
    assert sedes.deserialize(sedes.serialize(value)) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        (0, 'uint8'),
        (1, 'uint8'),
        (0, 'uint16'),
        (1, 'uint16'),

        (0, uint8),
        (1, uint8),
        (0, uint16),
        (1, uint16),

        (127, 'uint8'),
        (255, 'uint8'),
        (127, 'uint16'),
        (255, 'uint16'),

        (127, uint8),
        (255, uint8),
        (127, uint16),
        (255, uint16),
    ),
)
def test_integer_round_trip_codec(value, sedes):
    if isinstance(sedes, str):
        sedes_obj = eval(sedes)
    else:
        sedes_obj = sedes
    assert decode(encode(value, sedes), sedes_obj) == value


def test_fixed_length():
    for i in (0, 1, 255, 256**2, 256**3, 256**4 - 1):
        assert len(uint32.serialize(i)) == 4
