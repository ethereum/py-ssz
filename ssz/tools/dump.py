from typing import Sequence

from eth_utils import to_tuple

from ssz.hashable_container import HashableContainer
from ssz.hashable_list import HashableList
from ssz.hashable_vector import HashableVector
from ssz.sedes import (
    BaseSedes,
    Bitlist,
    Bitvector,
    Boolean,
    ByteVector,
    Container,
    List,
    Serializable,
    UInt,
    Vector,
)

from .codec import DefaultCodec


def to_formatted_dict(value, sedes=None, codec=DefaultCodec):
    return dump(value, sedes, codec)


def dump(value, sedes=None, codec=DefaultCodec):
    if isinstance(value, Serializable):
        return dump_serializable(value, codec)
    elif isinstance(value, HashableContainer):
        return dump_hashable_container(value, codec)
    elif isinstance(value, (HashableList, HashableVector)):
        return dump_hashable_sequence(value, codec)
    elif sedes is None:
        raise ValueError("Sedes may only be omitted for serializables or hashables")

    if isinstance(sedes, Boolean):
        return dump_boolean(value, sedes, codec)
    elif isinstance(sedes, UInt):
        return dump_integer(value, sedes, codec)
    elif isinstance(sedes, ByteVector):
        return dump_bytes(value, sedes, codec)
    elif isinstance(sedes, List):
        return dump_list(value, sedes, codec)
    elif isinstance(sedes, Vector):
        return dump_vector(value, sedes, codec)
    elif isinstance(sedes, (Bitlist, Bitvector)):
        return dump_bits(value, sedes, codec)
    elif isinstance(sedes, Container):
        return dump_container(value, sedes, codec)
    elif isinstance(sedes, BaseSedes):
        raise Exception(
            f"Unreachable: All sedes types have been checked, {sedes} was not found"
        )
    else:
        raise TypeError(f"Expected BaseSedes, got {type(sedes)}")


def dump_boolean(value, sedes, codec):
    if not isinstance(value, bool):
        raise ValueError(f"Expected value of type bool, got {type(value)}")
    return codec.encode_bool(value, sedes)


def dump_integer(value, sedes, codec):
    return codec.encode_integer(value, sedes)


def dump_bytes(value, sedes, codec):
    return codec.encode_bytes(value, sedes)


def dump_list(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    return tuple(dump(element, sedes.element_sedes, codec) for element in value)


def dump_vector(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    if not len(value) == sedes.length:
        raise ValueError(f"Expected {sedes.length} elements, got {len(value)}")
    return tuple(dump(element, sedes.element_sedes, codec) for element in value)


def dump_bits(value, sedes, codec):
    return codec.encode_bytes(sedes.serialize(value), sedes)


@to_tuple
def dump_container(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    elif not len(value) == len(sedes.field_sedes):
        raise ValueError(
            f"Expected {len(sedes.field_sedes)} elements, got {len(value)}"
        )

    for element, element_sedes in zip(value, sedes.field_sedes):
        yield dump(element, element_sedes, codec)


def dump_serializable(value, codec):
    dumped_values = dump(tuple(value), value._meta.container_sedes)
    return dict(zip(value._meta.field_names, dumped_values))


def dump_hashable_container(value, codec):
    dumped_values = dump(tuple(value), value._meta.container_sedes)
    return {
        field_name: dumped_value
        for (field_name, _), dumped_value in zip(value._meta.fields, dumped_values)
    }


def dump_hashable_sequence(value, codec):
    return tuple(dump(element, value.sedes.element_sedes, codec) for element in value)
