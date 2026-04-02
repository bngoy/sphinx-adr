"""Custom docutils nodes for sphinx-adr."""

from docutils import nodes


class adr_meta(nodes.General, nodes.Element):
    """Node representing the ADR metadata banner at the top of an ADR page.

    Renders as a horizontal bar showing status badge, date, authors, and tags.
    """

    pass


class adr_list(nodes.General, nodes.Element):
    """Placeholder node for the ADR timeline listing.

    Replaced during doctree-resolved with the actual timeline HTML.
    """

    pass


# -- HTML visitors -----------------------------------------------------------


def visit_adr_meta_html(self, node):
    adr_id = node.get("adr_id", "")
    status = node.get("status", "Proposed")
    status_lower = status.lower()
    date = node.get("date", "")
    authors = node.get("authors", "")
    tags = node.get("tags", [])
    superseded_by = node.get("superseded_by", "")
    superseded_by_uri = node.get("superseded_by_uri", "")

    self.body.append('<div class="adr-meta">\n')

    # ID badge
    if adr_id:
        self.body.append(f'  <span class="adr-id">{adr_id}</span>\n')

    # Status badge
    self.body.append(f'  <span class="adr-status adr-status-{status_lower}">{status}</span>\n')

    # Date
    if date:
        self.body.append(f'  <span class="adr-date">{date}</span>\n')

    # Authors
    if authors:
        self.body.append(f'  <span class="adr-authors">Authors: {authors}</span>\n')

    # Superseded-by link
    if superseded_by and status_lower == "superseded":
        if superseded_by_uri:
            self.body.append(
                f'  <span class="adr-superseded-by">'
                f'Superseded by: <a href="{superseded_by_uri}">{superseded_by}</a>'
                f"</span>\n"
            )
        else:
            self.body.append(
                f'  <span class="adr-superseded-by">Superseded by: {superseded_by}</span>\n'
            )

    # Tags
    if tags:
        self.body.append('  <span class="adr-tags">\n')
        for tag in tags:
            self.body.append(f'    <span class="adr-tag">{tag}</span>\n')
        self.body.append("  </span>\n")

    self.body.append("</div>\n")


def depart_adr_meta_html(self, node):
    pass


def visit_adr_list_html(self, node):
    # This node should have been replaced during doctree-resolved.
    # If it wasn't, render an empty container.
    self.body.append('<div class="adr-timeline"></div>\n')
    raise nodes.SkipNode


def depart_adr_list_html(self, node):
    pass


# -- Text/other visitors (no-op) --------------------------------------------


def visit_adr_meta_text(self, node):
    raise nodes.SkipNode


def depart_adr_meta_text(self, node):
    pass


def visit_adr_list_text(self, node):
    raise nodes.SkipNode


def depart_adr_list_text(self, node):
    pass
