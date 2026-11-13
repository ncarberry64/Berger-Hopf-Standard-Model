"""Actual D5 characteristic obstruction and executable affine graph E-jets.

No exterior is invented or integrated.  The generic graph RHS requires every
coefficient/forcing jet and a radiation-selected graph before it can be run.
"""
from pathlib import Path
from hashlib import sha256
from math import comb
import argparse
import json
import sys


def affine_outgoing_graph_energy_rhs(operator_jets, graph_jets, forcing_jets, affine_jets):
    """s-derivatives of R,R_E,R_EE and r,r_E,r_EE in v=R u+r.

    (u,v)_s=Q(E)(u,v)+f(E), Q=[[A,B],[C,D]]. Derivative
    arrays are literal derivatives, not Taylor coefficients. All products
    retain their order and use the analytic chart without conjugation.
    This is an application API, not a choice of physical exterior data.
    """
    import numpy as np
    Q,R,F,r=([np.asarray(x,complex) for x in a] for a in
             (operator_jets,graph_jets,forcing_jets,affine_jets))
    if any(len(a)!=3 for a in (Q,R,F,r)):
        raise ValueError('value, E and EE derivatives of all four operands are required')
    if R[0].ndim!=2 or r[0].ndim!=2:
        raise ValueError('matrix graph and affine source columns required')
    m,n=R[0].shape;k=r[0].shape[1]
    if min(m,n,k)<1 or any(a.shape!=shape or not np.isfinite(a).all()
       for group,shape in ((Q,(n+m,n+m)),(R,(m,n)),(F,(n+m,k)),(r,(m,k))) for a in group):
        raise ValueError('complete finite compatible operator/graph/forcing/affine jets required')
    A,B,C,D=([q[:n,:n] for q in Q],[q[:n,n:] for q in Q],
             [q[n:,:n] for q in Q],[q[n:,n:] for q in Q])
    fp,fm=[f[:n] for f in F],[f[n:] for f in F]
    def product2(x,y,order):
        return sum((comb(order,i)*(x[i]@y[order-i]) for i in range(order+1)),
                   np.zeros((x[0].shape[0],y[0].shape[1]),complex))
    BR=[product2(B,R,j) for j in range(3)]
    Br=[product2(B,r,j) for j in range(3)]
    dR=[C[j]+product2(D,R,j)-product2(R,A,j)-product2(R,BR,j) for j in range(3)]
    dr=[product2(D,r,j)-product2(R,Br,j)+fm[j]-product2(R,fp,j) for j in range(3)]
    return dR,dr


def run(repository, output):
    import numpy as np
    from flint import acb, acb_mat, arb, ctx
    root,out=Path(repository).resolve(),Path(output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(root/'src'));ctx.prec=192
    pins={};sources={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def source(name,filename,needles):
        p=root/'src/bhsm/interface'/filename;lines=p.read_text(encoding='utf8').splitlines()
        pins[str(p)]=sha256(p.read_bytes()).hexdigest();matches={}
        for needle in needles:
            ids=[i+1 for i,line in enumerate(lines)if needle in line]
            if not ids:raise ValueError('Original provider contract changed: '+needle)
            matches[needle]=ids
        sources[name]=dict(path=str(p),sha256=pins[str(p)],lines=matches)
    source('actual_first_order_action','muon_holomorphic_d5_trace_action.py',[
        'not turn a temporal Volterra trace into a field exterior',
        'def principal_normal_point_trace','def d5_unsquared_weak_trace',
        'does not select an exterior at the material wall'])
    source('full_spin_trace','muon_full_d5_localized_lepton_trace.py',[
        'dimension128','normal_operator_rule=','normal_mode_overlap_or_exterior_evaluated=False'])
    source('causal_prefix','muon_joined_d5_causal_tail_action.py',[
        'actual_final_field_remainder=states[-1]','physical_outgoing_annihilator_or_normalization_selected=False'])
    source('tail_schur_requires_domain','muon_retarded_spinor_tail_jet.py',[
        'caller supplies the child block','H_cp remains','def retarded_spinor_tail_two_jet'])
    source('finite_history_limit','muon_sigma_normal_collar_transport.py',[
        'outside actual canonical history','No partial integral is substituted'])
    source('annihilator_is_a_validator','muon_unsquared_physical_boundary_pole.py',[
        'does not construct a spectral projector','C(E)V(E)=0'])
    source('stop_conditional','ae4_current_c2_canonical_stop_domain_bridge.py',[
        'selected = all(conditions.values())','physical_stop_matched_operator_path_evaluated'])
    source('relative_future','ae4_future_collapse_relative_boundary_domain.py',[
        'omega_to_omega+i0_FROM_Im_omega>0','FUTURE_RETARDED_REGULARITY_OR_OUTGOING_SUPPORT_ONLY'])
    mdpath=root/'artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2'
    md=read(mdpath/'result.json')
    if md['retarded_field_exterior_or_complete_sigma_flow_normalization_realized']:
        raise ValueError('This obstruction must be reconsidered against the realized exterior')
    def mat(a):return acb_mat([[acb(arb(float(v.real)),arb(float(v.imag)))for v in row]for row in a])
    def maxupper(a):
        return max(float(np.nextafter(float(abs(a[i,j]).upper()),np.inf)) for i in range(a.nrows())for j in range(a.ncols()))
    def lower(v):return float(np.nextafter(float(v.lower()),-np.inf))
    def gram_rank_bound(x):
        gram=x.conjugate().transpose()*x
        gmin=min(gram[i,i].real-sum((abs(gram[i,j])for j in range(gram.ncols())if j!=i),arb(0))for i in range(gram.nrows()))
        if not gmin>0:raise ArithmeticError('Reached characteristic image did not certify all six columns')
        return dict(frozen_input_Gram_eigenvalue_strict_lower=lower(gmin),
                    frozen_input_singular_value_strict_lower=lower(gmin.sqrt()),
                    independent_reached_columns=gram.nrows())
    records=[];I=acb_mat(np.eye(128).tolist());fi=np.array([2,3,8,9,14,15]);amb=np.arange(128,256)
    for stage in range(2):
        z=read(mdpath/f'stage_{stage:04d}_current_geometry_normal_and_material_trace.npz')
        for sheet in('plus','minus'):
            T=mat(z[f'eta_{sheet}_original_principal_time_Clifford128'])
            N=mat(z[f'eta_{sheet}_original_principal_normal_Clifford128'])
            V=mat(z[f'eta_{sheet}_normal_mode_right_point_lift'][np.ix_(amb,fi)])
            A=T*N;P=[(I+A)/2,(I-A)/2]
            images=[p*V for p in P]
            rows=dict(time_square=maxupper(T*T-I),normal_square=maxupper(N*N+I),
                time_normal_anticommutator=maxupper(T*N+N*T),characteristic_square=maxupper(A*A-I),
                characteristic_reconstruction=maxupper(images[0]+images[1]-V))
            records.append(dict(stage=stage,sheet=sheet,actual_material_velocity=[float(z[f'eta_{sheet}_actual_material_velocity'].real),float(z[f'eta_{sheet}_actual_material_velocity'].imag)],
                original_full_carrier_dimension_per_family=128,analytic_Clifford_characteristic_dimensions=[64,64],
                reached_intrinsic_family_C6_indices=fi.tolist(),characteristic_image_rank_bounds=[gram_rank_bound(x)for x in images],
                exact_stored_B64_Clifford_identity_error_upper=rows,
                physical_outgoing_annihilator_selected=False,
                interpretation='Both analytic local characteristic images have full six-column rank. Neither local image vanishes on the supplied C6 trace; selecting one by deletion would add an unproved boundary law. On this complex germ these are not Hilbert-positive flux/frequency projectors.'))
    flow=read(root/'artifacts/muon_sigma_normal_collar_transport_20261012/trial_0000_run_2/result.json')
    prefix=read(root/'artifacts/muon_joined_d5_causal_tail_action_20261013/run_2/result.json')
    flow_end=[dict(status=x['status'],normal_length=x['s_end'],coordinate_time_end=x['coordinate_time_end'],
                   rho_end=x['rho_end'],partial_mode_norm=x['actual_partial_mode_norm'],
                   partial_not_full_normalization=x['partial_integral_not_full_mode_normalization'],
                   largest_complex_interpolation_face_raw_jump=max(c['complex_face_raw_jump_norm']for c in x['interpolation_corners']))for x in flow['normal_prefixes']]
    result=dict(classification='EVALUATED_SAME_ACTION_POINT_CHARACTERISTIC_OBSTRUCTION_TO_SELECTING_PHYSICAL_OUTGOING_E_JETS',
        records=records,source_citations=sources,input_hashes=pins,
        actual_existing_tail_limit=dict(normal_flow_prefixes=flow_end,
            actual_finite_causal_final_field_remainder_norm=prefix['actual_final_field_remainder_norm'],
            physical_drive_and_retarded_annihilator_unassigned_not_zero=prefix['physical_body_drive_and_retarded_exterior_annihilator_unassigned_not_zero'],
            interpretation='The actual normal flow reaches a supplied canonical-time face near the original wall, not an exterior/radiation endpoint. Prefix integrals cannot normalize the full mode; complex interpolation face returns are retained. The independent finite D5 prefix has a nonzero final field remainder.'),
        exact_first_missing_action_application=dict(
            operator='D(E)=A_n(s)*partial_s+A_parallel(s,E); Q_ext=-A_n^(-1)*A_parallel in an explicitly transported full characteristic frame, retaining connection/frame derivative contacts.',
            smallest_unavailable_mixing_application='Q_minus_plus_ext(s,E) Y_plus(s,E) outside the supplied canonical history/collar, on the actual reached columns; its E derivative is also unbound. Even this one action block cannot be inferred from point principal matrices or finite interior Schur data.',
            required_physical_field='Actual continuation of the exterior metric/coframe (N,C,R,shift and spin connection), gauge connection and sigma/eta density/mode on the connected field stratum. Intrinsic fixed-Y Higgs remains its once-only seam action. Existing cap/source polynomials are not exterior solutions.',
            radiation_selector='Same-action retarded/outgoing or actual certified stop endpoint, including encountered transmission/reset trace and prescribed incoming/source support. No separate CAR covariance is required for a fixed free retarded operator; surviving state-dependent bilinears have their own state inputs.',
            no_data_free_uniqueness='The boundary graph at the cut depends on Q_ext over its remaining interval and the endpoint radiation subspace. Its value and E derivative are not fixed by the finite endpoint coefficient jet. This is absence of a specified exterior field application, not evidence for adding a fitted loss.'),
        executable_boundary_dependencies=dict(
            affine_normal_equation='u_s=A u+B v+f_plus; v_s=C u+D v+f_minus; v=R(E)u+r(E)',
            graph_equation='R_s=C+D R-R A-R B R',affine_equation='r_s=(D-R B)r+f_minus-R f_plus',
            energy_jets='The exported affine_outgoing_graph_energy_rhs requires Q,Q_E,Q_EE; R,R_E,R_EE; f,f_E,f_EE; r,r_E,r_EE. It evaluates ordered product rules without conjugation, projection or unused third tensors. Physical IVP not executed because Q_ext and its radiation germ are not bound.',
            annihilator='In a supplied fixed graph frame C_out=(-R,I); C_out,E=(-R_E,0), C_out,EE=(-R_EE,0). In a moving full trace chart all chart jets must be included by product rule; these expressions are dependencies, not evaluated Bi/Bf.',
            boundary_composition='Gamma=Bi(E)+Bf(E)U(E); Gamma_E=Bi_E+Bf_E U+Bf U_E. Bi/Bf come from the actual initial/final allowed trace relation and transmission, not from a chosen local Hamiltonian eigenspace.',
            reached_only_minimum='It suffices to evaluate Bi R_pole+Bf(U R_pole), their E jets, and independent literal-left pairings on action-selected pole/range columns; a dense exterior inverse is unnecessary. The pole columns themselves are not supplied by this local characteristic check.',
            physical_Bi=None,physical_Bf=None,physical_Bi_E=None,physical_Bf_E=None),
        conditional_stop_limit='The canonical-stop provider requires certified exact transverse first hit, an owned endpoint/open stop stratum and Friedrichs hypothesis. It closes a retained nonnegative squared form conditionally, not an arbitrary unsquared first-order finite cut. None of these conditions is inferred from the last saved point.',
        claim_scope='New exact-stored coefficient arithmetic checks and a generic conditional RHS only. Original upstream geometry/source/continuum errors are not enclosed. Full spin/carrier terms are retained; no exterior zero, reflection, terminal zero or fitted loss is selected.',
        new_physical_integrations=0,physical_exterior_constructed=False,physical_pole_or_F2=None,
        full_physical_terminal_source_domain_derivative_admitted=False,matching_corrections_applied=0,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(dict(result=str(out/'result.json'),sha256=sha256((out/'result.json').read_bytes()).hexdigest(),
        minimum_reached_characteristic_singular_lower=min(c['frozen_input_singular_value_strict_lower']for a in records for c in a['characteristic_image_rank_bounds']))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.output)
