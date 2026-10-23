"""Evaluate original full488 coefficient/source action continuation."""
import argparse
import json
from pathlib import Path
from bhsm.interface.muon_wick_temporal_action import materialize_wick_temporal_action


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(materialize_wick_temporal_action(a.output), sort_keys=True))
