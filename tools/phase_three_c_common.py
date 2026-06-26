from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "artifacts" / "BHSM_phase_three_c_analytical_working_packet_v0_5.json"


def load_packet() -> dict[str, Any]:
    if not PACKET.exists():
        raise FileNotFoundError(
            "Missing Phase Three-C source packet: "
            "artifacts/BHSM_phase_three_c_analytical_working_packet_v0_5.json"
        )
    return json.loads(PACKET.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def packet_checksum() -> str:
    return hashlib.sha256(PACKET.read_bytes()).hexdigest().upper()


def guardrails() -> dict[str, bool]:
    return {
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def source_packet_ref() -> dict[str, str]:
    return {
        "source_artifact": "artifacts/BHSM_phase_three_c_analytical_working_packet_v0_5.json",
        "source_sha256": packet_checksum(),
    }
