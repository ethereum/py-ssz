import pytest

from ssz import (
    DeserializationError,
    SerializationError,
    decode,
    encode,
)
from ssz.sedes import (
    address_list,
    boolean_list,
    bytes_list,
    empty_list,
    hash32_list,
    uint32_list,
)


@pytest.mark.parametrize(
    'value,sedes,expected',
    (
        # Serialize Empty Objects
        ([], uint32_list, b'\x00\x00\x00\x00'),
        ((), uint32_list, b'\x00\x00\x00\x00'),
        ([], hash32_list, b'\x00\x00\x00\x00'),
        ((), hash32_list, b'\x00\x00\x00\x00'),
        ([], address_list, b'\x00\x00\x00\x00'),
        ((), address_list, b'\x00\x00\x00\x00'),
        ([], boolean_list, b'\x00\x00\x00\x00'),
        ((), boolean_list, b'\x00\x00\x00\x00'),
        ([], bytes_list, b'\x00\x00\x00\x00'),
        ((), bytes_list, b'\x00\x00\x00\x00'),

        # Serialize uint32 Iterables
        (
            [0, 1, 2, 3, 4],
            uint32_list,
            b'\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x01'
            b'\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04',
        ),
        (
            (0, 1, 2, 3, 4),
            uint32_list,
            b'\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x01'
            b'\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04',
        ),
        (
            range(5),
            uint32_list,
            b'\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x01'
            b'\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04',
        ),

        # Serialize hash32 Iterables
        ([b'\x00' * 32], hash32_list, b'\x00\x00\x00 ' + (b'\x00' * 32)),
        ([b'\x00' * 32, b'\x00' * 32], hash32_list, b'\x00\x00\x00@' + (b'\x00' * 64)),
        ((b'\x00' * 32, b'\x00' * 32), hash32_list, b'\x00\x00\x00@' + (b'\x00' * 64)),

        # Serialize address Iterables
        ([b'\x00' * 20], address_list, b'\x00\x00\x00\x14' + (b'\x00' * 20)),
        ([b'\x00' * 20, b'\x00' * 20], address_list, b'\x00\x00\x00(' + (b'\x00' * 40)),
        ((b'\x00' * 20, b'\x00' * 20), address_list, b'\x00\x00\x00(' + (b'\x00' * 40)),

        # Serialize boolean Iterables
        ([True, True, True, True], boolean_list, b'\x00\x00\x00\x04' + b'\x01' * 4),
        ((True, True, True, True), boolean_list, b'\x00\x00\x00\x04' + b'\x01' * 4),
        ([False, False, False, False], boolean_list, b'\x00\x00\x00\x04' + b'\x00' * 4),
        ((False, False, False, False), boolean_list, b'\x00\x00\x00\x04' + b'\x00' * 4),
        ([True, False, True, False], boolean_list, b'\x00\x00\x00\x04\x01\x00\x01\x00'),
        ((True, False, True, False), boolean_list, b'\x00\x00\x00\x04\x01\x00\x01\x00'),

        # Serialize bytes Iterables
        ([b'\x01'], bytes_list, b'\x00\x00\x00\x05\x00\x00\x00\x01\x01'),
        ([b'\x01', b'\x02'], bytes_list, b'\x00\x00\x00\n\x00\x00\x00\x01\x01\x00\x00\x00\x01\x02'),
        (
            [b'\x01\x02', b'\x02\x03'],
            bytes_list,
            b'\x00\x00\x00\x0c\x00\x00\x00'
            b'\x02\x01\x02\x00\x00\x00\x02\x02\x03',
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
        ("foo", hash32_list),
        ("foo", address_list),
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
        (b'\x00\x00\x00\x00', hash32_list, ()),
        (b'\x00\x00\x00\x00', address_list, ()),
        (b'\x00\x00\x00\x00', boolean_list, ()),

        # Deserialize uint32 Iterables
        (
            b'\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x01'
            b'\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04',
            uint32_list,
            (0, 1, 2, 3, 4),
        ),

        # Deserialize hash32 Iterables
        (b'\x00\x00\x00 ' + (b'\x00' * 32), hash32_list, (b'\x00' * 32,)),
        (b'\x00\x00\x00@' + (b'\x00' * 64), hash32_list, (b'\x00' * 32, b'\x00' * 32)),

        # Deserialize address Iterables
        (b'\x00\x00\x00\x14' + (b'\x00' * 20), address_list, (b'\x00' * 20,)),
        (b'\x00\x00\x00(' + (b'\x00' * 40), address_list, (b'\x00' * 20, b'\x00' * 20)),

        # Deserialize boolean Iterables
        (b'\x00\x00\x00\x04' + b'\x01' * 4, boolean_list, (True, True, True, True)),
        (b'\x00\x00\x00\x04' + b'\x00' * 4, boolean_list, (False, False, False, False)),
        (b'\x00\x00\x00\x04\x01\x00\x01\x00', boolean_list, (True, False, True, False)),

        # Deserialize bytes Iterables
        # Serialize bytes Iterables
        (b'\x00\x00\x00\x05\x00\x00\x00\x01\x01', bytes_list, (b'\x01',)),
        (b'\x00\x00\x00\n\x00\x00\x00\x01\x01\x00\x00\x00\x01\x02', bytes_list, (b'\x01', b'\x02')),
        (
            b'\x00\x00\x00\x0c\x00\x00\x00'
            b'\x02\x01\x02\x00\x00\x00\x02\x02\x03',
            bytes_list,
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
        (b'\x00\x00\x00', hash32_list),
        (b'\x00\x00\x00', address_list),
        (b'\x00\x00\x00', boolean_list),

        # Insufficient serialized list data as per found out list length
        (b'\x00\x00\x04', uint32_list),
        (b'\x00\x00\x04', hash32_list),
        (b'\x00\x00\x04', address_list),
        (b'\x00\x00\x04', boolean_list),

        # Serialized data given is more than what is required
        (b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00', uint32_list),
        (b'\x00\x00\x00 ' + (b'\x00' * 35), hash32_list),
        (b'\x00\x00\x00\x14' + (b'\x00' * 25), address_list),
        (b'\x00\x00\x00\x04' + b'\x01' * 5, boolean_list),

        # Non-empty lists for empty sedes
        (b'\x00\x00\x00\x01\x00', empty_list)
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

        ((), hash32_list),
        ((b'\x00' * 32,), hash32_list),
        ((b'\x00' * 32, b'\x00' * 32), hash32_list),

        ((), address_list),
        ((b'\x00' * 20,), address_list),
        ((b'\x00' * 20, b'\x00' * 20), address_list),

        ((), boolean_list),
        ((True, True, True, True), boolean_list),
        ((False, False, False, False), boolean_list),
        ((True, False, True, False), boolean_list),

        ((b'\x01',), bytes_list),
        ((b'\x01', b'\x02'), bytes_list),
        ((b'\x01\x02', b'\x02\x03'), bytes_list),
    ),
)
def test_list_round_trip(value, sedes):
    assert sedes.deserialize(sedes.serialize(value)) == value


@pytest.mark.parametrize(
    'value,sedes',
    (
        ((), uint32_list),
        ((0, 1, 2, 3, 4), uint32_list),

        ((), 'uint32_list'),
        ((0, 1, 2, 3, 4), 'uint32_list'),

        ((), hash32_list),
        ((b'\x00' * 32,), hash32_list),
        ((b'\x00' * 32, b'\x00' * 32), hash32_list),

        ((), 'hash32_list'),
        ((b'\x00' * 32,), 'hash32_list'),
        ((b'\x00' * 32, b'\x00' * 32), 'hash32_list'),

        ((), address_list),
        ((b'\x00' * 20,), address_list),
        ((b'\x00' * 20, b'\x00' * 20), address_list),

        ((), 'address_list'),
        ((b'\x00' * 20,), 'address_list'),
        ((b'\x00' * 20, b'\x00' * 20), 'address_list'),

        ((), boolean_list),
        ((True, True, True, True), boolean_list),
        ((False, False, False, False), boolean_list),
        ((True, False, True, False), boolean_list),

        ((), 'boolean_list'),
        ((True, True, True, True), 'boolean_list'),
        ((False, False, False, False), 'boolean_list'),
        ((True, False, True, False), 'boolean_list'),

        ((), bytes_list),
        ((b'\x01',), bytes_list),
        ((b'\x01', b'\x02'), bytes_list),
        ((b'\x01\x02', b'\x02\x03'), bytes_list),

        ((), 'bytes_list'),
        ((b'\x01',), 'bytes_list'),
        ((b'\x01', b'\x02'), 'bytes_list'),
        ((b'\x01\x02', b'\x02\x03'), 'bytes_list'),
    ),
)
def test_list_round_trip_codec(value, sedes):
    if isinstance(sedes, str):
        sedes_obj = eval(sedes)
    else:
        sedes_obj = sedes
    assert decode(encode(value, sedes), sedes_obj) == value
