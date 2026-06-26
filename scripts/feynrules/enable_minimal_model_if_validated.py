from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "artifacts" / "BHSM_live_feynrules_validation_attempt_v1_5.json"
DISABLED = ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr.disabled"
ENABLED = ROOT / "models" / "feynrules" / "BHSM_Minimal_Collider_Interface.fr"
RUN_DIR = ROOT / "runs" / "feynrules_validation"


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if not VALIDATION.exists():
        raise SystemExit("Missing live validation artifact; enablement refused.")
    payload = json.loads(VALIDATION.read_text(encoding="utf-8"))
    required = [
        payload.get("feynrules_syntax_validated"),
        payload.get("feynrules_model_load_validated"),
        payload.get("lagrangian_symbol_checked"),
        payload.get("excluded_vertices_confirmed"),
        payload.get("forbidden_content_confirmed_absent"),
    ]
    if not all(required):
        candidate = RUN_DIR / "BHSM_Minimal_Collider_Interface.candidate.unvalidated.fr"
        shutil.copyfile(DISABLED, candidate)
        print(f"Validation incomplete; wrote unvalidated candidate only: {candidate}")
        return 2
    if ENABLED.exists():
        backup = RUN_DIR / "BHSM_Minimal_Collider_Interface.fr.backup"
        shutil.copyfile(ENABLED, backup)
    shutil.copyfile(DISABLED, ENABLED)
    print(f"Enabled validated minimal FeynRules model: {ENABLED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

