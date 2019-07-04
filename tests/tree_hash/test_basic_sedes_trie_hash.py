from hypothesis import (
    given,
    strategies as st,
)
import pytest

import ssz
from ssz.constants import (
    CHUNK_SIZE,
)
from ssz.sedes import (
    UInt,
    boolean,
)
from ssz.utils import (
    pad_zeros,
)


@st.composite
def uint_and_value_strategy(draw):
    num_bits = 8 * 2**draw(st.integers(min_value=0, max_value=5))
    uint = UInt(num_bits)
    value = draw(st.integers(min_value=0, max_value=2**num_bits - 1))
    return uint, value


@pytest.mark.parametrize(
    'value,expected',
    (
        (True, pad_zeros(b"\x01")),
        (False, pad_zeros(b"\x00")),
    ),
)
def test_boolean(value, expected):
    assert ssz.hash_tree_root(value, boolean) == expected


@given(uint_and_value_strategy())
def test_uint(uint_and_value):
    uint, value = uint_and_value
    assert ssz.hash_tree_root(value, uint) == ssz.encode(value, uint).ljust(CHUNK_SIZE, b"\x00")
