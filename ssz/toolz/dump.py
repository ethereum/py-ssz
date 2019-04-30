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

from .formatters import (
    DefaultFormatter,
)


def to_formatted_dict(value, sedes=None, basic_sedes_formatter=DefaultFormatter):
    return dump(value, sedes, basic_sedes_formatter)


def dump(value, sedes=None, basic_sedes_formatter=DefaultFormatter):
    if sedes is None:
        if isinstance(value, Serializable):
            return dump_serializable(value, basic_sedes_formatter)
        else:
            raise ValueError("must provide sedes for non-Serializable")
    elif isinstance(sedes, Boolean):
        return dump_boolean(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, UInt):
        return dump_integer(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, (ByteList, ByteVector)):
        return dump_bytes(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, List):
        return dump_list(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, Vector):
        return dump_vector(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, Container):
        return dump_container(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, MetaSerializable):
        return dump_serializable(value, basic_sedes_formatter)
    elif isinstance(sedes, BaseSedes):
        raise Exception(f"Unreachable: All sedes types have been checked, {sedes} was not found")
    else:
        raise TypeError(f"Expected BaseSedes, got {type(sedes)}")


def dump_boolean(value, sedes, basic_sedes_formatter):
    if not isinstance(value, bool):
        raise ValueError(f"Expected value of type bool, got {type(value)}")
    return basic_sedes_formatter.format_bool(value, sedes)


def dump_integer(value, sedes, basic_sedes_formatter):
    return basic_sedes_formatter.format_integer(value, sedes)


def dump_bytes(value, sedes, basic_sedes_formatter):
    return basic_sedes_formatter.format_bytes(value, sedes)


def dump_list(value, sedes, basic_sedes_formatter):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    return tuple(dump(element, sedes.element_sedes, basic_sedes_formatter) for element in value)


def dump_vector(value, sedes, basic_sedes_formatter):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    if not len(value) == sedes.length:
        raise ValueError(f"Expected {sedes.length} elements, got {len(value)}")
    return tuple(dump(element, sedes.element_sedes, basic_sedes_formatter) for element in value)


@to_dict
def dump_container(value, sedes, basic_sedes_formatter):
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
            basic_sedes_formatter,
        )


def dump_serializable(value, basic_sedes_formatter):
    return dump(value.as_dict(), value._meta.container_sedes)
