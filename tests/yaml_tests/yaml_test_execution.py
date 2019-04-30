from collections.abc import (
    Mapping,
    Sequence,
)

from eth_utils import (
    decode_hex,
)

import ssz
from ssz.exceptions import (
    SSZException,
)
from ssz.sedes import (
    Container,
    List,
    Vector,
    sedes_by_name,
)
from ssz.toolz import (
    DefaultFormatter,
    from_formatted_dict,
)


class FailedTestCase(Exception):
    pass


class CustomFormatter(DefaultFormatter):
    @staticmethod
    def unformat_integer(value, sedes):
        return int(value)


def execute_ssz_test_case(test_case):
    sedes = parse_type_definition(test_case["type"])
    valid = test_case["valid"]

    if valid:
        execute_valid_ssz_test(test_case, sedes)
    else:
        execute_invalid_ssz_test(test_case, sedes)


def execute_valid_ssz_test(test_case, sedes):
    value = from_formatted_dict(test_case["value"], sedes, CustomFormatter)
    serial = decode_hex(test_case["ssz"])

    try:
        decoded = ssz.decode(serial, sedes)
    except SSZException:
        raise FailedTestCase("Deserializing valid SSZ failed")
    else:
        if decoded != value:
            raise FailedTestCase(f"Deserializing SSZ returned wrong result {decoded}")

    try:
        encoded = ssz.encode(value, sedes)
    except SSZException:
        raise FailedTestCase("Serializing valid value failed")
    else:
        if encoded != serial:
            raise FailedTestCase(f"Serializing value retunred wrong result {encoded}")


def execute_invalid_ssz_test(test_case, sedes):
    if "value" in test_case and "ssz" in test_case:
        raise ValueError("Test case for invalid inputs contains both value and ssz")

    if "value" in test_case:
        value = from_formatted_dict(test_case["value"], sedes, CustomFormatter)
        try:
            ssz.encode(value, sedes)
        except SSZException:
            pass
        else:
            raise FailedTestCase("Serializing invalid value did not yield an exception")

    elif "ssz" in test_case:
        serial = decode_hex(test_case["ssz"])
        try:
            ssz.decode(serial, sedes)
        except SSZException:
            pass
        else:
            raise FailedTestCase("Deserializing invalid SSZ did not yield an exception")

    else:
        raise ValueError("Test case for invalid inputs contains neither value nor ssz")


def execute_tree_hash_test_case(test_case):
    sedes = parse_type_definition(test_case["type"])
    value = from_formatted_dict(test_case["value"], sedes, CustomFormatter)
    expected_root = decode_hex(test_case["root"])
    calculated_root = ssz.hash_tree_root(value, sedes)
    assert calculated_root == expected_root


def parse_type_definition(type_definition):
    error_message = f"Could not parse type definition {type_definition}"

    if isinstance(type_definition, str):
        try:
            sedes = sedes_by_name[type_definition]
        except KeyError:
            raise ValueError(error_message)
        else:
            return sedes

    elif isinstance(type_definition, Sequence):
        if len(type_definition) == 1:
            return List(parse_type_definition(type_definition[0]))
        elif len(type_definition) == 2:
            element_type = parse_type_definition(type_definition[0])
            try:
                length = int(type_definition[1])
            except ValueError:
                raise ValueError(error_message)
            return Vector(element_type, length)
        else:
            raise ValueError(error_message)

    elif isinstance(type_definition, Mapping):
        return Container(tuple(
            (field_name, parse_type_definition(field_type))
            for field_name, field_type in type_definition.items()
        ))

    else:
        raise ValueError(error_message)
