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


def get_integer_serializer(serializer_type):
    '''
    Given serializer_type as 'int<N>' or 'uint<N>', this function
    returns the corresponding serializer object.
    '''
    integer_serializer = Integer(serializer_type)
    return integer_serializer


def infer_sedes(obj, serializer_type=None):
    """
    Try to find a sedes objects suitable for a given Python object.
    :param serializer_type: str
    The serializer_type parameter is optional and can be only
    of the format 'int<N>' or 'uint<N>'(as of now)
    """
    if isinstance(obj, bool):
        return boolean
    elif isinstance(obj, int):
        return get_integer_serializer(serializer_type)

    msg = 'Did not find sedes handling type {}'.format(type(obj).__name__)
    raise TypeError(msg)
