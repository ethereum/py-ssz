import pytest

from ssz.sedes import (
    Boolean,
    uint16,
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
