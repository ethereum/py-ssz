import inspect

from pyrsistent._transformations import (
    transform,
)

# transform is an internal function, so techinally could be changed without a breaking
# release. It's been stable for years, so we're testing it here to ensure it doesn't
# change rather than continuing to use an upper pin in dependencies.
# https://github.com/tobgu/pyrsistent/issues/180


def test_transform():
    expected = "def transform(structure, transformations):\n    r = structure\n    for path, command in _chunks(transformations, 2):\n        r = _do_to_path(r, path, command)\n    return r"  # noqa: E501
    assert inspect.getsource(transform).strip() == expected
