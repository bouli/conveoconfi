from pathlib import Path


README = Path(__file__).resolve().parents[1] / "README.md"


def test_readme_documents_migration_path():
    text = README.read_text(encoding="utf-8")

    required_snippets = [
        "pip install conveoconfi",
        "from conveoconfi import create_and_read_config_file, get_param",
        "default_files_dir",
        "default_template_dir",
        "create_and_read_config_file",
        "complete_config_file",
        "overwrite_config_file",
        "append_config_file",
        "get_param",
        "config_file_exists",
        "config_file_path",
        "Completion is recursive for dictionaries",
        "preserved",
    ]

    for snippet in required_snippets:
        assert snippet in text
