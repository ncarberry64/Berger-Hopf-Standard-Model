"""New source-space identifiability calculation; no old producer replay."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np


def read(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: np.array(z[k]) for k in z.files}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, payload):
    path.write_bytes((json.dumps(payload, indent=2, sort_keys=True,
                                allow_nan=False)+'\n').encode())


def inputs(root):
    a = root/'artifacts'
    return dict(
        point=a/'muon_retained_tail_core_20261005/run_1/points/node_03.npz',
        receipt=a/'muon_retained_tail_core_20261005/run_1/points/node_03.json',
        cut=a/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        wall=a/'muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz',
        green=a/'muon_joint_variational_attachment_20261005/run_2/node3_joint_known_variations.npz',
        matched=a/'muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz',
        ledger=a/'muon_connection_weight_20261001/representation_input.json',
        intrinsic=a/'action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json',
        premode=root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        action=root/'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
        owner=root/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        module=root/'src/bhsm/interface/muon_seam_offmode_identifiability.py',
        harmonic_product=root/'src/bhsm/interface/muon_matched_mechanical_source.py',
        gaunt=root/'src/bhsm/interface/muon_local_source_jet.py', script=Path(__file__).resolve())


def calculate(root):
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_seam_offmode_identifiability import (
        radial_witness, unit_higgs_coefficients, higgs_identity_residuals,
        evaluated_witness)
    refs = inputs(root)
    d = {k: read(refs[k]) for k in ('point', 'cut', 'wall', 'green', 'matched')}
    receipt = json.loads(refs['receipt'].read_text())
    # All scalar/source operands remain the original retained node3 values.
    b = receipt['attachment']['bulk_B']
    mu4 = float(d['wall']['M4'])
    radial = radial_witness(d['cut']['radial_weights'], d['point']['volume'],
                            d['point']['u'], d['point']['p'], b, mu4)
    radial['p'] = d['point']['p']
    basis = {n: d['wall'][f'normalized_wall_W_input_n{n}'] for n in (1, 3)}
    gamma0 = d['green']['Gamma'][0, ::16, ::16]
    h = unit_higgs_coefficients()
    match = higgs_identity_residuals(h, d['matched']['rotation_coefficients'])
    actions = evaluated_witness(basis, gamma0, radial['eta'], h, radial,
                                 d['cut']['radial_weights'], d['point']['volume'], mu4)
    return refs, d, receipt, radial, h, match, actions


def run(root, out, computed=None):
    if out.exists():
        raise FileExistsError('new output directory required')
    out.mkdir(parents=True)
    refs, d, receipt, radial, h, match, actions = computed or calculate(root)
    arrays = dict(h_scalar=radial['h'], chi_scalar=radial['chi'],
        eta=np.array(radial['eta']), eta_interval=radial['eta_interval'],
        unit_higgs_coefficients=h,
        gamma0=d['green']['Gamma'][0, ::16, ::16],
        source_coordinates=d['cut']['source_coordinates'],
        actual_state=d['point']['actual_state'], actual_Y_tau=d['point']['Y_tau'],
        geometric_bar_forward_pair=actions['forward_pair'],
        geometric_bar_reverse_pair=actions['reverse_pair'])
    for key in ('left', 'forward_h', 'e45', 'wall_test', 'reverse'):
        for n, value in actions[key].items():
            arrays[f'{key}_n{n}'] = value
    np.savez_compressed(out/'offmode_source_witness.npz', **arrays)
    result = dict(
        classification='conditional algebraic identifiability witness on actual retained source columns; NOT adopted attachment or native operator',
        node=3, action_arc=receipt['arc'], branch=receipt['first_action']['branch'],
        eta=radial['eta'], eta_frozen_nodal_interval=radial['eta_interval'].tolist(),
        eta_direct_binary64=radial['direct_binary64_eta'], h_max=radial['h_max'],
        projected_unit_higgs_source_norm=actions['unit_higgs_projected_source_norm'],
        proposed_E45_per_lambda_per_unit_YH_norm=float(np.sqrt(sum(
            np.linalg.norm(x)**2 for x in actions['e45'].values()))),
        proposed_reverse_connected_n5_norm=float(np.linalg.norm(actions['reverse'][5])),
        geometric_bar_pairing_absolute_residual=actions['reverse_bar_pairing_residual'],
        fundamental_higgs_matching=match,
        symbolic_lambda_value=None, Yukawa_or_Higgs_amplitude_inserted=False,
        physical_external_states_used=False, source_columns=12,
        forward_angular_levels=sorted(actions['e45']), reverse_angular_levels=sorted(actions['reverse']),
        original_source_contraction_norm=float(np.linalg.norm(
            actions['forward_pair']@d['cut']['source_coordinates'])),
        original_source_projected_image_norm=float(np.sqrt(sum(np.linalg.norm(
            x.reshape(-1, 12)@d['cut']['source_coordinates'])**2
            for x in actions['forward_h'].values()))),
        original_load_sensitivity_established=False,
        evaluated_reverse_role='distributed bulk Euler action with radial chi; NOT a boundary conormal',
        wall_field_map_or_joint_domain_adopted=False,
        n5_scope='evaluated cancellation on matched-image reverse tests only; not a resolvent tail theorem',
        actual_source_scope='b coordinate, original cached scalar p and n1/n3 independent source columns; no new Tb, sqrt(2), index2/3 or charge multiplier',
        conditional_W_B_gauge_intertwining_not_promoted=True,
        native_operator_updated=False, updated_coupled_solution=None,
        physical_a_mu=None, physical_g_mu=None, native_uncertainty=None,
        old_checks_repeated=0, old_production_repeated=0,
        error_scope='exact rational radial contraction of frozen dyadic inputs; binary64 harmonic products and bar-dual consistency control; no new continuum/quadrature/history/domain or physical bound')
    save(out/'result.json', result)
    save(out/'exact_nodal_eta.json', dict(
        numerator=radial['exact_eta_numerator'], denominator=radial['exact_eta_denominator'],
        formula='sum_i w_i volume_i p_i (p_i-b*u_i)/mu4',
        scope='frozen input floats interpreted exactly; inherited b and u not recertified'))
    save(out/'joint_equations.json', dict(
        adopted_premode='S5=sum_eps integral bar(Psi_eps) D5,eps Psi_eps; S_H=-integral [bar(Psi_+) YH Psi_-+h.c.]',
        adopted_intrinsic='w=(L_L,e_R) independent active wall unknowns; Euler_L=i slashD L-YH e; Euler_R=i slashD e-Hdag Ydag L',
        representation='L=(1,2,-1/2), e_R=(1,1,-1), H=(1,2,+1/2); e_c in rank16 is conjugate of e_R, not L-doublet right spin coordinates',
        missing_matching='prescribe how the two pre-mode seam spinors are expressed in parent normal data and independent w, or give joint variation/normal-output relation',
        joint_first_variation='for a proposed joint realization S_rest+S_H o F, delta S=delta S_rest+<e_H,D F[delta Psi,delta w]>; S_rest excludes this same bridge to avoid adding the intrinsic Yukawa twice. This decomposition is not a constructed AE4 action.',
        joint_variational_rule='<E_rest,5,delta Psi>_5+Green_rest[delta trace]+<E_rest,4,delta w>_4+<e_H,F_5 delta Psi+F_4 delta w>_4=load[delta x] on the adopted allowed-variation space',
        joint_normal_rule='ONLY if F_5=T gamma_trace, its pullback T^sharp_D e_H is a boundary cotangent added to the normal balance. A volume map K_L instead adds K_L^sharp_D e_H to the distributed bulk Euler equation and does not itself modify the Green form.',
        mixed_second_variation='<F_4 v4,H_H F_5 v5> + <e_H,F_45[v4,v5]> + prescribed domain/normal/pairing terms',
        proposed_witness_only='K_L=Pi_L B h (I-WB); g_L=L+lambda K_L Psi5; g_R=e_R; lambda real symbolic; replace bridge arguments only, NOT active kinetic field',
        restriction='K_L W=0 using inherited BW=I. This preserves restricted bridge, NOT claimed unrestricted equations, poles or native stationarity.',
        forward_per_lambda='E_R5=-Hdag Ydag K_L',
        reverse_per_lambda='E_5R=-K_L^sharp_D YH; K_L^sharp_D=Gamma05^-1 K_L^sharp_L2 Gamma04',
        reverse_map_type='bounded volume-to-wall map: reverse has radial chi and is distributed in bulk, NOT an evaluated seam conormal or selected boundary condition',
        actual_source_action='K_L p=eta Pi_L Xi. H1=w H0, H0=(0,1), in saved sigma1 section. Family Ydag and Higgs amplitude remain symbolic.',
        photon_coordinate='b; beta=Tb b; AQ=sqrt(2) beta already included in saved source, no action-index factor in vertex',
        photon_jet='K_L,A=Pi_L,A B h Pperp + Pi_L B_A h Pperp + Pi_L B h_A Pperp + Pi_L B h Pperp,A; Pperp,A=-W_A B-W B_A',
        source_family_identity='K_L,A W + K_L W_A=0 wherever the proposed family maintains BW=I; h_A=0 only if explicitly frozen as diagnostic definition; no physical W_A,B_A or H_A assigned zero',
        forward_photon_jet='-(Hdag Ydag)_A K_L - Hdag Ydag K_L,A plus owned pairing/domain variations',
        nonlinear_jet='D45(S_H o F)=D2 S_H[F_4,F_5]+D S_H[F_45]; source derivative acts on both terms and all arguments',
        additional_postulate='action-owned off-mode field identification/normal incidence must permit, forbid or specify complement-to-seam assignment and its same-source derivatives. No value of lambda is requested or chosen.',
        domain='no relation w=B Psi imposed. A bounded witness can perturb an already fixed dense joint domain, but does not construct the domain or prove it admissible in the full theory.',
        gauge_scope='frozen current section. Full gauge covariance needs W/B intertwining and transported Higgs/charge/source jets, not proven by a scalar normal norm.',
        no_double_counting='bridge is counted once in S_rest+S_H o F, not appended to the full intrinsic action with its Yukawa already included. Witness changes bridge arguments only; a full kinetic field redefinition requires additional terms. Neither proposed operation is installed.'))
    save(out/'input_hashes.json', {k: dict(path=str(p), sha256=sha(p)) for k, p in refs.items()})
    git = lambda *args: subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    save(out/'workspace.json', dict(head=git('rev-parse', 'HEAD'),
        branch=git('branch', '--show-current'), continuation_reference='065b6e0fe2b477e5b89867e5de6a9c685228ef02',
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        status_at_execution=git('status', '--short'), producer_calculations_replayed=False))
    save(out/'contribution_ledger.json', {k: None for k in (
        'native_bulk_heat', 'state_variation', 'contact', 'domain_boundary',
        'completion_counterterm', 'strong_within_native')})
    save(out/'output_hashes.json', {p.name: sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--duplicate-output', type=Path,
                   help='materialize the same in-memory new result twice; no second calculation')
    args = p.parse_args()
    root = args.repository.resolve()
    computed = calculate(root)
    run(root, args.output.resolve(), computed)
    if args.duplicate_output:
        run(root, args.duplicate_output.resolve(), computed)
