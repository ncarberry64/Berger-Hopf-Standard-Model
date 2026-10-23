"""Full partial metric stress distinguishes quotient volume from cap tension.

Read the actual retained real geometry. Evaluate an off-shell configuration
direction holding quotient radius and induced lapse fixed to first order,
but changing fiber length. This is not a physical constraint-solution family
and holds the independent c and ell_s arguments fixed only for this partial
coefficient comparison. No action coefficient, quiet state or exterior is
selected and no matching correction is applied.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def evaluate(repository, output):
    import numpy as np
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError('preserve previous actual applications')
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from bhsm.interface.muon_moving_geometric_action import _sqrt
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    folder='artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
    mdpath=folder+'/result.json'; data=folder+'/application.npz'
    md=json.loads((root/mdpath).read_bytes())
    if sha256((root/data).read_bytes()).hexdigest()!=md['numerical_sha256']:
        raise ValueError('actual retained input changed')
    with np.load(root/data, allow_pickle=False) as archive:
        raw=np.concatenate((archive['initial_independent_raw'][None],
                            archive['stage_independent_raw']))
    if not np.isrealobj(raw) or raw.shape[1]!=268 or not np.isfinite(raw).all():
        raise ValueError('actual real raw268 values required without projection')
    K4=5/(16*np.pi**2)
    allowed=np.r_[np.arange(37),np.arange(74,98)]
    rows=[]; directions=[]; covectors=[]
    for index, rr in enumerate(raw):
        w=intrinsic_m4_weight_jet(12, rr[:37],rr[37:74],rr[74:98],
            source_value=rr[98],source_rate=rr[99])
        A, B = w['fields']['A'],w['fields']['B']
        L=_sqrt(A*A+B*B); R=w['R4']; N=w['induced_lapse']
        gL=L.gradient/L.value; gR=R.gradient/R.value; gN=N.gradient/N.value
        C=np.array([gR[allowed],gN[allowed]])
        if np.linalg.matrix_rank(C)!=2:
            raise ValueError('two independent held metric coefficients required')
        transverse=gL[allowed]-C.T@np.linalg.solve(C@C.T,C@gL[allowed])
        norm=float(np.linalg.norm(transverse))
        if norm<=1e-8:
            raise ValueError('this actual chart has no resolved independent vertical direction')
        direction=np.zeros(100); direction[allowed]=transverse/norm
        # Signed Lorentz local coefficients, all multiplying ell_star^-4.
        area=-N*(A*B)**3
        mapped_gamma=K4/(VOLUME*L**3)
        intrinsic=-K4*w['wV']/VOLUME
        actual=mapped_gamma*area
        # The held coefficient here is matched ONLY at this one point.
        # Its variation is exactly what a constant ambient area term gives.
        constant_ambient=mapped_gamma.value*area
        scalar_trace_contrast=constant_ambient.gradient-actual.gradient
        delta_l=float(gL@direction)
        value=float(intrinsic.value)
        full_d=float(actual.gradient@direction)
        held_d=float(constant_ambient.gradient@direction)
        predicted=3*value*delta_l
        rows.append(dict(state='initial' if index==0 else f'stage_{index-1:04d}',
            quotient_radius=float(R.value),fibre_length=float(L.value),lapse=float(N.value),
            permitted_offshell_coordinate_count=len(allowed),
            direction_norm=float(np.linalg.norm(direction)),
            partial_log_radius_direction=float(gR@direction),
            partial_log_lapse_direction=float(gN@direction),
            partial_log_fibre_direction=delta_l,
            directional_C2_volume_action_per_ell_star_minus4=full_d,
            directional_matched_constant_ambient_area_per_ell_star_minus4=held_d,
            predicted_constant_area_vertical_direction_per_ell_star_minus4=predicted,
            constant_area_vertical_formula_residual=held_d-predicted,
            coefficient_value_match_residual=float(constant_ambient.value-actual.value),
            nonzero_full_partial_stress_contrast_norm_per_ell_star_minus4=float(np.linalg.norm(scalar_trace_contrast)),
            heldR_lapse_quotient_zeta_shape_direction=float((gN-gR)@direction)))
        directions.append(direction)
        covectors.append(np.array([actual.gradient,constant_ambient.gradient,scalar_trace_contrast]))
    arrays=dict(actual_real_raw268=raw,coordinate_directions=np.array(directions),
        signed_action_covectors_per_ell_star_minus4=np.array(covectors))
    source_paths=[
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/muon_literal_euclidean_wall_action.py',
        'src/bhsm/interface/forward_finite_endpoint_heat_force.py',
        'src/bhsm/interface/aether_replacement_geometry_force_v16_06.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        mdpath,data]
    result=dict(classification='ACTUAL_OFFSHELL_VERTICAL_METRIC_STRESS_CONTRAST_AT_FIXED_C_AND_ENVIRONMENTAL_LENGTH',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in source_paths},
        records=rows,
        physical_gamma_or_ell_star_assigned=False,
        ell_s_equals_ell_star_assumed=False,
        partial_scope='c and ell_s are held independent arguments for this metric-coefficient comparison; this is not their total physical branch derivative',
        allowed_direction_scope='off-shell retained q37 and lapse/shift m24 configuration chart; velocities and normal source/rate held. No full constraint-family existence claim.',
        stress_interpretation='C2 volume component has no vertical pressure at fixed quotient radius/lapse/c; a value-matched constant ambient tension has nonzero vertical pressure. Geometry-dependent coarea coefficient cancels that response.',
        actual_reference_owner='replacement_heat_minus_zeta_force computes Gamma_heat-Gamma_SM_zeta, not an arbitrary identical-operator heat subtraction. Zeta shape density is proportional to -lapse/R4.',
        fixed_c_reference_scale_powers=dict(C2_leading_volume_log_radius=3,
            removed_zeta_shape_log_radius=-1),
        reference_scope='These distinct fixed-c local scaling powers do not cancel the leading volume coefficient as a universal area subtraction. Total native cutoff and duration motion can change particular contractions and must be retained.',
        constitutive_compatibility_if_a0_were_entire_gamma='alpha_FSC=[5/(32*pi^4)]*ell_s^7*ell_star^-4*L^-3; constant alpha then requires 7 dlog ell_s=4 dlog ell_star+3 dlog L. Not an adopted identity or full-gamma closure.',
        constitutive_native_equations_do_not_add_alpha_variation='gamma=alpha_FSC ell_s^-7 and c=i(gamma,X)/r(gamma,X) define gamma,c for supplied alpha,ell_s,X where regular; field stationarity is not variation over alpha. No theorem of physical solution multiplicity is asserted.',
        full_surface_coefficient_determined=False,
        physical_outgoing_derivative_passed=False,
        physical_two_spin_residues=None,muon_magnetic_moment=None,
        coupled_matching_corrections=0,
        old_source_profile_D5_or_canonical_campaign_restarted=False,
        numerical_scope='binary64 analytic coefficient-jets and off-shell linear algebra at saved real states; not physical continuum or outgoing error enclosure')
    out.mkdir(parents=True)
    _compressed_npz(out/'vertical_stress_contrast.npz',arrays)
    result['array_archive_sha256']=sha256((out/'vertical_stress_contrast.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(rows,sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();evaluate(a.repository,a.output)
