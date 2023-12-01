import pytest

from ssz import (
    Serializable,
    bytes32,
    uint8,
)
from ssz.cache.cache import (
    SSZCache,
)


class Foo(Serializable):
    fields = (("field1", uint8), ("field2", bytes32))


@pytest.fixture
def foo_with_db():
    return Foo(field1=10, field2=b"\x12" * 32, cache=SSZCache(cache_size=2**10))


@pytest.fixture
def foo_without_db():
    return Foo(field1=10, field2=b"\x12" * 32)


def test_cache_sanity(foo_with_db, foo_without_db):
    assert foo_with_db.hash_tree_root == foo_without_db.hash_tree_root


def test_reset_cache_with_db(foo_with_db):
    foo_with_db.hash_tree_root
    assert len(foo_with_db.cache._cached_values) >= 0

    foo_with_db.reset_cache()
    assert len(foo_with_db.cache._cached_values) == 0


def test_reset_cache_without_db(foo_without_db):
    foo_without_db.hash_tree_root
    assert len(foo_without_db.cache) >= 0

    foo_without_db.reset_cache()
    assert len(foo_without_db.cache) == 0
