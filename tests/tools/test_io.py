import json

import pytest

from ssz.examples.state import (
    State,
    state,
)


@pytest.mark.parametrize(
    "int_as", (
        "int",
        "str",
        "hex",
    )
)
def test_import_export(tmpdir, int_as):
    path = tmpdir / "state.dump"
    with open(path, "w") as f:
        json.dump(state.to_formatted_dict(int_as=int_as), f)
    with open(path, "r") as f:
        read_state = State.from_formatted_dict(json.load(f), int_as=int_as)
    assert read_state.validator_registry[0].pubkey == state.validator_registry[0].pubkey
    assert read_state.validator_registry[0].exit_epoch == state.validator_registry[0].exit_epoch
