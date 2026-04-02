"""Pytest fixtures for sphinx-adr tests."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest


def _write_conf(tmp_path: Path, extra: str = "") -> Path:
    """Create a minimal Sphinx project in *tmp_path* and return its path."""
    (tmp_path / "conf.py").write_text(
        dedent(f"""\
        extensions = ["sphinx_adr"]
        exclude_patterns = ["_build"]
        {extra}
        """)
    )
    return tmp_path


@pytest.fixture()
def make_project(tmp_path: Path):
    """Factory fixture that creates a Sphinx project with given RST files."""

    def _factory(files: dict[str, str], conf_extra: str = "") -> Path:
        _write_conf(tmp_path, conf_extra)
        for name, content in files.items():
            p = tmp_path / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(dedent(content))
        return tmp_path

    return _factory
