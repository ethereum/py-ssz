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
def test_import_export(tmpdir, int_as):
    path = tmpdir / "zoo.dump"
    with open(path, "w") as f:
        json.dump(zoo.to_formatted_dict(int_as=int_as), f)
    with open(path, "r") as f:
        read_zoo = Zoo.from_formatted_dict(json.load(f), int_as=int_as)
    assert read_zoo.animals[0].clock_in_records[0].epoch == zoo.animals[0].clock_in_records[0].epoch
