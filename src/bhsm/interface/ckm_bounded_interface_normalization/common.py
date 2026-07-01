"""Shared contracts for the v2.7 bounded-interface normalization audit."""

from __future__ import annotations

from bhsm.interface.charged_current_action.common import channel_dimensions, input_guard, repository_root


STATUS_BOUNDED = "ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM"
STATUS_OPEN_ACTION = "OPEN_MISSING_NORMALIZED_PROJECTOR_SANDWICH_ACTION_TERM"
STATUS_OPEN_PROJECTORS = "OPEN_MISSING_PROJECTOR_DOMAIN_CODOMAIN_SELECTION"
STATUS_OPEN_PAIR = "OPEN_MISSING_PAIRED_TERM_NORMALIZATION"
STATUS_OPEN_IDENTIFICATION = "OPEN_MISSING_CKM_IDENTIFICATION_THEOREM"
STATUS_OPEN_SELECTION = "OPEN_MISSING_CKM_TRANSPORT_SPACE_SELECTION"
STATUS_MULTIPLE = "MULTIPLE_COMPETING_TRANSPORT_SPACES"
STATUS_REJECTED_BOUNDED = "REJECTED_BOUNDED_TERM_IMPLIES_ACTION_SELECTION"
STATUS_REJECTED_ARITHMETIC = "REJECTED_PROJECTOR_ARITHMETIC_IMPLIES_CKM_DERIVATION"
STATUS_RETIRED_MAXIMAL = "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"

CANDIDATE_ACTION_FORM = (
    "S_CKM ~ integral dmu_B [psi_d^dagger Pi_d J_du Pi_u psi_u "
    "+ psi_u^dagger Pi_u J_ud Pi_d psi_d]"
)
CANDIDATE_SPACE = "Hom(V_u,V_d) direct_sum Hom(V_d,V_u)"

REQUIRED_BOUNDARY_STATEMENTS = (
    "L_CKM_charged_current_bounded is a bounded interface term, not automatically a normalized action-selected transport operator.",
    "A normalized projector-sandwiched action term requires boundary/action measure, coefficient normalization, sector projectors, and action provenance.",
    "Projector arithmetic alone does not derive the CKM exponent.",
    "The CKM exponent remains not derived unless the normalized action selects a CKM transport space and the CKM identification theorem closes.",
    "No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.",
)
