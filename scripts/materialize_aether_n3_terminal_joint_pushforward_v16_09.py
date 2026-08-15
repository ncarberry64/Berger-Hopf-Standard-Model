"""Materialize the deterministic BHSM v16.09 N=3 domain-exit audit."""

from pathlib import Path

from bhsm.interface.aether_n3_terminal_joint_pushforward_v16_09 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
