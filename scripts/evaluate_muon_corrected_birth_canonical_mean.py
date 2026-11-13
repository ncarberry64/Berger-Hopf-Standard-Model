"""Export actual corrected birth canonical means and inherited forcing."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_corrected_birth_canonical_mean import materialize_corrected_birth_canonical_mean
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mean-directory',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(materialize_corrected_birth_canonical_mean(a.mean_directory,a.output),sort_keys=True))
