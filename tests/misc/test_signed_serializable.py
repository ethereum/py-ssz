import pytest

import ssz
from ssz.sedes import (
    byte_list,
    uint8,
)


def test_field_number_check():
    with pytest.raises(TypeError):
        class TestA(ssz.SignedSerializable):
            fields = ()

    with pytest.raises(TypeError):
        class TestB(ssz.SignedSerializable):
            fields = (
                ("signature", byte_list),
            )

    class TestC(ssz.SignedSerializable):
        fields = (
            ("field1", uint8),
            ("signature", byte_list),
        )


def test_field_name_check():
    with pytest.raises(TypeError):
        class TestA(ssz.SignedSerializable):
            fields = (
                ("field1", uint8),
                ("field2", byte_list),
            )

    with pytest.raises(TypeError):
        class TestB(ssz.SignedSerializable):
            fields = (
                ("signature", uint8),
                ("field1", byte_list),
            )


def test_signing_root():
    class Signed(ssz.SignedSerializable):
        fields = (
            ("field1", uint8),
            ("field2", byte_list),
            ("signature", byte_list),
        )

    class Unsigned(ssz.Serializable):
        fields = (
            ("field1", uint8),
            ("field2", byte_list),
        )

    signed = Signed(123, b"\xaa", b"\x00")
    unsigned = Unsigned(123, b"\xaa")
    assert signed.signing_root == unsigned.root


def test_eq():
    class Signed(ssz.SignedSerializable):
        fields = (
            ("field1", uint8),
            ("field2", byte_list),
            ("signature", byte_list),
        )

    signed_a = Signed(123, b"\xaa", b"\x00")
    signed_b = signed_a.copy()
    assert signed_a == signed_b

    signed_b = signed_b.copy(field1=456)
    assert signed_a != signed_b
