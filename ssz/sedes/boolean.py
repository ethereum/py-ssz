from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)


class Boolean:
    """
    A sedes for booleans.
    """
    def serialize(self, obj):
        if not isinstance(obj, bool):
            raise SerializationError('Can only serialize boolean values', obj)

        if obj is False:
            return b'\x00'
        elif obj is True:
            return b'\x01'
        else:
            raise Exception("Invariant: no other options for boolean values")

    def deserialize_segment(self, serialized_obj, start_index):
        """
        Deserialize the data from the given start_index
        """
        # Make sure we have sufficient data for inferring length of list
        if len(serialized_obj) < start_index + 1:
            raise DeserializationError(
                'Insufficient data for deserializing',
                serialized_obj
            )

        # Deal with only the first byte of the whole serialized data
        boolean_serialized_obj = serialized_obj[start_index: start_index + 1]
        if boolean_serialized_obj == b'\x00':
            deserialized_obj = False
        elif boolean_serialized_obj == b'\x01':
            deserialized_obj = True
        else:
            raise DeserializationError(
                'Invalid serialized boolean.  Must be either 0x01 or 0x00',
                serialized_obj
            )

        return deserialized_obj, start_index + 1

    def deserialize(self, data):
        deserialized_data, end_index = self.deserialize_segment(data, 0)
        if end_index != len(data):
            raise DeserializationError(
                'Data to be deserialized is too long',
                data
            )

        return deserialized_data


boolean = Boolean()
