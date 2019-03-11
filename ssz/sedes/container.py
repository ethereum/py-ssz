from typing import (
    Any,
    Dict,
    Generator,
    Sequence,
    Tuple,
    TypeVar,
)

from eth_utils import (
    to_dict,
)
from mypy_extensions import (
    TypedDict,
)

from ssz.constants import (
    LENGTH_PREFIX_SIZE,
)
from ssz.exceptions import (
    DeserializationError,
)
from ssz.hash import (
    hash_eth2,
)
from ssz.sedes.base import (
    BaseSedes,
)
from ssz.utils import (
    get_duplicates,
    get_length_prefix,
    validate_content_length,
)

AnyTypedDict = TypedDict("AnyTypedDict", {})
TAnyTypedDict = TypeVar("TAnyTypedDict", bound=AnyTypedDict)


class Container(BaseSedes[TAnyTypedDict, Dict[str, Any]]):

    def __init__(self, fields: Sequence[Tuple[str, BaseSedes[Any, Any]]]) -> None:
        field_names = tuple(field_name for field_name, field_sedes in fields)
        duplicate_field_names = get_duplicates(field_names)
        if duplicate_field_names:
            raise ValueError(
                f"The following fields are duplicated {','.join(sorted(duplicate_field_names))}"
            )

        self.fields = fields

    #
    # Serialization
    #
    def serialize(self, value: TAnyTypedDict) -> bytes:
        content = self.serialize_content(value)

        if not self.is_variable_length:
            return content
        else:
            validate_content_length(content)
            length_prefix = get_length_prefix(content)
            return length_prefix + content

    def serialize_content(self, value: TAnyTypedDict) -> bytes:
        return b"".join(
            field_sedes.serialize(value[field_name])
            for field_name, field_sedes in self.fields
        )

    #
    # Deserialization
    #
    def deserialize_segment(self, data: bytes, start_index: int) -> Tuple[Dict[str, Any], int]:
        if not self.is_variable_length:
            content_size = self.get_fixed_length()
            content, continuation_index = self.consume_bytes(data, start_index, content_size)
            return self.deserialize_content(content), continuation_index
        else:
            prefix, content_start_index = self.consume_bytes(data, start_index, LENGTH_PREFIX_SIZE)
            length = int.from_bytes(prefix, "little")
            content, continuation_index = self.consume_bytes(data, content_start_index, length)
            return self.deserialize_content(content), continuation_index

    @to_dict
    def deserialize_content(self, content: bytes) -> Generator[Tuple[str, Any], None, None]:
        field_start_index = 0
        for field_name, field_sedes in self.fields:
            field_value, next_field_start_index = field_sedes.deserialize_segment(
                content,
                field_start_index,
            )
            yield field_name, field_value

            if next_field_start_index <= field_start_index:
                raise Exception("Invariant: must always make progress")
            field_start_index = next_field_start_index

        if field_start_index < len(content):
            extra_bytes = len(content) - field_start_index
            raise DeserializationError(f"Serialized container ends with {extra_bytes} extra bytes")

        if field_start_index > len(content):
            raise Exception("Invariant: must not consume more data than available")

    def intermediate_tree_hash(self, value: TAnyTypedDict) -> bytes:
        field_hashes = [
            field_sedes.intermediate_tree_hash(value[field_name])
            for field_name, field_sedes in self.fields
        ]
        return hash_eth2(b"".join(field_hashes))

    #
    # Container size
    #
    @property
    def is_variable_length(self):
        return any(field_sedes.is_variable_length for _, field_sedes in self.fields)

    def get_fixed_length(self):
        if self.is_variable_length:
            raise ValueError("Container does not have a fixed length")

        return sum(field_sedes.get_fixed_length() for _, field_sedes in self.fields)
