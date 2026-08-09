from __future__ import annotations
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"src"
if str(SRC) not in sys.path:
    sys.path.insert(0,str(SRC))
from bhsm.interface.completion.driven_hypersphere_black_hole_flux_gate_v14_81 import materialize
if __name__=="__main__":
    for p in materialize(ROOT/"artifacts"):
        print(p)
