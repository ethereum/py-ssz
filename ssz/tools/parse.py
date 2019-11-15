from collections.abc import Mapping
from typing import Sequence

from eth_utils import to_tuple

from ssz.hashable_container import MetaHashableContainer
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
    UInt,
    Vector,
)
from ssz.sedes.serializable import MetaSerializable

from .codec import DefaultCodec


def from_formatted_dict(value, sedes, codec=DefaultCodec):
    return parse(value, sedes, codec)


def parse(value, sedes, codec=DefaultCodec):
    if isinstance(sedes, Boolean):
        return parse_boolean(value, sedes, codec)
    elif isinstance(sedes, UInt):
        return parse_integer(value, sedes, codec)
    elif isinstance(sedes, ByteVector):
        return parse_bytes(value, sedes, codec)
    elif isinstance(sedes, List):
        return parse_list(value, sedes, codec)
    elif isinstance(sedes, Vector):
        return parse_vector(value, sedes, codec)
    elif isinstance(sedes, Container):
        return parse_container(value, sedes, codec)
    elif isinstance(sedes, (Bitlist, Bitvector)):
        return parse_bits(value, sedes, codec)
    elif isinstance(sedes, MetaSerializable):
        return parse_serializable(value, sedes, codec)
    elif isinstance(sedes, MetaHashableContainer):
        return parse_hashable(value, sedes, codec)
    elif isinstance(sedes, BaseSedes):
        raise Exception(
            f"Unreachable: All sedes types have been checked, {sedes} was not found"
        )
    else:
        raise TypeError(f"Expected BaseSedes, got {type(sedes)}")


def parse_boolean(value, sedes, codec):
    if not isinstance(value, bool):
        raise ValueError(f"Expected value of type bool, got {type(value)}")
    return codec.decode_bool(value, sedes)


def parse_integer(value, sedes, codec):
    return codec.decode_integer(value, sedes)


def parse_bytes(value, sedes, codec):
    return codec.decode_bytes(value, sedes)


def parse_list(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    elements = tuple(parse(element, sedes.element_sedes, codec) for element in value)
    return HashableList.from_iterable(elements, sedes=sedes)


def parse_vector(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    if not len(value) == sedes.length:
        raise ValueError(f"Expected {sedes.length} elements, got {len(value)}")
    elements = tuple(parse(element, sedes.element_sedes, codec) for element in value)
    return HashableVector.from_iterable(elements, sedes=sedes)


def parse_bits(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")

    data = parse_bytes(value, sedes, codec)
    deserialized = sedes.deserialize(data)
    return tuple(parse_boolean(element, sedes, codec) for element in deserialized)


@to_tuple
def parse_container(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    elif not len(value) == len(sedes.field_sedes):
        raise ValueError(
            f"Expected {len(sedes.field_sedes)} elements, got {len(value)}"
        )

    for element, element_sedes in zip(value, sedes.field_sedes):
        yield parse(element, element_sedes, codec)


def parse_serializable(value, serializable_cls, codec):
    if not isinstance(value, Mapping):
        raise ValueError(f"Expected Mapping, got {type(value)}")
    parse_args = tuple(
        value[field_name] for field_name in serializable_cls._meta.field_names
    )
    input_args = parse(parse_args, serializable_cls._meta.container_sedes)
    input_kwargs = dict(zip(serializable_cls._meta.field_names, input_args))
    return serializable_cls(**input_kwargs)


def parse_hashable(value, hashable_cls, codec):
    if not isinstance(value, Mapping):
        raise ValueError(f"Expected Mapping, got {type(value)}")
    input_kwargs = {
        field_name: parse(value[field_name], field_type, codec)
        for field_name, field_type in hashable_cls._meta.fields
    }
    return hashable_cls.create(**input_kwargs)
