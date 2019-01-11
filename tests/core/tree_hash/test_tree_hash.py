import pytest

from ssz.exceptions import (
    TreeHashException,
)
from ssz.tree_hash.tree_hash import (
    _hash_tree_root,
)


@pytest.mark.parametrize(
    'input_object,sedes',
    (
        (None, "UselessSedes"),
        (123, "UselessSedes"),
    ),
)
def test_hash_tree_root_raise_exception(input_object, sedes):
    with pytest.raises(TreeHashException):
        _hash_tree_root(input_object, sedes)
