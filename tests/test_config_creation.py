import pytest
import yaml

from conveoconfi import (
    append_config_file,
    complete_config_file,
    config_file_exists,
    config_file_path,
    create_and_read_config_file,
    overwrite_config_file,
)


def _write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False)


def test_config_file_path_creates_missing_app_directory(tmp_path):
    app_dir = tmp_path / "app"

    path = config_file_path("config.yaml", app_dir)

    assert path == app_dir / "config.yaml"
    assert app_dir.is_dir()


def test_config_file_exists_reports_file_presence(tmp_path):
    app_dir = tmp_path / "app"

    assert config_file_exists("config.yaml", app_dir) is False

    _write_yaml(app_dir / "config.yaml", {"enabled": True})

    assert config_file_exists("config.yaml", app_dir) is True


def test_overwrite_config_file_writes_readable_yaml(tmp_path):
    app_dir = tmp_path / "app"

    overwrite_config_file(
        "config.yaml",
        app_dir,
        {"section": {"enabled": True}, "workers": 2},
    )

    assert yaml.safe_load((app_dir / "config.yaml").read_text(encoding="utf-8")) == {
        "section": {"enabled": True},
        "workers": 2,
    }


def test_append_config_file_appends_and_normalizes_yaml(tmp_path):
    app_dir = tmp_path / "app"
    _write_yaml(app_dir / "config.yaml", {"enabled": False, "workers": 1})

    data = append_config_file(
        "config.yaml",
        app_dir,
        {"workers": 2, "name": "São Paulo"},
    )

    assert data == {"enabled": False, "workers": 2, "name": "São Paulo"}
    config_text = (app_dir / "config.yaml").read_text(encoding="utf-8")
    assert config_text.count("workers:") == 1
    assert "São Paulo" in config_text
    assert yaml.safe_load(config_text) == data


def test_create_and_read_config_file_creates_missing_file_from_template(tmp_path):
    app_dir = tmp_path / "app"
    default_files_dir = tmp_path / "defaults"
    _write_yaml(
        default_files_dir / "config.yaml",
        {"database": {"host": "localhost"}, "workers": 2},
    )

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert data == {"database": {"host": "localhost"}, "workers": 2}
    assert yaml.safe_load((app_dir / "config.yaml").read_text(encoding="utf-8")) == data


def test_create_and_read_config_file_recovers_empty_existing_file(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "config.yaml").write_text("", encoding="utf-8")
    default_files_dir = tmp_path / "defaults"
    _write_yaml(default_files_dir / "config.yaml", {"enabled": True})

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert data == {"enabled": True}
    assert yaml.safe_load((app_dir / "config.yaml").read_text(encoding="utf-8")) == data


def test_create_and_read_config_file_reads_existing_non_empty_file(tmp_path):
    app_dir = tmp_path / "app"
    default_files_dir = tmp_path / "defaults"
    _write_yaml(app_dir / "config.yaml", {"enabled": False})
    _write_yaml(default_files_dir / "config.yaml", {"enabled": True})

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert data == {"enabled": False}


def test_create_and_read_config_file_completes_existing_file_recursively(tmp_path):
    app_dir = tmp_path / "app"
    default_files_dir = tmp_path / "defaults"
    _write_yaml(
        app_dir / "config.yaml",
        {
            "database": {"host": "db.local"},
            "feature": {"custom": True},
            "user_only": "kept",
        },
    )
    _write_yaml(
        default_files_dir / "config.yaml",
        {
            "database": {"host": "localhost", "port": 5432},
            "feature": {"enabled": True},
            "workers": 2,
        },
    )

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert data == {
        "database": {"host": "db.local", "port": 5432},
        "feature": {"custom": True, "enabled": True},
        "user_only": "kept",
        "workers": 2,
    }
    assert yaml.safe_load((app_dir / "config.yaml").read_text(encoding="utf-8")) == data


def test_complete_config_file_preserves_current_values_on_shape_conflicts(tmp_path):
    app_dir = tmp_path / "app"
    default_files_dir = tmp_path / "defaults"
    _write_yaml(
        app_dir / "config.yaml",
        {
            "section_became_scalar": {"user": "value"},
            "section_became_mapping": "user-value",
        },
    )
    _write_yaml(
        default_files_dir / "config.yaml",
        {
            "section_became_scalar": "default-value",
            "section_became_mapping": {"default": "value"},
        },
    )

    data = complete_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert data == {
        "section_became_scalar": {"user": "value"},
        "section_became_mapping": "user-value",
    }


def test_create_and_read_config_file_force_default_overwrites_existing_file(tmp_path):
    app_dir = tmp_path / "app"
    default_files_dir = tmp_path / "defaults"
    _write_yaml(app_dir / "config.yaml", {"enabled": False, "user_only": True})
    _write_yaml(default_files_dir / "config.yaml", {"enabled": True})

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        force_default=True,
        default_files_dir=default_files_dir,
    )

    assert data == {"enabled": True}
    assert yaml.safe_load((app_dir / "config.yaml").read_text(encoding="utf-8")) == data


def test_create_and_read_config_file_can_read_without_completing_existing_file(tmp_path):
    app_dir = tmp_path / "app"
    default_files_dir = tmp_path / "defaults"
    existing_data = {"database": {"host": "db.local"}}
    _write_yaml(app_dir / "config.yaml", existing_data)
    _write_yaml(
        default_files_dir / "config.yaml",
        {"database": {"host": "localhost", "port": 5432}, "workers": 2},
    )

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        complete_file=False,
        default_files_dir=default_files_dir,
    )

    assert data == existing_data
    assert yaml.safe_load((app_dir / "config.yaml").read_text(encoding="utf-8")) == existing_data


def test_create_and_read_config_file_requires_explicit_template_directory(tmp_path):
    with pytest.raises(FileNotFoundError, match="default template directory is required"):
        create_and_read_config_file("config.yaml", tmp_path / "app")


def test_create_and_read_config_file_reports_missing_template_path(tmp_path):
    default_files_dir = tmp_path / "defaults"

    with pytest.raises(FileNotFoundError, match="Default template.*config.yaml"):
        create_and_read_config_file(
            "config.yaml",
            tmp_path / "app",
            default_files_dir=default_files_dir,
        )
