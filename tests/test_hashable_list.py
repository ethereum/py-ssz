import math

import pytest

from hypothesis import (
    given,
)
import hypothesis.strategies as st

from eth_utils.toolz import (
    merge,
)

import ssz
from ssz.constants import (
    CHUNK_SIZE,
    EMPTY_CHUNK,
)
from ssz.sedes import (
    BytesN,
    uint512,
)
from ssz.hash import (
    hash_eth2,
)
from ssz.sedes.hashable_list import (
    calc_chunk_tree,
    calc_updated_chunk_tree,
    get_chunks,
    get_chunk_index_for_item,
    get_item_index_in_chunk,
    get_items_per_chunk,
    get_next_power_of_two,
    HashableList,
    validate_merkle_tree,
)


chunks = st.binary(min_size=CHUNK_SIZE, max_size=CHUNK_SIZE)
chunk_tuples = st.lists(chunks)
chunk_trees = chunk_tuples.map(calc_chunk_tree)

items = st.binary(min_size=1).flatmap(
    lambda prototype: st.lists(st.binary(min_size=len(prototype), max_size=len(prototype)))
)
small_items = st.binary(min_size=1, max_size=CHUNK_SIZE - 1).flatmap(
    lambda prototype: st.lists(st.binary(min_size=len(prototype), max_size=len(prototype)))
)
large_items = st.binary(min_size=CHUNK_SIZE, max_size=CHUNK_SIZE * 3).flatmap(
    lambda prototype: st.lists(st.binary(min_size=len(prototype), max_size=len(prototype)))
)


@st.composite
def chunk_trees_and_indices(draw):
    chunk_tree = draw(chunk_trees)
    chunk_index = draw(st.integers(min_value=0, max_value=len(chunk_tree[0]) - 1))
    return chunk_tree, chunk_index


@given(st.integers())
def test_next_power_of_two_is_power_of_two(value):
    assert math.log2(get_next_power_of_two(value)).is_integer()


@given(st.integers())
def test_next_power_of_two_is_greater_or_equal(value):
    next_power_of_two = get_next_power_of_two(value)
    assert next_power_of_two >= value


@given(st.integers())
def test_next_power_of_two_is_smallest_possible(value):
    next_power_of_two = get_next_power_of_two(value)
    if next_power_of_two > 1:
        previous_power_of_two = next_power_of_two // 2
        assert previous_power_of_two < value


@given(st.integers(min_value=1))
def test_items_fit_in_chunk(item_length):
    items_per_chunk = get_items_per_chunk(item_length)
    assert items_per_chunk == 1 or items_per_chunk * item_length <= CHUNK_SIZE


@given(st.integers(min_value=1))
def test_no_additional_items_fit_in_chunk(item_length):
    items_per_chunk = get_items_per_chunk(item_length)
    assert (items_per_chunk + 1) * item_length > CHUNK_SIZE


@given(large_items.filter(lambda items: len(items) > 0))
def test_large_items_dont_get_chunked(items):
    chunks = get_chunks(items)
    assert chunks == tuple(items)


@given(small_items)
def test_small_items_get_padded(items):
    chunks = get_chunks(items)
    assert all(len(chunk) == CHUNK_SIZE for chunk in chunks)


def test_empty_items_get_single_chunk():
    chunks = get_chunks([])
    assert chunks == (EMPTY_CHUNK,)


@given(items.filter(lambda items: len(items) > 0))
def test_items_appear_in_chunk(items):
    item_length = len(items[0])
    chunks = get_chunks(items)
    for item_index, item in enumerate(items):
        chunk_index = get_chunk_index_for_item(item_index, item_length)
        item_index_in_chunk = get_item_index_in_chunk(item_index, item_length)

        chunk = chunks[chunk_index]
        assert chunk[item_index_in_chunk * item_length:(item_index_in_chunk + 1) * item_length]


@given(chunk_tuples)
def test_chunks_appear_in_chunk_tree(chunks):
    chunk_tree = calc_chunk_tree(chunks)
    base_layer = chunk_tree[0]
    assert base_layer[:len(chunks)] == tuple(chunks)


@given(chunk_tuples.filter(lambda chunks: len(chunks) > 0))
def test_chunks_in_chunk_tree_are_padded(chunks):
    chunk_tree = calc_chunk_tree(chunks)
    base_layer = chunk_tree[0]
    if not math.log2(len(chunks)).is_integer():
        assert set(base_layer[len(chunks):]) == {EMPTY_CHUNK}
    else:
        assert base_layer[len(chunks):] == ()


@given(chunk_trees)
def test_chunk_tree_is_valid_merkle_tree(chunk_tree):
    validate_merkle_tree(chunk_tree)


@given(
    chunk_trees_and_indices(),
    chunks,
)
def test_updated_chunk_tree_updates_single_chunk(chunk_tree_and_index, chunk):
    chunk_tree, index = chunk_tree_and_index
    updated_chunk_tree = calc_updated_chunk_tree(chunk_tree, index, chunk)
    assert updated_chunk_tree[0][index] == chunk
    assert updated_chunk_tree[0][:index] == chunk_tree[0][:index]
    assert updated_chunk_tree[0][index + 1:] == chunk_tree[0][index + 1:]


@given(
    chunk_trees_and_indices(),
    chunks,
)
def test_updated_chunk_tree_is_valid_merkle_tree(chunk_tree_and_index, chunk):
    chunk_tree, index = chunk_tree_and_index
    updated_chunk_tree = calc_updated_chunk_tree(chunk_tree, index, chunk)
    validate_merkle_tree(updated_chunk_tree)


@pytest.mark.parametrize(("items", "sedes"), (
    ((), uint512),
    ((1,), uint512),
    ((1, 2, 3, 4, 5), uint512),
    ((b"\x00" * 128,), BytesN(128)),
    ((b"\x00" * 128, b"\x11" * 128, b"\x22" * 128,), BytesN(128)),
))
def test_hashable_list_initialization(items, sedes):
    hashable_list = HashableList(items, sedes)

    assert len(hashable_list) == len(items)

    for index, item in enumerate(items):
        assert hashable_list[index] == item

    chunks = get_chunks(tuple(ssz.encode(item, sedes) for item in items))
    root = calc_chunk_tree(chunks)[-1][0]
    assert hashable_list.root == hash_eth2(root + len(items).to_bytes(32, "little"))


@pytest.mark.parametrize(("items", "item_sedes", "replacements"), (
    ((), uint512, {}),
    ((1,), uint512, {0: 2}),
    ((1, 2, 3), uint512, {0: 4, 1: 5, 2: 6}),
))
def test_hashable_list_replace(items, item_sedes, replacements):
    original_list = HashableList(items, item_sedes)
    updated_list = original_list.copy(replace=replacements)

    expected_items = list(items)
    for index, item in replacements.items():
        expected_items[index] = item

    expected_list = HashableList(expected_items, item_sedes)

    assert len(updated_list) == len(expected_list)
    for item, expected_item in zip(updated_list, expected_list):
        assert item == expected_item

    assert updated_list.root == expected_list.root


@given(
    st.lists(st.integers(min_value=0)),
    st.integers(min_value=0),
)
def test_hashable_list_append(items, append):
    original_list = HashableList(items, uint512)
    updated_list = original_list.copy(append=append)

    assert updated_list[-1] == append
    assert len(updated_list) == len(original_list) + 1
    assert updated_list.root == HashableList(tuple(items) + (append,), uint512).root
