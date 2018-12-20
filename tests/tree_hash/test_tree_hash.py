import pytest

from ssz.sedes import (
    Boolean,
    hash32_list,
    uint16,
    uint32_list,
    uint512,
)
from ssz.tree_hash.tree_hash import (
    hash_tree_root,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        (True, b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),  # noqa
        (False, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),  # noqa
    ),
)
def test_boolean_serialize_values(value, expected):
    sedes = Boolean()
    assert hash_tree_root(value, sedes) == expected


@pytest.mark.parametrize(
    'value,sedes',
    (
        (0, uint16),
        (56, uint16),
        (55665566, uint512),
    ),
)
def test_non_iterables(value, sedes):
    assert len(hash_tree_root(value, sedes)) == 32


@pytest.mark.parametrize(
    'items,sedes',
    (
        # Specify values in Tuple
        ((123, 456, 789, ), uint32_list),
        (tuple(), uint32_list),
        ((b'\x56' * 32, ), hash32_list),
        ((b'\x56' * 32, ) * 100, hash32_list),
        ((b'\x56' * 32, ) * 101, hash32_list),
    ),
)
def test_iterables(items, sedes):
    # Make sure Lists are also tested
    for value in (items, list(items),):
        assert len(hash_tree_root(value, sedes)) == 32
