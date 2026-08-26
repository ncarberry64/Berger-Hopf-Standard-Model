"""Run the retained signed-row engine on the full segment-1214 joint tube."""

from __future__ import annotations

import audit_n12_c2_reduced_ddelta_operator_majorant as engine


SEGMENT_1214_JOINT_RADIUS = 5.5212888273161885e-11


def main() -> None:
    engine.RADIUS = SEGMENT_1214_JOINT_RADIUS
    engine.main()


if __name__ == "__main__":
    main()
