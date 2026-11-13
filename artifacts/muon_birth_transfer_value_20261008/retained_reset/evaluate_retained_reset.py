"""CLI shim for the owned retained E1/C2 reset value evaluator."""
from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.muon_birth_reset_evaluation import evaluate

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    evaluate(parser.parse_args().out)
