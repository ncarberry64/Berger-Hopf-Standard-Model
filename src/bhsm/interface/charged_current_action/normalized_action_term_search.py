"""Compatibility wrapper for charged-current action source search."""

from __future__ import annotations

from .source_search import search_charged_current_action_sources


def search_normalized_charged_current_action_terms() -> dict[str, object]:
    return search_charged_current_action_sources()

