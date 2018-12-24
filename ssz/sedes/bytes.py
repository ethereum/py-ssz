from ssz.constants import (
    BYTES_PREFIX_LENGTH,
)
from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)

from .base import (
    BaseSSZSedes,
)


class Bytes(BaseSSZSedes):
    """
    A sedes for byte objects.
    """

    def serialize(self, val):
        if not isinstance(val, (bytes, bytearray)):
            raise SerializationError(
                "Can only serialize bytes or bytearray objects",
                val
            )

        object_len = len(val)
        if object_len >= 2 ** (BYTES_PREFIX_LENGTH * 8):
            raise SerializationError(
                f'Object too long for its length to fit into {BYTES_PREFIX_LENGTH} bytes'
                f'after serialization',
                val
            )

        # Convert the length of bytes to a 4 bytes value
        object_len_bytes = object_len.to_bytes(BYTES_PREFIX_LENGTH, 'big')

        return object_len_bytes + val

    def deserialize_segment(self, data, start_index):
        """
        Deserialize the data from the given start_index
        """
        # Make sure we have sufficient data for inferring length of bytes object
        if len(data) < start_index + BYTES_PREFIX_LENGTH:
            raise DeserializationError(
                'Insufficient data: Cannot retrieve the length of bytes object',
                data
            )

        # object_len contains the length of the original bytes object
        object_len = int.from_bytes(data[start_index:start_index + BYTES_PREFIX_LENGTH], 'big')
        # object_start_index is the start index of bytes object in the serialized bytes string
        object_start_index = start_index + BYTES_PREFIX_LENGTH
        object_end_index = object_start_index + object_len

        # Make sure we have sufficent data for inferring the whole bytes object
        if len(data) < object_end_index:
            raise DeserializationError(
                'Insufficient data: Cannot retrieve the whole list bytes object',
                data
            )

        return data[object_start_index:object_end_index], object_end_index

    def deserialize(self, data):
        deserialized_data, end_index = self.deserialize_segment(data, 0)
        if end_index != len(data):
            raise DeserializationError(
                'Data to be deserialized is too long',
                data
            )

        return deserialized_data


bytes_sedes = Bytes()
