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

from ssz.exceptions import (
    DeserializationError,
)
from ssz.utils import (
    merkleize,
    mix_in_length,
)
from ssz.sedes.base import (
    BaseSedes,
    CompositeSedes,
)
from ssz.utils import (
    get_duplicates,
)

AnyTypedDict = TypedDict("AnyTypedDict", {})
TAnyTypedDict = TypeVar("TAnyTypedDict", bound=AnyTypedDict)


class Container(CompositeSedes[TAnyTypedDict, Dict[str, Any]]):

    def __init__(self, fields: Sequence[Tuple[str, BaseSedes[Any, Any]]]) -> None:
        field_names = tuple(field_name for field_name, field_sedes in fields)
        duplicate_field_names = get_duplicates(field_names)
        if duplicate_field_names:
            raise ValueError(
                f"The following fields are duplicated {','.join(sorted(duplicate_field_names))}"
            )

        self.fields = fields

    #
    # Container size
    #
    @property
    def is_static_sized(self):
        return all(field_sedes.is_static_sized for _, field_sedes in self.fields)

    def get_static_size(self):
        if self.is_static_sized:
            raise ValueError("Container contains dynamically sized elements")

        return sum(field_sedes.get_static_size() for _, field_sedes in self.fields)

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: TAnyTypedDict) -> bytes:
        merkle_leaves = tuple(
            field_sedes.serialize(value[field_name])
            for field_name, field_sedes in self.fields
        )
        return mix_in_length(merkleize(merkle_leaves), len(merkle_leaves))

    #
    # Serialization
    #
    def serialize_content(self, value: TAnyTypedDict) -> bytes:
        return b"".join(
            field_sedes.serialize(value[field_name])
            for field_name, field_sedes in self.fields
        )

    #
    # Deserialization
    #
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
