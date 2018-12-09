from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)


class UnsignedInteger:
    """
    A sedes for integers (uint<N>).
    """
    num_bytes = 0

    def __init__(self, num_bits):
        # Make sure the number of bits are multiple of 8
        if num_bits % 8 != 0:
            raise ValueError(
                "Number of bits should be multiple of 8"
            )
        if num_bits <= 0:
            raise ValueError(
                "Number of bits should be greater than 0"
            )
        self.num_bytes = num_bits // 8

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

    def deserialize_segment(self, data, start_index):
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
        return self.deserialize_segment(data, 0)[0]


uint8 = UnsignedInteger(8)
uint16 = UnsignedInteger(16)
uint24 = UnsignedInteger(24)
uint32 = UnsignedInteger(32)
uint40 = UnsignedInteger(40)
uint48 = UnsignedInteger(48)
uint56 = UnsignedInteger(56)
uint64 = UnsignedInteger(64)
uint128 = UnsignedInteger(128)
uint256 = UnsignedInteger(256)
uint384 = UnsignedInteger(384)
uint512 = UnsignedInteger(512)
