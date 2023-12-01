class SSZException(Exception):
    """
    Base class for exceptions raised by this package.
    """


class SerializationError(SSZException):
    """
    Exception raised if serialization fails.
    """


class DeserializationError(SSZException):
    """
    Exception raised if deserialization fails.
    """
