"""Materialize the dense BHSM v15.97 proper joint pushforward."""

from pathlib import Path

from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
