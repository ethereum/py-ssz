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
from ssz.toolz import (
    DefaultFormatter,
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
    output = to_formatted_dict(octopi, List(Animal))
    assert octopi == from_formatted_dict(output, List(Animal))


def test_custom_formatter():
    class CustomFormatter(DefaultFormatter):
        @staticmethod
        def format_integer(value, sedes):
            return encode_hex(sedes.serialize(value))

        @staticmethod
        def unformat_integer(value, sedes):
            return sedes.deserialize(decode_hex(value))

    output = to_formatted_dict(zoo, basic_sedes_formatter=CustomFormatter)
    read_zoo = from_formatted_dict(output, Zoo, CustomFormatter)
    assert read_zoo == zoo
