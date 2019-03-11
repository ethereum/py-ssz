from hypothesis import (
    given,
    strategies as st,
)
import pytest

from ssz.hash import (
    hash_eth2,
)
from ssz.sedes import (
    Boolean,
    BytesN,
    UInt,
    boolean,
    byte_list,
)
from ssz.tree_hash import (
    hash_tree_root,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        (True, b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),  # noqa
        (False, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),  # noqa
    ),
)
@pytest.mark.parametrize(
    'sedes,',
    (
        None,
        boolean,
        Boolean(),
    )
)
def test_boolean_serialize_values(value, sedes, expected):
    assert hash_tree_root(value, sedes) == expected


@given(data=st.data())
@pytest.mark.parametrize(
    'num_bits',
    (8, 16, 24, 32, 40, 48, 56, 64, 128, 256),
)
def test_unsign_integers_less_than_32_bytes(data, num_bits):
    uint_n = UInt(num_bits)
    value = data.draw(
        st.integers(
            min_value=0,
            max_value=2**num_bits - 1,
        )
    )
    expected = value.to_bytes(num_bits // 8, "little").ljust(32, b'\x00')
    assert hash_tree_root(value, uint_n) == expected


@given(data=st.data())
@pytest.mark.parametrize(
    'num_bits',
    (384, 512),
)
def test_unsign_integers_more_than_32_bytes(data, num_bits):
    uint_n = UInt(num_bits)
    value = data.draw(
        st.integers(
            min_value=0,
            max_value=2**num_bits - 1,
        )
    )
    expected = hash_eth2(value.to_bytes(num_bits // 8, "little"))
    assert hash_tree_root(value, uint_n) == expected


@given(value=st.binary())
def test_byte_list(value):
    assert len(hash_tree_root(value, byte_list)) == 32


@given(data=st.data())
@pytest.mark.parametrize(
    'length',
    (32, 48, 96),
)
def test_bytes_n(data, length):
    sedes = BytesN(length)
    value = data.draw(
        st.binary(
            min_size=length,
            max_size=length,
        )
    )
    assert len(hash_tree_root(value, sedes)) == 32
