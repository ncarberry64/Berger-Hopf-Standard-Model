"""Optional PDG adapter with deterministic offline fallbacks."""

from __future__ import annotations

from dataclasses import replace
from importlib.util import find_spec

from .validation import ExperimentalValue, curated_fallback_references


def is_pdg_available() -> bool:
    """Return whether an optional package named ``pdg`` is importable."""

    return find_spec("pdg") is not None


def try_load_pdg_reference(particle_key: str) -> ExperimentalValue | None:
    """Attempt no fragile query until a supported PDG package API is pinned.

    The function deliberately returns ``None`` for now.  This stable adapter
    boundary prevents optional package/API drift from breaking offline use.
    """

    if not is_pdg_available():
        return None
    # TODO: add a version-pinned adapter after the repository selects a PDG API.
    return None


def load_reference_with_fallback(particle_key: str) -> ExperimentalValue:
    """Load an optional PDG result or a curated, provenance-tagged fallback."""

    pdg_result = try_load_pdg_reference(particle_key)
    if pdg_result is not None:
        pdg_result.metadata["reference_loader"] = "optional_pdg_package"
        return pdg_result
    fallbacks = curated_fallback_references()
    if particle_key not in fallbacks:
        raise KeyError(f"no curated fallback reference for {particle_key!r}")
    base = fallbacks[particle_key]
    metadata = dict(base.metadata)
    metadata.update(
        {
            "reference_loader": "curated_offline_fallback",
            "pdg_package_available": is_pdg_available(),
            "pdg_query_status": (
                "API_ADAPTER_NOT_VERSION_PINNED" if is_pdg_available() else "PACKAGE_UNAVAILABLE"
            ),
        }
    )
    return replace(base, metadata=metadata)
