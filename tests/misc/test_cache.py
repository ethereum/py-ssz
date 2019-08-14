from ssz import (
    Serializable,
    bytes32,
    uint8,
)
from tests.utils.db import (
    CacheDB,
    MemoryDB,
)


class Foo(Serializable):
    fields = (
        ("field1", uint8),
        ("field2", bytes32),
    )


def test_cache_db():
    foo_with_db = Foo(
        field1=10,
        field2=b'\x12' * 32,
        cache=CacheDB(db=MemoryDB(), cache_size=2**10),
    )
    foo_without_db = Foo(
        field1=10,
        field2=b'\x12' * 32,
    )
    assert foo_with_db.hash_tree_root == foo_without_db.hash_tree_root
