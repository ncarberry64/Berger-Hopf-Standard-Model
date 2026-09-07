"""Export the certified frozen scalar response for a provenance-bound exhibit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json"
OUTPUT = ROOT / "data/museum/bhsm_gate7_scalar_response.json"
SOURCE_REVISION = "d75e77bbdcfba79a83b9c9f9c8c398ae8e7a79d4"


def build_payload():
    record = json.loads(SOURCE.read_text(encoding="utf-8"))
    if record.get("validation_passed") is not True or record.get("FULL_BHSM_COMPLETE") is not False:
        raise RuntimeError("validated scoped scalar certificate required")
    data = ROOT / record["data"]
    digest = hashlib.sha256(data.read_bytes()).hexdigest().upper()
    if digest != record["data_SHA256"]:
        raise RuntimeError("scalar array hash does not match its certificate")
    revision = SOURCE_REVISION
    for path in (SOURCE, data):
        relative = path.relative_to(ROOT).as_posix()
        committed = subprocess.check_output(["git", "show", f"{revision}:{relative}"], cwd=ROOT)
        actual = path.read_bytes()
        if path.suffix == ".json":
            committed, actual = (value.replace(b"\r\n", b"\n") for value in (committed, actual))
        if committed != actual:
            raise RuntimeError("Museum source must match its immutable Git revision")
    with np.load(data) as source:
        upper = np.asarray(source["causal_central_scalar_curvature_norm_upper"], dtype=float)
        local = np.asarray(source["local_projected_HS_second_residual_norm_upper"], dtype=float)
        precision = int(source["precision_bits"])
    if (upper.shape != (371,) or local.shape != (370,) or precision != 512
            or not all(np.all(np.isfinite(v)) and np.all(v >= 0) for v in (upper, local))
            or float(np.nextafter(np.max(upper), np.inf)) != record["maximum_causal_curvature_norm_upper"]
            or float(np.nextafter(np.max(local), np.inf)) != record["maximum_local_projected_HS_second_residual_norm_upper"]):
        raise RuntimeError("scalar exhibit data fails certificate consistency")
    # Match the certificate's final upward binary64 conversion for display.
    upper = np.where(upper == 0, 0., np.nextafter(upper, np.inf))
    local = np.nextafter(local, np.inf)
    return {
        "title": "A certified response along the computational path",
        "data_kind": "BHSM numerical certificate; not experimental measurements",
        "scope": "Frozen central scalar causal response only",
        "source_revision": revision,
        "source_certificate": SOURCE.relative_to(ROOT).as_posix(),
        "source_certificate_SHA256": hashlib.sha256(SOURCE.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper(),
        "source_data": record["data"],
        "source_data_SHA256": digest,
        "precision_bits": precision,
        "node_count": 371,
        "interval_count": 370,
        "maximum_response_upper": float(np.max(upper)),
        "maximum_response_node": int(np.argmax(upper)),
        "response_norm_upper": upper.tolist(),
        "local_residual_norm_upper": local.tolist(),
        "validation_passed": True,
        "claim_boundary": record["claim_boundary"],
        "FULL_BHSM_COMPLETE": False,
    }


if __name__ == "__main__":
    payload = build_payload()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "nodes": payload["node_count"],
                      "source_revision": payload["source_revision"]}))
