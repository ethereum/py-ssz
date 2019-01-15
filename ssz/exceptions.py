class SSZException(Exception):
    """
    Base class for exceptions raised by this package.
    """
    pass


class InvalidSedesError(SSZException):
    """
    Exception raised if encoding fails.
    """
    pass


class EncodingError(SSZException):
    """
    Exception raised if encoding fails.
    """
    pass


class DecodingError(SSZException):
    """
    Exception raised if decoding fails.
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


class TreeHashException(SSZException):
    """
    Exception raised if tree hash fails.
    """
    pass
