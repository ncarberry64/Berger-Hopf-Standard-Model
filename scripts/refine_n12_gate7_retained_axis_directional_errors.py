"""Refine the existing directional-error box on the retained longitudinal axis.

Uses only contracted directional equations already evaluated from the source
action. The initial box is an existing physical inclusion. Every intersection
is justified by a residual inequality on the unchanged original state domain.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import gzip
import json
from pathlib import Path
import sys
import numpy as np
from scipy.linalg import qr
from flint import arb, arb_mat, ctx
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor, vector_norm
from bhsm.interface.shared_parameter_residual import linear_support
from bhsm.interface.directional_error_refinement import intersect_majorant
import bhsm.interface.directional_error_refinement as refinement
import bhsm.interface.base_residual_cancellation as cancellation
import n12_gate7_base_residual_models as base_models
import n12_gate7_common_input_error_maps as error_maps
import evaluate_n12_gate7_coupled_residual_saved as saved
from certify_n12_gate7_endpoint_vector_transport import restore, upper


def main():
    parser = argparse.ArgumentParser()
    for name in ('evidence-root', 'residuals', 'parent', 'base-residual', 'refined', 'adjoint', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args(); ctx.prec = 512
    if args.out.exists(): raise FileExistsError('fresh refinement output required')
    root = args.evidence_root.resolve()
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    verified = saved.evaluate(root)
    record = json.loads((args.residuals/'record.json').read_bytes())
    parent = json.loads((args.parent/'record.json').read_bytes())
    if (record['algorithm'] != 'FULL_INPUT_CONTRACTED_DIRECTIONAL_RESIDUALS_V1'
            or record['components'] != list(range(61))
            or record['family'] != parent['family']
            or record['source_hashes']['adjoint'] != saved.sha(args.adjoint)
            or record['source_hashes']['refined_base_radii'] != saved.sha(args.refined)
            or any(record['source_hashes'].get(k) != v for k, v in verified['paired_source_hashes'].items())):
        raise ValueError('complete unchanged contracted directional equations required')
    dim = {'midpoint':373, 'endpoint':199}[record['family']]
    domain = TaylorDomain(record['original_state_groups'], dim)
    if record['original_state_groups'] != parent['original_state_groups']:
        raise ValueError('unchanged state domain required')
    block = base_models.load_block(args.base_residual, args.parent, args.refined,
        domain, list(range(dim)), verified)
    error_map = error_maps.load_error_map(root, parent, args.adjoint)
    axisfile = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axisfile, allow_pickle=False) as z:
        axes = z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:],axis=1)[:,None]
    axes[0] = 0
    axis_array = axes[14]
    axis = arb_mat(74, 1, [arb(float(v)) for v in axis_array])
    initial = [abs(v).upper() for v in (error_map*axis).entries()]
    gauge = max(vector_norm(axis.entries()), *initial)
    guarded = dict(evaluator=Path(__file__), arithmetic=Path(refinement.__file__),
        base_cancellation=Path(cancellation.__file__), base_loader=Path(base_models.__file__),
        input_error_maps=Path(error_maps.__file__), source_verifier=Path(saved.__file__),
        residual_producer=ROOT/'scripts/reconstruct_n12_gate7_directional_residuals.py',
        residual_record=args.residuals/'record.json', parent=args.parent/'record.json',
        base_record=args.base_residual/'record.json', base_models=args.base_residual/'models.json.gz',
        refined=args.refined, adjoint=args.adjoint, axis=axisfile)
    for i in range(61): guarded[f'component_{i:02d}'] = args.residuals/f'component_{i:02d}.json.gz'
    guarded['normalizations'] = args.residuals/'normalizations.json.gz'
    hashes = {k:saved.sha(v) for k,v in guarded.items()}
    if hashes['residual_producer'] != record['source_hashes']['evaluator']:
        raise ValueError('unchanged directional residual producer required')
    residuals = []
    def decode(values):
        if len(values) != 198*(dim+1)+1: raise ValueError('complete residual coefficients required')
        v = [restore(x) for x in values]
        model = InputLinearTaylor(domain, arb_mat(1,198,v[:198]),
            arb_mat(dim,198,v[198:-1]), v[-1], record['input_groups'])
        # Substitute only the fixed physical direction; eta remains symbolic.
        physical_c = sum((model.c[0,j]*axis[j,0] for j in range(74)), arb(0))
        physical_a = arb_mat(dim,74,[model.a[i,j] for i in range(dim) for j in range(74)])*axis
        packed = arb_mat(dim+1,125, [physical_c]+[model.c[0,j] for j in range(74,198)]
            +[v for i in range(dim) for v in [physical_a[i,0], *[model.a[i,j] for j in range(74,198)]]])
        return packed, model.r
    for i, item in enumerate(record['records']):
        if item['component'] != i or item['models_SHA256'] != hashes[f'component_{i:02d}']:
            raise ValueError('ordered fingerprinted directional equations required')
        data = json.loads(gzip.decompress(guarded[f'component_{i:02d}'].read_bytes()))
        for name in ('G2_coefficients','G3_coefficients'): residuals.append(decode(data[name]))
        print(json.dumps(dict(stage='residual_loaded',component=i)), flush=True)
    if record['normalizations_SHA256'] != hashes['normalizations']:
        raise ValueError('normalization equations fingerprint mismatch')
    normals = json.loads(gzip.decompress(guarded['normalizations'].read_bytes()))
    if len(normals) != 3: raise ValueError('two normalization equations and derived multiplier equation required')
    residuals.extend(decode(row) for row in normals)
    C = arb_mat(125,124,[m[0,j+1] for m,r in residuals for j in range(124)])
    # Floating QR selects equations only. The point covector is then formed
    # with Arb, and its entire defect remains in the inequality below.
    proposal = np.array([[float(C[i,j].mid()) for j in range(124)] for i in range(125)])
    scales = np.maximum(np.max(np.abs(proposal),axis=0), np.finfo(float).tiny)
    proposal = proposal/scales
    row_scales = np.maximum(np.max(np.abs(proposal),axis=1),np.finfo(float).tiny)
    _, _, pivots = qr((proposal/row_scales[:,None]).T, pivoting=True, mode='economic')
    selected = [int(i) for i in pivots[:124]]
    chosen = arb_mat(124,124,[C[i,j] for i in selected for j in range(124)])
    inverse = chosen.mid().inv().mid()
    P = arb_mat(124,125)
    for i in range(124):
        for j,k in enumerate(selected): P[i,k] = inverse[i,j]
    print(json.dumps(dict(stage='point_left_inverse_ready',selected=selected)),flush=True)
    raw_remainders = arb_mat(125,1,[r*gauge for m,r in residuals])
    remainder = arb_mat(124,125,[abs(v).upper() for v in P.entries()])*raw_remainders
    base_coefficients = arb_mat(124,dim+1,[v for g in block.residuals for v in [g.c,*g.a.entries()]])
    base_remainders = arb_mat(124,1,[g.r for g in block.residuals])
    forcing=[];coupling=arb_mat(124,124);details=[]
    for column in range(125):
        raw = arb_mat(125,dim+1,[m[i,column] for m,r in residuals for i in range(dim+1)])
        coefficients = P*raw
        target = arb_mat(124,124,[coefficients[j,i+1] for i in block.indices for j in range(124)])
        beta = (block.point_inverse_transpose*target).mid()
        coefficients -= beta.transpose()*base_coefficients
        tail = arb_mat(124,124,[abs(v).upper() for v in beta.transpose().entries()])*base_remainders
        values=[]
        for i in range(124):
            constant = coefficients[i,0] - (arb(i==column-1) if column else 0)
            support = (abs(constant).upper()
                +linear_support([coefficients[i,j+1] for j in range(dim)],domain.groups)+tail[i,0]).upper()
            if column: coupling[i,column-1]=support
            else: forcing.append((support+remainder[i,0]).upper())
            values.append(support)
        details.append(dict(column=column,maximum=upper(max(values)),base_tail=upper(max(tail.entries()))))
        print(json.dumps(dict(stage='majorant_column',column=column,maximum=float(max(values)))),flush=True)
    refined = intersect_majorant(initial, forcing, coupling, iterations=64)
    if {k:saved.sha(v) for k,v in guarded.items()} != hashes:
        raise ValueError('all sources must remain immutable throughout refinement')
    result = dict(algorithm='LONGITUDINAL_DIRECTIONAL_ERROR_RESIDUAL_INTERSECTION_V2',family=record['family'],
        selected_equations=selected,physical_axis_exact=[str(v.fmpq()) for v in axis.entries()],
        original_axis_error_bounds=[upper(v) for v in initial],refined_axis_error_bounds=[upper(v) for v in refined],
        forcing=[upper(v) for v in forcing],coupling=[[upper(coupling[i,j]) for j in range(124)] for i in range(124)],
        iterations=64,strictly_improved_coordinates=sum(bool(b<a) for a,b in zip(initial,refined,strict=True)),
        largest_initial_bound=upper(max(initial)),largest_refined_bound=upper(max(refined)),
        every_iteration_preserves_original_solution_graph=True,original_physical_domain_unchanged=True,
        base_residual_remainders_included=True,directional_residual_remainders_included=True,
        derived_multiplier_identity='psi^T G2 = psi_u^T G0 + psi_u[61]*||psi||^2 + slope*(1-||psi||^2)',
        original_state_groups=record['original_state_groups'],column_diagnostics=details,
        source_hashes=verified['paired_source_hashes'],guarded_input_SHA256=hashes,
        full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    args.out.write_bytes(saved.encoded(result))
    print(json.dumps(dict(stage='DONE',improved=result['strictly_improved_coordinates'],
        old=float(max(initial)),new=float(max(refined)))),flush=True)


if __name__ == '__main__': main()
