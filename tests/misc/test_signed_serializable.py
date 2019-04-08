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


def test_signed_root():
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
    assert signed.signed_root == unsigned.root
