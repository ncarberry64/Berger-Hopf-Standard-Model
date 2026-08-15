from pathlib import Path

from bhsm.interface.aether_formed_compact_sigma_response_v15_29 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
