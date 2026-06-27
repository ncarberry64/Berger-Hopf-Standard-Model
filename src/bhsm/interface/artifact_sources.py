"""Deterministic local discovery for BHSM JSON and documentation artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

SOURCE_STATUSES = (
    "DISCOVERED",
    "MISSING",
    "PARSE_FAILED",
    "UNSUPPORTED_FORMAT",
    "CLAIM_BOUNDARY_ONLY",
    "REFERENCE_ONLY",
)
DEFAULT_REPO_PATHS = ("artifacts", "docs", "manuscript", "data", "reports", "theory")
EXPECTED_ARTIFACTS = (
    "artifacts/CKM_no_fit_operator_output_v1.json",
    "artifacts/PMNS_no_fit_operator_output_v1.json",
    "artifacts/CP_no_fit_holonomy_output_v1.json",
    "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json",
    "docs/frozen_predictions.json",
    "theory/bhsm_v1_frozen_prediction_set.json",
)
GENERATED_ADAPTER_OUTPUTS = {
    "artifacts/BHSM_artifact_source_index_v0_3.json",
    "artifacts/BHSM_formula_registry_v0_3.json",
    "artifacts/BHSM_artifact_backed_prediction_report_v0_3.json",
    "artifacts/BHSM_artifact_backed_matrix_values_v0_3.json",
    "artifacts/BHSM_artifact_backed_boundary_values_v0_3.json",
    "artifacts/BHSM_artifact_adapter_claim_policy_v0_3.json",
    "artifacts/BHSM_artifact_adapter_manifest_v0_3.json",
}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_artifact_json(path: str | Path) -> Any:
    """Load one local JSON artifact with no network fallback."""

    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def safe_read_text_artifact(path: str | Path) -> str | None:
    """Read local text, returning ``None`` for decoding or I/O failures."""

    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return None


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key).lower())
            keys.update(_walk_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_walk_keys(item))
    return keys


@dataclass(frozen=True)
class ArtifactSource:
    artifact_key: str
    path: str
    exists: bool
    artifact_type: str
    detected_schema: str
    contains_frozen_prediction: bool
    contains_interface_prediction: bool
    contains_registry_entry: bool
    contains_theorem_candidate: bool
    contains_matrix: bool
    contains_constants: bool
    contains_claim_status: bool
    source_status: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["notes"] = list(self.notes)
        return payload


@dataclass(frozen=True)
class ArtifactSourceIndex:
    sources: tuple[ArtifactSource, ...]
    repo_paths_checked: tuple[str, ...]
    parse_failures: tuple[str, ...]
    missing_expected_artifacts: tuple[str, ...]
    index_name: str = "BHSM Artifact Source Index"
    version: str = "0.3"
    claim_boundary: str = "Artifact discovery identifies local sources; it does not infer theorem closure or empirical validation."

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_name": self.index_name,
            "version": self.version,
            "repo_paths_checked": list(self.repo_paths_checked),
            "artifact_count": len(self.sources),
            "sources": [source.to_dict() for source in self.sources],
            "parse_failures": list(self.parse_failures),
            "missing_expected_artifacts": list(self.missing_expected_artifacts),
            "claim_boundary": self.claim_boundary,
        }


@dataclass(frozen=True)
class ArtifactDiscoveryResult:
    index: ArtifactSourceIndex
    offline: bool = True
    internet_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {**self.index.to_dict(), "offline": self.offline, "internet_required": self.internet_required}


def _classify(path: Path, root: Path) -> ArtifactSource:
    relative = path.relative_to(root).as_posix()
    suffix = path.suffix.lower()
    parsed: Any = None
    text = safe_read_text_artifact(path)
    status = "DISCOVERED"
    notes: tuple[str, ...] = ()
    schema = "markdown_document" if suffix == ".md" else "text_document"
    if suffix == ".json":
        try:
            parsed = load_artifact_json(path)
            schema = "json_object" if isinstance(parsed, dict) else "json_array"
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            status = "PARSE_FAILED"
            schema = "json_parse_failed"
            notes = (type(exc).__name__,)
    elif suffix not in {".md", ".txt"}:
        status = "UNSUPPORTED_FORMAT"
        schema = "unsupported"

    lowered = (text or "").lower()
    keys = _walk_keys(parsed) if parsed is not None else set()
    filename = relative.lower()
    reference = any(token in filename for token in ("pdg", "reference", "experimental"))
    claim_only = suffix in {".md", ".txt"} and any(token in lowered for token in ("claim boundary", "forbidden claim"))
    if reference:
        status = "REFERENCE_ONLY"
    elif claim_only:
        status = "CLAIM_BOUNDARY_ONLY"
    artifact_key = path.stem
    return ArtifactSource(
        artifact_key=artifact_key,
        path=relative,
        exists=True,
        artifact_type=suffix.lstrip(".") or "unknown",
        detected_schema=schema,
        contains_frozen_prediction="frozen_prediction" in filename or "frozen prediction" in lowered or "prediction_sets" in keys,
        contains_interface_prediction="interface" in filename and ("prediction" in filename or "output" in filename),
        contains_registry_entry=any("registry" in key for key in keys) or "registry" in filename,
        contains_theorem_candidate=any("theorem" in key or "candidate" in key for key in keys) or "theorem" in filename,
        contains_matrix=bool({"matrix", "magnitude_matrix", "matrix_magnitudes", "h_nu", "k_nu"} & keys),
        contains_constants=bool({"constants", "profile_scale", "charged_boundary_values"} & keys),
        contains_claim_status=bool({"status", "public_status", "claim_status", "theorem_status"} & keys) or "claim" in lowered,
        source_status=status,
        notes=notes,
    )


def discover_bhsm_artifacts(
    repository: str | Path | None = None,
    repo_paths: Iterable[str] = DEFAULT_REPO_PATHS,
) -> ArtifactDiscoveryResult:
    """Build a stable index of supported local artifacts."""

    root = Path(repository).resolve() if repository is not None else repository_root()
    checked = tuple(repo_paths)
    paths: list[Path] = []
    for name in checked:
        base = root / name
        if base.is_dir():
            paths.extend(
                path
                for path in base.rglob("*")
                if path.is_file()
                and path.suffix.lower() in {".json", ".md", ".txt"}
                and path.relative_to(root).as_posix() not in GENERATED_ADAPTER_OUTPUTS
            )
    sources = tuple(_classify(path, root) for path in sorted(set(paths), key=lambda item: item.relative_to(root).as_posix()))
    failures = tuple(source.path for source in sources if source.source_status == "PARSE_FAILED")
    missing = tuple(path for path in EXPECTED_ARTIFACTS if not (root / path).is_file())
    return ArtifactDiscoveryResult(ArtifactSourceIndex(sources, checked, failures, missing))
