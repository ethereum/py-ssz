from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)


class Integer:
    """
    A sedes for integers (Handles both int<N> and uint<N>).
    """
    # This variable captures 'N' in 'int<N>' or 'uint<N>'
    num_bytes = 0
    allows_signed_ints = True

    def __init__(self, serializer_type):
        # Make sure that the serializer_type is string and defined
        invalid_serializer_msg = "Unvalid serializer type given, string of type 'intN' or 'uintN' expected"  # noqa: E501
        if serializer_type is None or not isinstance(serializer_type, str):
            raise SerializationError(invalid_serializer_msg, serializer_type)

        if serializer_type[:3] == 'int':
            num_bits = int(serializer_type[3:])
            assert num_bits % 8 == 0
            self.num_bytes = num_bits // 8
            self.allows_signed_ints = True

        elif serializer_type[:4] == 'uint':
            num_bits = int(serializer_type[4:])
            assert num_bits % 8 == 0
            self.num_bytes = num_bits // 8
            self.allows_signed_ints = False

        else:
            raise SerializationError(invalid_serializer_msg, serializer_type)

    def serialize(self, val):
        if isinstance(val, bool) or not isinstance(val, int):
            raise SerializationError('Can only serialize integer values', val)

        if not self.allows_signed_ints:
            assert val >= 0

        return val.to_bytes(self.num_bytes, 'big', signed=self.allows_signed_ints)

    def _deserialize(self, data, start_idx):
        # Make sure we have sufficient data for deserializing
        if len(data) + start_idx < self.num_bytes:
            raise DeserializationError(
                'Insufficient data for deserializing',
                data
            )
        end_idx = start_idx + self.num_bytes
        return int.from_bytes(data[start_idx:end_idx], 'big', signed=self.allows_signed_ints), end_idx  # noqa: E501

    def deserialize(self, data):
        return self._deserialize(data, 0)[0]


int8 = Integer('int8')
int16 = Integer('int16')
int32 = Integer('int32')
int64 = Integer('int64')

uint8 = Integer('uint8')
uint16 = Integer('uint16')
uint32 = Integer('uint32')
uint64 = Integer('uint64')
