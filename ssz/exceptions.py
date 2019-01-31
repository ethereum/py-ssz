class SSZException(Exception):
    """
    Base class for exceptions raised by this package.
    """
    pass


class SerializationError(SSZException):
    """
    Exception raised if serialization fails.
    """
    pass


class DeserializationError(SSZException):
    """
    Exception raised if deserialization fails.
    """
    pass
