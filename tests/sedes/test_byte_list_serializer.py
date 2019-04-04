import pytest

from ssz import (
    decode,
    encode,
)
from ssz.sedes import (
    byte_list,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        (b"", b''),
        (b"I", b'I'),
        (b"foo", b'foo'),
        (b"hello", b'hello'),
    ),
)
def test_bytes_serialize_values(value, expected):
    assert byte_list.serialize(value) == expected
    assert byte_list.serialize(bytearray(value)) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        (b'', b""),
        (b'I', b"I"),
        (b'foo', b"foo"),
        (b'hello', b"hello"),
    ),
)
def test_bytes_deserialize_values(value, expected):
    assert byte_list.deserialize(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        (b"", b''),
        (b"I", b'I'),
        (b"foo", b'foo'),
        (b"hello", b'hello'),
    ),
)
def test_bytes_round_trip(value, expected):
    assert byte_list.deserialize(byte_list.serialize(value)) == expected
    assert byte_list.deserialize(byte_list.serialize(bytearray(value))) == expected


@pytest.mark.parametrize(
    'value,sedes',
    (
        (b"", 'byte_list'),
        (b"I", 'byte_list'),
        (b"foo", 'byte_list'),
        (b"hello", 'byte_list'),

        (b"", byte_list),
        (b"I", byte_list),
        (b"foo", byte_list),
        (b"hello", byte_list),
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
    assert decode(encode(value), byte_list) == value
