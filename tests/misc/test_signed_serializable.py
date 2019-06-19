import pytest

import ssz
from ssz.fields import (
    ByteList,
    UInt8,
)


def test_field_number_check():
    with pytest.raises(TypeError):
        class TestB(ssz.SignedSerializable):
            signature = ByteList()

    class TestC(ssz.SignedSerializable):
        field1 = UInt8()
        signature = ByteList()


def test_field_name_check():
    with pytest.raises(TypeError):
        class TestA(ssz.SignedSerializable):
            field1 = UInt8()
            field2 = ByteList()

    with pytest.raises(TypeError):
        class TestB(ssz.SignedSerializable):
            signature = UInt8()
            field1 = ByteList()


def test_signing_root():
    class Signed(ssz.SignedSerializable):
        field1 = UInt8()
        field2 = ByteList()
        signature = ByteList()

    class Unsigned(ssz.Serializable):
        field1 = UInt8()
        field2 = ByteList()

    signed = Signed(123, b"\xaa", b"\x00")
    unsigned = Unsigned(123, b"\xaa")
    assert signed.signing_root == unsigned.root


def test_equality():
    class SigningFoo(ssz.SignedSerializable):
        field1 = UInt8()
        field2 = ByteList()
        signature = ByteList()

    signed_a = SigningFoo(12, b"\xaa", b"\x00")
    signed_b = signed_a.copy()
    assert signed_a == signed_b
    assert signed_a is not signed_b

    signed_b = signed_b.copy(field1=34)
    assert signed_a != signed_b

    # Serializable and SignedSerializable
    class Foo(ssz.Serializable):
        field1 = UInt8()
        field2 = ByteList()
        signature = ByteList()

    foo = Foo(
        signed_a.field1,
        signed_a.field2,
        signed_a.signature,
    )
    assert foo != signed_a
