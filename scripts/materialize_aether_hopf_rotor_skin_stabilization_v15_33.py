from pathlib import Path

from bhsm.interface.aether_hopf_rotor_skin_stabilization_v15_33 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
