"""Current branch-23 local operands for the formation operator assembly.

Recenter retained sector laws at the saved current incoming reset state.
No local gradient is relabeled as the reduced history-action force.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_parent_sector_jets as sectors
from checkpoint_n12_gate7_66d_tangent_binding import digest, encoded, bound, restore
from differentiate_n12_gate7_fiber_constrained_center import save_arrays

BASE = ROOT/'artifacts/flagship_integration'
CANDIDATE = BASE/'gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz'
POINT = BASE/'gate7_current_formation_stationarity_20260927/run1'
FRAME = BASE/'gate7_formation_action_basis_20260928/run1'


def dependency_report():
    rows = [
        dict(operand='Current branch-23 local action sector values/derivatives',
             producer='derive_n12_gate7_parent_sector_jets.local_sectors + accumulate',
             expected_base='Explicit 98D state; old driver uses historical center_state[:98]',
             recenterable=True, recomputation='One current incoming point; existing spatial quadrature; project local Hessians onto saved Q66 only',
             history=['endpoint-only']),
        dict(operand='Current incoming x(tau), durations, coefficient and duration jets',
             producer='regularized branch-23 action field; arb_current_history_transport; aether_forward_boundary_radius',
             expected_base='Current branch-23 field/domain and owned incoming duration/amplitude family',
             recenterable=True, recomputation='New incoming family integration/implicit response; no node13/reset connection or C2 prefix integration',
             history=['finite integrated history','coefficient-history dependent','duration dependent']),
        dict(operand='Incoming Weyl/Calderon forms and their mixed contractions',
             producer='arb_weyl_first_pullback; aether_ae2_one_seam_descriptor; heat_zeta_mixed_boundary_launch.element_mixed',
             expected_base='Current incoming coefficient and duration family, not a historical radius germ',
             recenterable=True, recomputation='Stream incoming element contractions and glue to retained current child response once',
             history=['spectral-history dependent','contact-history dependent']),
        dict(operand='Joint graded heat-minus-zeta coefficient cotangent and mixed terms',
             producer='forward_finite_endpoint_heat_force; heat_zeta_mixed_boundary_launch',
             expected_base='Same current positive joint operator/domain and coefficient jets',
             recenterable=True, recomputation='Joint operator functional; no generic second operator tensor; maximal-tail scope must remain explicit',
             history=['spectral-history dependent','coefficient-history dependent','duration dependent']),
        dict(operand='Reduced q66, H66 and B66x73',
             producer='implicit_objective_adjoint / reduce_implicit_mixed; formation_stationarity_kkt',
             expected_base='Complete current internal residual/base, its inverse or owned quotient, and contracted objective derivatives',
             recenterable=True, recomputation='Same-action internal reduction then saved-frame contraction; no stationary solve before these exist',
             history=['finite integrated history','contact-history dependent'])]
    old = json.loads((BASE/'gate7_formation_action_basis_20260928/public_readiness.json').read_bytes())
    retention = [dict(path=row['path'], bytes=row['bytes'], SHA256=digest(ROOT/row['path']))
                 for row in old['checks']['hygiene']['unexpected_large_files']]
    return dict(base_commit='b994615e', target='CURRENT_INCOMING_FORMATION_HISTORY_OPERATOR_ASSEMBLY',
                dependencies=rows, retention_findings_not_scientific_blockers=retention,
                current_source_role='External E0 Dirichlet generating trace; one internal E1/C2 seam. Supersedes older dynamic birth-graph interpretation.',
                source_role_owner='theory/n12_gate7_external_birth_source_role_supersession.md',
                no_Q66_reset_connection_or_C2_prefix_recomputed=True)


def calculate(out):
    ctx.prec = 512
    metadata = json.loads((POINT/'report.json').read_bytes())
    hashes = {k.replace('\\','/'):v for k,v in metadata['source_SHA256'].items()}
    if digest(CANDIDATE) != hashes[CANDIDATE.relative_to(ROOT).as_posix()]:
        raise ValueError('current incoming candidate changed')
    if digest(POINT/'arrays.npz') != metadata['arrays_SHA256']:
        raise ValueError('current reset-point packet changed')
    frame_report = json.loads((FRAME/'report.json').read_bytes())
    if digest(FRAME/'arrays.npz') != frame_report['arrays_SHA256']:
        raise ValueError('frozen action frame changed')
    with np.load(CANDIDATE) as z:
        state = np.array([arb(float(v)) for v in z['joint_state_raw'][98:196]], dtype=object)
        weights = [arb(float(v)) for v in z['state_weights']]
    with np.load(FRAME/'arrays.npz') as z:
        Qraw = restore(z, 'Q66_current_raw')
    with np.load(POINT/'arrays.npz') as z:
        current = {k:restore(z, 'E1_'+k) for k in ('momentum','force','conormal','momentum_arc_derivative','rate')}
    A = sectors.A
    names = sectors.NAMES
    values = {name:arb(0) for name in names}
    gradients = {name:arb_mat(98,1) for name in names}
    curvatures = {name:arb_mat(66,66) for name in names}
    iv, ig, ih = arb(0), arb_mat(98,1), arb_mat(98,98)
    with sectors.r.center.sparse.use_optimized_mixed(A):
        for node in range(A.POINTS):
            base = A._integrand(state,node,0)
            terms, inertia = sectors.local_sectors(base,node)
            for name, term in zip(names[:6],terms):
                v,g,h = sectors.accumulate(term,base.maps)
                values[name] += v; gradients[name] += g
                curvatures[name] += Qraw.transpose()*h*Qraw
            v,g,h = sectors.accumulate(inertia,base.maps)
            iv += v; ig += g; ih += h
        coefficient = arb(0.25/(2*A.HOPF_ORBIT_VOLUME**2))
        values['hopf_inertia'] = -coefficient/iv
        gradients['hopf_inertia'] = coefficient*ig/iv**2
        curvatures['hopf_inertia'] = Qraw.transpose()*(coefficient*(ih/iv**2-2*ig*ig.transpose()/iv**3))*Qraw
        maps,boundary = A._boundary(state,2)
        v,g,h = sectors.accumulate(boundary,maps)
        for name,share in zip(names[7:],(arb(1)/118,arb(33)/59,arb(51)/118)):
            values[name] = v*share; gradients[name] = g*share
            curvatures[name] = share*(Qraw.transpose()*h*Qraw)
        print('Current branch-23 sectors evaluated; replaying original action',flush=True)
        with sectors.r.center.factored.use_ball_factored_integrand(A,state):
            owned = A._arb_action_jets(state)
            g_owner = sectors.r.mat(owned.gradient_arb[:,None])
            h_owner = Qraw.transpose()*sectors.r.mat(owned.hessian_arb)*Qraw
            value_owner = sectors.r.center.action_value(state)
    total_g = sum(gradients.values(),arb_mat(98,1))
    total_h = sum(curvatures.values(),arb_mat(66,66))
    replay = dict(value=arb_mat([[sum(values.values(),arb(0))-value_owner]]),
                  gradient=total_g-g_owner, local_Q66_Hessian=total_h-h_owner)
    if not all(v.contains(0) for m in replay.values() for v in m.entries()):
        raise ArithmeticError('recentered sector sum fails original action replay')
    signs = [arb((-1)**j) for j in range(12)]
    ub = sum((state[1+j]*(-signs[j]) for j in range(12)),arb(0))
    vb = sum((state[25+j]*signs[j] for j in range(12)),arb(0))
    x = (arb(float(A.RADIUS0))/2).log()+state[0]+ub-(2*vb).cosh().log()/2
    logN = sum((state[74+j]*(-signs[j]) for j in range(12)),arb(0))
    dx = arb_mat(1,98);dx[0,0]=1
    for j in range(12):dx[0,1+j]=-signs[j];dx[0,25+j]=-signs[j]*(2*vb).tanh()
    velocity = arb_mat(98,1,list(state[37:74])+[arb(0)]*61)
    proper_rate = (dx*velocity)[0,0]/logN.exp()
    data = dict(current_incoming_state_raw=state, local_action_value=arb_mat([[value_owner]]),
        local_action_gradient_raw=total_g, local_action_partial_66=Qraw.transpose()*total_g,
        local_action_curvature_66=total_h, incoming_log_R4=arb_mat([[x]]),
        incoming_log_R4_raw_covector=dx, incoming_log_R4_partial_66=dx*Qraw,
        incoming_lapse=arb_mat([[logN.exp()]]), incoming_proper_log_radius_rate=arb_mat([[proper_rate]]),
        unit_scalar_potential=arb_mat([[(-2*x).exp()]]), unit_Dirac_superpotential=arb_mat([[(-x).exp()]]))
    for name in names:
        data[name+'_local_value']=arb_mat([[values[name]]])
        data[name+'_local_gradient_raw']=gradients[name]
        data[name+'_local_partial_66']=Qraw.transpose()*gradients[name]
        data[name+'_local_curvature_66']=curvatures[name]
    data.update({'incoming_'+k:v for k,v in current.items()})
    out.mkdir(parents=True,exist_ok=False)
    save_arrays(out/'arrays.npz',data)
    sources = [Path(__file__),Path(sectors.__file__),Path(A.__file__),CANDIDATE,
               POINT/'arrays.npz',POINT/'report.json',FRAME/'arrays.npz',FRAME/'report.json',
               ROOT/'theory/n12_gate7_external_birth_source_role_supersession.md']
    report = dict(package='FORMATION_OP_CURRENT',status='CURRENT_ENDPOINT_OPERANDS_EVALUATED_HISTORY_OPERATOR_INCOMPLETE',
        base='Current reset-connected candidate joint_state_raw[98:196], incoming E1 branch23',
        base_point_scope='Exact saved binary64 point lifted to Arb512; not a stationary root or uniform history certificate',
        complete=False, history_member_selected=False, local_results_are_not_reduced_formation_derivatives=True,
        sectors={name:dict(local_value_mid=str(values[name].mid().fmpq()),
                          local_value_approx=float(values[name].mid()),
                          history_requirement='finite integrated history for Gamma_form; endpoint-only local density evaluated',
                          classification='ACTIVE' if not name.startswith('boundary_') else 'ALREADY_INCLUDED') for name in names},
        endpoint_geometry=dict(log_R4=float(x.mid()),proper_log_radius_rate=float(proper_rate.mid())),
        replay={k:bound(v) for k,v in replay.items()},
        local_curvature_symmetry=bound(total_h-total_h.transpose()),
        formation_action_covector_66=None,formation_physical_hessian_66x66=None,formation_launch_forcing_66x73=None,
        missing_operands=['Current incoming coefficient/duration family and its action-selected internal response',
            'Joint incoming/C2 spectral operator and signed graded heat-minus-zeta cotangent including retained contacts',
            'Current internal F_n and contracted objective/residual derivatives in incoming and launch directions'],
        retained_dynamic_flux='Current conormal, configuration force, and regularized momentum rate saved separately; physical DP[X] and complete flux remain unevaluated',
        Q66_recomputed=False,reset_rebuilt=False,C2_prefix_rerun=False,stationary_solve_attempted=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({'status':report['status'],'replay':{k:v['approximate_upper'] for k,v in report['replay'].items()},'endpoint_geometry':report['endpoint_geometry']},indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--inventory',type=Path);p.add_argument('--out',type=Path)
    args=p.parse_args()
    if args.inventory:
        args.inventory.parent.mkdir(parents=True,exist_ok=True)
        report=dependency_report();args.inventory.write_bytes(encoded(report));print(json.dumps(report,indent=2))
    elif args.out:calculate(args.out)
    else:p.error('--inventory or --out required')
