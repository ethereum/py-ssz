from collections.abc import (
    Iterable,
)

from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes import (
    address,
    boolean,
    hash32,
    uint32,
)


class List:
    """
    A sedes for lists.

    WARNING: Avoid sets if possible, may not always lead to expected results
    (This is because iteration in sets doesn't always happen in the same order)
    """
    LENGTH_BYTES = 4

    def __init__(self, element_sedes=None, empty=False):
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

    def serialize(self, val):
        if (
                not isinstance(val, Iterable) or
                isinstance(val, bytes) or
                isinstance(val, bytearray) or
                isinstance(val, str)
        ):
            raise SerializationError(
                'Can only serialize Iterable objects, except Dictionaries',
                val
            )

        if self.empty and len(val) != 0:
            raise ValueError(
                "Empty List Sedes cannot serialize non-empty Iterables"
            )

        serialized_iterable_string = b"".join(
            self.element_sedes.serialize(element) for element in val
        )

        if len(serialized_iterable_string) >= 2 ** (self.LENGTH_BYTES * 8):
            raise SerializationError(
                'List too long to fit into {} bytes after serialization'.format(self.LENGTH_BYTES),
                val
            )
        serialized_len = len(serialized_iterable_string).to_bytes(self.LENGTH_BYTES, 'big')

        return serialized_len + serialized_iterable_string

    def deserialize_segment(self, data, start_index):
        """
        Deserialize the data from the given start_index
        """
        # Make sure we have sufficient data for inferring length of list
        if len(data) < start_index + self.LENGTH_BYTES:
            raise DeserializationError(
                'Insufficient data: Cannot retrieve the length of list',
                data
            )

        # Number of bytes of only the list data, excluding the prepended list length
        list_length = int.from_bytes(data[start_index:start_index + self.LENGTH_BYTES], 'big')
        list_end_index = start_index + self.LENGTH_BYTES + list_length
        # Make sure we have sufficent data for inferring the whole list
        if len(data) < list_end_index:
            raise DeserializationError(
                'Insufficient data: Cannot retrieve the whole list data',
                data
            )

        deserialized_list = []
        # element_start_index is the start index of an element in the serialized bytes string
        element_start_index = start_index + self.LENGTH_BYTES
        while element_start_index < list_end_index:
            element, element_start_index = self.element_sedes.deserialize_segment(
                data, element_start_index
            )
            deserialized_list.append(element)

        return tuple(deserialized_list), list_end_index

    def deserialize(self, data):
        deserialized_data, end_index = self.deserialize_segment(data, 0)
        if end_index != len(data):
            raise DeserializationError(
                'Data to be deserialized is too long',
                data
            )

        return deserialized_data


address_list = List(address)
boolean_list = List(boolean)
empty_list = List(empty=True)
hash32_list = List(hash32)
uint32_list = List(uint32)
