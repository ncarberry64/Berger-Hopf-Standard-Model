"""Replay the actual finite-action kinetic diagnostic without changing owners."""
import argparse
from pathlib import Path
from bhsm.interface.muon_mean_kinetic_crossing_diagnostic import materialize

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=materialize(a.output)
    print('same-action pairing cases:',len(r['targeted_pairings']))
    print('exact stored Schur cases:',len(r['constraint_Schur']))
