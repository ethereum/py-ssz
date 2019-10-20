from eth_utils import decode_hex, encode_hex


class DefaultCodec:
    @staticmethod
    def encode_integer(value: int, sedes):
        return value

    @staticmethod
    def encode_bool(value: bool, sedes):
        return value

    @staticmethod
    def encode_bytes(value: bytes, sedes):
        return encode_hex(value)

    @staticmethod
    def decode_bool(value, sedes) -> bool:
        return value

    @staticmethod
    def decode_integer(value, sedes) -> int:
        if not isinstance(value, int):
            raise ValueError(f"Expected value of type int, got {type(value)}")
        return value

    @staticmethod
    def decode_bytes(value, sedes) -> bytes:
        return decode_hex(value)
