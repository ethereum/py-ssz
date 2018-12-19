import pytest

from ssz import (
    DeserializationError,
    SerializationError,
    decode,
    encode,
)
from ssz.sedes import (
    bytes_sedes,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        (b"", b'\x00\x00\x00\x00'),
        (b"I", b'\x00\x00\x00\x01I'),
        (b"foo", b'\x00\x00\x00\x03foo'),
        (b"hello", b'\x00\x00\x00\x05hello'),

        (bytearray(b""), b'\x00\x00\x00\x00'),
        (bytearray(b"I"), b'\x00\x00\x00\x01I'),
        (bytearray(b"foo"), b'\x00\x00\x00\x03foo'),
        (bytearray(b"hello"), b'\x00\x00\x00\x05hello'),
    ),
)
def test_bytes_serialize_values(value, expected):
    assert bytes_sedes.serialize(value) == expected


@pytest.mark.parametrize(
    'value',
    (
        # Non-byte objects
        None,
        1,
        1.0,
        '',
        'True',
        [1, 2, 3],
        (1, 2, 3),
        {b"0": b"1"},
        {b"0", b"1", b"2", b"3"},
    ),
)
def test_bytes_serialize_bad_values(value):
    with pytest.raises(SerializationError):
        bytes_sedes.serialize(value)


@pytest.mark.parametrize(
    'value,expected',
    (
        (b'\x00\x00\x00\x00', b""),
        (b'\x00\x00\x00\x01I', b"I"),
        (b'\x00\x00\x00\x03foo', b"foo"),
        (b'\x00\x00\x00\x05hello', b"hello"),
    ),
)
def test_bytes_deserialize_values(value, expected):
    assert bytes_sedes.deserialize(value) == expected


@pytest.mark.parametrize(
    'value',
    (
        # Less than 4 bytes of serialized data
        b'\x00\x00\x01',

        # Insufficient serialized object data as per found out byte object length
        b'\x00\x00\x00\x04',

        # Serialized data given is more than what is required
        b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00'
    ),
)
def test_bytes_deserialization_bad_value(value):
    with pytest.raises(DeserializationError):
        bytes_sedes.deserialize(value)


@pytest.mark.parametrize(
    'value,expected',
    (
        (b"", b''),
        (b"I", b'I'),
        (b"foo", b'foo'),
        (b"hello", b'hello'),

        (bytearray(b""), b''),
        (bytearray(b"I"), b'I'),
        (bytearray(b"foo"), b'foo'),
        (bytearray(b"hello"), b'hello'),
    ),
)
def test_bytes_round_trip(value, expected):
    assert bytes_sedes.deserialize(bytes_sedes.serialize(value)) == expected


@pytest.mark.parametrize(
    'value,sedes',
    (
        (b"", 'bytes_sedes'),
        (b"I", 'bytes_sedes'),
        (b"foo", 'bytes_sedes'),
        (b"hello", 'bytes_sedes'),

        (b"", bytes_sedes),
        (b"I", bytes_sedes),
        (b"foo", bytes_sedes),
        (b"hello", bytes_sedes),
    ),
)
def test_bytes_round_trip_codec(value, sedes):
    if isinstance(sedes, str):
        sedes_obj = eval(sedes)
    else:
        sedes_obj = sedes
    assert decode(encode(value, sedes), sedes_obj) == value


@pytest.mark.parametrize(
    'value',
    (
        b"",
        b"I",
        b"foo",
        b"hello",
    ),
)
def test_bytes_round_trip_no_sedes(value):
    assert decode(encode(value), bytes_sedes) == value
