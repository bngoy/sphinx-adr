"""Tests for the sphinx-adr extension."""

from __future__ import annotations

from pathlib import Path

import pytest
from sphinx.application import Sphinx


def _build(srcdir: Path, tmp_path: Path) -> Sphinx:
    outdir = tmp_path / "_build"
    doctreedir = outdir / ".doctrees"
    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
    )
    app.build()
    return app


# ---------------------------------------------------------------------------
# Basic directive tests
# ---------------------------------------------------------------------------


def test_adr_directive_basic(make_project, tmp_path):
    """The ``adr`` directive stores metadata and the build succeeds."""
    srcdir = make_project(
        {
            "index.rst": ("Title\n=====\n\n.. toctree::\n\n   adr1\n"),
            "adr1.rst": (
                "ADR-1: Test Decision\n"
                "====================\n\n"
                ".. adr::\n"
                "   :id: ADR-0001\n"
                "   :status: Accepted\n"
                "   :date: 2024-01-15\n"
                "   :authors: Alice\n"
                "   :tags: tooling\n\n"
                "   A short excerpt.\n"
            ),
        }
    )
    app = _build(srcdir, tmp_path)

    # Check metadata was collected
    assert hasattr(app.env, "adr_all_adrs")
    assert "adr1" in app.env.adr_all_adrs
    adr = app.env.adr_all_adrs["adr1"]
    assert adr["id"] == "ADR-0001"
    assert adr["status"] == "Accepted"
    assert adr["date"] == "2024-01-15"
    assert adr["authors"] == "Alice"
    assert adr["tags"] == ["tooling"]
    assert "short excerpt" in adr["excerpt"]


def test_adr_directive_status_validation(make_project, tmp_path):
    """An invalid status value causes a build error."""
    srcdir = make_project(
        {
            "index.rst": "Title\n=====\n\n.. toctree::\n\n   adr1\n",
            "adr1.rst": ("ADR-1\n=====\n\n.. adr::\n   :id: ADR-0001\n   :status: Invalid\n"),
        }
    )
    # The build should produce a warning/error about invalid status
    outdir = tmp_path / "_build"
    doctreedir = outdir / ".doctrees"
    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
    )

    # Invalid status should cause a build warning
    app.build()
    # The directive raises a ValueError which Sphinx converts to a warning
    # and the ADR won't be registered
    assert "adr1" not in app.env.adr_all_adrs


def test_adr_meta_renders_in_html(make_project, tmp_path):
    """The meta banner appears in the built HTML."""
    srcdir = make_project(
        {
            "index.rst": "Title\n=====\n\n.. toctree::\n\n   adr1\n",
            "adr1.rst": (
                "ADR-1: My Decision\n"
                "===================\n\n"
                ".. adr::\n"
                "   :id: ADR-0001\n"
                "   :status: Proposed\n"
                "   :date: 2024-06-01\n"
                "   :tags: api, backend\n\n"
                "   Excerpt text here.\n"
            ),
        }
    )
    app = _build(srcdir, tmp_path)
    html = (Path(app.outdir) / "adr1.html").read_text()

    assert 'class="adr-meta"' in html
    assert 'class="adr-id"' in html
    assert "ADR-0001" in html
    assert "adr-status-proposed" in html
    assert "2024-06-01" in html
    assert "api" in html
    assert "backend" in html


# ---------------------------------------------------------------------------
# adrlist directive tests
# ---------------------------------------------------------------------------


def test_adrlist_renders_timeline(make_project, tmp_path):
    """The ``adrlist`` directive generates a timeline in HTML."""
    srcdir = make_project(
        {
            "index.rst": ("Title\n=====\n\n.. adrlist::\n\n.. toctree::\n\n   adr1\n   adr2\n"),
            "adr1.rst": (
                "ADR-1\n=====\n\n"
                ".. adr::\n"
                "   :id: ADR-0001\n"
                "   :status: Accepted\n"
                "   :date: 2024-01-01\n"
            ),
            "adr2.rst": (
                "ADR-2\n=====\n\n"
                ".. adr::\n"
                "   :id: ADR-0002\n"
                "   :status: Proposed\n"
                "   :date: 2024-02-01\n"
            ),
        }
    )
    app = _build(srcdir, tmp_path)
    html = (Path(app.outdir) / "index.html").read_text()

    assert 'class="adr-timeline"' in html
    assert "adr-timeline-item" in html
    assert "adr-dot-accepted" in html
    assert "adr-dot-proposed" in html
    assert "ADR-0001" in html
    assert "ADR-0002" in html


def test_adrlist_filter_by_status(make_project, tmp_path):
    """Filtering by status only shows matching ADRs."""
    srcdir = make_project(
        {
            "index.rst": (
                "Title\n"
                "=====\n\n"
                ".. adrlist::\n"
                "   :status: Accepted\n\n"
                ".. toctree::\n\n"
                "   adr1\n"
                "   adr2\n"
            ),
            "adr1.rst": (
                "ADR-1: Accepted One\n"
                "===================\n\n"
                ".. adr::\n"
                "   :id: ADR-0001\n"
                "   :status: Accepted\n"
                "   :date: 2024-01-01\n"
            ),
            "adr2.rst": (
                "ADR-2: Proposed One\n"
                "===================\n\n"
                ".. adr::\n"
                "   :id: ADR-0002\n"
                "   :status: Proposed\n"
                "   :date: 2024-02-01\n"
            ),
        }
    )
    app = _build(srcdir, tmp_path)
    html = (Path(app.outdir) / "index.html").read_text()

    assert "Accepted One" in html
    # The proposed one should be filtered out from the main timeline
    # (it still exists in the sidebar nav, just not in the adrlist)
    timeline_start = html.index('class="adr-timeline"')
    timeline_end = html.index("<!-- /adr-timeline -->")
    timeline_html = html[timeline_start:timeline_end]
    assert "adr-dot-proposed" not in timeline_html


def test_adrlist_sort_by_date(make_project, tmp_path):
    """ADRs are sorted by date descending by default."""
    srcdir = make_project(
        {
            "index.rst": ("Title\n=====\n\n.. adrlist::\n\n.. toctree::\n\n   adr1\n   adr2\n"),
            "adr1.rst": (
                "ADR-1: Older\n"
                "============\n\n"
                ".. adr::\n"
                "   :id: ADR-0001\n"
                "   :status: Accepted\n"
                "   :date: 2024-01-01\n"
            ),
            "adr2.rst": (
                "ADR-2: Newer\n"
                "============\n\n"
                ".. adr::\n"
                "   :id: ADR-0002\n"
                "   :status: Accepted\n"
                "   :date: 2024-06-01\n"
            ),
        }
    )
    app = _build(srcdir, tmp_path)
    html = (Path(app.outdir) / "index.html").read_text()

    # Extract just the timeline section for position comparison
    timeline_start = html.index('class="adr-timeline"')
    timeline_html = html[timeline_start:]
    newer_pos = timeline_html.index("Newer")
    older_pos = timeline_html.index("Older")
    assert newer_pos < older_pos


def test_full_demo_build(tmp_path):
    """The full demo documentation builds without errors."""
    docs_dir = Path(__file__).parent.parent / "docs"
    if not docs_dir.exists():
        pytest.skip("Demo docs not found")

    outdir = tmp_path / "_build"
    doctreedir = outdir / ".doctrees"
    app = Sphinx(
        srcdir=str(docs_dir),
        confdir=str(docs_dir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
    )
    app.build()

    # Should have built without errors
    assert app.statuscode == 0

    # Check the ADR index page has a timeline
    adr_index = (outdir / "adr" / "index.html").read_text()
    assert "adr-timeline" in adr_index
    assert "adr-timeline-item" in adr_index
