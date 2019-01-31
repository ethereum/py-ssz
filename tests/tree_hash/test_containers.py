import pytest

from ssz.hash import (
    hash_eth2,
)
from ssz.sedes import (
    List,
    Serializable,
    bytes_sedes,
    uint32,
    uint32_list,
)
from ssz.tree_hash import (
    hash_tree_root,
)


class SSZType1(Serializable):
    fields = [
        ('field1', uint32),
        ('field2', bytes_sedes),
        ('field3', uint32_list),
    ]


class SSZType2(Serializable):
    fields = [
        ('field2_1', SSZType1),
        ('field2_2', List(SSZType1)),
    ]


# Type3 and Type4 use to make sure tree hash works on inheritance serializable
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


class SSZUndeclaredFieldsType(Serializable):
    pass


_type_1_a = SSZType1(5, b'a', (0, 1))
_type_1_b = SSZType1(9, b'b', (2, 3))
_type_2 = SSZType2(_type_1_a.copy(), [_type_1_a.copy(), _type_1_b.copy()])
_type_3 = SSZType3(1, 2, 3)
_type_undeclared_fields = SSZUndeclaredFieldsType()


@pytest.mark.parametrize(
    'value,sedes',
    (
        (_type_1_a, SSZType1),
        (_type_1_b, SSZType1),
        (_type_2, SSZType2),
    ),
)
def test_serializables(value, sedes):

    assert len(hash_tree_root(value, sedes)) == 32
    # Also make sure `infer_sedes` works
    assert len(hash_tree_root(value)) == 32


@pytest.mark.parametrize(
    'value,sedes,expected',
    (
        (_type_3, SSZType3, hash_tree_root(_type_3, SSZType4)),
        (_type_undeclared_fields, SSZUndeclaredFieldsType, hash_eth2(b'')),
    ),
)
def test_special_serializables(value, sedes, expected):
    assert hash_tree_root(value, sedes) == expected
    assert hash_tree_root(value) == expected
