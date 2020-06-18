import pytest

from ssz.sedes import Bitvector


def test_bitvector_instantiation_bound():
    with pytest.raises(ValueError):
        bit_count = 0
        Bitvector(bit_count)
