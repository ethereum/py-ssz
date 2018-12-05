import pytest

from ssz import (
    DeserializationError,
    SerializationError,
    decode,
    encode,
)
from ssz.sedes import (
    Integer,
    int8,
    int16,
    int32,
    uint8,
    uint16,
    uint32,
    uint64,
)


@pytest.mark.parametrize(
    'value,serializer,expected',
    (
        (0, 'int8', b'\x00'),
        (1, 'int8', b'\x01'),
        (5, 'int8', b'\x05'),
        (5, 'int16', b'\x00\x05'),
        (5, 'int32', b'\x00\x00\x00\x05'),
        (127, 'int8', b'\x7f'),
        (127, 'int16', b'\x00\x7f'),
        (-127, 'int8', b'\x81'),
        (-128, 'int8', b'\x80'),
        (256, 'int16', b'\x01\x00'),
        (1024, 'int16', b'\x04\x00'),
    ),
)
def test_integer_serialize_values(value, serializer, expected):
    sedes = Integer(serializer)
    assert sedes.serialize(value) == expected


@pytest.mark.parametrize(
    'value,serializer,expected',
    (
        (5, 'uint8', b'\x05'),
        (5, 'uint16', b'\x00\x05'),
        (5, 'uint32', b'\x00\x00\x00\x05'),
        (127, 'uint8', b'\x7f'),
        (255, 'uint8', b'\xff'),
        (65535, 'uint16', b'\xff\xff'),
    ),
)
def test_unsigned_integer_serialize_values(value, serializer, expected):
    sedes = Integer(serializer)
    assert sedes.serialize(value) == expected


@pytest.mark.parametrize(
    'value,serializer',
    (
        (5, None),
        (5, ' '),
        (5, int32),
        (5, b'int32'),
        ('123', 'int32'),
        ('123', int32),
        (b'123', int32),
    ),
)
def test_any_integer_serialize_bad_values(value, serializer):
    with pytest.raises(SerializationError):
        sedes = Integer(serializer)
        sedes.serialize(value)


@pytest.mark.parametrize(
    'value,serializer',
    (
        (True, 'int32'),
        (False, 'int32'),
    ),
)
def test_rejects_bool(value, serializer):
    with pytest.raises(SerializationError):
        sedes = Integer(serializer)
        sedes.serialize(value)


@pytest.mark.parametrize(
    'deserializer,value,expected',
    (
        (int8, b'\x00', 0),
        (int8, b'\x01', 1),
        (int8, b'\x05', 5),
        (int16, b'\x00\x05', 5),
        (int32, b'\x00\x00\x00\x05', 5),
        (int8, b'\x7f', 127),
        (int16, b'\x00\x7f', 127),
        (int8, b'\x81', -127),
        (int8, b'\x80', -128),
        (int16, b'\x01\x00', 256),
        (int16, b'\x04\x00', 1024),
    ),
)
def test_integer_deserialization(deserializer, value, expected):
    assert deserializer.deserialize(value) == expected


@pytest.mark.parametrize(
    'deserializer,value,expected',
    (
        (uint8, b'\x05', 5),
        (uint16, b'\x00\x05', 5),
        (uint32, b'\x00\x00\x00\x05', 5),
        (uint8, b'\x7f', 127),
        (uint8, b'\xff', 255),
        (uint16, b'\xff\xff', 65535),
    ),
)
def test_unsigned_integer_deserialization(deserializer, value, expected):
    assert deserializer.deserialize(value) == expected


@pytest.mark.parametrize(
    'deserializer,value',
    (
        (uint16, b'\x05'),
        (uint32, b'\x00\x05'),
        (uint64, b'\x00\x00\x00\x05'),
        (uint16, b'\x7f'),
    ),
)
def test_any_integer_deserialization_bad_value(deserializer, value):
    with pytest.raises(DeserializationError):
        deserializer.deserialize(value)


@pytest.mark.parametrize(
    'serializer_type,value',
    (
        ('int8', -128),
        ('int8', 127),
        ('int16', -128),
        ('int16', 127),

        ('int16', 32767),
        ('int16', -32768),
        ('int32', 32767),
        ('int32', -32768),

        ('uint8', 0),
        ('uint8', 1),
        ('uint16', 0),
        ('uint16', 1),

        ('uint8', 127),
        ('uint8', 255),
        ('uint16', 127),
        ('uint16', 255),
    ),
)
def test_integer_round_trip(serializer_type, value):
    sedes = Integer(serializer_type)
    assert sedes.deserialize(sedes.serialize(value)) == value


@pytest.mark.parametrize(
    'serializer_type,value',
    (
        ('int8', -128),
        ('int8', 127),
        ('int16', -128),
        ('int16', 127),

        ('int16', 32767),
        ('int16', -32768),
        ('int32', 32767),
        ('int32', -32768),

        ('uint8', 0),
        ('uint8', 1),
        ('uint16', 0),
        ('uint16', 1),

        ('uint8', 127),
        ('uint8', 255),
        ('uint16', 127),
        ('uint16', 255),
    ),
)
def test_boolean_round_trip_codec(serializer_type, value):
    sedes = Integer(serializer_type)
    assert decode(encode(value, serializer_type), sedes) == value


def test_fixed_length():
    s = Integer('uint32')
    for i in (0, 1, 255, 256, 256**3, 256**4 - 1):
        assert len(s.serialize(i)) == 4
