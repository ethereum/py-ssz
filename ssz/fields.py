from typing import (
    Any,
    Sequence,
    Tuple,
)

from ssz import sedes
from ssz.sedes.serializable import (
    Field,
)


#
# int
#
class IntField(Field):
    def __get__(self, instance, owner) -> int:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: int) -> None:
        super().__set__(instance, value)


class UInt8(IntField):
    def __init__(self):
        super().__init__(sedes.uint8)


class UInt16(IntField):
    def __init__(self):
        super().__init__(sedes.uint8)


class UInt32(IntField):
    def __init__(self):
        super().__init__(sedes.uint8)


class UInt64(IntField):
    def __init__(self):
        super().__init__(sedes.uint8)


class UInt128(IntField):
    def __init__(self):
        super().__init__(sedes.uint8)


class UInt256(IntField):
    def __init__(self):
        super().__init__(sedes.uint8)


#
# bytes
#
class BytesField(Field):
    def __get__(self, instance, owner) -> bytes:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: bytes) -> None:
        super().__set__(instance, value)


class ByteList(BytesField):
    def __init__(self):
        super().__init__(sedes.byte_list)


class Bytes4(BytesField):
    def __init__(self):
        super().__init__(sedes.bytes4)


class Bytes32(BytesField):
    def __init__(self):
        super().__init__(sedes.bytes32)


class Bytes48(BytesField):
    def __init__(self):
        super().__init__(sedes.bytes48)


class Bytes96(BytesField):
    def __init__(self):
        super().__init__(sedes.bytes96)


#
# bool
#
class BoolField(Field):
    def __get__(self, instance, owner) -> bool:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: bool) -> None:
        super().__set__(instance, value)


class Boolean(BoolField):
    def __init__(self):
        super().__init__(sedes.boolean)


#
# Sequences
#
class SequenceField(Field):
    def __get__(self, instance, owner) -> Tuple[Any, ...]:
        return super().__get__(instance, owner)

    def __set__(self, instance, value: Sequence[Any]) -> None:
        super().__set__(instance, value)


class Vector(SequenceField):
    def __init__(self, element_sedes, length):
        super().__init__(sedes.Vector(element_sedes, length))


class List(SequenceField):
    def __init__(self, element_sedes):
        super().__init__(sedes.List(element_sedes))
