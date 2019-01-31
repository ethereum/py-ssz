from hypothesis import (
    given,
    strategies as st,
)
import pytest

from ssz import (
    hash_tree_root,
)
from ssz.sedes import (
    BytesN,
    List,
    bytes32,
    bytes_sedes,
    uint32,
)

bytes32_list = List(bytes32)
bytes_list = List(bytes_sedes)
uint32_list = List(uint32)


@pytest.mark.parametrize(
    'items',
    (
        (123, 456, 789, ),
        tuple(),
    ),
)
@pytest.mark.parametrize(
    'sequence_type,',
    (
        list,
        tuple,
    )
)
def test_uint32_list_sanity(items, sequence_type):
    value = sequence_type(items)
    assert len(hash_tree_root(value, uint32_list)) == 32


@given(items=st.lists(
    st.integers(
        min_value=0,
        max_value=2**32 - 1,
    )
)
)
@pytest.mark.parametrize(
    'sequence_type,',
    (
        list,
        tuple,
    )
)
def test_uint32_list_randomized(items, sequence_type):
    value = sequence_type(items)
    assert len(hash_tree_root(value, uint32_list)) == 32


@pytest.mark.parametrize(
    'items',
    (
        tuple(),
        (b'\x56' * 32, ),
        (b'\x56' * 32, ) * 100,
        (b'\x56' * 32, ) * 101,
    ),
)
@pytest.mark.parametrize(
    'sequence_type,',
    (
        list,
        tuple,
    )
)
def test_bytes_32_list_sanity(items, sequence_type):
    value = sequence_type(items)
    assert len(hash_tree_root(value, bytes32_list)) == 32


@given(data=st.data())
@pytest.mark.parametrize(
    'length',
    (32, 48, 96),
)
@pytest.mark.parametrize(
    'sequence_type,',
    (
        list,
        tuple,
    )
)
def test_bytes_n_list_randomized(data, length, sequence_type):
    sedes = List(BytesN(length))
    items = data.draw(
        st.lists(
            st.binary(
                min_size=length,
                max_size=length,
            )
        )
    )
    value = sequence_type(items)
    assert len(hash_tree_root(value, sedes)) == 32


@pytest.mark.parametrize(
    'items',
    (
        tuple(),
        (b'\x56', b'\xab' * 2, b'\xcd' * 3),
        (b'', b'\x56', ),
    ),
)
@pytest.mark.parametrize(
    'sequence_type,',
    (
        list,
        tuple,
    )
)
def test_bytes_sedes_list_sanity(items, sequence_type):
    value = sequence_type(items)
    assert len(hash_tree_root(value, bytes_list)) == 32


@given(items=st.lists(st.binary()))
@pytest.mark.parametrize(
    'sequence_type,',
    (
        list,
        tuple,
    )
)
def test_bytes_sedes_list_randomized(items, sequence_type):
    value = sequence_type(items)
    assert len(hash_tree_root(value, bytes_list)) == 32
