from pathlib import Path

from bhsm.interface.aether_york_response_initial_data_v15_42 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
