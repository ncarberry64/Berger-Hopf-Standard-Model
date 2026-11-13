"""Adopted branch-transfer support law and current muon birth-value audit.

This owner amendment supplies the semantic event criterion. It adds no
scalar support coordinate, new species, action density or numerical solver.
Retained transition laws and physical transfer values remain distinct.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path


CLASSIFICATION = 'BHSM_AE4_BRANCH_RELATIVE_SUPPORT_TRANSITION'
SUPPORT_OWNER = 'BHSM-AE4-BRANCH-RELATIVE-SUPPORT-2026-10-08'
CUTOFF_OWNER = 'BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08'
EVENT_DEFINITION = 'BRANCH_REALIZATION_TRANSFER_EVENT'
SUPERSEDED_GAP = 'OUTWARD_SPACETIME_SUPPORT_CESSATION_EVENT_CONDITION'
FIRST_MISSING_OPERAND = 'I_PHYS_MUON_BIRTH_TRANSFER_VALUE'
STARTING_HEAD = '1e5933fe6e027eb25fdf2ee92f526f6025465ab1'
SCIENTIFIC_REFERENCE = '524ed90689bd5923c249bba2e699abf627e703cd'
ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIRECTORY = 'artifacts/ae4_branch_relative_support_transition_20261008'


def branch_transfer_definition():
    """The human owner's operational definition; not an evaluated event."""
    return dict(
        owner=SUPPORT_OWNER, event=EVENT_DEFINITION, status='ADOPTED_OWNER_DEFINITION',
        authority='Norman owner clarification supplied by the current human user on 2026-10-08',
        support_interval='Maximal connected future interval I_B on which the same constrained physical branch B is admissible, dynamically realized and admits forward continuation',
        transition_time='tau_(B->C)=sup I_B PROVIDED a successor C is dynamically realized across that same event with inherited matching',
        conjunction=[
            'B has no admissible realized forward continuation in its owned physical branch/domain',
            'One or more successor C are action-admissible AND dynamically realized at the same event',
            'Inherited constraints, canonical/interface and Noether/current matching hold',
        ],
        proof_certificate_failure_is_physical_loss=False,
        arbitrary_current_zero_is_event=False, upsilon_zero_is_event=False,
        descriptor_zero_is_event=False, canonical_stop_alone_is_event=False,
        last_cached_point_is_event=False, new_support_scalar=False,
        successor_admissibility_without_realization_is_sufficient=False,
    )


def branch_relative_cutoff_contract():
    """Birth-side cutoff amendment for a created child C, specifically muon."""
    return dict(
        cutoff_owner_tag=CUTOFF_OWNER,
        supersedes_cutoff_owner_tag='BHSM-AE4-MODE-FREQUENCY-CUTOFF-2026-10-07',
        support_event_definition=EVENT_DEFINITION,
        surface_rule='Sigma_star^mu=Sigma_(P->mu)=Sigma_P,out=Sigma_mu,in',
        general_child_surface_rule='Sigma_star^C=Sigma_(B->C)',
        branch_rule='ACTION_SELECTED_MUON_FORMATION_MODE_ON_CHILD_SIDE_OF_THE_COMMON_PRECURSOR_TO_MUON_BIRTH_EVENT',
        evaluation_side='MUON_CHILD_PLUS_SIDE_AT_BIRTH',
        plus_side_meaning='One-sided newly realized muon branch at the common surface; no finite temporal offset',
        cutoff_event='MUON_BIRTH__P_TO_MU',
        decay_event='MUON_DECAY__MU_TO_DAUGHTERS__SEPARATE_LATER_APPLICATION',
        decay_surface_sets_birth_cutoff=False,
        birth_resistance='r_mu^+=<psi_mu^+,R_mu^+ psi_mu^+>',
        birth_inertia='i_mu^+=<psi_mu^+,I_mu^+ psi_mu^+>',
        muon_heat_length_squared_rule='ell_star,mu^2=c_mu=i_mu^+/r_mu^+',
        energy_equality_at_birth='<psi_mu^+,(R_mu^+-H_event,drive)psi_mu^+>=0',
        energy_equality_automatically_removed_by_transfer=False,
        energy_equality_evaluated=False,
        same_branch_formation_is_same_branch_cessation_by_default=False,
        parent_loss_and_child_formation_can_share_event=True,
        normal_source='xi_psi^(s)=psi_mu^+,(s) n_star^(s) on every active regular stratum',
        preferred_normalization='<psi_mu^+,I_mu^+ psi_mu^+>=1',
        base_unit_norm_implies_zero_total_inertia_jets=False,
        experimental_lifetime_selects_event=False,
    )


@dataclass(frozen=True)
class BranchTransferEvidence:
    """Acceptance gate for supplied physical evidence, never a selector.

    The repository audit supplies none of these completed muon evidence
    values. A failed proof certificate cannot satisfy noncontinuation.
    """
    parent_branch: str
    child_branch: str
    event_identity: str
    common_action_domain_identity: str
    parent_noncontinuation: bool
    successor_admissible: bool
    successor_realized: bool
    inherited_matching: bool
    proof_failure_only: bool = False

    def __post_init__(self):
        for name in ('parent_noncontinuation', 'successor_admissible',
                     'successor_realized', 'inherited_matching', 'proof_failure_only'):
            if type(getattr(self, name)) is not bool:
                raise ValueError('physical evidence flags must be explicit booleans: ' + name)
        for name in ('parent_branch', 'child_branch', 'event_identity',
                     'common_action_domain_identity'):
            if not isinstance(getattr(self, name), str):
                raise ValueError('evidence identities must be strings: ' + name)

    @property
    def transfer_established(self):
        identities = (self.parent_branch, self.child_branch, self.event_identity,
                      self.common_action_domain_identity)
        return bool(all(item.strip() for item in identities)
                    and self.parent_branch.strip() != self.child_branch.strip()
                    and self.parent_noncontinuation and self.successor_admissible
                    and self.successor_realized and self.inherited_matching
                    and not self.proof_failure_only)


def current_muon_birth_realization(repository: Path | str = ROOT):
    """Current physical-question report consuming reviewed retained evidence."""
    folder = Path(repository) / ARTIFACT_DIRECTORY
    names = ('parent_transition_audit.json', 'child_birth_audit.json',
             'muon_operand_reuse_audit.json')
    audits = {name: json.loads((folder / name).read_text(encoding='utf8')) for name in names}
    for name, audit in audits.items():
        provenance = audit.get('provenance', audit)
        head = provenance.get('starting_HEAD', provenance.get('starting_head'))
        if (head != STARTING_HEAD
                or provenance.get('scientific_reference') != SCIENTIFIC_REFERENCE):
            raise ValueError('retained transition audit has a different scientific identity: ' + name)
    binding = dict(owner=SUPPORT_OWNER, event=EVENT_DEFINITION,
                   branch='codex/muon-parent-maxwell-density-review',
                   birth='P->mu at E1, with the physical identification application pending',
                   starting_HEAD=STARTING_HEAD, scientific_reference=SCIENTIFIC_REFERENCE,
                   required_value=FIRST_MISSING_OPERAND)
    identity = sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    required = ('Phi_star', 'Sigma_star', 'psi_star', 'xi_psi', 'b_psi', 'S_SL',
                'R', 'stationary_base', 'lambda', 'pairing', 'domain', 'active_strata')
    return deepcopy(dict(
        classification=CLASSIFICATION, starting_HEAD=STARTING_HEAD,
        scientific_reference=SCIENTIFIC_REFERENCE,
        branch='codex/muon-parent-maxwell-density-review',
        support_definition=branch_transfer_definition(),
        classical_action_contract=dict(
            owner='BHSM-AE-3.2.16-COVARIANT-BUBBLE-INTERFACE-MECHANICS',
            scalar='S_SL=S_bulk,event+S_bulk,child+S_owned_boundary_corner-sum_s integral_W_s gamma_s dmu_h',
            constrained_action='L=S_SL+lambda^dagger R',
            mechanical_equation='I_lambda D_tau^2 a_lambda+[gamma J_Sigma+H_impedance]a_lambda=f_event,lambda',
            domain='Same constrained regular-stratum Euler/trace/conormal/reset/BRST domain with inherited opposite orientations and future-retarded continuation; actual common birth pullback unevaluated',
            registered_regular_strata=['M8','M5+','M5-','M4'],
            strata_preserved='Registered S8 -> relative S5|4 -> intrinsic S4; no unsourced reduction or duplicate co-variation',
            inventory_path='artifacts/ae4_support_loss_classical_realization_20261007/classical_owner_audit.json',
            inventory_event_gap_is_historical=True,
            quantum_heat_added_to_classical_resistance=False,
        ),
        cutoff_owner_amendment=branch_relative_cutoff_contract(),
        supersession=dict(old_gap=SUPERSEDED_GAP, old_gap_is_current=False,
                         replacement_definition=EVENT_DEFINITION,
                         old_research_receipts_preserved=True),
        chronology=dict(
            retained_geometry_transition='E0->C1(branch23)->E1->C2(branch24)',
            temporal_precursor_component='Incoming C1 at E1; not the outgoing C2 spatial M5 parent-bulk',
            precursor_new_species_or_action=False,
            muon_birth='tau_(P->mu)=tau_P,out=tau_mu,in',
            muon_decay='tau_(mu->D)=tau_mu,out=tau_D,in',
            muon_support_interval='tau_mu,in<tau<tau_mu,out',
            tau_mu_in=None, tau_mu_out=None,
            temporal_precursor_to_physical_muon_binding_evaluated=False,
        ),
        first_missing_operand=dict(
            name=FIRST_MISSING_OPERAND, status='TRANSITION_OPERAND_UNEVALUATED', value=None,
            exact_object='Value-level application of the already-derived physical enclosure/state transport to the retained incoming C1/E1 data and muon-side C2 full-field traces on one common event/domain, with inherited constraint/canonical/interface/Noether matching',
            why_needed='Admissible generic C2 continuation and a preserved muon projector do not by themselves evaluate the dynamically realized muon transfer from this precursor event',
            not_a_missing_semantic_definition=True,
            missing_generic_reset_or_family_selector=False,
        ),
        physical_birth_transition_instantiated=False,
        binding_identity=identity,
        binding_scope='Common requirement binding only; no physical stationary base/domain identity asserted',
        required_outputs={name:dict(binding_identity=identity, status='UNEVALUATED',
                                   value=[None]*7 if name=='b_psi' else None,
                                   blocked_by=FIRST_MISSING_OPERAND) for name in required},
        normal_source=dict(
            definition='xi_psi^(s)=psi_mu^+,(s) n_star^(s)',
            normalization_requires_full_same_owner_inertia=True,
            normalization_evaluated=False, full_active_section_required=True,
            seven_port_order=['trace_1','trace_2','trace_3','canonical_momentum_1',
                              'canonical_momentum_2','dynamic_flux_1','dynamic_flux_2'],
            seven_port_formula='[T u_psi+(D_psi T)q;D_psi P;D_psi F-D_psi G-D2P[X_flow,u_psi]-DP[D_psi X_flow]]',
            orientation='Inherited event/child opposite outward conormals and canonical signs',
            eighth_support_coordinate_added=False, descriptor_or_launch_substitution=False),
        notation_guard='The scalar b_psi=Psi^dagger rhs in the retained singular normal form is distinct from the seven-port b_psi; its nonzero certificate does not evaluate the port source. Transported matter Phi/Psi traces are distinct from the mechanical formation mode psi_mu^+.',
        energy_birth_test=dict(
            equation='<psi_mu^+,(R_mu^+-H_event,drive)psi_mu^+>=0',
            conditional_identity='F_E=<psi,H_form psi>+<psi,(H_impedance-H_bulk,constrained)psi> on the same normal chart, drive/J and pairing',
            identity_premise='Same reduced bulk restoring operator, Jacobi/drive pullbacks and muon formation mode/domain; do not equate unrelated ordered pencils',
            evaluated_value=None, surface_moved_or_fitted=False,
            zero_Legendre_energy_is_this_equation=False),
        stationary_base=dict(equations=['L_eta=0','R=0'], base=None, multipliers=None,
                             domain=None,pairing=None,chart_pullback=None),
        downstream={name:dict(status='UNEVALUATED__BIRTH_TRANSFER_VALUE_NOT_SUPPLIED',value=None)
                    for name in ('L_etaeta','R_eta','S_eta_s','R_eta_s','R_s','L_ss',
                                 'h_psi','H_KKT','delta_psi','z_psi','r','i','r_v','r_J','r_vJ',
                                 'i_v','i_J','i_vJ','c','AE4_heat','relative_zeta_eta','R_ind',
                                 'native_photon_response','paired_e_mu_heat','signed_Pauli',
                                 'a_mu','g_mu')},
        claim_statuses=dict(
            ADOPTED_OWNER_DEFINITION='Human branch-relative support law and child-birth cutoff amendment',
            DERIVED='Conditional local regular-sheet noncontinuation; retained transition, localization, family transport, normal/port and conditional energy laws',
            EVALUATED='New static provenance audit and deterministic report serialization only',
            RETAINED_CERTIFIED='Existing orientation, reset and positive-duration continuation certificates at their original scope; not rerun',
            CONTROL_ONLY='Prior finite KKT/heat demonstrations; not rerun or promoted',
            UNEVALUATED='I_phys muon birth transfer values, physical mode/base/source and downstream values',
            OWNER_DEFINITION_GAP='Superseded: the branch-transfer definition is now supplied'),
        retained_evidence=audits,
        execution=dict(old_producers_rerun=0,new_physical_KKT_solves=0,new_generic_KKT_algebra=0,
                       finite_control_runs=0,Gate7_campaigns=0,launch73_recomputations=0),
        error_scope='Static branch-transfer/provenance audit; no numerical physical birth event, branch/source, KKT impedance, heat or uncertainty/continuum error evaluated',
    ))
