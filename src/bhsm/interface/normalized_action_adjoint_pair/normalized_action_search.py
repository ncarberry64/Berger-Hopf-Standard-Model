"""Compatibility wrapper for the normalized-action source search."""

from __future__ import annotations

from .source_search import search_normalized_action_adjoint_pair_sources


def search_normalized_action_sources() -> dict[str, object]:
    return search_normalized_action_adjoint_pair_sources()

