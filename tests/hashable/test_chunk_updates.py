from hypothesis import given
from hypothesis import strategies as st

from ssz.hashable_structure import (
    get_appended_chunks,
    get_num_padding_elements,
    get_updated_chunks,
    update_element_in_chunk,
    update_elements_in_chunk,
)
from tests.hashable.chunk_strategies import (
    chunk_st,
    chunk_updates_st,
    element_size_st,
    element_st,
    elements_st,
    in_chunk_index_and_element_st,
)


@given(chunk_st(), in_chunk_index_and_element_st())
def test_update_element_in_chunk(original_chunk, in_chunk_index_and_element):
    index, element = in_chunk_index_and_element
    updated_chunk = update_element_in_chunk(original_chunk, index, element)
    element_size = len(element)
    assert (
        updated_chunk[: index * element_size] == original_chunk[: index * element_size]
    )
    assert updated_chunk[index * element_size : (index + 1) * element_size] == element
    assert (
        updated_chunk[(index + 1) * element_size :]
        == original_chunk[(index + 1) * element_size :]
    )


@given(st.data(), chunk_st(), element_size_st())
def test_update_elements_in_chunk(data, original_chunk, element_size):
    updates = data.draw(chunk_updates_st(32 // element_size, element_size))
    updated_chunk = update_elements_in_chunk(original_chunk, updates)

    expected_updated_chunk = original_chunk
    for index, element in updates.items():
        expected_updated_chunk = update_element_in_chunk(
            expected_updated_chunk, index, element
        )

    assert updated_chunk == expected_updated_chunk


@given(st.integers(min_value=0), element_size_st())
def test_get_num_padding(num_original_elements, element_size):
    num_original_chunks = (num_original_elements * element_size + 31) // 32

    num_padding = get_num_padding_elements(
        num_original_chunks, num_original_elements, element_size
    )
    assert ((num_original_elements + num_padding) * element_size) % 32 == 0
    assert (
        num_original_elements + num_padding
    ) * element_size == num_original_chunks * 32
    assert 0 <= num_padding < 32 // element_size


@given(elements_st(), st.integers(min_value=0))
def test_appended_chunks(appended_elements, num_padding_elements):
    chunks = get_appended_chunks(appended_elements, num_padding_elements)

    effective_appended_elements = appended_elements[num_padding_elements:]
    if not effective_appended_elements:
        assert chunks == ()

    joined_elements = b"".join(effective_appended_elements)
    joined_chunks = b"".join(chunks)

    padding_length = (len(joined_elements) + 31) // 32 * 32 - len(joined_elements)
    assert len(joined_chunks) == len(joined_elements) + padding_length
    assert joined_chunks == joined_elements + b"\x00" * padding_length


@given(st.data(), element_size_st())
def test_updated_chunks(data, element_size):
    original_elements = data.draw(st.lists(element_st(size=element_size), min_size=1))
    original_chunks = get_appended_chunks(original_elements, 0)
    num_padding_elements = get_num_padding_elements(
        len(original_chunks), len(original_elements), element_size
    )
    num_elements_per_chunk = 32 // element_size

    appended_elements = data.draw(st.lists(element_st(size=element_size)))
    updated_elements = data.draw(chunk_updates_st(len(original_elements), element_size))

    updated_chunks = get_updated_chunks(
        updated_elements,
        appended_elements,
        original_chunks,
        len(original_elements),
        num_padding_elements,
    )

    assert 0 <= min(updated_chunks.keys(), default=0)
    assert max(updated_chunks.keys(), default=0) < len(original_chunks)

    for element_index, element in updated_elements.items():
        chunk_index = element_index // num_elements_per_chunk
        in_chunk_index = element_index % num_elements_per_chunk
        first_byte_in_chunk = in_chunk_index * element_size
        last_byte_in_chunk = first_byte_in_chunk + element_size

        assert chunk_index in updated_chunks
        updated_chunk = updated_chunks[chunk_index]
        updated_element = updated_chunk[first_byte_in_chunk:last_byte_in_chunk]
        assert updated_element == element

    if num_padding_elements > 0 and appended_elements:
        padding_replacement = b"".join(appended_elements[:num_padding_elements])
        first_padding_element_index = len(original_elements) % num_elements_per_chunk
        last_padding_element_index = first_padding_element_index + min(
            num_padding_elements, len(appended_elements)
        )
        first_padding_replacement_byte = first_padding_element_index * element_size
        last_padding_replacement_byte = last_padding_element_index * element_size

        last_chunk = updated_chunks[len(original_chunks) - 1]

        assert (
            last_chunk[first_padding_replacement_byte:last_padding_replacement_byte]
            == padding_replacement
        )
