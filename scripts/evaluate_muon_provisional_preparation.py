"""Execute a restricted packet/Gauss Picard iterate, retaining absolute defects.

The constant-angular continuation component is not the adopted Gaussian beam.
It consumes the current inherited iterate without replaying earlier solves.
"""
from __future__ import annotations

import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT)]
from bhsm.interface.muon_provisional_packet_gauss import (
    sign_projected_constant_sections, evaluate_constant_packet,
    solve_temporal_difference,
)
from bhsm.interface.muon_coupled_reference_replacement import (
    _geometry_fields, assemble_known_coupled, MULTIPLIER_ROWS,
)
from bhsm.interface.muon_adopted_incoming_reference import stationary_parent_field_realization
from bhsm.interface.muon_stationary_native_reference_load import field_pullback, lorentz_load, factor_twojet
from bhsm.interface.muon_incoming_comparison_time_lift import causal_comparison_coefficients
from bhsm.interface.muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_primal_electromagnetic_source import higgs_aligned_charge
from bhsm.interface.muon_prepared_weak_gauss_dressing import _annihilators4
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.retained_response.finite_time_response import write_npz

SOURCE = 'artifacts/muon_stationary_native_reference_load_20261019/run_5/native_reference_load.npz'
PAIR = 'artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation/actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz'
PREPARATION = 'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'
HBARC_GEV_FM = 0.1973269804593025


def maximum(a):
    return float(np.max(abs(a))) if np.size(a) else 0.


def hamiltonian(theta):
    """Original causal application, independently of the native heat spectrum."""
    G = lepton_unit_trace_gauge_representation()['generators']
    connection = np.empty((1, 4, 18, 18), complex)
    connection[0, 0] = np.einsum('c,cij->ij', theta[2:6]/theta[1], G)
    connection[0, 1:] = np.einsum('ac,cij->aij', theta[6:18].reshape(3, 4), G)
    H = theta[18:20]+1j*theta[20:22]
    return canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1, 3, 18, 18)), H=H[None],
        R4=theta[0], gauge_connection=connection)['hamiltonian_map'][0]


def pair_action_cotangent(theta, theta_gradient, section):
    """Partial original action variation at fixed canonical field/clock data.

    In coordinate time S=chi^dag i partial_t chi-chi^dag(N_ind h)chi.
    Differentiating the state itself here would double count the source.
    """
    causal = causal_comparison_coefficients(theta, theta_gradient)
    U = section['particle_modes'][0]*np.sqrt(2*np.pi**2)
    V = section['antiparticle_modes'][0]*np.sqrt(2*np.pi**2)
    D = .5*(U@U.conj().T-V@V.conj().T)
    h, hx = causal['H'], causal['H_source']
    gradient = -np.einsum('ab,kba->k', D,
        theta[1]*hx+theta_gradient[1, :, None, None]*h)
    if maximum(gradient.imag) > 1e-12:
        raise ArithmeticError('real action cotangent acquired an imaginary part')
    return gradient.real, D, causal


def run(output):
    if output.exists():
        raise FileExistsError('choose a fresh output; existing applications are preserved')
    with np.load(ROOT/SOURCE, allow_pickle=False) as z:
        saved = {k:z[k].copy() for k in z.files}
    with np.load(ROOT/PAIR, allow_pickle=False) as z:
        rho = z['pair_Fock_density16'].copy()
    x0 = saved['input_iterate151']
    theta0 = saved['actual_theta']
    raw = np.zeros(268)
    raw[:100] = _geometry_fields(x0)
    raw[100:180] = x0[62:142]
    raw[260:264] = x0[146:150]
    realization = stationary_parent_field_realization(raw, radial_points=48, enrich_temporal=True)
    seed = x0[62:146].copy()

    def packet(c):
        theta = theta0.copy()
        theta[2:6] = c[60:64]
        h = hamiltonian(theta)
        section = sign_projected_constant_sections(h, theta[18:20]+1j*theta[20:22])
        return theta, h, section, evaluate_constant_packet(section, pair_density=rho,
            annihilators=_annihilators4(), normalization_owner='chi_cap=R4^(3/2)psi/(2pi²); original cap action divided by(2pi²)^2 gives unit Haar CAR kinetic form; full normalized Y0')

    def load(c):
        return packet(c)[3]['integrated_material_At_source4']

    print('Executing coupled constant-angular sections and original temporal Gauss rows', flush=True)
    solved = solve_temporal_difference(realization, seed, load,
        continuation_strengths=tuple(2.**k for k in range(-12,1)))
    c = solved['coefficients']
    converged_c = solved['last_converged_coefficients']
    converged_source = load(converged_c)
    converged_rows = (realization['evaluate'](converged_c)['gradient']-
        realization['evaluate'](seed)['gradient'])
    converged_rows[60:64] += solved['achieved_continuation_strength']*converged_source
    x = x0.copy()
    x[62:146] = c
    theta, h, section, source = packet(c)
    pull = field_pullback(x)
    if maximum(pull['value']-theta) > 1e-12:
        raise ArithmeticError('wall and parent charts disagree')
    pair_gradient, D, causal = pair_action_cotangent(theta, pull['gradient'], section)
    q = higgs_aligned_charge(theta[18:20]+1j*theta[20:22], np.zeros(2, complex))
    charge = float(np.trace(D@q['charge']).real)
    temporal_identity = pair_gradient[62+np.arange(60,64)]-source['integrated_material_At_source4']

    # These are fresh original applications at the moved fields, never old arrays
    # relabelled as a new physical residual or a statistical state kernel.
    print('Evaluating original full known action rows at the new provisional iterate', flush=True)
    nodes, weights = leggauss(48)
    rho_nodes, radial_weights = WALL*(nodes+1)/2, WALL*weights/2
    known = assemble_known_coupled(x, rho=rho_nodes, radial_weights=radial_weights)
    print('Evaluating native0 component at the matching new fields and fixed numerical cutoff', flush=True)
    native = None
    native_application = dict(status='NOT_EVALUATED')
    try:
        native = lorentz_load(x, cutoff=1., points_per_panel=24)
        native_application = dict(status='EVALUATED_MATCHING_FIELDS_FIXED_NUMERICAL_CUTOFF',
            value=float(native['value']))
    except ArithmeticError as error:
        factors = factor_twojet(theta)
        w, omega = factors['W'][0], factors['Omega'][0]
        lower = 1/np.linalg.norm(np.linalg.solve(w,np.eye(18)))
        b = np.linalg.norm(omega)
        comm = np.linalg.norm(w@(-1j*omega)-(-1j*omega)@w)
        native_application = dict(status='ORIGINAL_CONTINUATION_BOUND_NOT_ESTABLISHED',
            exception=str(error), W_gap_lower=float(lower), Omega_Frobenius=float(b),
            commutator_Frobenius=float(comm), uniform_delta=float(lower**2-3*b*b-comm),
            interpretation='failure of this sufficient native continuation bound; neither nonexistence nor a statistical-state determination; old native force not substituted')
    partial = known['known_gradient']+pair_gradient
    if native is not None:
        partial = partial+native['gradient']
    classical = realization['evaluate'](c)
    fine_evaluate = stationary_parent_field_realization(raw, radial_points=96, enrich_temporal=True)['evaluate']
    fine, fine_seed = fine_evaluate(c), fine_evaluate(seed)
    gauss_fine = fine['gradient'][solved['temporal_indices']]-fine_seed['gradient'][solved['temporal_indices']]
    insertion = np.zeros((84,4)); insertion[60:64] = np.eye(4)
    gauss_fine += insertion[solved['temporal_indices']]@source['integrated_material_At_source4']

    # Independent time application: symmetric differences of exp(-i h tau),
    # compared to original Hamiltonian maps at an actual nonzero proper time.
    F0 = np.concatenate((section['particle_modes'][0], section['antiparticle_modes'][0]), axis=1)
    tau, dt = .125, 2e-5
    Ft = expm(-1j*h*tau)@F0
    fplus, fminus = expm(-1j*h*(tau+dt))@F0, expm(-1j*h*(tau-dt))@F0
    time_rows = 1j*(fplus-fminus)/(2*dt)-h@Ft
    evolved_D = expm(-1j*h*tau)@D@expm(1j*h*tau)
    G = lepton_unit_trace_gauge_representation()['generators']
    evolved_source = np.einsum('ab,cba->c', evolved_D, 1j*G).real

    # A declared symmetric TEST incidence only: X^i=L n_i on the round S3.
    # This is not the unknown physical collider-to-Cauchy map. Haar symmetry
    # gives <n_i>=0 and <n_i^2>=1/4 exactly for these constant sections.
    L = float(theta[0]*HBARC_GEV_FM/np.exp(x[-1]))
    Cu, Cv = section['particle_modes'][0]*np.sqrt(2*np.pi**2), section['antiparticle_modes'][0]*np.sqrt(2*np.pi**2)
    energies_u = np.diag(Cu.conj().T@h@Cu).real*np.exp(x[-1])*1000
    energies_v = -np.diag(Cv.conj().T@h@Cv).real*np.exp(x[-1])*1000
    full84 = classical['gradient'].copy()
    full84[60:64] += source['integrated_material_At_source4']
    arrays = dict(input_iterate151=x0, provisional_iterate151=x,
        input_theta22=theta0, provisional_theta22=theta,
        particle_modes=section['particle_modes'], antiparticle_modes=section['antiparticle_modes'],
        proper_time_evolved_sections18x4=Ft, proper_time_original_rows18x4=time_rows,
        canonical_pair_difference18x18=D, original_H18=h,
        original_action_pair_gradient151=pair_gradient,
        material_source_density4=source['lepton_material_At_action_source_density'], integrated_material_source4=source['integrated_material_At_source4'],
        evolved_integrated_material_source4=evolved_source,
        original_classical_rows84=classical['gradient'], original_classical_plus_pair_rows84=full84,
        original_known_rows151=known['original_gradient'], known_subtotal_rows151=known['known_gradient'],
        partial_available_known_pair_rows151=partial,
        absolute_partial_temporal_rows20=partial[62+solved['temporal_indices']],
        gauss_difference_rows20=solved['temporal_original_difference_rows'], higher_quadrature_gauss_difference_rows20=gauss_fine,
        gauss_last_attempted_strength_difference_rows20=solved['temporal_last_attempted_difference_rows'],
        temporal_indices20=solved['temporal_indices'],
        last_converged_coefficients84=converged_c,
        last_converged_integrated_material_source4=converged_source,
        last_converged_gauss_difference_rows20=converged_rows[solved['temporal_indices']],
        original_charge_exchange18x18=1j*(h@q['charge']-q['charge']@h),
        required_physical_calibration_coefficient=np.array(known['required_cF']),
        energy_initializer_particle_MeV=energies_u, energy_initializer_antiparticle_MeV=energies_v)
    if native is not None:
        arrays['matching_native0_gradient151'] = native['gradient']
        arrays['native0_response_from_seed151'] = native['gradient']-saved['actual_gradient']
    output.mkdir(parents=True)
    path = output/'application.npz'
    write_npz(path, arrays)
    report = dict(schema='bhsm.provisional-packet-gauss.v1',
        classification='EXECUTED_RESTRICTED_CONSTANT_ANGULAR_COUPLED_PREPARATION_PICARD_ITERATE',
        physical_admission=False, physical_guard=2e-10,
        preparation='fixed500MeV/beam,100fm per-axisRMS,centers+-1000fm unchanged; the following continuation initializer does not achieve it',
        executed_equations=dict(section='U=Y0 Pplus S (Sdag Pplus S)^(-1/2), V=Y0 Pminus S (Sdag Pminus S)^(-1/2); S=(Sleft+Sright)/sqrt2 spin seeds, Y0=1/sqrt(2pi²), full electron-family6 signs',
            evolution='i partial_tau chi=[-i alpha^a(Ea+Aa)/R+1.5 gamma5/R+M_Y(H)-iAt/N]chi',
            source='j_c=1/2 sum_s(U_sdag iGc U_s-V_sdag iGc V_s); mu=1 for chi_cap=R4^(3/2)psi/(2pi²), cap action/S3volume²; canonical Haar CAR, no second volume factor',
            gauss='g_At(c)-g_At(c0)+t wall_trace^T integral_S3 j(c) dOmega=0, t:0->1; original Maxwell plus wall-Higgs derivative rows',
            frozen_remainder='Picard subproblem holds changes of native/complement/matched-state/domain/other-sector loads pending; neither their absolute values nor the seed full residual are assigned zero',
            original_action_cotangent='delta S_pair=-Tr[D_pair delta(N_ind h)] at fixed canonical chi/time data; original temporal source checked separately'),
        boundary=dict(domain='complete right-body constant scalar harmonic times full18 on closed round S3; represented L2 Haar pairing; smooth H1 subdomain',
            parent='rho in [0,pi/2], original regular radial basis plus1-x^alpha temporal extension; all20 temporal coefficients vary including four wall values',
            held='inherited geometry62, Ar16, spatial gauge48, H4, scale initializer; their original residuals are retained',
            symmetry_test_incidence='X^i=L*n_i, L=R4*hbarc/exp(e), n on unitS3; this is only a test incidence, not the physical collider map',
            full_required_incidence='Gamma0 Psi5=u_R Splus W R4^(-3/2) chi_geom+Gamma0 chi_off; chi_geom=(2pi²)chi_cap. Normal profiles, normalization integral, physical collider pullback and complement remain separate'),
        initializer_moments=dict(achieved_total_Higgs_charge=charge,
            achieved_test_dipole_fm=0., adopted_dipole_target_fm=2000., test_dipole_defect_fm=-2000.,
            species_number_CAR_normalization=[1.,1.], test_centroids_fm=[[0.,0.,0.],[0.,0.,0.]],
            test_RMS_each_axis_fm=L/2, adopted_RMS_each_axis_fm=100., test_coordinate_radius_fm=L,
            mean_particle_energy_MeV=energies_u.tolist(), mean_antiparticle_energy_MeV=energies_v.tolist(),
            energy_unit_GeV=float(np.exp(x[-1])), scale_status='unadmitted inherited initializer; GF exp(2e)-cF remains independent',
            required_cF_at_initializer=float(known['required_cF'])),
        residuals=dict(gauss_difference20_max=maximum(solved['temporal_original_difference_rows']),
            higher_radial_quadrature_difference20_max=maximum(gauss_fine),
            source_cotangent_identity_max=maximum(temporal_identity),
            complete_represented_Cauchy_Gram_max=maximum(F0.conj().T@F0*(2*np.pi**2)-np.eye(4)),
            independent_Dirac_time_difference_max=maximum(time_rows),
            original_classical_plus_pair84_max=maximum(full84),
            absolute_partial_temporal20_max=maximum(partial[62+solved['temporal_indices']]),
            fresh_available_known_pair150_max=maximum(partial[:150]),
            available_subtotal_includes_matching_native0=native is not None,
            original_multiplier24_partial_max=maximum(partial[MULTIPLIER_ROWS]),
            original_Higgs4_partial_max=maximum(partial[146:150]),
            original_charge_exchange_operator_max=maximum(1j*(h@q['charge']-q['charge']@h)),
            original_charge_exchange_pair_contraction=float(np.trace(D@(1j*(h@q['charge']-q['charge']@h))).real)),
        continuation_status=solved['status'], continuation=solved['history'],
        achieved_continuation_strength=solved['achieved_continuation_strength'],
        last_converged_gauss_difference20_max=maximum(converged_rows[solved['temporal_indices']]),
        last_attempted_continuation_strength=solved['last_attempted_continuation_strength'],
        last_attempted_gauss_difference20_max=maximum(solved['temporal_last_attempted_difference_rows']),
        packet_derivative_failures=solved['packet_derivative_failures'],
        matching_native0_application=native_application,
        unresolved_contributions=dict(native_complement_domain_phase='d(Gamma_complement/domain/phase)',
            matched_state='dGamma_matched_state, includes consumed coincidence two-point relative to the same subtraction; no vacuum or Wick choice',
            retained_local_overlap='-dGamma_retained_local_overlap exactly once; no fraction assigned to native0',
            other_native_sectors='all angular and bosonic components outside recomputed native0',
            cutoff='c=1 here is a frozen numerical coordinate; physical c=I_total/R_total with its derivatives remains',
            boundary_normal_exterior='actual conormal/interface/exterior and domain terms',
            area='gamma*dS_area; gamma not set to zero',
            calibration='GF exp(2e)-cF[fields,normalized physical modes,domain]=0; cF application pending',
            state_boundary='C_ref,as^+ projected on consumed matched vertices, plus interacting mixed gauge/Higgs-fermion contractions where consumed; sign polarization and transport alone do not give that boundary value'),
        downstream='exclusive chronological two-point, inclusive contour four-point, complete matched occupation remain distinct; none computed by this packet source application',
        native_accounting='native0 attempted only at matching provisional fields, fixed numerical cutoff1; if its original continuation bound fails its load is excluded and individually unresolved. Effective-action load is not a statistical state kernel; saved seed force is never substituted',
        arrays=dict(path=path.name,sha256=sha256(path.read_bytes()).hexdigest()),
        inputs={rel:sha256((ROOT/rel).read_bytes()).hexdigest() for rel in (SOURCE,PAIR,PREPARATION)},
        executed_source={rel:sha256((ROOT/rel).read_bytes()).hexdigest() for rel in (
            'scripts/evaluate_muon_provisional_preparation.py','src/bhsm/interface/muon_provisional_packet_gauss.py')})
    (output/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(output=str(output),moments=report['initializer_moments'],residuals=report['residuals']),sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output.resolve())
