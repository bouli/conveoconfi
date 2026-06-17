import yaml

from conveoconfi import create_and_read_config_file, get_param


UPSTREAM_REFERENCES = {
    "cheapchocolate": {
        "commit": "4bdd25d522788cb6463c3f0eca494de2a9244a76",
        "date": "2026-06-17T09:18:39+02:00",
        "description": "Bump version: 0.5.4 -> 0.6.0",
    },
    "ohmyscrapper": {
        "commit": "fc6223ddaeade264fcc0e857712ff97d9de49546",
        "date": "2026-06-07T16:17:25+02:00",
        "description": "Bump version: 0.10.1 -> 0.10.2",
    },
    "aphantasist": {
        "commit": "a4f70a890909823dd8d4462529bc20ddc4f375a5",
        "date": "2026-01-07T18:35:08+01:00",
        "description": "Bump version: 0.0.1 -> 0.1.0",
    },
}


def _write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False)


def test_cheapchocolate_style_config_completes_nested_mail_state(tmp_path):
    app_dir = tmp_path / "cheapchocolate-app"
    default_files_dir = tmp_path / "cheapchocolate-defaults"
    _write_yaml(
        app_dir / "config.yaml",
        {
            "mails": {
                "remote_read_state": {
                    "enabled": False,
                    "seen_folder": "custom-seen",
                }
            },
            "default_dirs": {"downloads": "/custom/downloads"},
        },
    )
    _write_yaml(
        default_files_dir / "config.yaml",
        {
            "mails": {
                "remote_read_state": {
                    "enabled": True,
                    "seen_folder": "seen",
                    "unseen_folder": "unseen",
                },
                "attachments": {"dir": "attachments"},
            },
            "default_dirs": {
                "downloads": "downloads",
                "cache": "cache",
            },
        },
    )

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert UPSTREAM_REFERENCES["cheapchocolate"]["commit"]
    assert data == {
        "mails": {
            "remote_read_state": {
                "enabled": False,
                "seen_folder": "custom-seen",
                "unseen_folder": "unseen",
            },
            "attachments": {"dir": "attachments"},
        },
        "default_dirs": {
            "downloads": "/custom/downloads",
            "cache": "cache",
        },
    }
    assert yaml.safe_load((app_dir / "config.yaml").read_text(encoding="utf-8")) == data


def test_ohmyscrapper_style_config_creates_and_completes_project_sections(tmp_path):
    app_dir = tmp_path / "ohmyscrapper-app"
    default_files_dir = tmp_path / "ohmyscrapper-defaults"
    defaults = {
        "db": {"driver": "sqlite", "path": "scraper.sqlite"},
        "default_dirs": {"data": "data", "cache": "cache"},
        "default_files": {"queue": "queue.yaml", "url_types": "url_types.yaml"},
        "ai": {"enabled": False, "model": "gpt-4.1-mini"},
        "sniffing": {"timeout": 30, "max_depth": 2},
        "queue": {"workers": 1, "retry_limit": 3},
    }
    _write_yaml(default_files_dir / "config.yaml", defaults)

    created = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert UPSTREAM_REFERENCES["ohmyscrapper"]["commit"]
    assert created == defaults

    _write_yaml(
        app_dir / "config.yaml",
        {
            "db": {"path": "custom.sqlite"},
            "default_dirs": {"data": "/srv/scrapes"},
            "default_files": {"queue": "custom-queue.yaml"},
            "ai": {"enabled": True},
            "sniffing": {"timeout": 10},
            "queue": {"workers": 4},
        },
    )

    completed = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert completed == {
        "db": {"path": "custom.sqlite", "driver": "sqlite"},
        "default_dirs": {"data": "/srv/scrapes", "cache": "cache"},
        "default_files": {"queue": "custom-queue.yaml", "url_types": "url_types.yaml"},
        "ai": {"enabled": True, "model": "gpt-4.1-mini"},
        "sniffing": {"timeout": 10, "max_depth": 2},
        "queue": {"workers": 4, "retry_limit": 3},
    }


def test_aphantasist_style_simple_config_uses_default_values(tmp_path):
    app_dir = tmp_path / "aphantasist-app"
    default_files_dir = tmp_path / "aphantasist-defaults"
    _write_yaml(
        default_files_dir / "config.yaml",
        {
            "default_dirs": {"images": "images", "output": "output"},
            "default_files": {"database": "aphantasist.sqlite"},
            "generation": {"width": 1024, "height": 1024},
        },
    )

    data = create_and_read_config_file(
        "config.yaml",
        app_dir,
        default_files_dir=default_files_dir,
    )
    images_dir = get_param(
        "default_dirs",
        "images",
        app_dir,
        default_files_dir=default_files_dir,
    )

    assert UPSTREAM_REFERENCES["aphantasist"]["commit"]
    assert data == {
        "default_dirs": {"images": "images", "output": "output"},
        "default_files": {"database": "aphantasist.sqlite"},
        "generation": {"width": 1024, "height": 1024},
    }
    assert images_dir == "images"
