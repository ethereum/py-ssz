import pytest

from ssz.hashable_structure import (
    BaseHashableStructure,
    get_updated_and_appended_chunks,
    update_element_in_chunk,
    update_elements_in_chunk,
)
from ssz.sedes import List, uint8, uint128


@pytest.mark.parametrize(
    ("original_chunk", "element_index", "element", "updated_chunk"),
    (
        (b"aabbcc", 0, b"xx", b"xxbbcc"),
        (b"aabbcc", 1, b"xx", b"aaxxcc"),
        (b"aabbcc", 2, b"xx", b"aabbxx"),
        (b"aabbcc", 0, b"xxxxxx", b"xxxxxx"),
    ),
)
def test_update_element_in_chunk(original_chunk, element_index, element, updated_chunk):
    assert (
        update_element_in_chunk(original_chunk, element_index, element) == updated_chunk
    )


@pytest.mark.parametrize(
    ("original_chunk", "updates", "updated_chunk"),
    (
        (b"aabbcc", {}, b"aabbcc"),
        (b"aabbcc", {0: b"xx"}, b"xxbbcc"),
        (b"aabbcc", {0: b"xx", 2: b"yy"}, b"xxbbyy"),
    ),
)
def test_update_elements_in_chunk(original_chunk, updates, updated_chunk):
    assert update_elements_in_chunk(original_chunk, updates) == updated_chunk


@pytest.mark.parametrize(
    (
        "updated_elements",
        "appended_elements",
        "original_chunks",
        "num_original_elements",
        "updated_chunks",
        "appended_chunks",
    ),
    (
        ({}, [], [b"00000000000000000000000000000000"], 0, {}, []),
        (
            {0: b"xx"},
            [],
            [b"xx000000000000000000000000000000"],
            8,
            {0: b"xx000000000000000000000000000000"},
            [],
        ),
        (
            {0: b"xx", 15: b"yy"},
            [],
            [b"00000000000000000000000000000000"],
            8,
            {0: b"xx0000000000000000000000000000yy"},
            [],
        ),
        (
            {16: b"xx"},
            [],
            [b"00000000000000000000000000000000", b"00000000000000000000000000000000"],
            20,
            {1: b"xx000000000000000000000000000000"},
            [],
        ),
        (
            {0: b"xx", 31: b"yy"},
            [],
            [b"00000000000000000000000000000000", b"00000000000000000000000000000000"],
            20,
            {
                0: b"xx000000000000000000000000000000",
                1: b"000000000000000000000000000000yy",
            },
            [],
        ),
        (
            {},
            [b"xx"],
            [b"00000000000000000000000000000000"],
            0,
            {0: b"xx000000000000000000000000000000"},
            [],
        ),
        (
            {},
            [b"xx"],
            [b"00000000000000000000000000000000"],
            8,
            {0: b"0000000000000000xx00000000000000"},
            [],
        ),
        (
            {},
            [b"xx"],
            [b"00000000000000000000000000000000"],
            16,
            {},
            [b"xx" + b"\x00" * 30],
        ),
        (
            {},
            [b"xx", b"yy"],
            [b"00000000000000000000000000000000"],
            16,
            {},
            [b"xxyy" + b"\x00" * 28],
        ),
    ),
)
def test_get_updated_and_appended_chunks(
    updated_elements,
    appended_elements,
    original_chunks,
    num_original_elements,
    updated_chunks,
    appended_chunks,
):
    updated, appended = get_updated_and_appended_chunks(
        updated_elements, appended_elements, original_chunks, num_original_elements
    )
    assert updated == updated_chunks
    assert appended == appended_chunks


@pytest.mark.parametrize(
    ("elements", "sedes"),
    (
        ([], List(uint8, 8)),
        ([1, 2, 3], List(uint8, 8)),
        ([1, 2, 3], List(uint128, 8)),
        ([[1, 2], [1], [1, 2, 3, 4, 5]], List(List(uint128, 8), 8)),
    ),
)
def test_hashable_structure_initialization(elements, sedes):
    hashable_structure = BaseHashableStructure.from_iterable(elements, sedes)
    assert len(hashable_structure) == len(elements)
    for element_in_structure, element in zip(hashable_structure, elements):
        assert element_in_structure == element
