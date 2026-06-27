"""Artifact-backed CP phase and matrix-attachment inspection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..artifact_sources import load_artifact_json, repository_root
from ..matrix_adapters import load_cp_phase_artifact

ATTACHMENT_THEOREM_PATH = "artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json"


@dataclass(frozen=True)
class CPOIntPhaseAttachment:
    delta_bh: float | None
    delta_formula: str | None
    boundary_phase: dict[str, float] | None
    ckm_attachment: bool
    pmns_attachment: bool
    standalone_attachment: bool
    status: str
    source_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_artifacts"] = list(self.source_artifacts)
        return payload


def load_cp_phase_attachment(repository: str | Path | None = None) -> CPOIntPhaseAttachment:
    root = Path(repository).resolve() if repository is not None else repository_root()
    phase = load_cp_phase_artifact(root)
    blocker_path = root / ATTACHMENT_THEOREM_PATH
    blocker = load_artifact_json(blocker_path) if blocker_path.is_file() else {}
    value = phase.value if isinstance(phase.value, dict) else {}
    sources = tuple(path for path in (phase.provenance.source_path, ATTACHMENT_THEOREM_PATH) if path and (root / path).is_file())
    ckm_pmns = bool(blocker.get("attached_to_CKM_PMNS_mixing", False))
    available = phase.source_status == "DISCOVERED"
    return CPOIntPhaseAttachment(
        delta_bh=value.get("delta_BH"),
        delta_formula=value.get("delta_BH_formula"),
        boundary_phase=value.get("Z6_boundary_phase"),
        ckm_attachment=available and ckm_pmns,
        pmns_attachment=available and ckm_pmns,
        standalone_attachment=bool(blocker.get("standalone_attachment_defined", False)),
        status="MATRIX_PHASE_ATTACHMENT_AVAILABLE_STANDALONE_OPEN" if available and ckm_pmns else "ARTIFACT_NOT_FOUND",
        source_artifacts=sources,
    )
