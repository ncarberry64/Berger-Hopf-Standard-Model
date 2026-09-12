"""Run the complete midpoint eigenpair proof on the tighter paired domain."""
import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_coupled_hs_midpoint_domain as midpoint

spec=importlib.util.spec_from_file_location('_bhsm_coupled_midpoint_eigenpair_engine',ROOT/'scripts/certify_n12_gate7_affine_midpoint_eigenpair_pilot.py')
engine=importlib.util.module_from_spec(spec);sys.modules[spec.name]=engine;spec.loader.exec_module(engine)
engine.midpoint=midpoint
engine.WORK=WORK=ROOT/'artifacts/flagship_integration/.coupled_midpoint_eigenpair_pilot_work'
engine.THEORY=THEORY=ROOT/'theory/n12_gate7_coupled_midpoint_pipeline.md'
engine.ALGORITHM=ALGORITHM='COUPLED_NORMALIZED_ACTUAL_HS_MIDPOINT_EIGENPAIR_ARB512_V1'
p=engine.p
original_load_inputs=engine.load_inputs


def load_inputs(index):
    source=original_load_inputs(index)
    p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(Path(__file__)):p.values.sha(Path(__file__))})
    p.verify_sources(source['binding'])
    return source


engine.load_inputs=load_inputs
evaluate=engine.evaluate
main=engine.main

if __name__=='__main__':main()
