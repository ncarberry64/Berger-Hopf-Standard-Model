from __future__ import annotations
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"src"
if str(SRC) not in sys.path:
    sys.path.insert(0,str(SRC))
from bhsm.interface.completion.hopf_u1_obstruction_diagonal_locking_v14_73 import materialize
if __name__=="__main__":
    for p in materialize(ROOT/"artifacts"):
        print(p)
