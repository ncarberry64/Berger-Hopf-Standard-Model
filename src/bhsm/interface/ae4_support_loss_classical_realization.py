"""One inspected classical support-loss realization contract.

The classical bulk/interface action supplies the mechanical KKT response.
The quantum AE4 heat owner consumes its cutoff c=i/r downstream. This module
records the concrete event-definition stop found in the retained equations;
it adds no KKT algebra, trial flux condition, mode or numerical control.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping


CLASSIFICATION = 'BHSM_AE4_SUPPORT_LOSS_CLASSICAL_REALIZATION'
CLASSICAL_OWNER = 'BHSM-AE-3.2.16-COVARIANT-BUBBLE-INTERFACE-MECHANICS'
HEAT_OWNER = 'BHSM-AE-4.0.0_STRATIFIED_DIRAC_ZETA_HEAT'
FIRST_MISSING_DEFINITION = 'OUTWARD_SPACETIME_SUPPORT_CESSATION_EVENT_CONDITION'
STARTING_HEAD = '00fa89d62e4c74ee9fd0b41611b3468ad035b5db'
SCIENTIFIC_REFERENCE = '524ed90689bd5923c249bba2e699abf627e703cd'
REQUIRED_OUTPUTS = (
    'Phi_star', 'Sigma_star', 'psi_star', 'xi_psi', 'b_psi', 'S_SL',
    'R', 'pairing', 'domain', 'stationary_base', 'lambda',
)
PORT_ORDER = ('trace_1', 'trace_2', 'trace_3', 'canonical_momentum_1',
              'canonical_momentum_2', 'dynamic_flux_1', 'dynamic_flux_2')
ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIRECTORY = 'artifacts/ae4_support_loss_classical_realization_20261007'


@dataclass(frozen=True)
class RealizationOutput:
    """A named requirement in one definition binding, with no invented value."""
    name: str
    binding_identity: str
    definition: str
    provenance: tuple[str, ...]
    status: str = 'UNEVALUATED__SUPPORT_LOSS_EVENT_NOT_DEFINED'

    def report(self):
        return dict(name=self.name, binding_identity=self.binding_identity,
                    definition=self.definition, provenance=list(self.provenance),
                    status=self.status, value=[None] * 7 if self.name == 'b_psi' else None,
                    blocked_by=FIRST_MISSING_DEFINITION)


@dataclass(frozen=True)
class SupportLossClassicalRealization:
    """Concrete inspected requirements, not a solved physical realization.

    binding_identity identifies this single owner/base/domain *requirement*
    bundle. Actual base/domain/pairing are still unevaluated; the identifier
    is not proof that a physical common pullback or solution exists.
    """
    binding_identity: str
    outputs: tuple[RealizationOutput, ...]
    classical_audit: Mapping[str, Any]
    outward_audit: Mapping[str, Any]
    physical_audit: Mapping[str, Any]

    def __post_init__(self):
        # Capture independent producer snapshots. Frozen dataclasses alone do
        # not protect the nested dictionaries supplied by callers.
        object.__setattr__(self, 'classical_audit', deepcopy(self.classical_audit))
        object.__setattr__(self, 'outward_audit', deepcopy(self.outward_audit))
        object.__setattr__(self, 'physical_audit', deepcopy(self.physical_audit))
        self._validate()

    def _validate(self):
        """Reject altered provenance before it can be published as a report."""
        names = tuple(x.name for x in self.outputs)
        if names != REQUIRED_OUTPUTS or len(set(names)) != len(names):
            raise ValueError('all realization outputs required exactly once')
        if any(x.binding_identity != self.binding_identity for x in self.outputs):
            raise ValueError('mixed owner/base/domain requirement identities')
        if any(audit.get('starting_HEAD') != STARTING_HEAD
               or audit.get('scientific_reference') != SCIENTIFIC_REFERENCE
               for audit in (self.classical_audit, self.outward_audit, self.physical_audit)):
            raise ValueError('all producer audits must belong to the same scientific starting identity')
        if self.classical_audit['classical_owner']['action_version'] != CLASSICAL_OWNER:
            raise ValueError('the retained classical mechanics owner must be identified explicitly')
        missing = self.outward_audit.get('first_missing_definition', {})
        if (missing.get('name') != FIRST_MISSING_DEFINITION
                or missing.get('status') != 'UNDEFINED_IN_INSPECTED_OWNER'
                or missing.get('value') is not None):
            raise ValueError('this inspected contract stops at the operational outward-support definition')
        if self.classical_audit['classical_owner']['quantum_heat_in_classical_action']:
            raise ValueError('quantum E1 heat is downstream, not an extra classical restoring sector')

    def report(self):
        self._validate()
        payload = dict(
            classification=CLASSIFICATION,
            status='REALIZATION_CONTRACT_AUDITED__EVENT_DEFINITION_STOP',
            starting_HEAD=STARTING_HEAD, scientific_reference=SCIENTIFIC_REFERENCE,
            branch='codex/muon-parent-maxwell-density-review',
            binding_identity=self.binding_identity,
            physical_solution=False,
            owner_separation=dict(
                support_loss_classical_owner=CLASSICAL_OWNER,
                support_loss_scalar_action='S_SL=S_bulk,event+S_bulk,child+S_owned_boundary_corner-sum_s integral_W_s gamma_s dmu_h',
                mechanical_equation='I_lambda D_tau^2 a_lambda+[gamma J_Sigma+H_impedance]a_lambda=f_event,lambda',
                classical_outputs=['support-loss branch', 'I', 'R_total', 'normal displacement', 'KKT stationary response', 'z_psi'],
                classical_constraints='R(eta,X)=0; L=S_SL+lambda^dagger R',
                downstream_heat_owner=HEAT_OWNER,
                downstream_heat_action='Gamma_AE4=-(1/2)STr E1(c P_strat)+relative-zeta/eta completion',
                interface_between_owners='c=ell_star^2=i/r',
                quantum_heat_in_classical_restoring_action=False,
                owner_equality_required=False,
            ),
            owner_base_domain_pairing=dict(
                classical_authority=CLASSICAL_OWNER,
                binding_identity=self.binding_identity,
                stationary_base=None, domain=None, pairing=None,
                stationary_multipliers=None,
                common_physical_identity_instantiated=False,
                chart_pullback=None,
                identity_scope='One common requirement bundle; physical identity is not asserted before the event/base/domain exist',
            ),
            branch_identity=dict(
                selection='Initiating-event physical mode branch at an action-owned simple oriented formation crossing',
                transport='Continuous physical transport to the separate first future support-loss surface',
                mode_value=None,
                selected_mode_is_descriptor_or_launch=False,
                selected_mode_is_N12_ordered_stop_eigenline=False,
            ),
            event_conditions=dict(
                energy_equality=dict(
                    equation='<psi_star,(R_total-H_event,drive)psi_star>=0',
                    premise='Same physical mode, pairing and positive kinetic inertia on the same surface',
                    status='DEFINITION_ADOPTED__NOT_NUMERICALLY_EVALUATED', value=None),
                outward_support_cessation=self.outward_audit['first_missing_definition'],
                conjunction_required=True, first_future_selection=True,
                event_surface=None, root_search_performed=False,
                formation_zero_used=False, artificial_C2_cut_used=False,
                canonical_stop_used=False, descriptor_zero_used=False,
                last_cached_history_point_used=False,
            ),
            outward_support_condition_provenance=self.outward_audit,
            physical_questions_audit=self.physical_audit,
            claim_statuses=dict(
                DERIVED='Retained scalar, stress, kinetic/current, matching and port laws; conditional statements keep their domain assumptions',
                EVALUATED='This bounded source/provenance audit and its reproducibility checks; no physical support-loss operands',
                CONTROL_ONLY='Previously evaluated finite KKT/heat controls and diagnostic attachment matrices; unchanged and not rerun',
                UNEVALUATED='Selected event, transported mode, normalized normal source, seven-port values, stationary base and physical downstream quantities',
                OWNER_DEFINITION_GAP=FIRST_MISSING_DEFINITION,
            ),
            required_outputs={x.name: x.report() for x in self.outputs},
            normal_section=dict(
                equation='xi_psi^(s)=psi_star^(s) n_star^(s), with the owned stratum embedding pullback',
                full_active_section_required=True,
                registered_regular_strata=['M8', 'M5+', 'M5-', 'M4'],
                active_regular_strata=None,
                event_child_copies='Two trace copies of one abstract carrier; inherited opposite outward conormals',
                nonnull_normal='Owned unit normal', null_piece='Owned conormal-density convention required',
                corners='Boundaries of regular carrier pieces, not an independently selected carrier action',
                pregeometry_membrane_installed=False,
                source_parameter='dX_embed/ds|_0=xi_psi',
                canonical_seven_port_order=list(PORT_ORDER),
                seven_port_formula='[T u_psi+(D_psi T)q;D_psi P;D_psi F-D_psi G-D2P[X_flow,u_psi]-DP[D_psi X_flow]]',
                flow_embedding_distinction='X_flow in DP[X_flow] is the Euler-Dirac phase-flow tangent; X_embed is the carrier embedding displaced by xi_psi',
                historical_scalar_b_psi_is_seven_port=False,
                moving_reaction_formula='D(B Lambda)[xi_psi]=DB[xi_psi] Lambda+B D Lambda[xi_psi]',
            ),
            normalization=dict(
                preferred_condition='<psi_star,I_star psi_star>=1',
                inertia='Full same-classical-owner physical-clock kinetic form, including owned bulk response',
                positivity_required=True, normalization_evaluated=False,
                base_i=None, i_v=None, i_J=None, i_vJ=None,
                zero_total_inertia_jets_inferred=False,
                Euclidean_or_surface_only_norm_used=False,
            ),
            action_sectors=self.classical_audit['sector_accounting'],
            classical_owner_provenance=self.classical_audit,
            constraint_system=dict(
                metric_matcher='h_ab-gamma_eps,ab=0 with its existing reaction multiplier',
                retained_groups='Owned Hamiltonian/momentum/Gauss, BRST-compatible and reset/incidence constraints in their existing domains',
                multiplier_terms='lambda^dagger R exactly once, with inherited signed pairings',
                source_dependent_terms='R_s,R_eta,s^dagger lambda,lambda^dagger R_ss retained by the existing direct KKT machinery',
                stationary_equations=['L_eta=0', 'R=0'],
                solved_stationary_base=False,
                historical_lapse_shift_or_event_multipliers_borrowed=False,
            ),
            downstream_status={name: dict(status='NOT_REACHED__EVENT_DEFINITION_STOP', value=None,
                                        blocked_by=FIRST_MISSING_DEFINITION)
                               for name in ('h_psi', 'H_KKT', 'delta_psi', 'z_psi', 'r', 'i', 'v_J_total_jets',
                                            'c', 'fixed_and_moving_length_AE4_heat', 'relative_zeta_eta',
                                            'local_subtraction', 'R_ind', 'completed_native_photon_response',
                                            'paired_electron_muon_heat', 'Pauli_readout', 'a_mu', 'g_mu')},
            first_missing_definition=self.outward_audit['first_missing_definition'],
            first_stop_is_not_a_sufficiency_theorem='Defining the cessation condition does not by itself solve the coupled physical action/domain/branch/base requirements',
            execution=dict(new_physical_KKT_solves=0, new_generic_KKT_algebra=0,
                           new_finite_control_runs=0, Gate7_campaigns=0, launch_73_recomputations=0,
                           local_QED_changes=0, primitive_photon_refinements=0, historical_artifacts_changed=False),
            exact_error_scope='Definition/provenance audit only; no numerical event, source, impedance, physical uncertainty or continuum error evaluation',
        )
        return deepcopy(payload)


def inspected_support_loss_realization(repository: Path | str = ROOT):
    """Bind the audited required outputs to one classical realization record."""
    repository = Path(repository)
    folder = repository / ARTIFACT_DIRECTORY
    classical = json.loads((folder / 'classical_owner_audit.json').read_text(encoding='utf8'))
    outward = json.loads((folder / 'outward_support_audit.json').read_text(encoding='utf8'))
    physical = json.loads((folder / 'physical_questions_audit.json').read_text(encoding='utf8'))
    binding = dict(classical_owner=CLASSICAL_OWNER, heat_owner=HEAT_OWNER,
                   starting_HEAD=STARTING_HEAD, scientific_reference=SCIENTIFIC_REFERENCE,
                   branch_rule='Continuous transported physical formation branch at separate first future support loss',
                   event_definition=FIRST_MISSING_DEFINITION,
                   base='UNEVALUATED_AT_PENDING_EVENT', domain='SAME_CLASSICAL_ACTION_DOMAIN_REQUIRED',
                   pairing='SAME_CLASSICAL_ACTION_DUAL_REQUIRED')
    binding_identity = sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    definitions = dict(
        Phi_star='Full event/child classical fields at the selected support-loss stationary base',
        Sigma_star='First future surface satisfying BOTH mode-frequency equality and action-defined outward-support cessation',
        psi_star='Continuously transported initiating physical mode; complete compatible stratum normal section',
        xi_psi='psi_star n_star in the retained stratum embedding and orientation convention',
        b_psi='Existing boundary kinematic image with exactly 3 trace + 2 canonical momentum + 2 dynamic-flux entries',
        S_SL='Registered active classical event/child bulk + selected minimal membrane + existing boundary/corner completion on one pullback',
        R='Existing uneliminated same-owner metric, gauge/BRST, reset/incidence and other constraints; not additional restoring action sectors',
        pairing='Geometric weak-action dual on the same constrained physical chart and transported normal section',
        domain='One compatible regular-stratum event/child trace, conormal, reset and gauge/BRST domain at Sigma_star',
        stationary_base='Same-owner base satisfying L_eta=0 and R=0, with explicit chart pullback if needed',
        **{'lambda': 'Actual stationary constraint multipliers in that same classical chart, not historical cached coordinates'},
    )
    provenances = (
        'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        'src/bhsm/interface/owner_authorized_encapsulation_interface_action.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        ARTIFACT_DIRECTORY + '/classical_owner_audit.json',
        ARTIFACT_DIRECTORY + '/outward_support_audit.json',
        ARTIFACT_DIRECTORY + '/physical_questions_audit.json',
    )
    outputs = tuple(RealizationOutput(name, binding_identity, definitions[name], provenances)
                    for name in REQUIRED_OUTPUTS)
    return SupportLossClassicalRealization(binding_identity, outputs, classical, outward, physical)
