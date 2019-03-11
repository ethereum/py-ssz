import pytest

from ssz import (
    DeserializationError,
    SerializationError,
    decode,
    encode,
)
from ssz.sedes import (
    List,
    boolean,
    byte_list,
    bytes32,
    bytes48,
    bytes96,
    empty_list,
    uint32,
)

boolean_list = List(boolean)
bytes32_list = List(bytes32)
bytes48_list = List(bytes48)
bytes96_list = List(bytes96)
byte_list_list = List(byte_list)
uint32_list = List(uint32)


@pytest.mark.parametrize(
    'value,sedes,expected',
    (
        # Serialize Empty Objects
        ([], uint32_list, b'\x00\x00\x00\x00'),
        ((), uint32_list, b'\x00\x00\x00\x00'),
        ([], bytes32_list, b'\x00\x00\x00\x00'),
        ((), bytes32_list, b'\x00\x00\x00\x00'),
        ([], bytes48_list, b'\x00\x00\x00\x00'),
        ((), bytes48_list, b'\x00\x00\x00\x00'),
        ([], bytes96_list, b'\x00\x00\x00\x00'),
        ((), bytes96_list, b'\x00\x00\x00\x00'),
        ([], boolean_list, b'\x00\x00\x00\x00'),
        ((), boolean_list, b'\x00\x00\x00\x00'),
        ([], byte_list_list, b'\x00\x00\x00\x00'),
        ((), byte_list_list, b'\x00\x00\x00\x00'),

        # Serialize uint32 Iterables
        (
            [0, 1, 2, 3, 4],
            uint32_list,
            b'\x14\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
            b'\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00',
        ),
        (
            (0, 1, 2, 3, 4),
            uint32_list,
            b'\x14\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
            b'\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00',
        ),
        (
            range(5),
            uint32_list,
            b'\x14\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
            b'\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00',
        ),

        # Serialize bytes32 Iterables
        ([b'\x00' * 32], bytes32_list, b'\x20\x00\x00\x00' + (b'\x00' * 32)),
        ([b'\x00' * 32, b'\x00' * 32], bytes32_list, b'\x40\x00\x00\x00' + (b'\x00' * 64)),
        ((b'\x00' * 32, b'\x00' * 32), bytes32_list, b'\x40\x00\x00\x00' + (b'\x00' * 64)),

        # Serialize bytes48 Iterables
        ([b'\x00' * 48], bytes48_list, b'\x30\x00\x00\x00' + (b'\x00' * 48)),
        ([b'\x00' * 48, b'\x00' * 48], bytes48_list, b'\x60\x00\x00\x00' + (b'\x00' * 96)),
        ((b'\x00' * 48, b'\x00' * 48), bytes48_list, b'\x60\x00\x00\x00' + (b'\x00' * 96)),

        # Serialize bytes96 Iterables
        ([b'\x00' * 96], bytes96_list, b'\x60\x00\x00\x00' + (b'\x00' * 96)),
        ([b'\x00' * 96, b'\x00' * 96], bytes96_list, b'\xc0\x00\x00\x00' + (b'\x00' * 192)),
        ((b'\x00' * 96, b'\x00' * 96), bytes96_list, b'\xc0\x00\x00\x00' + (b'\x00' * 192)),


        # Serialize boolean Iterables
        ([True, True, True, True], boolean_list, b'\x04\x00\x00\x00' + b'\x01' * 4),
        ((True, True, True, True), boolean_list, b'\x04\x00\x00\x00' + b'\x01' * 4),
        ([False, False, False, False], boolean_list, b'\x04\x00\x00\x00' + b'\x00' * 4),
        ((False, False, False, False), boolean_list, b'\x04\x00\x00\x00' + b'\x00' * 4),
        ([True, False, True, False], boolean_list, b'\x04\x00\x00\x00\x01\x00\x01\x00'),
        ((True, False, True, False), boolean_list, b'\x04\x00\x00\x00\x01\x00\x01\x00'),

        # Serialize bytes Iterables
        ([b'\x01'], byte_list_list, b'\x05\x00\x00\x00\x01\x00\x00\x00\x01'),
        (
            [b'\x01', b'\x02'],
            byte_list_list,
            b'\x0a\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x02',
        ),
        (
            [b'\x01\x02', b'\x02\x03'],
            byte_list_list,
            b'\x0c\x00\x00\x00'
            b'\x02\x00\x00\x00\x01\x02'
            b'\x02\x00\x00\x00\x02\x03',
        ),
    ),
)
def test_list_serialize_values(value, sedes, expected):
    assert sedes.serialize(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ([], b'\x00\x00\x00\x00'),
        ((), b'\x00\x00\x00\x00'),
    ),
)
def test_list_serialize_values_no_element_sedes(value, expected):
    assert encode(value) == expected


@pytest.mark.parametrize(
    'value,sedes',
    (
        # Serialize non-list objects
        ("foo", uint32_list),
        (b"foo", uint32_list),
        (bytearray(b"foo"), uint32_list),
        ("foo", bytes32_list),
        ("foo", bytes48_list),
        ("foo", bytes96_list),
        ("foo", boolean_list),
    ),
)
def test_list_serialize_bad_values(value, sedes):
    with pytest.raises(SerializationError):
        sedes.serialize(value)


@pytest.mark.parametrize(
    'value,sedes,expected',
    (
        # Deserialize Empty Objects
        (b'\x00\x00\x00\x00', empty_list, ()),
        (b'\x00\x00\x00\x00', uint32_list, ()),
        (b'\x00\x00\x00\x00', bytes32_list, ()),
        (b'\x00\x00\x00\x00', bytes48_list, ()),
        (b'\x00\x00\x00\x00', bytes96_list, ()),
        (b'\x00\x00\x00\x00', boolean_list, ()),

        # Deserialize uint32 Iterables
        (
            b'\x14\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
            b'\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00',
            uint32_list,
            (0, 1, 2, 3, 4),
        ),

        # Deserialize bytes32 Iterables
        (b'\x20\x00\x00\x00' + (b'\x00' * 32), bytes32_list, (b'\x00' * 32,)),
        (b'\x40\x00\x00\x00' + (b'\x00' * 64), bytes32_list, (b'\x00' * 32, b'\x00' * 32)),

        # Deserialize bytes48 Iterables
        (b'\x30\x00\x00\x00' + (b'\x00' * 48), bytes48_list, (b'\x00' * 48,)),
        (b'\x60\x00\x00\x00' + (b'\x00' * 96), bytes48_list, (b'\x00' * 48, b'\x00' * 48)),

        # Deserialize bytes96 Iterables
        (b'\x60\x00\x00\x00' + (b'\x00' * 96), bytes96_list, (b'\x00' * 96,)),
        (b'\xc0\x00\x00\x00' + (b'\x00' * 192), bytes96_list, (b'\x00' * 96, b'\x00' * 96)),

        # Deserialize boolean Iterables
        (b'\x04\x00\x00\x00' + b'\x01' * 4, boolean_list, (True, True, True, True)),
        (b'\x04\x00\x00\x00' + b'\x00' * 4, boolean_list, (False, False, False, False)),
        (b'\x04\x00\x00\x00\x01\x00\x01\x00', boolean_list, (True, False, True, False)),

        # Deserialize bytes Iterables
        # Serialize bytes Iterables
        (b'\x05\x00\x00\x00\x01\x00\x00\x00\x01', byte_list_list, (b'\x01',)),
        (
            b'\x0a\x00\x00\x00'
            b'\x01\x00\x00\x00\x01'
            b'\x01\x00\x00\x00\x02',
            byte_list_list,
            (b'\x01', b'\x02'),
        ),
        (
            b'\x0c\x00\x00\x00'
            b'\x02\x00\x00\x00\x01\x02'
            b'\x02\x00\x00\x00\x02\x03',
            byte_list_list,
            (b'\x01\x02', b'\x02\x03'),
        ),
    ),
)
def test_list_deserialize_values(value, sedes, expected):
    assert sedes.deserialize(value) == expected


@pytest.mark.parametrize(
    'value,sedes',
    (
        # Less than 4 bytes of serialized data
        (b'\x00\x00\x00', uint32_list),
        (b'\x00\x00\x00', bytes32_list),
        (b'\x00\x00\x00', bytes48_list),
        (b'\x00\x00\x00', bytes96_list),
        (b'\x00\x00\x00', boolean_list),

        # Insufficient serialized list data as per found out list length
        (b'\x04\x00\x00\x00\x00', uint32_list),
        (b'\x04\x00\x00\x00\x00', bytes32_list),
        (b'\x04\x00\x00\x00\x00', bytes48_list),
        (b'\x04\x00\x00\x00\x00', bytes96_list),
        (b'\x04\x00\x00\x00\x00', boolean_list),

        # Serialized data given is more than what is required
        (b'\x08\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00' + b'\x00', uint32_list),
        (b'\x20\x00\x00\x00' + (b'\x00' * 35), bytes32_list),
        (b'\x14\x00\x00\x00' + (b'\x00' * 53), bytes48_list),
        (b'\x14\x00\x00\x00' + (b'\x00' * 101), bytes96_list),
        (b'\x04\x00\x00\x00' + b'\x01' * 5, boolean_list),

        # Non-empty lists for empty sedes
        (b'\x01\x00\x00\x00\x00', empty_list)
    ),
)
def test_list_deserialize_bad_values(value, sedes):
    with pytest.raises(DeserializationError):
        sedes.deserialize(value)


@pytest.mark.parametrize(
    'value,sedes',
    (
        ((), uint32_list),
        ((0, 1, 2, 3, 4), uint32_list),

        ((), bytes32_list),
        ((b'\x00' * 32,), bytes32_list),
        ((b'\x00' * 32, b'\x00' * 32), bytes32_list),

        ((), bytes48_list),
        ((b'\x00' * 48,), bytes48_list),
        ((b'\x00' * 48, b'\x00' * 48), bytes48_list),

        ((), bytes96_list),
        ((b'\x00' * 96,), bytes96_list),
        ((b'\x00' * 96, b'\x00' * 96), bytes96_list),

        ((), boolean_list),
        ((True, True, True, True), boolean_list),
        ((False, False, False, False), boolean_list),
        ((True, False, True, False), boolean_list),

        ((b'\x01',), byte_list_list),
        ((b'\x01', b'\x02'), byte_list_list),
        ((b'\x01\x02', b'\x02\x03'), byte_list_list),
    ),
)
def test_list_round_trip(value, sedes):
    assert sedes.deserialize(sedes.serialize(value)) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        ((), uint32_list),
        ((0, 1, 2, 3, 4), uint32_list),

        ((), bytes32_list),
        ((b'\x00' * 32,), bytes32_list),
        ((b'\x00' * 32, b'\x00' * 32), bytes32_list),

        ((), bytes48_list),
        ((b'\x00' * 48,), bytes48_list),
        ((b'\x00' * 48, b'\x00' * 48), bytes48_list),

        ((), bytes96_list),
        ((b'\x00' * 96,), bytes96_list),
        ((b'\x00' * 96, b'\x00' * 96), bytes96_list),

        ((), boolean_list),
        ((True, True, True, True), boolean_list),
        ((False, False, False, False), boolean_list),
        ((True, False, True, False), boolean_list),

        ((), byte_list_list),
        ((b'\x01',), byte_list_list),
        ((b'\x01', b'\x02'), byte_list_list),
        ((b'\x01\x02', b'\x02\x03'), byte_list_list),
    ),
)
def test_list_round_trip_codec(value, sedes):
    if isinstance(sedes, str):
        sedes_obj = eval(sedes)
    else:
        sedes_obj = sedes
    assert decode(encode(value, sedes), sedes_obj) == value
