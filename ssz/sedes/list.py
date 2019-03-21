from typing import (
    Generator,
    Iterable,
    Tuple,
    TypeVar,
)

from eth_utils import (
    to_tuple,
)
from eth_utils.toolz import (
    first,
)

from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes.base import (
    BaseSedes,
    BasicSedes,
    CompositeSedes,
)
from ssz.utils import (
    merkleize,
    mix_in_length,
    pack,
)

TSerializable = TypeVar("TSerializable")
TDeserialized = TypeVar("TDeserialized")


class List(CompositeSedes[Iterable[TSerializable], Tuple[TDeserialized, ...]]):

    def __init__(self,
                 element_sedes: BaseSedes[TSerializable, TDeserialized] = None,
                 empty: bool = False) -> None:
        if element_sedes and empty:
            raise ValueError(
                "Either one of Element Sedes or Empty has to be specified"
            )

        elif not element_sedes and not empty:
            raise ValueError(
                "Either Element Sedes or Empty has to be specified"
            )

        # This sedes object corresponds to each element of the iterable
        self.element_sedes = element_sedes
        # This empty bool indicates whether this sedes is meant for empty lists
        self.empty = empty

    #
    # Size
    #
    @property
    def is_static_sized(self):
        return False

    def get_static_size(self):
        raise ValueError("List has no static size")

    #
    # Serialization
    #
    def serialize_content(self, value: Iterable[TSerializable]) -> bytes:
        if isinstance(value, (bytes, bytearray, str)):
            raise SerializationError("Can not serialize strings as lists")

        if self.empty:
            self._validate_emptiness(value)

        return b"".join(
            self.element_sedes.serialize(element) for element in value
        )

    @staticmethod
    def _validate_emptiness(value: Iterable[TSerializable]) -> None:
        try:
            first(value)
        except StopIteration:
            pass
        else:
            raise SerializationError(
                "Can only serialize empty Iterables"
            )

    #
    # Deserialization
    #
    @to_tuple
    def deserialize_content(self, content: bytes) -> Generator[TDeserialized, None, None]:
        if self.empty and len(content) > 0:
            raise DeserializationError(f"Serialized list is not empty")

        element_start_index = 0
        while element_start_index < len(content):
            element, next_element_start_index = self.element_sedes.deserialize_segment(
                content,
                element_start_index,
            )

            if next_element_start_index <= element_start_index:
                raise Exception("Invariant: must always make progress")
            element_start_index = next_element_start_index

            yield element

        if element_start_index > len(content):
            raise Exception("Invariant: must not consume more data than available")

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: Iterable[TSerializable]) -> bytes:
        if isinstance(self.element_sedes, BasicSedes):
            serialized_items = tuple(
                self.element_sedes.serialize(element)
                for element in value
            )
            length = len(serialized_items)
            merkle_leaves = pack(serialized_items)
        else:
            merkle_leaves = tuple(
                self.element_sedes.hash_tree_root(element)
                for element in value
            )
            length = len(merkle_leaves)
        return mix_in_length(merkleize(merkle_leaves), length)


empty_list: List[None, None] = List(empty=True)
