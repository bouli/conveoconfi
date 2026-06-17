import conveoconfi


def test_package_import_exposes_legacy_function_names():
    expected_names = {
        "append_config_file",
        "complete_config_file",
        "config_file_exists",
        "config_file_path",
        "create_and_read_config_file",
        "get_param",
        "overwrite_config_file",
    }

    assert expected_names <= set(conveoconfi.__all__)
    for name in expected_names:
        assert callable(getattr(conveoconfi, name))
