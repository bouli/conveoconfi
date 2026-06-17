# conveoconfi

Reusable YAML template-backed configuration helpers for Python applications.

`conveoconfi` provides a small function-based API for convention-over-
configuration behavior:

- create missing application config directories
- create missing YAML config files from application-owned default templates
- complete existing YAML files with newly added defaults
- preserve existing user-provided values and extra keys
- read child parameters from `config.yaml`

## Installation

Install the package with pip, or declare it in your project's dependency
metadata.

```bash
pip install conveoconfi
```

`conveoconfi` declares `PyYAML` as a runtime dependency, so applications do not
need to add a separate YAML dependency for these helpers.

## Default Templates

Applications keep their own YAML default templates, such as `config.yaml`,
`logging.yaml`, or `feature_flags.yaml`. Pass that template directory explicitly
when reading or completing config files.

```python
from pathlib import Path

from conveoconfi import create_and_read_config_file


APP_DIR = Path.home() / ".myapp"
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

## Template Discovery Decision

The public API requires applications to pass their template directory
explicitly with `default_files_dir` or `default_template_dir`. `conveoconfi`
does not search for templates in its own package directory because those files
belong to the consuming application, not to this reusable dependency.

Explicit template paths keep behavior predictable in tests, work with any
project layout, and fail with a direct `FileNotFoundError` when templates are
not configured. Projects that want a shorter call site can wrap `conveoconfi`
once in their own code and bind the app's template path there.

## Public API

The public API exposes these function names from the package root:

- `create_and_read_config_file(file_name, default_app_dir, force_default=False, complete_file=True, default_files_dir=None, default_template_dir=None)`
- `complete_config_file(file_name, default_app_dir, default_files_dir=None, default_template_dir=None)`
- `overwrite_config_file(file_name, default_app_dir, data)`
- `append_config_file(file_name, default_app_dir, data)`
- `get_param(parent_param, param, default_app_dir, default_files_dir=None, default_template_dir=None)`
- `config_file_exists(file_name, default_app_dir)`
- `config_file_path(file_name, default_app_dir)`

`config_file_path` creates the application config directory before returning the
path. `get_param` reads from `config.yaml`.

## Completion Behavior

By default, `create_and_read_config_file` completes existing config files from
the matching default template and writes the completed result back to disk.
Completion is recursive for dictionaries:

```yaml
# Existing user config
notifications:
  email:
    enabled: false

# Default template
notifications:
  email:
    enabled: true
    sender: hello@example.com
```

The completed file keeps the user's `enabled: false` value and adds only the
missing `sender` value. User-defined extra keys are preserved. If a
current value and default value disagree on shape, such as a scalar versus a
dictionary, the current user value is preserved.

Use `force_default=True` to deliberately replace an existing config file with
template defaults. Use `complete_file=False` to read an existing file without
mutating it.
