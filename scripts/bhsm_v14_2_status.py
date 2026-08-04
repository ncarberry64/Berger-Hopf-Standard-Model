"""Print the deterministic BHSM v14.2 completion status."""

from __future__ import annotations

from bhsm.interface.completion.eta_knot_color_completion_v14_2 import (
    cli_status,
    deterministic_json,
)


if __name__ == "__main__":
    print(deterministic_json(cli_status()), end="")
