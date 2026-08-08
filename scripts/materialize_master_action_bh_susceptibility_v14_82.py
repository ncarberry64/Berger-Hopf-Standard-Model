from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from bhsm.interface.completion.master_action_bh_susceptibility_v14_82 import materialize
for p in materialize(ROOT/"artifacts"): print(p)
