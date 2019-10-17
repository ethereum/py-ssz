import glob
import os

from eth_utils import to_tuple
from ruamel.yaml import YAML
from yaml_test_execution import execute_ssz_test_case, execute_tree_hash_test_case

YAML_BASE_DIR = os.path.abspath(os.path.join(__file__, "../../eth2.0-tests/"))
SSZ_TEST_FILES = glob.glob(
    os.path.join(YAML_BASE_DIR, "ssz", "**/*.yaml"), recursive=True
)
TREE_HASH_TEST_FILES = glob.glob(
    os.path.join(YAML_BASE_DIR, "tree_hash", "**/*.yaml"), recursive=True
)


@to_tuple
def load_test_cases(filenames):
    yaml = YAML()

    for filename in sorted(filenames):
        with open(filename) as f:
            test = yaml.load(f)

        for test_case in test["test_cases"]:
            yield test_case, make_test_id(filename, test_case)


def make_test_id(filename, test_case):
    return f"{filename}:{test_case.lc.line}"


def pytest_generate_tests(metafunc):
    fixture_to_test_files = {
        "ssz_test_case": SSZ_TEST_FILES,
        "tree_hash_test_case": TREE_HASH_TEST_FILES,
    }
    for fixture_name, test_files in fixture_to_test_files.items():
        if fixture_name in metafunc.fixturenames:
            test_cases_with_ids = load_test_cases(test_files)
            if len(test_cases_with_ids) > 0:
                test_cases, test_ids = zip(*test_cases_with_ids)
            else:
                test_cases, test_ids = (), ()

            metafunc.parametrize(fixture_name, test_cases, ids=test_ids)


def test_ssz(ssz_test_case):
    execute_ssz_test_case(ssz_test_case)


def test_tree_hash(tree_hash_test_case):
    execute_tree_hash_test_case(tree_hash_test_case)
