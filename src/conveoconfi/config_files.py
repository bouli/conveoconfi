"""Legacy-compatible config file API surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _not_implemented(function_name: str) -> None:
    raise NotImplementedError(f"{function_name} is not implemented yet")


def _read_yaml_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _write_yaml_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)


def _default_template_path(
    file_name: str,
    default_files_dir: str | Path | None = None,
    default_template_dir: str | Path | None = None,
) -> Path:
    if default_files_dir is not None and default_template_dir is not None:
        raise ValueError(
            "Pass only one of default_files_dir or default_template_dir, not both"
        )

    template_dir = default_files_dir if default_files_dir is not None else default_template_dir
    if template_dir is None:
        raise FileNotFoundError(
            "A default template directory is required. Pass default_files_dir "
            "or default_template_dir."
        )

    template_path = Path(template_dir).expanduser() / file_name
    if not template_path.is_file():
        raise FileNotFoundError(
            f"Default template for {file_name!r} was not found at {template_path}"
        )

    return template_path


def _read_default_template(
    file_name: str,
    default_files_dir: str | Path | None = None,
    default_template_dir: str | Path | None = None,
) -> Any:
    template_path = _default_template_path(
        file_name,
        default_files_dir=default_files_dir,
        default_template_dir=default_template_dir,
    )
    data = _read_yaml_file(template_path)
    if data is None:
        raise ValueError(f"Default template {template_path} is empty")
    return data


def _complete_config_data(current_data: Any, default_data: Any) -> Any:
    if not isinstance(current_data, dict) or not isinstance(default_data, dict):
        return current_data

    completed_data = dict(current_data)
    for key, default_value in default_data.items():
        if key not in completed_data:
            completed_data[key] = default_value
            continue

        current_value = completed_data[key]
        if isinstance(current_value, dict) and isinstance(default_value, dict):
            completed_data[key] = _complete_config_data(current_value, default_value)

    return completed_data


def create_and_read_config_file(
    file_name: str,
    default_app_dir: str | Path,
    force_default: bool = False,
    complete_file: bool = True,
    default_files_dir: str | Path | None = None,
    default_template_dir: str | Path | None = None,
):
    """Create a missing config file from a YAML template and return parsed data."""
    path = config_file_path(file_name, default_app_dir)
    if force_default or not path.exists():
        data = _read_default_template(
            file_name,
            default_files_dir=default_files_dir,
            default_template_dir=default_template_dir,
        )
        _write_yaml_file(path, data)
        return data

    data = _read_yaml_file(path)
    if data is None:
        data = _read_default_template(
            file_name,
            default_files_dir=default_files_dir,
            default_template_dir=default_template_dir,
        )
        _write_yaml_file(path, data)
    elif complete_file:
        data = complete_config_file(
            file_name,
            default_app_dir,
            default_files_dir=default_files_dir,
            default_template_dir=default_template_dir,
        )
    return data


def complete_config_file(
    file_name: str,
    default_app_dir: str | Path,
    default_files_dir: str | Path | None = None,
    default_template_dir: str | Path | None = None,
):
    """Complete a config file with missing values from its default template."""
    path = config_file_path(file_name, default_app_dir)
    data = _read_yaml_file(path)
    default_data = _read_default_template(
        file_name,
        default_files_dir=default_files_dir,
        default_template_dir=default_template_dir,
    )

    if data is None:
        _write_yaml_file(path, default_data)
        return default_data

    completed_data = _complete_config_data(data, default_data)
    if completed_data != data:
        _write_yaml_file(path, completed_data)
    return completed_data


def overwrite_config_file(file_name: str, default_app_dir: str | Path, data: Any) -> None:
    """Overwrite a config file with YAML data."""
    _write_yaml_file(config_file_path(file_name, default_app_dir), data)


def append_config_file(file_name: str, default_app_dir: str | Path, data: Any) -> Any:
    """Append YAML data to a config file, then rewrite normalized YAML."""
    path = config_file_path(file_name, default_app_dir)
    with path.open("a", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)

    normalized_data = _read_yaml_file(path)
    _write_yaml_file(path, normalized_data)
    return normalized_data


def get_param(*args, **kwargs):
    _not_implemented("get_param")


def config_file_exists(file_name: str, default_app_dir: str | Path) -> bool:
    return config_file_path(file_name, default_app_dir).is_file()


def config_file_path(file_name: str, default_app_dir: str | Path) -> Path:
    app_dir = Path(default_app_dir).expanduser()
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / file_name
