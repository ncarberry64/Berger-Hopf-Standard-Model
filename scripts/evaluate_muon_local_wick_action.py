"""Evaluate the literal local gauge/Higgs/ghost analytic continuation."""
import argparse
import json
from pathlib import Path
from bhsm.interface.muon_local_wick_action import materialize_local_wick_application


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase-directory', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--cell-index', type=int, default=0)
    a = p.parse_args()
    print(json.dumps(materialize_local_wick_application(a.phase_directory, a.output,
        cell_index=a.cell_index), sort_keys=True))


if __name__ == '__main__':
    main()
