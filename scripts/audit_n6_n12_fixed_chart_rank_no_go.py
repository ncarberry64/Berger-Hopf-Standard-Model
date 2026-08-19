"""Write the deterministic fixed-chart endpoint-rank theorem artifact."""

import json
from pathlib import Path

from bhsm.interface.aether_n6_n12_fixed_chart_rank_no_go_v21_37 import (
    fixed_chart_rank_no_go_audit,
)


TARGET = Path("artifacts/BHSM_N6_N12_FIXED_CHART_RANK_NO_GO_V21_37.json")
payload = fixed_chart_rank_no_go_audit()
TARGET.write_text(
    json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, indent=2, sort_keys=True))
