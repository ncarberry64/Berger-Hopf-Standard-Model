"""New owner reconciliation and perturbation controls; no production replay."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_native_impedance_energy_response import reconcile_owners
from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import native_spectral_length_contract
from control_muon_impedance_eigenbranch import execute_control


def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_reduction_identities():
    z,s,d,m=sp.symbols('Z S D M',real=True);Eres=(z+s)/m;Ebulk=z/m;Edrive=d/m
    residual=sp.simplify((Ebulk-Edrive).subs(d,z+s))
    # Exact implication control: a simple formation eigenline is not, in
    # general, a resistance-energy eigenline. These are NOT physical inputs.
    x,y=sp.symbols('x y',real=True);u=x+y;tau=u*u
    A=sp.Matrix([[tau,u],[u,1]]);R=sp.Matrix([[2,1],[1,3]])
    line=sp.Matrix([1,-u]);psi=line/sp.sqrt(1+u*u)
    Eline=sp.simplify((psi.T*R*psi)[0])
    result=dict(classification='EXACT_ALGEBRA_AND_IDENTIFICATION_CONTROL_ONLY',
        one_mode_ratio='D/(gamma J+Z); no independently selected scalar impedance',
        total_resistance_threshold_identity=str(sp.simplify((Eres-Edrive).subs(d,z+s))),
        bulk_only_threshold_residual=str(residual),
        geometric_pairing_not_assumed_identity=True,
        formation_vs_energy=dict(control_R=[[int(v) for v in row] for row in R.tolist()],
            control_A_at_zero=[[int(v) for v in row] for row in A.subs({x:0,y:0}).tolist()],
            analytic_crossing='tau=(x+y)^2',
            formation_equation=sp.simplify(A*psi)==sp.zeros(2,1),
            line_normalized=sp.simplify((psi.T*psi)[0])==1,
            selected_energy=str(Eline),
            energy_eigenline_residual_squared_at_zero=int(((R-2*sp.eye(2))*sp.Matrix([1,0])).norm()**2),
            E_x=int(sp.diff(Eline,x).subs({x:0,y:0})),
            E_y=int(sp.diff(Eline,y).subs({x:0,y:0})),
            E_xy=int(sp.diff(Eline,x,y).subs({x:0,y:0})),
            bare_R_x=0,bare_R_y=0,bare_R_xy=0,
            crossing_tau_x=0,crossing_tau_y=0,crossing_tau_xy=2,
            hypothetical_formation_example_not_installed=True))
    return result


def run(output):
    if output.exists():raise FileExistsError('Fresh output required; preserve checkpoints')
    output.mkdir(parents=True);start=time.perf_counter()
    paths=dict(
        AE4_owner=ROOT/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        mechanics=ROOT/'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        Track2_decision=ROOT/'src/bhsm/interface/owner_authorized_encapsulation_interface_action.py',
        mechanics_record=ROOT/'artifacts/action_extension/BHSM_COVARIANT_BUBBLE_INTERFACE_MECHANICS.json',
        Track2_record=ROOT/'artifacts/action_extension/BHSM_OWNER_AUTHORIZED_ENCAPSULATION_INTERFACE_ACTION_CLASSIFICATION.json',
        AE4_report=ROOT/'theory/ae4_stratified_dirac_zeta_induced_owner.md',
        mechanics_report=ROOT/'theory/bhsm_covariant_bubble_interface_mechanics.md',
        Track2_report=ROOT/'theory/bhsm_owner_authorized_encapsulation_interface_action.md',
        earlier_source_result=ROOT/'artifacts/muon_native_induced_polarization_20261006/run_1/result.json',
        earlier_source_contacts=ROOT/'artifacts/muon_native_induced_polarization_20261006/run_1/affine_source_contacts.npz',
        earlier_weak_rows=ROOT/'artifacts/muon_native_induced_polarization_20261006/run_1/compact_weak_first_jets.npz',
        frozen=ROOT/'artifacts/muon_source_jet_20261002/frozen_local.json',
        builder=ROOT/'src/bhsm/interface/muon_native_impedance_energy_response.py',
        control=ROOT/'scripts/control_muon_impedance_eigenbranch.py',replay=Path(__file__))
    save(output/'input_hashes.json',{k:dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),
        canonical_LF_sha256=hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()) for k,p in paths.items()})
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    save(output/'starting_revision.json',dict(HEAD=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',working_tree_status=git('status','--short')))
    chronology={k:git('log','--follow','-1','--format=%H|%aI|%cI|%s','--',str(paths[k].relative_to(ROOT)))
                for k in ('AE4_owner','Track2_decision','mechanics')}
    save(output/'owner_chronology.json',chronology)
    mechanics=json.loads(paths['mechanics_record'].read_text());interface=json.loads(paths['Track2_record'].read_text())
    reconciliation=reconcile_owners(native_spectral_length_contract(),mechanics,interface)
    save(output/'owner_reconciliation.json',reconciliation)
    save(output/'checkpoint.json',dict(stage='actual owner reconciliation saved; no physical scalar selected'))
    exact=exact_reduction_identities();save(output/'exact_reduction_identities.json',exact)
    # SymPy integers in lists are rendered as ordinary integers in this record.
    control,arrays=execute_control();save(output/'arithmetic_eigenbranch_control.json',control)
    np.savez_compressed(output/'control_reduced_actions.npz',
        **{k:v for k,v in arrays.items() if isinstance(v,(np.ndarray,int,float,complex))})
    formulas=dict(classification='DERIVED_CONDITIONAL_OPERATOR_REDUCTION_FORMULAS',
        threshold='R=gamma J_Sigma+H_impedance; A_form=R-D; (R-D)psi_star=0',
        normalization='psi_dagger M_E psi=1 only once the physical M_E is derived; M_E=I not declared',
        selected_line_energy='E_R=psi_dagger R psi/(psi_dagger M_E psi)',
        selected_line_first='E_R,x=psi_dagger(R_x-E_R M_x)psi + psi_x_dagger(R-E_R M)psi + psi_dagger(R-E_R M)psi_x',
        normalized_line_mixed='E_R,xy=N_xy-E_R d_xy with N=psi_dagger R psi and d=psi_dagger M psi=1; all psi_x,psi_y,psi_xy, R/M first/mixed jets retained',
        energy_eigenbranch_extra_hypothesis='H_owned psi=E M_owned psi simple isolated, common differentiable form pullback',
        T_x='H_x-E M_x',E_x='psi_dagger T_x psi',
        reduced_solve='[H-E M, M psi; psi_dagger M,0] [r_x;lambda_x]=[-T_x psi;0]; psi_x=r_x-(psi_dagger M_x psi)psi/2',
        energy_mixed='psi_dagger(H_xy-E M_xy-E_x M_y-E_y M_x)psi + psi_dagger T_x r_y + psi_dagger T_y r_x',
        phase='Im(psi_dagger M psi_x)=0 for real Hermitian source directions',
        complex_current='extend real-coordinate Hessian coefficients linearly using the frozen current weights, never conjugate them',
        crossing='differentiate the selected formation eigenvalue lambda=0; tau_x=-lambda_x/lambda_tau and the full mixed implicit derivative',
        total_surface='E_total,x=E_x+E_tau tau_x; E_total,xy=E_xy+E_tau_x tau_y+E_tau_y tau_x+E_tau_tau tau_x tau_y+E_tau tau_xy',
        crossing_and_eigenline_motion_counted_once=True,
        ell='1/E_total',ell_x='-E_total,x/E_total^2',ell_xy='2 E_total,x E_total,y/E_total^3-E_total,xy/E_total^2',
        c_x='-2 E_total,x/E_total^3',c_xy='6 E_total,x E_total,y/E_total^4-2 E_total,xy/E_total^3',
        physical_values=None)
    save(output/'conditional_response_equations.json',formulas)
    prior=json.loads(paths['earlier_source_result'].read_text())
    result=dict(classification=reconciliation['classification'],
        preferred_physical_E_vJ_evaluated=False,
        new_result='operator-level supersession and exact one-mode threshold residual; missing AE4 energy/surface identification established without inventing a scalar law',
        reconciliation=reconciliation,exact_reduction=exact,arithmetic_control=control,
        physical=dict(H_owned=None,M_owned=None,psi_star=None,H_v=None,H_J=None,H_vJ=None,
            M_v=None,M_J=None,M_vJ=None,E=None,E_v=None,E_J=None,E_vJ=None,
            crossing_jets=None,ell_jets=None,c_jets=None,AE4_length_contribution=None,
            R_ind=None,completed_photon_response=None,family_native_heat=None,a_mu=None,g_mu=None),
        native_heat_default_length_used=False,synthetic_rho_hold_inserted=False,
        new_scalar_constitutive_law_inserted=False,physical_eigenvalue_or_frequency_chosen=False,
        inherited_domains_changed=False,Gate7_invoked=False,
        prior_local_source_result_preserved=dict(contacts_norm=prior['checks']['mixed_contact_norm'],
            compact_K_J_norm=prior['checks']['local_weak_K_J_norm'],targeted_checks_not_rerun=7),
        frozen_local=json.loads(paths['frozen'].read_text()),
        error_scope=dict(identities='exact symbolic identities',
            finite_control='binary64 generalized eigensolve, directional/normalization residuals and finite-difference consistency; NOT a rigorous truncation or physical error bound',
            physical_numerical=None,physical_theoretical=None),
        execution=dict(old_producers_replayed=0,old_targeted_checks_rerun=0,
            physical_eigenbranches_evaluated=0,physical_heat_contractions=0,
            new_control_dimension=3,elapsed_seconds=time.perf_counter()-start))
    save(output/'result.json',result)
    save(output/'minimal_owner_amendment.json',reconciliation['minimal_amendment'])
    save(output/'checkpoint.json',dict(id='BHSM_MUON_AE4_RHO_B2_LENGTH_OWNER_RECONCILIATION_20261006',
        stage='definition amendment identified; no independent scalar-law numerical solve authorized',
        result='result.json',physical_E_vJ=None,physical_a_mu=None,
        next='same-action selected-line common-charge energy and support-loss/formation-event identification'))
    save(output/'output_hashes.json',{p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps(dict(output=str(output),classification=result['classification'],
        physical_E_vJ_evaluated=False,control_E_xy=control['E_xy'],
        control_last_mixed_fd_error=control['finite_differences'][-1]['mixed_error'],seconds=result['execution']['elapsed_seconds'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
