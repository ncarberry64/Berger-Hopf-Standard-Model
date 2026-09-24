"""Transfer state-only midpoint equations after exact operand equality checks.

The new physical input map never occurs in the 124 base equations. Both
families use identical base predictors, correction radii and state domain.
The lambda slot is independently rebuilt from the identical Rayleigh jet by
both producers, so its preparatory placeholder radius is not an operand.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys
from fractions import Fraction
from flint import ctx
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
import bhsm.interface.shared_action_taylor as arithmetic
import n12_gate7_base_residual_models as loader
import n12_gate7_left_saved_family as left
import evaluate_n12_gate7_coupled_residual_saved as right


def evaluate(root, parent, refined, old_parent, old_refined, old_models, new_terms, old_terms, out):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    new_verified = left.evaluate(root)
    old_verified = right.evaluate(root)
    paths = dict(parent=parent/'record.json', refined=refined,
        old_parent=old_parent/'record.json', old_refined=old_refined,
        old_record=old_models/'record.json', old_models=old_models/'models.json.gz',
        verifier=Path(left.__file__), loader=Path(loader.__file__),
        arithmetic=Path(arithmetic.__file__), evaluator=Path(__file__),
        left_action_producer=ROOT/'scripts/certify_n12_gate7_left_input_output.py',
        old_base_producer=ROOT/'scripts/certify_n12_gate7_base_residual_ranges.py')
    paths.update(new_rayleigh=new_terms/'rayleigh.json.gz', old_rayleigh=old_terms/'rayleigh.json.gz',
        new_manifest=new_terms/'sources.json', old_manifest=old_terms/'sources.json',
        old_cache_producer=ROOT/'scripts/certify_n12_gate7_base_residual_vector.py')
    hashes = {k:left.sha(p) for k,p in paths.items()}
    new = json.loads(paths['parent'].read_bytes())
    old = json.loads(paths['old_parent'].read_bytes())
    nr = json.loads(refined.read_bytes())
    rr = json.loads(old_refined.read_bytes())
    base = json.loads(paths['old_record'].read_bytes())
    if (new.get('family') != 'midpoint' or new.get('side') != 'left'
            or old.get('family') != 'midpoint'
            or new['original_state_groups'] != old['original_state_groups']
            or new['source_hashes']['refined_base_radii'] != hashes['refined']
            or old['source_hashes']['refined_base_radii'] != hashes['old_refined']
            or new['source_hashes']['evaluator'] != hashes['left_action_producer']
            or base['source_hashes']['evaluator'] != hashes['old_base_producer']
            or nr.get('algorithm') != 'ORIGINAL_LEFT_BASE_INCLUSION_WITH_RESPONSE_MEAN_VALUE_V1'
            or new_verified['families']['midpoint']['midpoint_base_arrays_identical_to_right'] is not True):
        raise ValueError('reviewed identical midpoint base construction required')
    for record, verified in ((new, new_verified), (nr, new_verified),
                             (old, old_verified), (rr, old_verified)):
        if any(record['source_hashes'].get(k) != v for k,v in verified['paired_source_hashes'].items()):
            raise ValueError('all original paired source bindings must match')
    if (len(nr['correction_radii_exact']) != 124
            or any(Fraction(nr['correction_radii_exact'][i]) != Fraction(rr['correction_radii_exact'][i])
                   for i in range(124) if i != 61)):
        raise ValueError('identical effective base correction radii required')
    nm = json.loads(paths['new_manifest'].read_bytes())
    om = json.loads(paths['old_manifest'].read_bytes())
    nj = json.loads(gzip.decompress(paths['new_rayleigh'].read_bytes()))
    oj = json.loads(gzip.decompress(paths['old_rayleigh'].read_bytes()))
    if (nm != new['source_hashes'] or om.get('evaluator') != hashes['old_cache_producer']
            or any(om.get(k) != v for k,v in base['source_hashes'].items() if k != 'evaluator')
            or nj['binding'] != hashes['new_manifest'] or oj['binding'] != hashes['old_manifest']
            or nj.get('kind') != 'Taylor' or nj['values'] != oj['coefficients']):
        raise ValueError('identical source-bound Rayleigh coefficients and remainders required')
    # Replay every exact saved residual support, all equations and its parent
    # binding before copying coefficients. This is not a new action evaluation.
    domain = TaylorDomain(old['original_state_groups'], 373)
    loader.load_block(old_models, old_parent, old_refined, domain, list(range(373)), old_verified)
    result = dict(base)
    result.update(side='left', source_hashes={**new_verified['paired_source_hashes'],
        'parent_record':hashes['parent'], 'refined_base_radii':hashes['refined'],
        'arithmetic':hashes['arithmetic'], 'evaluator':hashes['evaluator']},
        state_only_operand_equality_verified=True,
        physical_input_map_absent_from_base_equations=True,
        eigenvalue_radius_recomputed_from_identical_rayleigh_predictor=True,
        guarded_reuse_SHA256=hashes, original_right_model_SHA256=hashes['old_models'],
        new_action_derivative_evaluations=0)
    if {k:left.sha(p) for k,p in paths.items()} != hashes:
        raise ValueError('proof sources changed during reuse verification')
    out.mkdir(parents=True, exist_ok=False)
    (out/'models.json.gz').write_bytes(paths['old_models'].read_bytes())
    (out/'record.json').write_bytes(left.encoded(result))
    print(json.dumps(dict(base_components_reused=124,
        models_SHA256=result['models_SHA256'], new_action_derivative_evaluations=0)), flush=True)


def main():
    parser = argparse.ArgumentParser()
    for name in ('evidence-root', 'parent', 'refined', 'old-parent', 'old-refined', 'old-models', 'new-terms', 'old-terms', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    evaluate(args.evidence_root.resolve(), args.parent, args.refined,
             args.old_parent, args.old_refined, args.old_models, args.new_terms, args.old_terms, args.out)


if __name__ == '__main__':
    main()
