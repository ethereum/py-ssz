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
    Serializable,
    UInt,
    Vector,
)
from ssz.sedes.serializable import (
    MetaSerializable,
)

from .codec import (
    DefaultCodec,
)


def to_formatted_dict(value, sedes=None, codec=DefaultCodec):
    return dump(value, sedes, codec)


def dump(value, sedes=None, codec=DefaultCodec):
    if sedes is None:
        if isinstance(value, Serializable):
            return dump_serializable(value, codec)
        else:
            raise ValueError("must provide sedes for non-Serializable")

    if isinstance(sedes, Boolean):
        return dump_boolean(value, sedes, codec)
    elif isinstance(sedes, UInt):
        return dump_integer(value, sedes, codec)
    elif isinstance(sedes, (ByteList, ByteVector)):
        return dump_bytes(value, sedes, codec)
    elif isinstance(sedes, List):
        return dump_list(value, sedes, codec)
    elif isinstance(sedes, Vector):
        return dump_vector(value, sedes, codec)
    elif isinstance(sedes, Container):
        return dump_container(value, sedes, codec)
    elif isinstance(sedes, MetaSerializable):
        return dump_serializable(value, codec)
    elif isinstance(sedes, BaseSedes):
        raise Exception(f"Unreachable: All sedes types have been checked, {sedes} was not found")
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


@to_dict
def dump_container(value, sedes, codec):
    if not isinstance(value, Mapping):
        raise ValueError(f"Expected mapping, got {type(value)}")
    field_names_got = set(value.keys())
    field_names_expected = set(field_name for field_name, _ in sedes.fields)
    if field_names_got != field_names_expected:
        raise ValueError(
            f"Unexpected fields: {field_names_got.difference(field_names_expected)}"
        )
    for field_name, field_value in value.items():
        yield field_name, dump(
            field_value,
            sedes.field_name_to_sedes[field_name],
            codec,
        )


def dump_serializable(value, codec):
    return dump(value.as_dict(), value._meta.container_sedes)
