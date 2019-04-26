import pytest

import ssz
from ssz.examples import (
    State,
    state,
)


@pytest.mark.parametrize(
    "export_function, import_function", (
        (ssz.tools.to_json, ssz.tools.from_json),
        (ssz.tools.to_yaml, ssz.tools.from_yaml),
    )
)
def test_import_export(tmpdir, export_function, import_function):
    path = tmpdir / "state.dump"
    with open(path, "w") as f:
        f.write(export_function(state))
    with open(path, "r") as f:
        read_state = import_function(f.read(), State)
    assert read_state.validator_registry[0].pubkey == state.validator_registry[0].pubkey
    assert read_state.validator_registry[0].exit_epoch == state.validator_registry[0].exit_epoch
