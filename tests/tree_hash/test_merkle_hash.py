import pytest

from ssz.utils import (
    hash_eth2,
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
            b'\x01' + int(1).to_bytes(32, "little"),
        ),
        (
            (b'\x01', b'\x01', b'\x01',),
            b'\x01\x01\x01' + int(3).to_bytes(32, "little"),
        ),
        # two items in one chunk
        (
            (b'\x55' * 64, b'\x66' * 64, b'\x77' * 64,),
            (
                hash_eth2(b'\x55' * 64 + b'\x66' * 64 + b'\x77' * 64) +
                int(3).to_bytes(32, "little")
            ),
        ),
        (
            (b'\x55' * 96, b'\x66' * 96, b'\x77' * 96, b'\x88' * 96),
            (
                hash_eth2((
                    hash_eth2(b'\x55' * 96 + b'\x66' * 96) +
                    hash_eth2(b'\x77' * 96 + b'\x88' * 96)
                )) +
                int(4).to_bytes(32, "little")
            ),
        ),
    ),
)
def test_merkle_hash(value, expected):
    assert merkle_hash(value) == hash_eth2(expected)
