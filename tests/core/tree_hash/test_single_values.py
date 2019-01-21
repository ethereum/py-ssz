from hypothesis import (
    given,
    strategies as st,
)
import pytest

from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes import (
    Boolean,
    boolean,
    UnsignedInteger,
)
from ssz.tree_hash.hash_eth2 import (
    hash_eth2,
)
from ssz.tree_hash.tree_hash import (
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
    uintn = UnsignedInteger(num_bits)
    value = data.draw(
        st.integers(
            min_value=0,
            max_value=2**num_bits - 1,
        )
    )
    expected = value.to_bytes(num_bits // 8, 'big').ljust(32, b'\x00')
    assert hash_tree_root(value, uintn) == expected


@given(data=st.data())
@pytest.mark.parametrize(
    'num_bits',
    (384, 512),
)
def test_unsign_integers_more_than_32_bytes(data, num_bits):
    uintn = UnsignedInteger(num_bits)
    value = data.draw(
        st.integers(
            min_value=0,
            max_value=2**num_bits - 1,
        )
    )
    expected = hash_eth2(value.to_bytes(num_bits // 8, 'big'))
    assert hash_tree_root(value, uintn) == expected
