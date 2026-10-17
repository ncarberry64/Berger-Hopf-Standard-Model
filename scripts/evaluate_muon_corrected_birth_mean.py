"""Execute actual true moving-birth second mean; preserve all previous runs."""
from pathlib import Path
import sys,argparse,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_corrected_birth_mean import materialize_corrected_birth_mean
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--difference-step',type=float,default=2e-5);p.add_argument('--no-certificate',action='store_true')
    a=p.parse_args();print(json.dumps(materialize_corrected_birth_mean(a.output,difference_step=a.difference_step,
        certify=not a.no_certificate),sort_keys=True))
