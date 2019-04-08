import pytest

import ssz
from ssz.sedes import (
    uint8,
)


def test_duplicate_fields():
    with pytest.raises(TypeError):
        class Test(ssz.Serializable):
            fields = (
                ("field1", uint8),
                ("field1", uint8),
            )


def test_field_immutability():
    class Test(ssz.Serializable):
        fields = (
            ("field1", uint8),
        )

    test = Test(4)
    with pytest.raises(AttributeError):
        test.field1 = 5


@pytest.mark.parametrize(
    ("args", "kwargs"),
    (
        ((), {}),
        ((1,), {}),
        ((1, 2, 3), {}),
        ((), {"field1": 1}),
        ((), {"field1": 1, "field2": 2, "field3": 3}),
        ((1), {"field1": 1, "field2": 2}),
        ((1, 2), {"field2": 2}),
    )
)
def test_initialization_with_invalid_arguments(args, kwargs):
    class Test(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", uint8),
        )

    with pytest.raises(TypeError):
        Test(*args, **kwargs)


@pytest.mark.parametrize(
    ("args", "kwargs"),
    (
        ((1, 2), {}),
        ((1,), {"field2": 2}),
        ((), {"field1": 1, "field2": 2}),
    )
)
def test_initialization_with_valid_arguments(args, kwargs):
    class Test(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", uint8),
        )

    test = Test(*args, **kwargs)
    assert test.field1 == 1
    assert test.field2 == 2


def test_copy():
    class Test(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", uint8),
        )

    original = Test(1, 2)
    copy = original.copy()

    assert isinstance(copy, Test)
    assert copy is not original
    assert copy == original


def test_copy_nested():
    class Inner(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", uint8),
        )

    class Outer(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", Inner),
        )

    original = Outer(1, Inner(2, 3))
    copy = original.copy()

    assert isinstance(copy, Outer)
    assert copy is not original
    assert copy.field2 is not original.field2
    assert copy.field1 == 1
    assert copy.field2.field1 == 2
    assert copy.field2.field2 == 3


def test_equality():
    class TestA(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", uint8),
        )

    class TestB(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", uint8),
        )

    class TestC(ssz.Serializable):
        fields = (
            ("field2", uint8),
            ("field1", uint8),
        )

    test_a1 = TestA(1, 2)
    test_a2 = TestA(1, 2)
    test_a3 = TestA(1, 3)
    test_b1 = TestB(1, 2)
    test_c1 = TestC(1, 2)
    test_c2 = TestC(2, 1)

    assert test_a1 == test_a1
    assert test_a2 == test_a1
    assert test_a3 != test_a1
    assert test_b1 == test_a1
    assert test_c1 == test_a1
    assert test_c2 != test_a1


def test_root():
    class Test(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", uint8),
        )

    test = Test(1, 2)
    assert test.root == ssz.hash_tree_root(test, Test)
