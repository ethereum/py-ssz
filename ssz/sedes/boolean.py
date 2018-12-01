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

    def deserialize(self, serialized_obj):
        if serialized_obj == b'\x00':
            return False
        elif serialized_obj == b'\x01':
            return True
        else:
            raise DeserializationError(
                'Invalid serialized boolean.  Must be either 0x01 or 0x00',
                serialized_obj
            )


boolean = Boolean()
