import pytest

from ssz.sedes import (
    bytes32_list,
    uint32_list,
)
from ssz.tree_hash.tree_hash import (
    hash_tree_root,
)


@pytest.mark.parametrize(
    'items,sedes',
    (
        # Specify values in Tuple
        ((123, 456, 789, ), uint32_list),
        (tuple(), uint32_list),
        ((b'\x56' * 32, ), bytes32_list),
        ((b'\x56' * 32, ) * 100, bytes32_list),
        ((b'\x56' * 32, ) * 101, bytes32_list),
    ),
)
def test_iterables(items, sedes):
    # Make sure Lists are also tested
    for value in (items, list(items),):
        assert len(hash_tree_root(value, sedes)) == 32
