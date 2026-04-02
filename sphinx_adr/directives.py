"""Directives for sphinx-adr: ``.. adr::`` and ``.. adrlist::``."""

from __future__ import annotations

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .nodes import adr_list, adr_meta

VALID_STATUSES = {"proposed", "accepted", "deprecated", "superseded"}


def _parse_comma_list(value: str) -> list[str]:
    """Split a comma-separated string into a stripped list."""
    return [item.strip() for item in value.split(",") if item.strip()]


def _status_option(argument: str) -> str:
    """Validate and normalise a status option value."""
    value = argument.strip().capitalize()
    if value.lower() not in VALID_STATUSES:
        raise ValueError(
            f"Invalid ADR status '{argument}'. "
            f"Must be one of: {', '.join(s.capitalize() for s in sorted(VALID_STATUSES))}"
        )
    return value


class AdrDirective(SphinxDirective):
    """Mark the current page as an Architecture Decision Record.

    Usage::

        .. adr::
           :status: Accepted
           :date: 2024-01-15
           :authors: Alice, Bob
           :tags: tooling, documentation
           :superseded-by: adr/0005-new-approach

           Short summary / excerpt of the decision.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        "id": directives.unchanged_required,
        "status": _status_option,
        "date": directives.unchanged_required,
        "authors": directives.unchanged,
        "tags": directives.unchanged,
        "superseded-by": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        docname = env.docname

        # :id: is required — Sphinx will emit a warning if missing
        adr_id = self.options.get("id", "")
        if not adr_id:
            msg = self.state.document.reporter.warning(
                "ADR directive missing required :id: option",
                line=self.lineno,
            )
            return [msg]

        status = self.options.get("status", "Proposed")
        date = self.options.get("date", "")
        authors = self.options.get("authors", "")
        tags = _parse_comma_list(self.options.get("tags", ""))
        superseded_by = self.options.get("superseded-by", "")

        # Store excerpt from directive body
        excerpt = "\n".join(self.content) if self.content else ""

        # Store metadata in the build environment
        if not hasattr(env, "adr_all_adrs"):
            env.adr_all_adrs = {}

        env.adr_all_adrs[docname] = {
            "docname": docname,
            "id": adr_id,
            "status": status,
            "date": date,
            "authors": authors,
            "tags": tags,
            "superseded_by": superseded_by,
            "excerpt": excerpt,
        }

        # Create the metadata banner node
        meta_node = adr_meta()
        meta_node["adr_id"] = adr_id
        meta_node["status"] = status
        meta_node["date"] = date
        meta_node["authors"] = authors
        meta_node["tags"] = tags
        meta_node["superseded_by"] = superseded_by

        return [meta_node]


class AdrListDirective(SphinxDirective):
    """Generate a timeline listing of ADRs.

    Usage::

        .. adrlist::
           :status: Accepted, Proposed
           :tags: tooling
           :sort: date-desc
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        "status": directives.unchanged,
        "tags": directives.unchanged,
        "sort": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        node = adr_list()
        node["filter_status"] = _parse_comma_list(self.options.get("status", ""))
        node["filter_tags"] = _parse_comma_list(self.options.get("tags", ""))
        node["sort"] = self.options.get("sort", "date-desc")
        return [node]
