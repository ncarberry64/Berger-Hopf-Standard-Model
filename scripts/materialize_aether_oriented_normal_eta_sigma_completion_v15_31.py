from pathlib import Path

from bhsm.interface.aether_oriented_normal_eta_sigma_completion_v15_31 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
