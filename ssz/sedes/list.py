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
from ssz.sedes import (
    address,
    boolean,
    bytes_sedes,
    hash32,
    uint32,
)
from ssz.sedes.base import (
    BaseSedes,
    LengthPrefixedSedes,
)


T = TypeVar("T")
S = TypeVar("S")


class List(LengthPrefixedSedes[Iterable[T], Tuple[S, ...]]):
    """
    A sedes for lists.

    WARNING: Avoid sets if possible, may not always lead to expected results
    (This is because iteration in sets doesn't always happen in the same order)
    """

    length_bytes = 4

    def __init__(self, element_sedes: BaseSedes[T, S] = None, empty: bool = False) -> None:
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

    def serialize_content(self, value: Iterable[T]) -> bytes:
        if isinstance(value, (bytes, bytearray, str)):
            raise SerializationError("Can not serialize strings as lists")

        if self.empty:
            self._validate_emptiness(value)

        return b"".join(
            self.element_sedes.serialize(element) for element in value
        )

    @staticmethod
    def _validate_emptiness(value: Iterable[T]) -> None:
        try:
            first(value)
        except StopIteration:
            pass
        else:
            raise SerializationError(
                "Can only serialize empty Iterables"
            )

    @to_tuple
    def deserialize_content(self, content: bytes) -> Generator[S, None, None]:
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


address_list = List(address)
boolean_list = List(boolean)
bytes_list = List(bytes_sedes)
empty_list: List[None, None] = List(empty=True)
hash32_list = List(hash32)
uint32_list = List(uint32)
