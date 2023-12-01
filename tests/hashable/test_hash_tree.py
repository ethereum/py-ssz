from hypothesis import (
    assume,
    given,
    strategies as st,
)
import pytest

from ssz.constants import (
    ZERO_HASHES,
)
from ssz.hash_tree import (
    HashTree,
)
from ssz.utils import (
    merkleize,
)
from tests.hashable.chunk_strategies import (
    chunk_st,
    chunks_and_chunk_count_st,
    hash_tree_st,
)


@given(chunks_and_chunk_count_st())
def test_compute(chunks_and_chunk_count):
    root = merkleize(*chunks_and_chunk_count)
    hash_tree = HashTree.compute(*chunks_and_chunk_count)
    assert hash_tree.chunks == chunks_and_chunk_count[0]
    assert hash_tree.root == root
    assert hash_tree.chunk_count == chunks_and_chunk_count[1]


@pytest.mark.parametrize(
    ("chunks", "chunk_count"),
    (
        ([], None),
        ([ZERO_HASHES[0]], -1),
        ([ZERO_HASHES[0]] * 2, 1),
        ([ZERO_HASHES[0]] * 3, 2),
    ),
)
def test_invalid_hash_tree(chunks, chunk_count):
    with pytest.raises(ValueError):
        HashTree.compute(chunks, chunk_count)


@given(chunks_and_chunk_count_st())
def test_equal(chunks_and_chunk_count):
    hash_tree_a = HashTree.compute(*chunks_and_chunk_count)
    hash_tree_b = HashTree.compute(*chunks_and_chunk_count)
    assert hash_tree_a == hash_tree_b
    assert hash(hash_tree_a) == hash(hash_tree_b)


@given(st.lists(chunks_and_chunk_count_st(), min_size=2, max_size=2, unique=True))
def test_not_equal(chunks_and_chunk_counts):
    hash_tree_a = HashTree.compute(*chunks_and_chunk_counts[0])
    hash_tree_b = HashTree.compute(*chunks_and_chunk_counts[1])
    assert hash_tree_a != hash_tree_b
    assert hash(hash_tree_a) != hash(hash_tree_b)


@given(hash_tree_st())
def test_len(hash_tree):
    assert len(hash_tree) == len(hash_tree.chunks)


@given(hash_tree_st())
def test_get_item(hash_tree):
    for index in range(len(hash_tree)):
        negative_index = index - len(hash_tree)
        assert hash_tree[index] == hash_tree.chunks[index]
        assert hash_tree[negative_index] == hash_tree.chunks[negative_index]


@given(hash_tree_st())
def test_index(hash_tree):
    for chunk in hash_tree:
        assert hash_tree.index(chunk) == hash_tree.chunks.index(chunk)


@given(hash_tree_st())
def test_count(hash_tree):
    for chunk in hash_tree:
        assert hash_tree.count(chunk) == hash_tree.chunks.count(chunk)


@given(hash_tree_st(), chunk_st())
def test_append(hash_tree, chunk):
    # extend chunk_count if necessary
    if hash_tree.chunk_count is not None and len(hash_tree) == hash_tree.chunk_count:
        hash_tree = HashTree.compute(hash_tree.chunks, hash_tree.chunk_count + 1)

    result = HashTree.compute(hash_tree.chunks.append(chunk), hash_tree.chunk_count)
    assert hash_tree.append(chunk) == result


@given(hash_tree_st(), st.lists(chunk_st()))
def test_extend(hash_tree, chunks):
    # only extend up to chunk_count
    if hash_tree.chunk_count is not None:
        chunks = chunks[: hash_tree.chunk_count - len(hash_tree)]
    result = HashTree.compute(
        hash_tree.chunks.extend(chunks), chunk_count=hash_tree.chunk_count
    )
    assert hash_tree.extend(chunks) == result
    assert hash_tree + chunks == result


@given(hash_tree_st(), chunk_st())
def test_set(hash_tree, chunk):
    for index in range(len(hash_tree)):
        result = HashTree.compute(
            hash_tree.chunks.set(index, chunk), hash_tree.chunk_count
        )
        assert hash_tree.set(index, chunk) == result


@given(hash_tree_st())
def test_delete(hash_tree):
    assume(len(hash_tree) > 1)

    for index in range(len(hash_tree)):
        result = HashTree.compute(hash_tree.chunks.delete(index), hash_tree.chunk_count)
        assert hash_tree.delete(index) == result


@given(hash_tree_st())
def test_remove(hash_tree):
    for chunk in hash_tree:
        chunks = hash_tree.chunks.remove(chunk)
        assume(len(chunks) >= 1)
        result = HashTree.compute(chunks, hash_tree.chunk_count)
        assert hash_tree.remove(chunk) == result
