import glob
import os

from eth_utils import (
    to_list,
)
import pytest
from ruamel.yaml import (
    YAML,
)

from .yaml_test_execution import (
    execute_test_case,
)

YAML_BASE_DIR = os.path.abspath(os.path.join(__file__, "../../../yaml_test_files"))
YAML_FILES = glob.glob(os.path.join(YAML_BASE_DIR, "**/*.yaml"), recursive=True)


@to_list
def load_test_cases(filenames):
    yaml = YAML()

    for filename in filenames:
        with open(filename) as f:
            test = yaml.load(f)

        for index, test_case in enumerate(test["test_cases"]):
            yield test_case, make_test_id(filename, index)


def make_test_id(filename, test_case_index):
    basename = os.path.basename(filename)
    return f"{basename}[{test_case_index}]"


test_cases, test_ids = zip(*load_test_cases(YAML_FILES))


@pytest.mark.parametrize("test_case", test_cases, ids=test_ids)
def test_yaml_test_case(test_case):
    execute_test_case(test_case)
