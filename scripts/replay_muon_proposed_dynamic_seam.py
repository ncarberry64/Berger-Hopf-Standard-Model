"""Cache-only application of a NOT-ADOPTED material-seam postulate."""
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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')


def references(root):
    return {
        'wall': root/'artifacts/muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz',
        'green': root/'artifacts/muon_joint_variational_attachment_20261005/run_2/node3_joint_known_variations.npz',
        'node3': root/'artifacts/muon_retained_tail_core_20261005/run_1/points/node_03.json',
        'representation': root/'artifacts/muon_connection_weight_20261001/representation_input.json',
        'premode_action': root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        'intrinsic_action': root/'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
        'domain': root/'src/bhsm/interface/ae31_c2_chiral_green_domain.py',
        'owner': root/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        'source_producer': root/'src/bhsm/interface/muon_parent_source_contact.py',
        'green_producer': root/'src/bhsm/interface/muon_joint_variational_attachment.py',
        'source_coordinate_producer': root/'src/bhsm/interface/muon_local_source_jet.py',
        'module': root/'src/bhsm/interface/muon_proposed_dynamic_seam.py',
        'script': root/'scripts/replay_muon_proposed_dynamic_seam.py',
        'derivation': root/'theory/muon_proposed_dynamic_seam_20261005.md',
        'tests': root/'tests/test_muon_proposed_dynamic_seam.py'}


def calculate(root):
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_proposed_dynamic_seam import (
        actual_source_readout, actual_green_controls)
    refs = references(root)
    with np.load(refs['wall'], allow_pickle=False) as z:
        wall = {k: np.array(z[k]) for k in z.files}
    with np.load(refs['green'], allow_pickle=False) as z:
        green = {k: np.array(z[k]) for k in z.files}
    if not np.array_equal(wall['actual_state'], green['actual_state']):
        raise ValueError('wall/Green state mismatch')
    if not np.array_equal(wall['source_coordinates'], green['source_coordinates']):
        raise ValueError('source coordinates mismatch')
    if not np.array_equal(wall['Xi_full'], green['source_image_basis']):
        raise ValueError('source column frame mismatch')
    arrays, numeric = actual_source_readout(wall, green)
    arrays.update(actual_state=wall['actual_state'], source_coordinates=wall['source_coordinates'])
    controls = actual_green_controls(wall, green)
    return refs, arrays, numeric, controls


def run(root, output):
    if output.exists():
        raise FileExistsError('new dedicated output required')
    refs, arrays, numeric, controls = calculate(root)
    output.mkdir(parents=True)
    result = dict(
        classification='PROPOSED_DYNAMIC_AVERAGE_TRACE_MATERIAL_COMPLETION_NOT_ADOPTED',
        continuation='223e2bd7fd3fa89358595676addbc3f8386a0ce0',
        source_coordinate='b; beta=T_b b, A_Q=sqrt(2) beta; conversions already in saved source',
        source_frame='node3 action_arc6, twelve saved independent columns, n1+n3 connected output; common Spin x SM section',
        field_rule='F_b= kappa^-1 iota_b^sharp Gamma_average,b; P Gamma_average=E_b w; (I-P) Gamma_jump=0',
        E='kappa*iota; kappa=1/sqrt(2 I); physical wall LL plus charge-conjugated e_R in doubled carrier',
        jump='Gamma_jump=j*(gamma_plus-U_b^-1 gamma_minus); j=Dirac_bar_Green_density/mu4',
        wall_row='A4 w-E_b^sharp Gamma_jump Psi',
        additional_action='S_seam=-1/2*(<w,E^sharp Gamma_jump Psi>4+<Gamma_jump Psi,Ew>boundary)',
        replacement='matched material smooth transmission replaced by dynamic jump; original reset, temporal prefix and canonical stop untouched',
        evaluated='J_chi,L=-b_volume Pi_L Xi; unmatched average trace retained; e_R zero from actual carrier support',
        same_photon_total_jet='J_A=F_A chi+F chi_A; all map/pairing/source/domain jets retained in derivation and ordered evaluator; not physically evaluated',
        normalization_partial_kernel='partial_dJ_d_log_kappa_at_fixed_trace=-J; trace motion cancels explicit kappa dependence along the preserved material relation',
        charge_conjugate_scope='formal doubled bookkeeping with Psi_N=(Psi,C Psi) redundancy; no unconstrained doubled heat trace evaluated or justified',
        reverse_role='boundary cotangent/normal balance; no distributed h=p/u witness installed',
        kinetic_matching_test='R^sharp A_joint R=W^sharp A5 W+A4 on Rw=(Ww,w) with zero jump; equality to retained localized Euler action not supplied by BW=I',
        admissibility='local material adjoint/density arguments conditional; no claim of complete closed stratified Lorentz realization',
        new_physical_postulate=True, native_operator_updated=False, parent_solution_updated=False,
        diagnostic_K_L_installed=False, lambda_selected=False, new_profile=False, new_witness=False,
        old_production_or_visibility_replayed=False, numeric=numeric, algebra_controls=controls,
        error_scope=dict(
            arithmetic='binary64 products of frozen source/scalar/Green arrays; output intervals enclose scalar multiplication rounding only',
            inherited_b_volume_error=None, inherited_inclusion_and_domain_error=None,
            total_same_photon_jet_evaluated=False, continuum_or_physical_bound=None),
        native_ledger={k:None for k in ('native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native')},
        physical_a_mu=None, physical_g_mu=None, native_uncertainty=None,
        next_unresolved_rule='action-owned joint seam postulate satisfying material domain and localized kinetic matching; this proposed normal bilinear/domain is not derived or adopted')
    # Exact products of frozen binary64 components, enclosed without re-solving
    # or refining any old scalar. Bounds are per component, not operator norms.
    from fractions import Fraction
    b = Fraction.from_float(numeric['b_volume'])
    rounding = {}
    wall_path = refs['wall']
    with np.load(wall_path, allow_pickle=False) as wall:
        for n in (1,3):
            x = wall[f'normalized_wall_W_input_n{n}'].reshape(4,16,n+1,n+1,12)
            y = arrays[f'J_chi_left_n{n}'].reshape(x.shape)
            lo = np.array(y.real); hi = np.array(y.real)
            il = np.array(y.imag); ih = np.array(y.imag)
            max_error = Fraction(0)
            for spin in (0,1):
                for carrier in (6,7):
                    for idx in np.ndindex(x.shape[2:]):
                        pos = (spin,carrier)+idx
                        for component, lower, upper in ((0,lo,hi),(1,il,ih)):
                            operand = float((x[pos].real,x[pos].imag)[component])
                            rounded = float((y[pos].real,y[pos].imag)[component])
                            exact = -b*Fraction.from_float(operand)
                            error = abs(exact-Fraction.from_float(rounded))
                            max_error = max(max_error,error)
                            lower[pos] = rounded if Fraction.from_float(rounded)<=exact else np.nextafter(rounded,-np.inf)
                            upper[pos] = rounded if Fraction.from_float(rounded)>=exact else np.nextafter(rounded,np.inf)
            output_shape=arrays[f'J_chi_left_n{n}'].shape
            arrays[f'J_chi_left_real_lower_n{n}']=lo.reshape(output_shape)
            arrays[f'J_chi_left_real_upper_n{n}']=hi.reshape(output_shape)
            arrays[f'J_chi_left_imag_lower_n{n}']=il.reshape(output_shape)
            arrays[f'J_chi_left_imag_upper_n{n}']=ih.reshape(output_shape)
            rounding[f'n{n}'] = dict(max_component_rounding_error_upper=float(np.nextafter(float(max_error),np.inf)),
                scope='exact scalar products of frozen binary inputs only; inherited b/source errors excluded')
    np.savez_compressed(output/'proposed_seam_actions.npz', **arrays)
    result['rounding']=rounding
    save(output/'result.json', result)
    save(output/'input_hashes.json', {k:dict(path=str(p.resolve()),sha256=sha(p)) for k,p in refs.items()})
    git = lambda *a: subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(output/'workspace.json', dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd', status=git('status','--short')))
    save(output/'checkpoint.json', dict(id='BHSM_MUON_PROPOSED_DYNAMIC_SEAM_20261005',
        result='concrete new postulate and conditional actions, outside frozen operator',
        readout='J_chi,L=-b_volume Pi_L Xi', total_jet='ordered formulas; no numerical full photon jet',
        next=result['next_unresolved_rule']))
    save(output/'output_hashes.json', {p.name:sha(p) for p in output.iterdir() if p.is_file()})
    print(json.dumps(dict(classification=result['classification'],numeric=numeric,
                          controls=controls,rounding=rounding),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(args.repository.resolve(),args.output.resolve())
