def test_import_and_version():
    import ssz

    assert isinstance(ssz.__version__, str)
