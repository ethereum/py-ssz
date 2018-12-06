from ssz.exceptions import (
    InvalidSedesError,
    SerializationError,
)
from ssz.sedes import (
    Integer,
    boolean,
)


def is_sedes(obj):
    """
    Check if `obj` is a sedes object.
    A sedes object is characterized by having the methods
    `serialize(obj)` and `deserialize(serial)`.
    """
    return hasattr(obj, 'serialize') and hasattr(obj, 'deserialize')


def get_sedes_from_string(sedes_type):
    """
    Given the sedes type in string format, this function returns
    the corresponding serializer object.

    sedes_type can be 'boolean', 'uint<N>' etc.
    """
    if sedes_type == 'boolean':
        return boolean
    elif sedes_type[:4] == 'uint':
        # Try to get the number of bits
        try:
            num_bits = int(sedes_type[4:])
        except:
            raise InvalidSedesError(
                "Invalid uint sedes object: Number of bits should be an integer",
                sedes_type
            )

        # Make sure the number of bits are multiple of 8
        if num_bits % 8 != 0:
            raise InvalidSedesError(
                "Invalid uint sedes object: Number of bits should be multiple of 8",
                sedes_type
            )

        num_bytes = num_bits // 8
        return Integer(num_bytes)


def infer_sedes(obj):
    """
    Try to find a sedes objects suitable for a given Python object.
    """
    if isinstance(obj, bool):
        return boolean
    elif isinstance(obj, int):
        raise SerializationError(
            'uint sedes object or uint string needs to be specified for ints',
            obj
        )

    msg = 'Did not find sedes handling type {}'.format(type(obj).__name__)
    raise TypeError(msg)
