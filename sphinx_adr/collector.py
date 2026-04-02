"""Environment event handlers for collecting and rendering ADR data."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

from .nodes import adr_list


def init_adr_env(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    """Initialise the ADR storage on the build environment."""
    if not hasattr(env, "adr_all_adrs"):
        env.adr_all_adrs: dict[str, dict[str, Any]] = {}


def purge_adr_doc(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Remove ADR data when a document is re-read (incremental builds)."""
    if hasattr(env, "adr_all_adrs"):
        env.adr_all_adrs.pop(docname, None)


def merge_adr_info(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: list[str],
    other: BuildEnvironment,
) -> None:
    """Merge ADR data from parallel sub-builds."""
    if not hasattr(env, "adr_all_adrs"):
        env.adr_all_adrs = {}
    if hasattr(other, "adr_all_adrs"):
        env.adr_all_adrs.update(other.adr_all_adrs)


def _parse_date(date_str: str) -> datetime:
    """Best-effort date parsing for sorting."""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    # Fallback: sort undated entries to the end
    return datetime.max


_STATUS_ORDER = {
    "proposed": 0,
    "accepted": 1,
    "deprecated": 2,
    "superseded": 3,
}


def _sort_adrs(adrs: list[dict], sort_key: str) -> list[dict]:
    if sort_key == "date-asc":
        return sorted(adrs, key=lambda a: _parse_date(a.get("date", "")))
    if sort_key == "status":
        return sorted(
            adrs,
            key=lambda a: _STATUS_ORDER.get(a.get("status", "").lower(), 99),
        )
    # Default: date-desc
    return sorted(adrs, key=lambda a: _parse_date(a.get("date", "")), reverse=True)


def process_adr_lists(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Replace ``adr_list`` placeholder nodes with rendered timeline HTML."""
    env = app.builder.env
    if not hasattr(env, "adr_all_adrs"):
        return

    all_adrs = env.adr_all_adrs

    for node in doctree.findall(adr_list):
        # Apply filters
        filter_status = [s.lower() for s in node.get("filter_status", [])]
        filter_tags = [t.lower() for t in node.get("filter_tags", [])]
        sort_key = node.get("sort", "date-desc")

        adrs = list(all_adrs.values())

        if filter_status:
            adrs = [a for a in adrs if a["status"].lower() in filter_status]
        if filter_tags:
            adrs = [
                a
                for a in adrs
                if any(t.lower() in filter_tags for t in a.get("tags", []))
            ]

        adrs = _sort_adrs(adrs, sort_key)

        # Resolve titles from the doctree/env
        for adr in adrs:
            adr_docname = adr["docname"]
            title = env.titles.get(adr_docname)
            adr["title"] = title.astext() if title else adr_docname

        # Resolve superseded-by URIs
        for adr in adrs:
            sup = adr.get("superseded_by", "")
            if sup:
                # Try to resolve as a docname
                if sup in all_adrs:
                    adr["superseded_by_title"] = all_adrs[sup].get(
                        "title", sup
                    )

        # Build the timeline HTML
        html = _render_timeline(app, adrs, docname)

        new_node = nodes.raw("", html, format="html")
        node.replace_self([new_node])


def inject_adr_nav_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict,
    doctree: Any,
) -> None:
    """Inject ADR sidebar navigation data into the Jinja2 template context."""
    env = app.builder.env
    if not hasattr(env, "adr_all_adrs"):
        context["adr_nav_entries"] = []
        return

    all_adrs = env.adr_all_adrs
    if not all_adrs:
        context["adr_nav_entries"] = []
        return

    adrs = _sort_adrs(list(all_adrs.values()), "date-desc")

    entries = []
    for adr in adrs:
        adr_docname = adr["docname"]
        title = env.titles.get(adr_docname)
        title_text = title.astext() if title else adr_docname
        status = adr.get("status", "Proposed")

        try:
            uri = app.builder.get_relative_uri(pagename, adr_docname)
        except Exception:
            uri = adr_docname + ".html"

        entries.append(
            {
                "id": adr.get("id", ""),
                "title": title_text,
                "uri": uri,
                "status": status,
                "status_lower": status.lower(),
                "date": adr.get("date", ""),
                "current": pagename == adr_docname,
            }
        )

    context["adr_nav_entries"] = entries


def _render_timeline(
    app: Sphinx, adrs: list[dict], current_docname: str
) -> str:
    """Render ADRs as a vertical timeline."""
    if not adrs:
        return '<div class="adr-timeline"><p>No ADRs found.</p></div>'

    lines = ['<div class="adr-timeline">']

    for adr in adrs:
        adr_id = adr.get("id", "")
        status = adr.get("status", "Proposed")
        status_lower = status.lower()
        date = adr.get("date", "")
        title = adr.get("title", adr["docname"])
        excerpt = adr.get("excerpt", "")
        tags = adr.get("tags", [])
        authors = adr.get("authors", "")

        # Build relative URI from the current doc to the ADR doc
        try:
            uri = app.builder.get_relative_uri(current_docname, adr["docname"])
        except Exception:
            uri = adr["docname"] + ".html"

        lines.append(f'  <div class="adr-timeline-item adr-timeline-{status_lower}">')
        lines.append(f'    <div class="adr-timeline-dot adr-dot-{status_lower}"></div>')
        lines.append('    <div class="adr-timeline-content">')
        lines.append('      <div class="adr-timeline-header">')
        if adr_id:
            lines.append(
                f'        <span class="adr-id">{adr_id}</span>'
            )
        lines.append(
            f'        <a href="{uri}" class="adr-timeline-title">{title}</a>'
        )
        lines.append(
            f'        <span class="adr-status adr-status-{status_lower}">{status}</span>'
        )
        lines.append("      </div>")

        # Meta line
        meta_parts = []
        if date:
            meta_parts.append(f'<span class="adr-timeline-date">{date}</span>')
        if authors:
            meta_parts.append(f'<span class="adr-timeline-authors">{authors}</span>')
        if meta_parts:
            lines.append(
                '      <div class="adr-timeline-meta">'
                + " &middot; ".join(meta_parts)
                + "</div>"
            )

        # Excerpt
        if excerpt:
            lines.append(f'      <p class="adr-timeline-excerpt">{excerpt}</p>')

        # Tags
        if tags:
            lines.append('      <div class="adr-timeline-tags">')
            for tag in tags:
                lines.append(f'        <span class="adr-tag">{tag}</span>')
            lines.append("      </div>")

        lines.append("    </div>")
        lines.append("  </div>")

    lines.append("</div><!-- /adr-timeline -->")
    return "\n".join(lines)
