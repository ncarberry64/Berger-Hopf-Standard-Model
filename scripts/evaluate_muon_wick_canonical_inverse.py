"""Execute the continued full488 canonical inverse on its inherited contour."""
from pathlib import Path
import sys,argparse,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_wick_canonical_inverse import materialize_wick_canonical_inverse
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--refinements',nargs='+',type=int,default=[16,32,64]);a=p.parse_args()
    print(json.dumps(materialize_wick_canonical_inverse(a.output,refinements=tuple(a.refinements)),sort_keys=True))
