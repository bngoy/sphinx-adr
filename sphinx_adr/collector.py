"""Environment event handlers for collecting and rendering ADR data."""

from __future__ import annotations

import pickle
from datetime import datetime
from typing import Any

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

from .nodes import adr_list


def init_adr_env(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    """Initialise the ADR storage on the build environment."""
    if not hasattr(env, "adr_all_adrs"):
        env.adr_all_adrs: dict[str, dict[str, Any]] = {}
    if not hasattr(env, "adr_list_hosts"):
        env.adr_list_hosts: set[str] = set()


def purge_adr_doc(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Remove ADR data when a document is re-read (incremental builds)."""
    if hasattr(env, "adr_all_adrs"):
        env.adr_all_adrs.pop(docname, None)
    if hasattr(env, "adr_list_hosts"):
        env.adr_list_hosts.discard(docname)


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
    if not hasattr(env, "adr_list_hosts"):
        env.adr_list_hosts = set()
    if hasattr(other, "adr_list_hosts"):
        env.adr_list_hosts.update(other.adr_list_hosts)


def register_adr_toctrees(app: Sphinx, env: BuildEnvironment) -> None:
    """Register ADR docs in the toctree so Sphinx doesn't warn about orphans.

    Called during ``env-updated``, after all documents have been read but
    before ``check_consistency``.  When ``adr_sidebar_toc`` is True the
    entries also appear in the sidebar navigation; when False (the default),
    a hidden toctree suppresses warnings without adding sidebar entries.
    """
    if not hasattr(env, "adr_all_adrs") or not hasattr(env, "adr_list_hosts"):
        return

    all_adr_docnames = list(env.adr_all_adrs.keys())
    if not all_adr_docnames:
        return

    show_sidebar = app.config.adr_sidebar_toc

    for host_docname in env.adr_list_hosts:
        adr_docs = [d for d in all_adr_docnames if d != host_docname]
        if not adr_docs:
            continue

        # 1. Update env metadata so Sphinx knows these docs are included
        for adr_docname in adr_docs:
            env.files_to_rebuild.setdefault(adr_docname, set()).add(host_docname)
        existing = env.toctree_includes.get(host_docname, [])
        to_add = [d for d in adr_docs if d not in existing]
        if to_add:
            env.toctree_includes.setdefault(host_docname, []).extend(to_add)

        # 2. When sidebar is enabled, inject a toctree node into the host's
        #    pickled doctree so Sphinx's sidebar rendering shows the entries.
        #    When disabled (default), we only register in files_to_rebuild /
        #    toctree_includes to suppress "not in any toctree" warnings.
        if show_sidebar:
            _inject_toctree_node(env, host_docname, adr_docs)


def _inject_toctree_node(
    env: BuildEnvironment,
    host_docname: str,
    adr_docnames: list[str],
) -> None:
    """Inject a visible toctree node into a pickled doctree and its TOC entry."""
    # Build the toctree node
    toc = addnodes.toctree()
    toc["parent"] = host_docname
    toc["entries"] = [(None, d) for d in adr_docnames]
    toc["includefiles"] = list(adr_docnames)
    toc["maxdepth"] = 1
    toc["glob"] = False
    toc["hidden"] = False
    toc["numbered"] = 0
    toc["titlesonly"] = True
    toc["caption"] = None
    toc["rawcaption"] = ""
    toc["rawentries"] = []

    # 1. Inject into the pickled doctree (used by master_doctree for sidebar)
    doctree_path = env.doctreedir / f"{host_docname}.doctree"
    if doctree_path.exists():
        with open(doctree_path, "rb") as f:
            doctree = pickle.load(f)
        wrapper = nodes.compound(classes=["toctree-wrapper"])
        wrapper.append(toc.deepcopy())
        doctree.append(wrapper)
        with open(doctree_path, "wb") as f:
            pickle.dump(doctree, f, pickle.HIGHEST_PROTOCOL)
        env._pickled_doctree_cache.pop(host_docname, None)

    # 2. Inject into env.tocs so sidebar resolution finds the entries
    if host_docname in env.tocs:
        toc_tree = env.tocs[host_docname]
        # Append the toctree node inside the last bullet_list
        if toc_tree.children:
            last = toc_tree.children[-1]
            if isinstance(last, nodes.bullet_list) and last.children:
                last_item = last.children[-1]
                last_item.append(toc.deepcopy())
            else:
                toc_tree.append(toc.deepcopy())
        else:
            toc_tree.append(toc.deepcopy())


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


def _render_timeline(
    app: Sphinx, adrs: list[dict], current_docname: str
) -> str:
    """Render ADRs as a vertical timeline."""
    if not adrs:
        return '<div class="adr-timeline"><p>No ADRs found.</p></div>'

    lines = ['<div class="adr-timeline">']

    for adr in adrs:
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

    lines.append("</div>")
    return "\n".join(lines)
