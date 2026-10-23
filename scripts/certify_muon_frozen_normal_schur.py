"""Run the implemented finite normal arithmetic certification in package context."""
from pathlib import Path
import runpy
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
runpy.run_module('bhsm.interface.muon_frozen_normal_schur_certificate',run_name='__main__')
