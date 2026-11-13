"""Evaluate only NEW family jets using saved native-route source actions."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np

def load(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())

def run(root,out):
    if out.exists():raise FileExistsError('a new numerical output is required')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_native_family_difference import coefficients,polynomial_family_check
    # Existing heat machinery is recovered intact, not rewritten. Its native
    # invocation requires an owned positive body and length; neither default
    # heat_length=1 nor heat of these finite source images is permitted here.
    from bhsm.interface.arb_heat_pencil_contractions import HeatPencil
    refs=dict(source=root/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz',
        child=root/'artifacts/muon_source_jet_20261002/replay_reference/evaluated_child_forms.npz',
        owned=root/'artifacts/muon_owned_connection_20261002/replay_reference/owned_connection_actions.npz',
        mixed=root/'artifacts/muon_native_family_difference_20261006/inputs/canonical_muon_mixed_sources.npz',
        family_action=root/'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
        chiral_domain=root/'src/bhsm/interface/ae31_c2_chiral_green_domain.py',
        ward=root/'src/bhsm/interface/ae31_c2_local_em_ward_identity.py',
        source_builder=root/'src/bhsm/interface/muon_local_source_jet.py',
        owned_builder=root/'src/bhsm/interface/muon_owned_connection_application.py',
        canonical_body=root/'artifacts/muon_native_family_difference_20261006/inputs/fermion_body.py',
        native_owner=root/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        NGE=root/'artifacts/muon_native_family_difference_20261006/inputs/nge_mixed_operator.py',
        kernel=root/'src/bhsm/interface/arb_heat_pencil_contractions.py',
        kernel_dependency=root/'src/bhsm/interface/gate7_current_action.py',
        frozen=root/'artifacts/muon_first_order_complement_20261006/frozen_locals.json',
        user_handoff=root/'artifacts/muon_native_family_difference_20261006/inputs/user_handoff.txt',
        module=root/'src/bhsm/interface/muon_native_family_difference.py',script=Path(__file__).resolve())
    start=time.perf_counter()
    d={k:load(refs[k]) for k in ('source','child','owned','mixed')}
    arrays,proof=coefficients(d['source'],d['owned'],d['mixed'],d['child'])
    poly,check=polynomial_family_check(arrays['weak_mass_background_form'],arrays['weak_mass_squared_form'])
    arrays.update(poly)
    native_operand=dict(name='zero-source coexact photon form action on the reached NGE source currents',
        equation='M_0,Q A_0,Q w=K_0,Q w; K_0,Q(v,w)=delta_A^2 S_AE4(v,w) on the inherited BRST/zero-mode quotient',
        sufficient_application='u_zeta=solve(K_0,Q+zeta M_0,Q,J_gamma); J_gamma is produced by Gamma_s and Gamma_bar, including their connected output',
        first_current='retained actual Gamma_s_unit_source_fermion_boson_external, same b source and mass interpolation; inverse is full owned response, not isolated8x8 compression',
        producer='same AE4 positive coexact electromagnetic Hessian, primitive component/Q norm plus induced matching remainder, constraints, domain and completion',
        consumer='boson block of the sourced generalized heat pencil used by HeatPencil.mixed or equivalent graded coefficient contractions',
        available='primitive Maxwell/mixed source actions and parent component response; not an evaluated complete positive same-owner photon body',
        not_a_new_datum='action/implementation application required, not a selected seam parameter or a demand for a new history',
        common_block_does_not_cancel='mass dependence of the fermion branch changes its mixed heat weight with the same photon body')
    ledger={k:dict(classification='UNEVALUATED',paired_contribution=None) for k in
        ('native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native')}
    ledger['contact']['evaluated_subterm']='fixed charged spatial K_sb=0 by mass/source representation; complete native contacts uncomputed'
    result=dict(classification='NATIVE_ROUTE_ACTUAL_FAMILY_SOURCE_JETS_AND_POLYNOMIAL_FORM_CHECK_NOT_NATIVE_PAULI',
        proof=proof,form_family_quadrature=check,
        native_heat=dict(kernel='HeatPencil.mixed/mixed_direction recovered unchanged',invocations=0,
            Gamma_sb=None,paired_Pauli=None,ell_star=None,default_length_used=False,
            family_quadrature=None,endpoint_vs_integrated_heat=None,first_missing_operand=native_operand),
        generalized_jet_equations=dict(A_s='solve(M,K_s-M_s A)',A_b='solve(M,K_b-M_b A)',
            A_sb='solve(M,K_sb-M_sb A-M_s A_b-M_b A_s)',
            Gamma_sb='STr(DQ[A_b] A_s+Q A_sb); retain [bar_zeta zeta] and signed-transfer Pauli derivative'),
        state=dict(fixed_entire_sourced_family='state-independent; paired derivative zero in this scope',
            complete_paired_visible_kernel=None,
            independent_family_variations='W_mu^- and W_e^- must EACH vanish for state independence on unrestricted admissible family-diagonal tangents',
            common_X_only='if a derived state map supplies SAME X, evaluate W_mu^- minus W_e^-; equality not supplied by common spin structure'),
        source=dict(photon='b_A, amplitude source; not physical soft transfer',
            fermion_legs='actual Gamma_s/Gamma_bar retained as canonical test sources with full n2 output',
            fixed_bare_current_mass_jets='zero at fixed E0; moving physical injections remain unevaluated',
            physical_mass_dependent_Pauli_projector_jet=None,physical_external_state_jets=None),
        contributions=ledger,signed_transfer=dict(native_directions=0,values=None,central_quotients=None,post_division_errors=None),
        preserved=dict(accepted_parent_solution=True,seam_proposal_historical_unadopted=True,seam_campaign_run=False,
            QED_Higgs_weak_locals_unchanged=True,electron_QED_difference_not_added=True),
        physical_a_mu=None,physical_g_mu=None,absolute_electron_native_reference=None,
        calibrated_GeV_mass_used=False,experimental_comparison=False,
        numerical_scope='Arb coefficients from retained decimal ratios; actual source/action maps binary64; no native numerical, spectral-tail, continuum or theoretical uncertainty bound')
    out.mkdir(parents=True);np.savez_compressed(out/'family_source_actions.npz',**arrays)
    save(out/'result.json',result);save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in refs.items()})
    save(out/'execution.json',dict(command='replay_muon_native_family_difference.py --output '+str(out),
        wall_seconds=time.perf_counter()-start,old_production_rerun=False,old_tests_repeated=False,
        new='cache-based family/source actions and polynomial two-point family quadrature',
        native_heat_invocations=0,physical_transfer_directions=0,expensive_solve_launched=False))
    save(out/'checkpoint.json',dict(id='BHSM_MUON_NATIVE_FAMILY_SOURCE_JETS_20261006',
        actual_starting_HEAD='b0b5cdec48735f6e2ae40051a32662297882b7e4',
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        next_operand=native_operand,paired_native_difference=None))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(dict(proof=proof,quadrature=check,native_heat_evaluations=0),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
