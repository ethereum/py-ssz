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
    """
    LENGTH_BYTES = 4

    def __init__(self, sedes):
        # This sedes object corresponds to each item of the list
        self.sedes = sedes

    def serialize(self, val):
        if not isinstance(val, list):
            raise SerializationError('Can only serialize lists', val)
        # Make sure all items in list are of same type
        if not all((type(item)) == (type(val[0])) for item in val):
            raise SerializationError('Can only serialize lists having elements of same type', val)

        serialized_list_string = b''
        for item in val:
            serialized_list_string += self.sedes.serialize(item)
        if len(serialized_list_string) >= 2 ** (self.LENGTH_BYTES * 8):
            raise SerializationError(
                'List too long to fit into {} bytes after serialization'.format(self.LENGTH_BYTES),
                val
            )
        serialized_len = len(serialized_list_string).to_bytes(self.LENGTH_BYTES, 'big')

        return serialized_len + serialized_list_string

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
        item_index = start_index + self.LENGTH_BYTES
        while item_index < list_end_index:
            object, item_index = self.sedes.deserialize_segment(data, item_index)
            deserialized_list.append(object)

        return deserialized_list, list_end_index

    def deserialize(self, data):
        deserialized_data, end_index = self.deserialize_segment(data, 0)
        if end_index != len(data):
            raise DeserializationError(
                'Data to be deserialized is too long',
                data
            )

        return deserialized_data


addr_list = List(address)
bool_list = List(boolean)
hash_list = List(hash32)
int_list = List(uint32)
