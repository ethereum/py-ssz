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
from ssz.hash import (
    hash_eth2,
)
from ssz.sedes.base import (
    BaseSedes,
    LengthPrefixedSedes,
)
from ssz.utils import (
    get_duplicates,
)

AnyTypedDict = TypedDict("AnyTypedDict", {})
TAnyTypedDict = TypeVar("TAnyTypedDict", bound=AnyTypedDict)


class Container(LengthPrefixedSedes[TAnyTypedDict, Dict[str, Any]]):

    length_bytes = 4

    def __init__(self, fields: Sequence[Tuple[str, BaseSedes[Any, Any]]]) -> None:
        field_names = tuple(field_name for field_name, field_sedes in fields)
        duplicate_field_names = get_duplicates(field_names)
        if duplicate_field_names:
            raise ValueError(
                f"The following fields are duplicated {','.join(sorted(duplicate_field_names))}"
            )

        self.fields = fields

    def serialize_content(self, value: TAnyTypedDict) -> bytes:
        return b"".join(
            field_sedes.serialize(value[field_name])
            for field_name, field_sedes in self.fields
        )

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
