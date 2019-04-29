from collections.abc import (
    Mapping,
    Sequence,
)

from eth_utils import (
    decode_hex,
    encode_hex,
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
    BaseSerializable,
    MetaSerializable,
)


class FormattedDictIO:
    def __init__(self, int_as):
        self.int_as = int_as

    def _parse_int(self, value):
        if self.int_as == "int":
            if not isinstance(value, int):
                raise ValueError(f"Expected value of type int, got {type(value)}")
            return value
        elif self.int_as == "str":
            if not isinstance(value, str):
                raise ValueError(f"Expected value of type str, got {type(value)}")
            return int(value)
        elif self.int_as == "hex":
            return int.from_bytes(decode_hex(value), "little")
        else:
            raise TypeError('Expected "int", "str", or "hex"')

    def _dump_int(self, value, size):
        if self.int_as == "int":
            return value
        elif self.int_as == "str":
            return str(value)
        elif self.int_as == "hex":
            return encode_hex(value.to_bytes(size, "little"))
        else:
            raise TypeError('Expected "int", "str", or "hex"')

    def parse_value(self, value, sedes=None):
        if isinstance(sedes, MetaSerializable):
            serializable_cls = sedes
            input_dict = self.parse_value(value, sedes._meta.container_sedes)
            return serializable_cls(**input_dict)

        elif isinstance(sedes, Boolean):
            if not isinstance(value, bool):
                raise ValueError(f"Expected value of type bool, got {type(value)}")
            return value

        elif isinstance(sedes, UInt):
            return self._parse_int(value)

        elif isinstance(sedes, List):
            if not isinstance(value, Sequence):
                raise ValueError(f"Expected list, got {type(value)}")
            return tuple(self.parse_value(element, sedes.element_sedes) for element in value)

        elif isinstance(sedes, Vector):
            if not isinstance(value, Sequence):
                raise ValueError(f"Expected list, got {type(value)}")
            if not len(value) == sedes.length:
                raise ValueError(f"Expected {sedes.length} elements, got {len(value)}")
            return tuple(self.parse_value(element, sedes.element_sedes) for element in value)

        elif isinstance(sedes, (ByteList, ByteVector)):
            return decode_hex(value)

        elif isinstance(sedes, Container):
            if not isinstance(value, Mapping):
                raise ValueError(f"Expected mapping, got {type(value)}")
            field_names_got = set(value.keys())
            field_names_expected = set(field_name for field_name, _ in sedes.fields)
            if field_names_got != field_names_expected:
                raise ValueError(
                    f"Unexpected fields: {field_names_got.difference(field_names_expected)}"
                )
            return {
                field_name: self.parse_value(field_value, sedes.field_name_to_sedes[field_name])
                for field_name, field_value in value.items()
            }

        elif isinstance(sedes, BaseSedes):
            raise Exception("Unreachable: All sedes types have been checked")

        else:
            raise TypeError("Expected BaseSedes")

    def dump_value(self, value, sedes=None):
        if sedes is None or isinstance(value, BaseSerializable):
            if not isinstance(value, BaseSerializable):
                raise ValueError(f"Expected value is a BaseSerializable, got {type(value)}")
            return self.dump_value(value.as_dict(), value._meta.container_sedes)

        elif isinstance(sedes, Boolean):
            if not isinstance(value, bool):
                raise ValueError(f"Expected value of type bool, got {type(value)}")
            return value

        elif isinstance(sedes, UInt):
            return self._dump_int(value, sedes.size)

        elif isinstance(sedes, List):
            if not isinstance(value, Sequence):
                raise ValueError(f"Expected list, got {type(value)}")
            return tuple(self.dump_value(element, sedes.element_sedes) for element in value)

        elif isinstance(sedes, Vector):
            if not isinstance(value, Sequence):
                raise ValueError(f"Expected list, got {type(value)}")
            if not len(value) == sedes.length:
                raise ValueError(f"Expected {sedes.length} elements, got {len(value)}")
            return tuple(self.dump_value(element, sedes.element_sedes) for element in value)

        elif isinstance(sedes, (ByteList, ByteVector)):
            return encode_hex(value)

        elif isinstance(sedes, Container):
            if not isinstance(value, Mapping):
                raise ValueError(f"Expected mapping, got {type(value)}")
            field_names_got = set(value.keys())
            field_names_expected = set(field_name for field_name, _ in sedes.fields)
            if field_names_got != field_names_expected:
                raise ValueError(
                    f"Unexpected fields: {field_names_got.difference(field_names_expected)}"
                )
            return {
                field_name: self.dump_value(field_value, sedes.field_name_to_sedes[field_name])
                for field_name, field_value in value.items()
            }
        elif isinstance(sedes, BaseSedes):
            raise Exception("Unreachable: All sedes types have been checked")

        else:
            raise TypeError("Expected BaseSedes")
