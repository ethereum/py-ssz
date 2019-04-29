import json

import pytest

from ssz.examples.zoo import (
    Zoo,
    zoo,
)


@pytest.mark.parametrize(
    "int_as", (
        "int",
        "str",
        "hex",
    )
)
def test_import_export(int_as):
    json_str = json.dumps(zoo.to_formatted_dict(int_as=int_as))
    read_zoo = Zoo.from_formatted_dict(json.loads(json_str), int_as=int_as)
    assert read_zoo == zoo
