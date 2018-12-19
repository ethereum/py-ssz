import pytest

from ssz.tree_hash.hash_eth2 import (
    hash_eth2,
)
from ssz.tree_hash.merkle_hash import (
    merkle_hash,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        # 128 bytes empty list + 32 bytes length of data
        (
            tuple(),
            b'\x00' * (128 + 32),
        ),
        (
            (b'\x01',),
            b'\x01' + int(1).to_bytes(32, 'big'),
        ),
        (
            (b'\x01', b'\x01', b'\x01',),
            b'\x01\x01\x01' + int(3).to_bytes(32, 'big'),
        ),
        (
            (b'\x55' * 64, b'\x66' * 64, b'\x77' * 64,),
            (
                hash_eth2(b'\x55' * 64 + b'\x66' * 64 + b'\x77' * 64) +
                int(3).to_bytes(32, 'big')
            ),
        ),
        (
            (b'\x55' * 96, b'\x66' * 96, b'\x77' * 96, b'\x88' * 96),
            (
                hash_eth2((
                    hash_eth2(b'\x55' * 96 + b'\x66' * 96) +
                    hash_eth2(b'\x77' * 96 + b'\x88' * 96)
                )) +
                int(4).to_bytes(32, 'big')
            ),
        ),
    ),
)
def test_merkle_hash(value, expected):
    assert merkle_hash(value) == hash_eth2(expected)
