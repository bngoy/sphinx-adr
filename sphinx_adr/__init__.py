"""sphinx-adr: Sphinx extension for Architecture Decision Records."""

from __future__ import annotations

import os
from typing import Any

from sphinx.application import Sphinx

from .collector import init_adr_env, merge_adr_info, process_adr_lists, purge_adr_doc
from .directives import AdrDirective, AdrListDirective
from .nodes import (
    adr_list,
    adr_meta,
    depart_adr_list_html,
    depart_adr_meta_html,
    depart_adr_meta_text,
    depart_adr_list_text,
    visit_adr_list_html,
    visit_adr_list_text,
    visit_adr_meta_html,
    visit_adr_meta_text,
)

__version__ = "0.1.0"


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the sphinx-adr extension."""

    # -- Configuration values ------------------------------------------------
    app.add_config_value(
        "adr_statuses",
        ["Proposed", "Accepted", "Deprecated", "Superseded"],
        "env",
    )

    # -- Custom nodes --------------------------------------------------------
    app.add_node(
        adr_meta,
        html=(visit_adr_meta_html, depart_adr_meta_html),
        text=(visit_adr_meta_text, depart_adr_meta_text),
    )
    app.add_node(
        adr_list,
        html=(visit_adr_list_html, depart_adr_list_html),
        text=(visit_adr_list_text, depart_adr_list_text),
    )

    # -- Directives ----------------------------------------------------------
    app.add_directive("adr", AdrDirective)
    app.add_directive("adrlist", AdrListDirective)

    # -- Events --------------------------------------------------------------
    app.connect("env-before-read-docs", init_adr_env)
    app.connect("doctree-resolved", process_adr_lists)
    app.connect("env-purge-doc", purge_adr_doc)
    app.connect("env-merge-info", merge_adr_info)

    # -- Static files --------------------------------------------------------
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.connect(
        "builder-inited",
        lambda app: app.config._raw_config.setdefault("html_static_path", []),
    )
    app.add_css_file("sphinx_adr.css")

    # Register the static directory so Sphinx copies it
    app.connect("builder-inited", _add_static_path)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _add_static_path(app: Sphinx) -> None:
    """Add our static directory to the Sphinx static paths."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if static_dir not in app.config.html_static_path:
        app.config.html_static_path.append(static_dir)
