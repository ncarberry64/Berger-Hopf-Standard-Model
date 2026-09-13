"""Private full-basis producers using verified centers and component bounds."""
import importlib.util
from pathlib import Path
import sys
import diagnose_n12_gate7_component_centered_uniform_derivatives as component
import bhsm_immutable_input_hash_cache as input_cache


def make_engine(root,stage,wrapper):
    if stage not in ('endpoint','midpoint'):raise ValueError('explicit physical stage required')
    path=root/f'scripts/certify_n12_gate7_coupled_{stage}_uniform_derivatives.py'
    spec=importlib.util.spec_from_file_location(f'_bhsm_component_centered_{stage}_uniform_df',path)
    engine=importlib.util.module_from_spec(spec);sys.modules[spec.name]=engine;spec.loader.exec_module(engine)
    original_load=engine.load_inputs;original_main=engine.main;original_theory=engine.THEORY
    engine.WORK=root/f'artifacts/flagship_integration/.component_centered_{stage}_uniform_df_work'
    engine.THEORY=root/'theory/n12_gate7_centered_coupled_variation_residual.md'
    engine.ALGORITHM=f'COMPONENT_CENTERED_{stage.upper()}_UNIFORM_PHYSICAL_DF_ARB512_V1'

    def load_inputs(index):
        source=original_load(index);d=component.diagnostic
        for file in (Path(wrapper),Path(__file__),original_theory,engine.THEORY,
                     Path(component.__file__),Path(d.__file__),Path(d.signed.__file__),
                     Path(d.refinement.__file__),Path(d.refinement.normalization.__file__),
                     Path(component.rows.__file__),Path(input_cache.__file__)):
            engine.p.geometry.residual.merge(source['binding']['files'],{engine.p.df.file_key(file):engine.p.values.sha(file)})
        engine.p.verify_sources(source['binding'])
        return source

    def evaluate(source):
        arrays,proof=component.evaluate(engine,source,0,99)
        if arrays['derivative'].shape!=(99,99):raise ArithmeticError('complete physical basis required')
        report=dict(validation_passed=True,
            scope='ACTUAL_HS_MIDPOINT_OUTER_DOMAIN' if stage=='midpoint' else 'SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE',
            uniform_physical_first_derivatives_enclosed=True,actual_HS_midpoint_domain_enclosed=stage=='midpoint',
            weighted_augmented_basis_columns=99,full_descriptor_direction_included=True,
            original_complete_first_variation_reused=True,verified_anchor_derivative_contained=True,
            componentwise_centered_variations=True,coupled_normalization_and_variation_proof=proof,
            uniform_physical_hessians_enclosed=False,higher_remainder_enclosed=False,
            physical_quotient_identified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
        return arrays,report

    def main():
        import json
        residual=engine.p.geometry.residual
        targets=[(engine.p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
        with input_cache.cache_hashes(targets,excluded_roots=[engine.WORK]) as stats:
            try:original_main()
            finally:print(json.dumps(dict(immutable_input_hash_cache=stats)),flush=True)

    engine.load_inputs=load_inputs;engine.evaluate=evaluate;engine.main=main
    return engine
