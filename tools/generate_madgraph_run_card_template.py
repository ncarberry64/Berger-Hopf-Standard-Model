from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "madgraph_run_card_template_v0_1.txt"
WARNING = """# BHSM MadGraph run-card template v0.1.0
# BHSM UFO model is not yet exported.
# This run card is a structural placeholder.
# Do not use for physics analysis.
#
# Required before execution:
# - complete collider-ready BHSM 4D Lagrangian
# - Feynman rules
# - production UFO model directory
# - validated parameter card
# - validated process card
# - pinned validation targets
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a non-executing BHSM MadGraph run-card template.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(WARNING, encoding="utf-8")
    print(f"Wrote structural placeholder run card: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
