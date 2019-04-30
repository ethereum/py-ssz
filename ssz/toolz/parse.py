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

from .formatters import (
    DefaultFormatter,
)


def from_formatted_dict(value, sedes, basic_sedes_formatter=DefaultFormatter):
    return parse(value, sedes, basic_sedes_formatter)


def parse(value, sedes, basic_sedes_formatter=DefaultFormatter):
    if isinstance(sedes, Boolean):
        return parse_boolean(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, UInt):
        return parse_integer(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, (ByteList, ByteVector)):
        return parse_bytes(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, List):
        return parse_list(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, Vector):
        return parse_vector(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, Container):
        return parse_container(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, MetaSerializable):
        return parse_serializable(value, sedes, basic_sedes_formatter)
    elif isinstance(sedes, BaseSedes):
        raise Exception(f"Unreachable: All sedes types have been checked, {sedes} was not found")
    else:
        raise TypeError(f"Expected BaseSedes, got {type(sedes)}")


def parse_boolean(value, sedes, basic_sedes_formatter):
    if not isinstance(value, bool):
        raise ValueError(f"Expected value of type bool, got {type(value)}")
    return basic_sedes_formatter.format_bool(value, sedes)


def parse_integer(value, sedes, basic_sedes_formatter):
    return basic_sedes_formatter.unformat_integer(value, sedes)


def parse_bytes(value, sedes, basic_sedes_formatter):
    return basic_sedes_formatter.unformat_bytes(value, sedes)


def parse_list(value, sedes, basic_sedes_formatter):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    return tuple(parse(element, sedes.element_sedes, basic_sedes_formatter) for element in value)


def parse_vector(value, sedes, basic_sedes_formatter):
    if not isinstance(value, Sequence):
        raise ValueError(f"Expected Sequence, got {type(value)}")
    if not len(value) == sedes.length:
        raise ValueError(f"Expected {sedes.length} elements, got {len(value)}")
    return tuple(parse(element, sedes.element_sedes, basic_sedes_formatter) for element in value)


@to_dict
def parse_container(value, sedes, basic_sedes_formatter):
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
            basic_sedes_formatter,
        )


def parse_serializable(value, serializable_cls, basic_sedes_formatter):
    input_dict = parse(value, serializable_cls._meta.container_sedes)
    return serializable_cls(**input_dict)
