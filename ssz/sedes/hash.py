from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)


class Hash:
    """
    A sedes for hashes (hash<N>).
    """
    num_bytes = 0

    def __init__(self, num_bytes):
        if num_bytes <= 0:
            raise ValueError(
                "Number of bytes should be non-negavtive"
            )

        self.num_bytes = num_bytes

    def serialize(self, val):
        if not isinstance(val, bytes):
            raise SerializationError('Hash should be of type bytes', val)
        if len(val) != self.num_bytes:
            raise SerializationError(
                "Can only serialize values of {} bytes".format(self.num_bytes),
                val
            )

        return val

    def deserialize_segment(self, data, start_index):
        """
        Deserialize the data from the given start_index
        """
        # Make sure we have sufficient data for deserializing
        if len(data) < self.num_bytes + start_index:
            raise DeserializationError(
                'Insufficient data for deserializing',
                data
            )
        end_index = start_index + self.num_bytes
        return data[start_index:end_index], end_index

    def deserialize(self, data):
        deserialized_data, end_index = self.deserialize_segment(data, 0)
        if end_index != len(data):
            raise DeserializationError(
                'Data to be deserialized is too long',
                data
            )

        return deserialized_data


hash32 = Hash(32)
address = Hash(20)
