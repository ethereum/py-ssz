import json

from eth_utils import (
    decode_hex,
    encode_hex,
)

from ssz.examples.zoo import (
    Animal,
    Zoo,
    octopus,
    zoo,
)
from ssz.sedes import (
    List,
)
from ssz.tools import (
    DefaultCodec,
    from_formatted_dict,
    to_formatted_dict,
)


def test_parsing_and_dumping():
    json_str = json.dumps(to_formatted_dict(zoo))
    read_zoo = from_formatted_dict(json.loads(json_str), Zoo)
    assert read_zoo == zoo


def test_dump_serializble_with_explicit_sedes():
    to_formatted_dict(zoo, Zoo)


def test_not_serializable():
    octopi = (octopus, octopus, octopus)
    output = to_formatted_dict(octopi, List(Animal, 2**32))
    assert octopi == from_formatted_dict(output, List(Animal, 2**32))


def test_custom_codec():
    class CustomCodec(DefaultCodec):
        @staticmethod
        def format_integer(value, sedes):
            return encode_hex(sedes.serialize(value))

        @staticmethod
        def unformat_integer(value, sedes):
            return sedes.deserialize(decode_hex(value))

    output = to_formatted_dict(zoo, codec=CustomCodec)
    read_zoo = from_formatted_dict(output, Zoo, CustomCodec)
    assert read_zoo == zoo
