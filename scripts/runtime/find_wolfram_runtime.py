from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from phase_three_n_common import find_mathematica_app, find_wolfram_kernel, find_wolframscript  # noqa: E402


def main() -> int:
    wolframscript = find_wolframscript()
    kernel = find_wolfram_kernel()
    mathematica = find_mathematica_app()
    print(
        json.dumps(
            {
                "wolframscript": {"detected": wolframscript[0], "path": wolframscript[1], "version": wolframscript[2]},
                "wolfram_kernel": {"detected": kernel[0], "path": kernel[1], "version": kernel[2]},
                "mathematica": {"detected": mathematica[0], "path": mathematica[1]},
                "license_note": "No license bypass or unauthorized install attempted.",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

