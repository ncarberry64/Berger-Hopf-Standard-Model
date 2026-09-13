"""Assemble the same uniform local operator using paired component-centered derivatives."""
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_component_centered_endpoint_uniform_derivatives as endpoint
import certify_n12_gate7_component_centered_midpoint_uniform_derivatives as midpoint
import bhsm_immutable_input_hash_cache as input_cache

spec=importlib.util.spec_from_file_location('_bhsm_component_centered_uniform_local_engine',ROOT/'scripts/certify_n12_gate7_uniform_physical_local_defects.py')
engine=importlib.util.module_from_spec(spec);sys.modules[spec.name]=engine;spec.loader.exec_module(engine)
engine.endpoint=endpoint;engine.midpoint=midpoint
engine.WORK=WORK=ROOT/'artifacts/flagship_integration/.component_centered_uniform_physical_local_defect_work'
engine.ALGORITHM=ALGORITHM='COMPONENT_CENTERED_UNIFORM_PHYSICAL_HS_FROZEN_LOCAL_NEWTON_DEFECT_ARB512_V1'
p=engine.p;THEORY=engine.THEORY
original_load=engine.load_inputs;original_main=engine.main

def load_inputs(index):
    source=original_load(index)
    for file in (Path(__file__),Path(input_cache.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    p.verify_sources(source['binding'])
    return source

engine.load_inputs=load_inputs
evaluate=engine.evaluate

def main():
    import json
    residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with input_cache.cache_hashes(targets,excluded_roots=[WORK]) as stats:
        try:original_main()
        finally:print(json.dumps(dict(immutable_input_hash_cache=stats)),flush=True)

if __name__=='__main__':main()
