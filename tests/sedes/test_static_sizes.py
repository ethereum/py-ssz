import pytest

from ssz.sedes import (
    Container,
    List,
    Tuple,
    boolean,
    uint8,
    uint512,
)


@pytest.mark.parametrize(
    ("sedes", "size"),
    (
        (boolean, 1),
        (uint8, 1),
        (uint512, 64),
        (Tuple(0, uint8), 0),
        (Tuple(2, uint8), 2),
        (Container(()), 0),
        (Container((("a", uint8), ("b", Tuple(4, uint8)))), 5),
        (Tuple(0, List(uint8)), 0),
        (Tuple(4, Container((("a", uint8), ("b", Tuple(4, uint8))))), 20),
    ),
)
def test_static_size(sedes, size):
    assert sedes.is_static_sized
    assert sedes.get_static_size() == size


@pytest.mark.parametrize(
    "sedes",
    (
        List(uint8),
        List(Tuple(2, uint8)),
        List(List(uint8)),
        List(Container((("a", uint8), ("b", Tuple(4, uint8))))),
        Tuple(2, List(uint8)),
        Container((("a", List(uint8)),)),
        Container((("a", uint8), ("b", List(uint8)), ("c", uint8))),
        Container((("a", Container((("a", List(uint8)),))),)),
    ),
)
def test_dynamic_size(sedes):
    assert not sedes.is_static_sized
    with pytest.raises(ValueError):
        sedes.get_static_size()
