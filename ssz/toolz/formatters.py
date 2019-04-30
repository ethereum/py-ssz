from eth_utils import (
    decode_hex,
    encode_hex,
)


class DefaultFormatter:
    @staticmethod
    def format_integer(value: int, sedes):
        return value

    @staticmethod
    def format_bool(value: bool, sedes):
        return value

    @staticmethod
    def format_bytes(value: bytes, sedes):
        return encode_hex(value)

    @staticmethod
    def unformat_bool(value, sedes) -> bool:
        return value

    @staticmethod
    def unformat_integer(value, sedes) -> int:
        if not isinstance(value, int):
            raise ValueError(f"Expected value of type int, got {type(value)}")
        return value

    @staticmethod
    def unformat_bytes(value, sedes) -> bytes:
        return decode_hex(value)
