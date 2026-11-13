"""Owned C2 leading-volume coefficient and actual finite coarea contacts.

This evaluates a component, not the full physical membrane coefficient.
The heat length remains symbolic: every numerical coefficient multiplies
ell_star**(-4). No physical boundary condition or common-length equality is
selected, and no previous field/source/heat-history campaign is rerun.
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
        raise FileExistsError('preserve the prior materialization')
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.aether_common_quantum_superdeterminant_v15_96 import graded_operator_ledger
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from bhsm.interface.muon_moving_geometric_action import _sqrt
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

    ledger = graded_operator_ledger()
    if ledger['gauge_transverse']['degeneracy_per_species'] != '2*(m^2-1)':
        raise ValueError('the owned transverse angular ledger changed')
    if ledger['Weyl']['degeneracy_per_species'] != '(n+1)*(n+2)':
        raise ValueError('the owned Weyl angular ledger changed')
    if ledger['Hubbard_Strattonovich']['degeneracy_per_species'] != 'm^2':
        raise ValueError('the owned HS angular ledger changed')
    leading = dict(
        transverse=ledger['gauge_transverse']['supertrace_sign']
            *ledger['gauge_transverse']['species']*2,
        Weyl=ledger['Weyl']['supertrace_sign']*ledger['Weyl']['species'],
        HS=ledger['Hubbard_Strattonovich']['supertrace_sign']
            *ledger['Hubbard_Strattonovich']['species'])
    if ledger['gauge_longitudinal_ghost']['net_supertrace_sign'] != 0:
        raise ValueError('the retained BRST-pair cancellation changed')
    effective = sum(leading.values())
    if effective != -20:
        raise ValueError('the exact retained C2 leading shell coefficient changed')
    k4 = -effective/(4*(4*np.pi)**2)
    if not np.isclose(k4, 5/(16*np.pi**2), rtol=0, atol=2e-17):
        raise ValueError('proper-time F4 conversion changed')

    folder='artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
    mdpath=folder+'/result.json'; arraypath=folder+'/application.npz'
    md=json.loads((root/mdpath).read_bytes())
    if sha256((root/arraypath).read_bytes()).hexdigest()!=md['numerical_sha256']:
        raise ValueError('historical real input changed')
    with np.load(root/arraypath, allow_pickle=False) as source:
        raw=np.concatenate((source['initial_independent_raw'][None],
                            source['stage_independent_raw']))
    if raw.ndim!=2 or raw.shape[1]!=268 or not np.isrealobj(raw) or not np.isfinite(raw).all():
        raise ValueError('the actual real initial/stage input is required without projection')
    names=['initial']+[f'stage_{j:04d}' for j in range(len(raw)-1)]
    rows=[]; arrays=dict(actual_raw268=raw)
    values=[]; gradients=[]; hessians=[]; completed=[]; omitted=[]
    for name, rr in zip(names, raw):
        w=intrinsic_m4_weight_jet(12, rr[:37], rr[37:74], rr[74:98],
            source_value=rr[98], source_rate=rr[99])
        A, B = w['fields']['A'], w['fields']['B']
        L = _sqrt(A*A+B*B)
        coarea = (A*B)**3-w['R4']**3*L**3
        area = -w['induced_lapse']*(A*B)**3
        # Physical dmu7=dmu4 * VOLUME*L^3. Both actions are divided
        # by the same VOLUME^2 in the retained reduced cap equations.
        gamma7 = k4/(VOLUME*L**3)  # coefficient of ell_star**(-4), not gamma assigned at ell=1
        pulled_density = gamma7*area
        intrinsic_density = -k4*w['wV']/VOLUME
        residual = pulled_density-intrinsic_density
        held_gamma_gradient = gamma7.value*area.gradient
        missing_gradient = pulled_density.gradient-held_gamma_gradient
        values.append(gamma7.value); gradients.append(gamma7.gradient)
        hessians.append(gamma7.hessian)
        completed.append(pulled_density.gradient); omitted.append(missing_gradient)
        rows.append(dict(state=name,
            fibre_metric_length=float(L.value), quotient_radius=float(w['R4'].value),
            physical_fibre_volume=float(VOLUME*L.value**3),
            gamma7_coefficient_per_ell_star_minus4=float(gamma7.value),
            Lorentz_surface_density_coefficient_per_ell_star_minus4=float(pulled_density.value),
            coarea_polynomial_value_residual=float(coarea.value),
            coarea_polynomial_gradient_max_residual=float(np.max(abs(coarea.gradient))),
            coarea_polynomial_Hessian_max_residual=float(np.max(abs(coarea.hessian))),
            full_density_value_identity_residual=float(residual.value),
            full_density_gradient_identity_max_residual=float(np.max(abs(residual.gradient))),
            full_density_Hessian_identity_max_residual=float(np.max(abs(residual.hessian))),
            omitted_fibre_first_contact_norm_if_gamma7_held=float(np.linalg.norm(missing_gradient)),
            gamma7_geometry_gradient_norm_per_ell_star_minus4=float(np.linalg.norm(gamma7.gradient)),
            gamma7_geometry_Hessian_norm_per_ell_star_minus4=float(np.linalg.norm(gamma7.hessian))))
    arrays.update(gamma7_coefficient_per_ell_star_minus4=np.array(values),
        gamma7_geometry_gradients_per_ell_star_minus4=np.array(gradients),
        gamma7_geometry_Hessians_per_ell_star_minus4=np.array(hessians),
        Lorentz_density_gradients_per_ell_star_minus4=np.array(completed),
        omitted_fibre_first_contacts_if_gamma7_held=np.array(omitted))
    paths=[
        'src/bhsm/interface/aether_common_quantum_superdeterminant_v15_96.py',
        'src/bhsm/interface/aether_ae2_one_seam_descriptor.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py',
        'src/bhsm/interface/muon_moving_geometric_action.py',
        'src/bhsm/interface/muon_literal_euclidean_wall_action.py',
        'theory/n12_forward_brst_heat_tail_cancellation.md',
        'theory/n12_gate7_1222_core_diagram_matching_audit.md',
        mdpath, arraypath]
    result=dict(
        classification='OWNED_C2_LEADING_M4_VOLUME_COMPONENT_WITH_ACTUAL_FINITE_COAREA_JETS',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes={p:sha256((root/p).read_bytes()).hexdigest() for p in paths},
        declared_graded_angular_ledger=ledger,
        leading_shell_coefficients=leading,
        effective_C2_scalar_heat_density_coefficient=effective,
        effective_coefficient_is_not_a_claim_of_full_SM_fibre_rank=True,
        retired_periodic_domain_not_reused=True,
        coefficient_of_M4_volume_per_ell_star_minus4=float(k4),
        exact_M4_coefficient='5/(16*pi^2)',
        M4_coefficient_derivation='(-1/4)*(-20)/(4*pi)^2 from F4 and declared C2 proper-time principal heat density',
        required_local_principal_scope='same proper-time scalar/product-Dirac principal extension as the retained C2 ledger; not a completed interacting P_strat',
        coarea_identity='(A*B)^3=R4^3*L^3, L=sqrt(A^2+B^2), dmu7=dmu4*[Vol(S3_unit)*L^3]',
        mapped_M8_wall_coefficient='gamma7_component=[5/(32*pi^4)]*ell_star^(-4)*L^(-3)',
        shared_normalization='physical M4 and ambient-cap actions divided by the same Vol(S3_unit)^2; quotient factor retained once',
        direct_boundary_component='For local mixed D/Robin actual domain: -STr(chi)*ell_star^(-m)/[4*m*(4*pi)^(m/2)]. For matched transmittal leading a1 vanishes; no full stratified boundary condition selected here.',
        scale_contact_rule='For gamma7=K c^(-2)L^(-3), gamma7_a/gamma7=-2*c_a/c-3*L_a/L. Full E/B jets require actual cutoff and fibre jets; arrays hold symbolic c fixed.',
        double_count_guard='This is a component of the SAME Gamma_strat. Do not add it again if already represented by the intrinsic vacuum/scalar constant/area coefficient after matching and subtraction. No second matter determinant is introduced.',
        relative_reference_scope='This is the unsubtracted leading coefficient of the declared C2 ledger. A heat reference with identical leading local density cancels it in the relative heat difference. The actual common reference/subtraction prescription must be applied before claiming a net surface coefficient.',
        records=rows,
        numerical_ell_star_or_alpha_FSC_assigned=False,
        ell_s_equals_ell_star_assumed=False,
        physical_surface_gamma_derived=False,
        completed_physical_operator_domain=False,
        physical_outgoing_E_B_derivative_gate_passed=False,
        physical_muon_moment=None,coupled_matching_corrections=0,
        source_profile_D5_history_or_graded_heat_campaign_replayed=False,
        precision_scope='exact coefficient/coarea algebra evaluated in binary64 on saved real geometry; no physical continuum error enclosure')
    out.mkdir(parents=True)
    _compressed_npz(out/'coarea_component.npz', arrays)
    result['array_archive_sha256']=sha256((out/'coarea_component.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(effective_C2_coefficient=effective,k4=float(k4),records=rows),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();evaluate(a.repository,a.output)
