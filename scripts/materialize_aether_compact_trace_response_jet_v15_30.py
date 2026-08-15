from pathlib import Path

from bhsm.interface.aether_compact_trace_response_jet_v15_30 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
