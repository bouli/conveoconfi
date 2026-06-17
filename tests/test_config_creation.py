import pytest
import yaml

from conveoconfi import config_file_path, create_and_read_config_file


def _write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False)


def test_config_file_path_creates_missing_app_directory(tmp_path):
    app_dir = tmp_path / "app"

    path = config_file_path("config.yaml", app_dir)

    assert path == app_dir / "config.yaml"
    assert app_dir.is_dir()


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
