import re

import pytest

from ssz import (
    decode,
    encode,
)
from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes import (
    List,
    Serializable,
    bytes_sedes,
    uint32,
    uint32_list,
)
from ssz.utils import (
    infer_sedes,
)


class SSZType1(Serializable):
    fields = [
        ('field1', uint32),
        ('field2', bytes_sedes),
        ('field3', uint32_list)
    ]


class SSZType2(Serializable):
    fields = [
        ('field2_1', SSZType1),
        ('field2_2', List(SSZType1)),
    ]


class SSZType3(Serializable):
    fields = [
        ('field1', uint32),
        ('field2', uint32),
        ('field3', uint32),
    ]

    def __init__(self, field2, field1, field3, **kwargs):
        super().__init__(field1=field1, field2=field2, field3=field3, **kwargs)


class SSZType4(SSZType3):
    pass


_type_1_a = SSZType1(5, b'a', (0, 1))
_type_1_b = SSZType1(9, b'b', (2, 3))
_type_2 = SSZType2(_type_1_a.copy(), [_type_1_a.copy(), _type_1_b.copy()])


@pytest.fixture
def type_1_a():
    return _type_1_a.copy()


@pytest.fixture
def type_1_b():
    return _type_1_b.copy()


@pytest.fixture
def type_2():
    return _type_2.copy()


@pytest.fixture(params=[_type_1_a, _type_1_b, _type_2])
def ssz_obj(request):
    return request.param.copy()


@pytest.mark.parametrize(
    'ssztype,args,kwargs,exception_includes',
    (
        # missing fields args
        (SSZType1, [], {}, ['field1', 'field2', 'field3']),
        (SSZType1, [8], {}, ['field2', 'field3']),
        (SSZType1, [7, 8], {}, ['field3']),
        # missing fields kwargs
        (SSZType1, [], {'field1': 7}, ['field2', 'field3']),
        (SSZType1, [], {'field1': 7, 'field2': 8}, ['field3']),
        (SSZType1, [], {'field2': 7, 'field3': (1, b'')}, ['field1']),
        (SSZType1, [], {'field3': (1, b'')}, ['field1', 'field2']),
        (SSZType1, [], {'field2': 7}, ['field1', 'field3']),
        # missing fields args and kwargs
        (SSZType1, [7], {'field2': 8}, ['field3']),
        (SSZType1, [7], {'field3': (1, b'')}, ['field2']),
        # duplicate fields
        (SSZType1, [7], {'field1': 8}, ['field1']),
        (SSZType1, [7, 8], {'field1': 8, 'field2': 7}, ['field1', 'field2']),
    ),
)
def test_serializable_initialization_validation(ssztype, args, kwargs, exception_includes):
    for msg_part in exception_includes:
        with pytest.raises(TypeError, match=msg_part):
            ssztype(*args, **kwargs)


@pytest.mark.parametrize(
    'args,kwargs',
    (
        ([2, 1, 3], {}),
        ([2, 1], {'field3': 3}),
        ([2], {'field3': 3, 'field1': 1}),
        ([], {'field3': 3, 'field1': 1, 'field2': 2}),
    ),
)
def test_serializable_initialization_args_kwargs_mix(args, kwargs):
    obj = SSZType3(*args, **kwargs)

    assert obj.field1 == 1
    assert obj.field2 == 2
    assert obj.field3 == 3


@pytest.mark.parametrize(
    'lookup,expected',
    (
        (0, 5),
        (1, b'a'),
        (2, (0, 1)),
        (slice(0, 1), (5,)),
        (slice(0, 2), (5, b'a')),
        (slice(0, 3), (5, b'a', (0, 1))),
        (slice(1, 3), (b'a', (0, 1))),
        (slice(2, 3), ((0, 1),)),
        (slice(None, 3), (5, b'a', (0, 1))),
        (slice(None, 2), (5, b'a')),
        (slice(None, 1), (5,)),
        (slice(None, 0), tuple()),
        (slice(0, None), (5, b'a', (0, 1))),
        (slice(1, None), (b'a', (0, 1))),
        (slice(2, None), ((0, 1),)),
        (slice(2, None), ((0, 1),)),
        (slice(None, None), (5, b'a', (0, 1))),
        (slice(-1, None), ((0, 1),)),
        (slice(-2, None), (b'a', (0, 1),)),
        (slice(-3, None), (5, b'a', (0, 1),)),
    ),
)
def test_serializable_getitem_lookups(type_1_a, lookup, expected):
    actual = type_1_a[lookup]
    assert actual == expected


def test_serializable_subclass_retains_field_info_from_parent():
    obj = SSZType4(2, 1, 3)
    assert obj.field1 == 1
    assert obj.field2 == 2
    assert obj.field3 == 3


def test_deserialization_for_custom_init_method():
    type_3 = SSZType3(2, 1, 3)
    assert type_3.field1 == 1
    assert type_3.field2 == 2
    assert type_3.field3 == 3

    result = decode(encode(type_3), sedes=SSZType3)
    assert result.field1 == 1
    assert result.field2 == 2
    assert result.field3 == 3

    result_sedes_encode = decode(encode(type_3, SSZType3), sedes=SSZType3)
    assert result_sedes_encode.field1 == 1
    assert result_sedes_encode.field2 == 2
    assert result_sedes_encode.field3 == 3


def test_serializable_sedes_inference(type_1_a, type_1_b, type_2):
    assert infer_sedes(type_1_a) == SSZType1
    assert infer_sedes(type_1_b) == SSZType1
    assert infer_sedes(type_2) == SSZType2


def test_serializable_invalid_serialization_value(type_1_a, type_1_b, type_2):
    with pytest.raises(SerializationError):
        SSZType1.serialize(type_2)
    with pytest.raises(SerializationError):
        SSZType2.serialize(type_1_a)
    with pytest.raises(SerializationError):
        SSZType2.serialize(type_1_b)


@pytest.mark.parametrize(
    'value,sedes',
    (
        # Less than 4 bytes of serialized data
        (b'\x00\x00\x00', SSZType1),
        (b'\x00\x00\x00', SSZType2),
        (b'\x00\x00\x00', SSZType3),
        (b'\x00\x00\x00', SSZType4),

        # Insufficient serialized container data as per found out container length
        (b'\x00\x00\x00\x04', SSZType1),
        (b'\x00\x00\x00\x04', SSZType2),
        (b'\x00\x00\x00\x04', SSZType3),
        (b'\x00\x00\x00\x04', SSZType4),

        # Serialized data given is more than what is required
        (b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00', SSZType1),
        (b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00', SSZType2),
        (b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00', SSZType3),
        (b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01' + b'\x00', SSZType4),
    ),
)
def test_container_deserialize_bad_values(value, sedes):
    with pytest.raises(DeserializationError):
        sedes.deserialize(value)


@pytest.mark.parametrize(
    'value,sedes,expected',
    (
        # Below the values are called as functions, because they are fixtures
        (
            type_1_a(),
            SSZType1,
            b'\x00\x00\x00\x15\x00\x00\x00\x05\x00\x00\x00\x01a'
            b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01',
        ),
        (
            type_1_b(),
            SSZType1,
            b'\x00\x00\x00\x15\x00\x00\x00\t\x00\x00\x00\x01b'
            b'\x00\x00\x00\x08\x00\x00\x00\x02\x00\x00\x00\x03',
        ),
        (
            type_2(),
            SSZType2,
            b'\x00\x00\x00O\x00\x00\x00\x15\x00\x00\x00\x05\x00\x00\x00'
            b'\x01a\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00'
            b'\x00\x002\x00\x00\x00\x15\x00\x00\x00\x05\x00\x00\x00\x01a'
            b'\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x15\x00'
            b'\x00\x00\t\x00\x00\x00\x01b\x00\x00\x00\x08\x00\x00'
            b'\x00\x02\x00\x00\x00\x03',
        ),
    )
)
def test_serializable_serialization(value, sedes, expected):
    assert sedes.serialize(value) == expected


def test_serializable_deserialization(type_1_a, type_1_b, type_2):
    serial_1_a = SSZType1.serialize(type_1_a)
    serial_1_b = SSZType1.serialize(type_1_b)
    serial_2 = SSZType2.serialize(type_2)

    res_type_1_a = SSZType1.deserialize(serial_1_a)
    res_type_1_b = SSZType1.deserialize(serial_1_b)
    res_type_2 = SSZType2.deserialize(serial_2)

    assert res_type_1_a == type_1_a
    assert res_type_1_b == type_1_b
    assert res_type_2 == type_2


def test_serializable_field_immutability(type_1_a, type_1_b, type_2):
    with pytest.raises(AttributeError, match=r"can't set attribute"):
        type_1_a.field1 += 1
    assert type_1_a.field1 == 5

    with pytest.raises(AttributeError, match=r"can't set attribute"):
        type_1_a.field2 = b'x'
    assert type_1_a.field2 == b'a'

    with pytest.raises(AttributeError, match=r"can't set attribute"):
        type_2.field2_1.field1 += 1
    assert type_2.field2_1.field1 == 5

    with pytest.raises(TypeError, match=r"'tuple' object does not support item assignment"):
        type_2.field2_2[1] = type_1_a
    assert type_2.field2_2[1] == type_1_b


def test_serializable_iterator():
    values = (5, b'a', (1, b'c'))
    obj = SSZType1(*values)
    assert tuple(obj) == values


def test_serializable_equality(type_1_a, type_1_b, type_2):
    # equality
    assert type_1_a == type_1_a
    assert type_1_a == SSZType1(*type_1_a)
    assert type_1_b == type_1_b
    assert type_1_b == SSZType1(*type_1_b)

    assert type_2 == type_2
    assert type_1_a != type_1_b
    assert type_1_b != type_2
    assert type_2 != type_1_a


def test_serializable_basic_copy(type_1_a):
    n_type_1_a = type_1_a.copy()
    assert n_type_1_a == type_1_a
    assert n_type_1_a is not type_1_a


def test_serializable_copy_with_nested_serializables(type_2):
    n_type_2 = type_2.copy()
    assert n_type_2 == type_2
    assert n_type_2 is not type_2

    assert n_type_2.field2_1 == type_2.field2_1
    assert n_type_2.field2_1 is not type_2.field2_1

    assert n_type_2.field2_2 == type_2.field2_2
    assert all(left == right for left, right in zip(n_type_2.field2_2, type_2.field2_2))
    assert all(left is not right for left, right in zip(n_type_2.field2_2, type_2.field2_2))


def test_serializable_with_duplicate_field_names_is_error():
    msg1 = "duplicated in the `fields` declaration: field_a"
    with pytest.raises(TypeError, match=msg1):
        class ParentA(Serializable):
            fields = (
                ('field_a', uint32),
                ('field_c', uint32),
                ('field_d', uint32),
                ('field_a', uint32),
            )

    msg2 = "duplicated in the `fields` declaration: field_a,field_c"
    with pytest.raises(TypeError, match=msg2):
        class ParentB(Serializable):
            fields = (
                ('field_a', uint32),
                ('field_c', uint32),
                ('field_d', uint32),
                ('field_a', uint32),
                ('field_c', uint32),
            )


def test_serializable_inheritance_enforces_inclusion_of_parent_fields():
    class Parent(Serializable):
        fields = (
            ('field_a', uint32),
            ('field_b', uint32),
            ('field_c', uint32),
            ('field_d', uint32),
        )

    with pytest.raises(TypeError, match="field_a,field_c"):
        class Child(Parent):
            fields = (
                ('field_b', uint32),
                ('field_d', uint32),
            )


def test_serializable_single_inheritance_with_no_fields():
    class Parent(Serializable):
        fields = (
            ('field_a', uint32),
            ('field_b', uint32),
        )

    class Child(Parent):
        pass

    parent = Parent(1, 2)
    assert parent.field_a == 1
    assert parent.field_b == 2
    assert Parent.serialize(parent) == b'\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x02'

    child = Child(3, 4)
    assert child.field_a == 3
    assert child.field_b == 4
    assert Child.serialize(child) == b'\x00\x00\x00\x08\x00\x00\x00\x03\x00\x00\x00\x04'


def test_serializable_single_inheritance_with_fields():
    class Parent(Serializable):
        fields = (
            ('field_a', uint32),
            ('field_b', uint32),
        )

    class Child(Parent):
        fields = (
            ('field_a', uint32),
            ('field_b', uint32),
            ('field_c', uint32),
        )

    parent = Parent(1, 2)
    assert parent.field_a == 1
    assert parent.field_b == 2
    assert Parent.serialize(parent) == b'\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x02'

    with pytest.raises(TypeError):
        # ensure that the fields don't somehow leak into the parent class.
        Parent(1, 2, 3)

    child = Child(3, 4, 5)
    assert child.field_a == 3
    assert child.field_b == 4
    assert child.field_c == 5
    assert Child.serialize(child) == (b'\x00\x00\x00\x0c\x00\x00\x00\x03'
                                      b'\x00\x00\x00\x04\x00\x00\x00\x05')


def test_serializable_inheritance_with_sedes_overrides():
    class Parent(Serializable):
        fields = (
            ('field_a', uint32),
            ('field_b', uint32),
        )

    class Child(Parent):
        fields = (
            ('field_a', bytes_sedes),
            ('field_b', bytes_sedes),
            ('field_c', bytes_sedes),
        )

    parent = Parent(1, 2)
    assert parent.field_a == 1
    assert parent.field_b == 2
    assert Parent.serialize(parent) == b'\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x02'

    child = Child(b'1', b'2', b'3')
    assert child.field_a == b'1'
    assert child.field_b == b'2'
    assert child.field_c == b'3'
    assert Child.serialize(child) == (b'\x00\x00\x00\x0f\x00\x00\x00\x011\x00'
                                      b'\x00\x00\x012\x00\x00\x00\x013')


def test_serializable_multiple_inheritance_requires_all_parent_fields():
    class ParentA(Serializable):
        fields = (
            ('field_a', uint32),
        )

    class ParentB(Serializable):
        fields = (
            ('field_b', uint32),
        )

    with pytest.raises(TypeError, match="The following fields are missing: field_b"):
        class ChildA(ParentA, ParentB):
            fields = (
                ('field_a', uint32),
            )

    with pytest.raises(TypeError, match="The following fields are missing: field_a"):
        class ChildB(ParentA, ParentB):
            fields = (
                ('field_b', uint32),
            )

    with pytest.raises(TypeError, match="The following fields are missing: field_a,field_b"):
        class ChildC(ParentA, ParentB):
            fields = (
                ('field_c', uint32),
                ('field_d', uint32),
            )


@pytest.mark.parametrize(
    'name',
    (
        '0_starts_with_digit',
        ' starts_with_space',
        '$starts_with_dollar',
        'has_dollar_$_inside',
        'has spaces',
    )
)
def test_serializable_field_names_must_be_valid_identifiers(name):
    msg = "not valid python identifiers: `{0}`".format(re.escape(name))
    with pytest.raises(TypeError, match=msg):
        class Klass(Serializable):
            fields = (
                (name, uint32),
            )


def test_serializable_inheritance_from_base_with_no_fields():
    """
    Ensure that we can create base classes of the base `Serializable` without
    declaring fields.
    """
    class ExtendedSerializable(Serializable):
        pass

    class FurtherExtendedSerializable(ExtendedSerializable):
        pass
