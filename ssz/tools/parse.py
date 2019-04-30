from typing import (
    Mapping,
    Sequence,
)

from eth_utils import (
    to_dict,
)

from ssz.sedes import (
    BaseSedes,
    Boolean,
    ByteList,
    ByteVector,
    Container,
    List,
    UInt,
    Vector,
)
from ssz.sedes.serializable import (
    MetaSerializable,
)

from .codec import (
    DefaultCodec,
)


def from_formatted_dict(value, sedes, codec=DefaultCodec):
    return parse(value, sedes, codec)


def parse(value, sedes, codec=DefaultCodec):
    if isinstance(sedes, Boolean):
        return parse_boolean(value, sedes, codec)
    elif isinstance(sedes, UInt):
        return parse_integer(value, sedes, codec)
    elif isinstance(sedes, (ByteList, ByteVector)):
        return parse_bytes(value, sedes, codec)
    elif isinstance(sedes, List):
        return parse_list(value, sedes, codec)
    elif isinstance(sedes, Vector):
        return parse_vector(value, sedes, codec)
    elif isinstance(sedes, Container):
        return parse_container(value, sedes, codec)
    elif isinstance(sedes, MetaSerializable):
        return parse_serializable(value, sedes, codec)
    elif isinstance(sedes, BaseSedes):
        raise Exception(f"Unreachable: All sedes types have been checked, {sedes} was not found")
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
    return tuple(parse(element, sedes.element_sedes, codec) for element in value)


def parse_vector(value, sedes, codec):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    if not len(value) == sedes.length:
        raise ValueError(f"Expected {sedes.length} elements, got {len(value)}")
    return tuple(parse(element, sedes.element_sedes, codec) for element in value)


@to_dict
def parse_container(value, sedes, codec):
    if not isinstance(value, Mapping):
        raise ValueError(f"Expected mapping, got {type(value)}")
    field_names_got = set(value.keys())
    field_names_expected = set(field_name for field_name, _ in sedes.fields)
    if field_names_got != field_names_expected:
        raise ValueError(
            f"Unexpected fields: {field_names_got.difference(field_names_expected)}"
        )
    for field_name, field_value in value.items():
        yield field_name, parse(
            field_value,
            sedes.field_name_to_sedes[field_name],
            codec,
        )


def parse_serializable(value, serializable_cls, codec):
    input_dict = parse(value, serializable_cls._meta.container_sedes)
    return serializable_cls(**input_dict)
