from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.completion.full_dirac_a4_trace_v14_50 import completion_payload


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "artifacts" / "BHSM_full_Dirac_a4_trace_v14_50.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(completion_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(target)


if __name__ == "__main__":
    main()
