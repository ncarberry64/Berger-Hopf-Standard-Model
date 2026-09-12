"""Reproduce complete endpoint derivatives with coupled normalization."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from n12_gate7_refined_uniform_derivative_adapter import make_engine
engine=make_engine(ROOT,'endpoint',Path(__file__))
p=engine.p;WORK=engine.WORK;THEORY=engine.THEORY;ALGORITHM=engine.ALGORITHM
load_inputs=engine.load_inputs;evaluate=engine.evaluate;main=engine.main
if __name__=='__main__':main()
