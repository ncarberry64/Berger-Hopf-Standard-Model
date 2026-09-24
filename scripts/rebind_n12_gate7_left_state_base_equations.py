"""Reuse left state-only base equations after changing output cancellation.

The physical source, base predictor, correction radii, groups and exact
Rayleigh jet must agree. Directional output covectors do not occur in any
of the 124 state-only equations. Every saved equation support is replayed.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys
from flint import ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
import bhsm.interface.shared_action_taylor as arithmetic
import n12_gate7_base_residual_models as loader
import n12_gate7_left_saved_family as saved


def evaluate(root, parent, old_parent, refined, old_models, new_terms, old_terms, out):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    verified = saved.evaluate(root)
    paths = dict(parent=parent/'record.json', old_parent=old_parent/'record.json',
        refined=refined, old_record=old_models/'record.json',
        old_models=old_models/'models.json.gz',
        new_manifest=new_terms/'sources.json', old_manifest=old_terms/'sources.json',
        new_rayleigh=new_terms/'rayleigh.json.gz', old_rayleigh=old_terms/'rayleigh.json.gz',
        original_output=ROOT/'scripts/certify_n12_gate7_left_input_output.py',
        deferred_output=ROOT/'scripts/certify_n12_gate7_left_deferred_base_output.py',
        original_base=ROOT/'scripts/certify_n12_gate7_left_base_residual_vector.py',
        midpoint_base_reuse=ROOT/'scripts/reuse_n12_gate7_left_midpoint_base_residuals.py',
        verifier=Path(saved.__file__), arithmetic=Path(arithmetic.__file__),
        loader=Path(loader.__file__), evaluator=Path(__file__))
    hashes = {k:saved.sha(p) for k,p in paths.items()}
    new = json.loads(paths['parent'].read_bytes())
    old = json.loads(paths['old_parent'].read_bytes())
    base = json.loads(paths['old_record'].read_bytes())
    if (new.get('side') != 'left' or old.get('side') != 'left'
            or new.get('family') != old.get('family')
            or new['family'] not in ('midpoint', 'endpoint')
            or new.get('base_cancellation_deferred') is not True
            or new.get('base_equations_deferred') != 124
            or new['source_hashes']['evaluator'] != hashes['deferred_output']
            or old['source_hashes']['evaluator'] != hashes['original_output']
            or base['source_hashes']['evaluator'] not in
                (hashes['original_base'], hashes['midpoint_base_reuse'])):
        raise ValueError('reviewed left base and deferred-output constructions required')
    for record in (new, old):
        if (record['source_hashes']['refined_base_radii'] != hashes['refined']
                or any(record['source_hashes'].get(k) != v
                       for k,v in verified['paired_source_hashes'].items())):
            raise ValueError('identical original physical sources and base radii required')
    for key in ('original_state_groups','input_map','input_groups','axis_correction_radii'):
        if new[key] != old[key]:
            raise ValueError('unchanged state and directional parametrization required')
    for key in ('adjoint','refined_base_radii','implementation','shared_action_taylor',
                'shared_parameter_residual','source_verifier'):
        if new['source_hashes'][key] != old['source_hashes'][key]:
            raise ValueError('unchanged predictor construction and arithmetic required')
    manifests = [json.loads(paths[k].read_bytes()) for k in ('new_manifest','old_manifest')]
    jets = [json.loads(gzip.decompress(paths[k].read_bytes()))
            for k in ('new_rayleigh','old_rayleigh')]
    if (manifests != [new['source_hashes'], old['source_hashes']]
            or any(j['binding'] != hashes[k] or j.get('kind') != 'Taylor'
                   for j,k in zip(jets,('new_manifest','old_manifest'),strict=True))
            or jets[0]['values'] != jets[1]['values']):
        raise ValueError('identical source-bound Rayleigh coefficients and remainder required')
    dimension = {'midpoint':373, 'endpoint':199}[old['family']]
    domain = TaylorDomain(old['original_state_groups'], dimension)
    loader.load_block(old_models, old_parent, refined, domain, list(range(dimension)), verified)
    result = dict(base)
    result.update(source_hashes={**verified['paired_source_hashes'],
        'parent_record':hashes['parent'], 'refined_base_radii':hashes['refined'],
        'arithmetic':hashes['arithmetic'], 'evaluator':hashes['evaluator']},
        guarded_parent_rebinding_SHA256=hashes,
        state_only_operand_equality_verified=True,
        physical_input_map_absent_from_base_equations=True,
        directional_output_covectors_absent_from_base_equations=True,
        base_equations_supports_replayed=124,
        new_action_derivative_evaluations=0)
    if hashes != {k:saved.sha(p) for k,p in paths.items()}:
        raise ValueError('proof sources changed during reuse verification')
    out.mkdir(parents=True, exist_ok=False)
    (out/'models.json.gz').write_bytes(paths['old_models'].read_bytes())
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(family=old['family'],base_equations_reused=124,
        models_SHA256=result['models_SHA256'],new_action_derivative_evaluations=0)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    for name in ('evidence-root','parent','old-parent','refined','old-models',
                 'new-terms','old-terms','out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    evaluate(args.evidence_root.resolve(),args.parent,args.old_parent,args.refined,
             args.old_models,args.new_terms,args.old_terms,args.out)


if __name__ == '__main__':
    main()
