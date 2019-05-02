import json

from eth_utils import (
    decode_hex,
    encode_hex,
)

import ssz
from ssz.examples.zoo import (
    Animal,
    Zoo,
    octopus,
    zoo,
)
from ssz.sedes import (
    List,
)


def test_parsing_and_dumping():
    json_str = json.dumps(ssz.tools.to_formatted_dict(zoo))
    read_zoo = ssz.tools.from_formatted_dict(json.loads(json_str), Zoo)
    assert read_zoo == zoo


def test_dump_serializble_with_explicit_sedes():
    ssz.tools.to_formatted_dict(zoo, Zoo)


def test_not_serializable():
    octopi = (octopus, octopus, octopus)
    output = ssz.tools.to_formatted_dict(octopi, List(Animal))
    assert octopi == ssz.tools.from_formatted_dict(output, List(Animal))


def test_custom_codec():
    class CustomCodec(ssz.tools.DefaultCodec):
        @staticmethod
        def format_integer(value, sedes):
            return encode_hex(sedes.serialize(value))

        @staticmethod
        def unformat_integer(value, sedes):
            return sedes.deserialize(decode_hex(value))

    output = ssz.tools.to_formatted_dict(zoo, codec=CustomCodec)
    read_zoo = ssz.tools.from_formatted_dict(output, Zoo, CustomCodec)
    assert read_zoo == zoo
