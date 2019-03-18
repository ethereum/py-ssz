import glob
import os

from eth_utils import (
    to_tuple,
)
from ruamel.yaml import (
    YAML,
)

from yaml_test_execution import (
    execute_test_case,
)

YAML_BASE_DIR = os.path.abspath(os.path.join(__file__, "../../eth2.0-tests/ssz"))
YAML_FILES = glob.glob(os.path.join(YAML_BASE_DIR, "**/*.yaml"), recursive=True)


@to_tuple
def load_test_cases(filenames):
    yaml = YAML()

    for filename in filenames:
        with open(filename) as f:
            test = yaml.load(f)

        for test_case in test["test_cases"]:
            yield test_case, make_test_id(filename, test_case)


def make_test_id(filename, test_case):
    return f"{filename}:{test_case.lc.line}"


def pytest_generate_tests(metafunc):
    test_cases_with_ids = load_test_cases(YAML_FILES)
    if len(test_cases_with_ids) > 0:
        test_cases, test_ids = zip(*load_test_cases(YAML_FILES))
    else:
        test_cases, test_ids = (), ()

    metafunc.parametrize("test_case", test_cases, ids=test_ids)


def test_yaml_test_case(test_case):
    execute_test_case(test_case)
