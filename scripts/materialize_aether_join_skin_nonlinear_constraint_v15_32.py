from pathlib import Path

from bhsm.interface.aether_join_skin_nonlinear_constraint_v15_32 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
