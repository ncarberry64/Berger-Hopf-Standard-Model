"""Private producer instances for coupled-normalization derivative refinements."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import n12_gate7_coupled_normalization_derivative_refinement as refinement
import bhsm_immutable_input_hash_cache as input_cache


def make_engine(root,stage,wrapper):
    if stage not in ('endpoint','midpoint'):raise ValueError('explicit endpoint or midpoint stage required')
    path=root/f'scripts/certify_n12_gate7_coupled_{stage}_uniform_derivatives.py'
    spec=importlib.util.spec_from_file_location(f'_bhsm_refined_{stage}_uniform_df_engine',path)
    engine=importlib.util.module_from_spec(spec);sys.modules[spec.name]=engine;spec.loader.exec_module(engine)
    original_load=engine.load_inputs;original_evaluate=engine.evaluate;original_main=engine.main
    original_theory=engine.THEORY
    base=SimpleNamespace(p=engine.p,inverse=engine.inverse,evaluate_batch=engine.evaluate_batch)
    engine.WORK=root/f'artifacts/flagship_integration/.refined_coupled_{stage}_uniform_df_work'
    engine.THEORY=root/'theory/n12_gate7_coupled_normalization_derivative.md'
    engine.ALGORITHM=f'REFINED_COUPLED_{stage.upper()}_UNIFORM_PHYSICAL_DF_ARB512_V1'

    def load_inputs(index):
        source=original_load(index)
        for file in (Path(wrapper),Path(__file__),original_theory,Path(refinement.__file__),Path(refinement.normalization.__file__),Path(input_cache.__file__)):
            engine.p.geometry.residual.merge(source['binding']['files'],{engine.p.df.file_key(file):engine.p.values.sha(file)})
        engine.p.verify_sources(source['binding'])
        return source

    def evaluate_batch(source,start,stop):
        arrays,proof=refinement.refine_batch(base,source,start,stop)
        return arrays['derivative'],arrays['preconditioned_variation_rhs'],proof

    def evaluate(source):
        arrays,report=original_evaluate(source)
        report['coupled_normalization_batches']=report.pop('coupled_inverse_bounds')
        report['common_border_scale_canceled_before_differentiation']=True
        report['original_complete_derivative_overlap_verified']=True
        return arrays,report

    def main():
        import json
        residual=engine.p.geometry.residual
        targets=[(engine.p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
        with input_cache.cache_hashes(targets,excluded_roots=[engine.WORK]) as stats:
            try:original_main()
            finally:print(json.dumps(dict(immutable_input_hash_cache=stats)),flush=True)

    engine.load_inputs=load_inputs;engine.evaluate_batch=evaluate_batch;engine.evaluate=evaluate;engine.main=main
    return engine
