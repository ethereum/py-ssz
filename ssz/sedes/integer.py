from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)


class Integer:
    """
    A sedes for integers (uint<N>).
    """
    num_bytes = 0

    def __init__(self, num_bytes):
        self.num_bytes = num_bytes

    def serialize(self, val):
        if isinstance(val, bool) or not isinstance(val, int):
            raise SerializationError(
                'As per specified sedes object, can only serialize non-negative integer values',
                val
            )

        if val < 0:
            raise SerializationError(
                'As per specified sedes object, can only serialize non-negative integer values',
                val
            )

        try:
            serialized_obj = val.to_bytes(self.num_bytes, 'big')
        except OverflowError as err:
            raise SerializationError('As per specified sedes object, %s' % err, val)

        return serialized_obj

    def deserialize_from(self, data, start_index):
        """
        Deserialize the data from the given start_index
        """
        # Make sure we have sufficient data for deserializing
        if len(data) + start_index < self.num_bytes:
            raise DeserializationError(
                'Insufficient data for deserializing',
                data
            )
        end_index = start_index + self.num_bytes
        return int.from_bytes(data[start_index:end_index], 'big'), end_index

    def deserialize(self, data):
        return self.deserialize_from(data, 0)[0]


uint8 = Integer(1)
uint16 = Integer(2)
uint32 = Integer(4)
uint64 = Integer(8)
