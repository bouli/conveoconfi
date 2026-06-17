# conveoconfi

Reusable YAML template-backed configuration helpers for projects that used to
carry their own `core.config_files` module.

`conveoconfi` keeps the legacy function-based API while moving the shared
convention-over-configuration behavior into one dependency:

- create missing application config directories
- create missing YAML config files from project-owned default templates
- complete existing YAML files with newly added defaults
- preserve existing user-provided values and extra keys
- read child parameters from `config.yaml`

## Installation

Install the package in the consuming project, or declare it in that project's
dependency metadata.

```bash
pip install conveoconfi
```

For a local migration before publishing, point your dependency manager at this
repository path. For example:

```toml
[project]
dependencies = [
    "conveoconfi @ file:///absolute/path/to/conveoconfi",
]
```

`conveoconfi` declares `PyYAML` as a runtime dependency, so consumers do not need
to add a separate YAML dependency for this compatibility layer.

## Migration

Replace imports from the project-local module with imports from the shared
package.

```python
# Before
from cheapchocolate.core.config_files import create_and_read_config_file, get_param

# After
from conveoconfi import create_and_read_config_file, get_param
```

The same pattern applies to projects such as `ohmyscrapper` and `aphantasist`:
replace `from <project>.core.config_files import ...` with
`from conveoconfi import ...`, then delete the duplicated local
`config_files.py` after tests pass.

## Default Templates

Consuming projects keep their own YAML default templates, such as
`config.yaml`, `mail_folders.yaml`, `url_types.yaml`, or `url_sniffing.yaml`.
Pass that template directory explicitly when reading or completing config files.

```python
from pathlib import Path

from conveoconfi import create_and_read_config_file


APP_DIR = Path.home() / ".cheapchocolate"
DEFAULT_FILES_DIR = Path(__file__).parent / "default_files"

config = create_and_read_config_file(
    "config.yaml",
    APP_DIR,
    default_files_dir=DEFAULT_FILES_DIR,
)
```

The equivalent keyword `default_template_dir` is also supported. Pass only one
of `default_files_dir` or `default_template_dir`.

Template lookup failures are explicit. If a default directory is omitted, or the
requested template file is missing, `conveoconfi` raises a `FileNotFoundError`
that names the lookup problem.

## Public API

The compatibility API exposes these legacy function names from the package root:

- `create_and_read_config_file(file_name, default_app_dir, force_default=False, complete_file=True, default_files_dir=None, default_template_dir=None)`
- `complete_config_file(file_name, default_app_dir, default_files_dir=None, default_template_dir=None)`
- `overwrite_config_file(file_name, default_app_dir, data)`
- `append_config_file(file_name, default_app_dir, data)`
- `get_param(parent_param, param, default_app_dir, default_files_dir=None, default_template_dir=None)`
- `config_file_exists(file_name, default_app_dir)`
- `config_file_path(file_name, default_app_dir)`

`config_file_path` creates the application config directory before returning the
path. `get_param` reads from `config.yaml`, matching the old project-local
helpers.

## Completion Behavior

By default, `create_and_read_config_file` completes existing config files from
the matching default template and writes the completed result back to disk.
Completion is recursive for dictionaries:

```yaml
# Existing user config
mails:
  remote_read_state:
    enabled: false

# Default template
mails:
  remote_read_state:
    enabled: true
    unseen_folder: unseen
```

The completed file keeps the user's `enabled: false` value and adds only the
missing `unseen_folder` value. User-defined extra keys are preserved. If a
current value and default value disagree on shape, such as a scalar versus a
dictionary, the current user value is preserved.

Use `force_default=True` to deliberately replace an existing config file with
template defaults. Use `complete_file=False` to read an existing file without
mutating it.
