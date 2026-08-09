from pathlib import Path

from bhsm.interface.completion.global_envelopment_cap_selection_v14_60 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for path in materialize(root / "artifacts"):
        print(path)
