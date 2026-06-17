"""Legacy-compatible config file API surface.

Implementations are added incrementally by the task issues.
"""


def _not_implemented(function_name: str) -> None:
    raise NotImplementedError(f"{function_name} is not implemented yet")


def create_and_read_config_file(*args, **kwargs):
    _not_implemented("create_and_read_config_file")


def complete_config_file(*args, **kwargs):
    _not_implemented("complete_config_file")


def overwrite_config_file(*args, **kwargs):
    _not_implemented("overwrite_config_file")


def append_config_file(*args, **kwargs):
    _not_implemented("append_config_file")


def get_param(*args, **kwargs):
    _not_implemented("get_param")


def config_file_exists(*args, **kwargs):
    _not_implemented("config_file_exists")


def config_file_path(*args, **kwargs):
    _not_implemented("config_file_path")
