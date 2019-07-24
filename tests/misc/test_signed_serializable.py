import pytest

import ssz
from ssz.sedes import (
    bytes1,
    uint8,
)


def test_field_number_check():
    with pytest.raises(TypeError):
        class TestA(ssz.SignedSerializable):
            fields = ()

    with pytest.raises(TypeError):
        class TestB(ssz.SignedSerializable):
            fields = (
                ("signature", bytes1),
            )

    class TestC(ssz.SignedSerializable):
        fields = (
            ("field1", uint8),
            ("signature", bytes1),
        )


def test_field_name_check():
    with pytest.raises(TypeError):
        class TestA(ssz.SignedSerializable):
            fields = (
                ("field1", uint8),
                ("field2", bytes1),
            )

    with pytest.raises(TypeError):
        class TestB(ssz.SignedSerializable):
            fields = (
                ("signature", uint8),
                ("field1", bytes1),
            )


def test_signing_root():
    class Signed(ssz.SignedSerializable):
        fields = (
            ("field1", uint8),
            ("field2", bytes1),
            ("signature", bytes1),
        )

    class Unsigned(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", bytes1),
        )

    signed = Signed(123, b"\xaa", b"\x00")
    unsigned = Unsigned(123, b"\xaa")
    assert signed.signing_root == unsigned.hash_tree_root


def test_equality():
    class SigningFoo(ssz.SignedSerializable):
        fields = (
            ("field1", uint8),
            ("field2", bytes1),
            ("signature", bytes1),
        )

    signed_a = SigningFoo(12, b"\xaa", b"\x00")
    signed_b = signed_a.copy()
    assert signed_a == signed_b
    assert signed_a is not signed_b

    signed_b = signed_b.copy(field1=34)
    assert signed_a != signed_b

    # Serializable and SignedSerializable
    class Foo(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", bytes1),
            ("signature", bytes1),
        )

    foo = Foo(
        signed_a.field1,
        signed_a.field2,
        signed_a.signature,
    )
    assert foo != signed_a
