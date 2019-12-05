from hypothesis import strategies as st
from pyrsistent import pvector

from ssz.hash_tree import HashTree


def chunk_count_st():
    return st.one_of(st.none(), st.integers(min_value=1, max_value=2 ** 5))


def chunk_st():
    return st.binary(min_size=32, max_size=32)


def element_size_st():
    return st.builds(lambda power: 2 ** power, st.integers(min_value=0, max_value=5))


@st.composite
def element_st(draw, size=None):
    if size is None:
        size = draw(element_size_st())
    return draw(st.binary(min_size=size, max_size=size))


@st.composite
def elements_st(draw, size=None, **kwargs):
    if size is None:
        size = draw(element_size_st())
    return draw(st.lists(element_st(size), **kwargs))


def in_chunk_index_st(element_size):
    return st.integers(min_value=0, max_value=32 // element_size - 1)


@st.composite
def in_chunk_index_and_element_st(draw, size=None):
    element = draw(element_st(size))
    index = draw(in_chunk_index_st(element_size=len(element)))
    return index, element


@st.composite
def chunk_updates_st(draw, num_original_elements, element_size):
    indices = draw(
        st.lists(
            st.integers(min_value=0, max_value=num_original_elements - 1), unique=True
        )
    )
    elements = draw(
        st.lists(element_st(element_size), min_size=len(indices), max_size=len(indices))
    )
    return dict(zip(indices, elements))


@st.composite
def chunks_and_chunk_count_st(draw):
    chunk_count = draw(chunk_count_st())
    if chunk_count:
        max_size = chunk_count
    else:
        max_size = 5
    chunks = draw(st.lists(chunk_st(), min_size=1, max_size=max_size))
    return pvector(chunks), chunk_count


def hash_tree_st():
    return st.builds(
        lambda chunks_and_chunk_count: HashTree.compute(*chunks_and_chunk_count),
        chunks_and_chunk_count_st(),
    )
