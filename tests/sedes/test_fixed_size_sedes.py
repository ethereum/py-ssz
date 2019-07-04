import pytest

from ssz.sedes import (
    ByteVector,
    Container,
    List,
    Vector,
    boolean,
    byte,
    byte_list,
    bytes32,
    bytes48,
    bytes96,
    uint8,
    uint256,
)


@pytest.mark.parametrize(
    ("sedes", "size"),
    (
        (boolean, 1),
        (uint8, 1),
        (uint256, 32),
        (Vector(uint8, 0), 0),
        (Vector(uint8, 2), 2),
        (Container((uint8, Vector(uint8, 4))), 5),
        (Vector(List(uint8, 2**32), 0), 0),
        (Vector(Container((uint8, Vector(uint8, 4))), 4), 20),
        (byte, 1),
        (ByteVector(0), 0),
        (bytes32, 32),
        (bytes48, 48),
        (bytes96, 96),
    ),
)
def test_fixed_size(sedes, size):
    assert sedes.is_fixed_sized
    assert sedes.get_fixed_size() == size


@pytest.mark.parametrize(
    "sedes",
    (
        List(uint8, 2**32),
        List(Vector(uint8, 2), 2**32),
        List(List(uint8, 2**32), 2**32),
        List(Container((uint8, Vector(uint8, 4))), 2**32),
        Vector(List(uint8, 2**32), 2),
        Container((List(uint8, 2**32),)),
        Container((uint8, List(uint8, 2**32), uint8)),
        Container((Container((List(uint8, 2**32),)),)),
        byte_list,
    ),
)
def test_dynamic_size(sedes):
    assert not sedes.is_fixed_sized
    with pytest.raises(ValueError):
        sedes.get_fixed_size()
