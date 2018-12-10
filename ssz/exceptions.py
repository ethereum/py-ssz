class SSZException(Exception):
    """
    Base class for exceptions raised by this package.
    """
    pass


class InvalidSedesError(SSZException):
    """
    Exception raised if encoding fails.
    """

    def __init__(self, message, sedes):
        super(InvalidSedesError, self).__init__(message)
        self.sedes = sedes


class EncodingError(SSZException):
    """
    Exception raised if encoding fails.
    """

    def __init__(self, message, obj):
        super(EncodingError, self).__init__(message)
        self.obj = obj


class DecodingError(SSZException):
    """
    Exception raised if decoding fails.
    """

    def __init__(self, message, ssz):
        super(DecodingError, self).__init__(message)
        self.ssz = ssz


class SerializationError(SSZException):
    """
    Exception raised if serialization fails.
    """

    def __init__(self, message, obj):
        super(SerializationError, self).__init__(message)
        self.obj = obj


class DeserializationError(SSZException):
    """
    Exception raised if deserialization fails.
    """

    def __init__(self, message, serial):
        super(DeserializationError, self).__init__(message)
        self.serial = serial
