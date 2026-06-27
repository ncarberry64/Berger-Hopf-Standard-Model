"""Optional live-reference/cache adapter with offline fallback semantics."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .pdg_interface import is_pdg_available, load_reference_with_fallback, try_load_pdg_reference
from .validation import ExperimentalValue


@dataclass
class PDGFetchResult:
    particle_key: str
    status: str
    reference: ExperimentalValue
    live_attempted: bool
    fallback_used: bool
    cache_used: bool
    reference_only: bool = True
    derivation_input: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reference"] = self.reference.to_dict()
        return payload


@dataclass
class PDGCache:
    directory: Path = Path(".cache/bhsm_pdg")

    def path_for(self, particle_key: str) -> Path:
        return self.directory / f"{particle_key}.json"

    def write_cache(self, result: PDGFetchResult) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.path_for(result.particle_key)
        path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_cached_reference(self, particle_key: str) -> dict[str, Any] | None:
        path = self.path_for(particle_key)
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


class LivePDGProvider:
    """Provider boundary; live querying remains optional and version-pinned later."""

    def __init__(self, cache: PDGCache | None = None) -> None:
        self.cache = cache or PDGCache()

    def fetch_particle_reference(self, particle_key: str, offline_ok: bool = True) -> PDGFetchResult:
        live = try_load_pdg_reference(particle_key) if is_pdg_available() else None
        if live is not None:
            result = PDGFetchResult(particle_key, "live_reference_loaded", live, True, False, False)
            self.cache.write_cache(result)
            return result
        if not offline_ok:
            raise RuntimeError("live PDG adapter unavailable; rerun with offline fallback enabled")
        fallback = load_reference_with_fallback(particle_key)
        return PDGFetchResult(particle_key, "fallback_used", fallback, is_pdg_available(), True, False)


def is_live_pdg_available() -> bool:
    return is_pdg_available()


def load_reference_with_live_then_fallback(particle_key: str, offline_ok: bool = True) -> PDGFetchResult:
    return LivePDGProvider().fetch_particle_reference(particle_key, offline_ok=offline_ok)
