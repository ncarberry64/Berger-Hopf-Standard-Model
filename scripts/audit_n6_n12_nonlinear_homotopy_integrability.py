"""Write the deterministic N6-to-N12 nonlinear homotopy audit artifact."""

import json
from pathlib import Path

from bhsm.interface.aether_n6_n12_nonlinear_homotopy_integrability_v21_36 import (
    nonlinear_homotopy_integrability_audit,
)


TARGET = Path(
    "artifacts/BHSM_N6_N12_NONLINEAR_HOMOTOPY_INTEGRABILITY_V21_36.json"
)


payload = nonlinear_homotopy_integrability_audit()
TARGET.write_text(
    json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, indent=2, sort_keys=True))
