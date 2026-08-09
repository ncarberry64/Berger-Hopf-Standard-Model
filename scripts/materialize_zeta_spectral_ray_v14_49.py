from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.completion.zeta_spectral_ray_v14_49 import status_payload


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "artifacts" / "BHSM_zeta_spectral_ray_v14_49.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(status_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(target)


if __name__ == "__main__":
    main()
