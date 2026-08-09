from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.completion.completion_minimum_input_v14_48 import completion_payload

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "BHSM_completion_minimum_input_v14_48.json"


def main() -> None:
    OUTPUT.write_text(
        json.dumps(completion_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
