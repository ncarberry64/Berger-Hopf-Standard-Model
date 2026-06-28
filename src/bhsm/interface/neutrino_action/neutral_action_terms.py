"""Source-traced neutral action terms already present in BHSM."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from .common import NeutralActionTerm, guard_fields, provenance


def _term(
    root: Path,
    *,
    key: str,
    status: str,
    equation: str,
    role: str,
    coefficient: str,
    source: str,
    action_derived: bool,
    boundary: str,
    missing: str,
) -> NeutralActionTerm:
    sources = (source,) if (root / source).is_file() else ()
    return NeutralActionTerm(
        candidate_key=key,
        status=status,
        value=equation,
        unit=None,
        dimension="symbolic action term",
        numeric_value=None,
        symbolic_value=equation,
        source_type="local BHSM action or theorem-discharge source",
        source_artifacts=sources,
        source_equations=(equation,),
        provenance=provenance(sources),
        author_ontology_dependency="physical neutral boundary field and propagation/interaction support",
        claim_boundary=boundary,
        remaining_missing_object=missing,
        term_key=key,
        role=role,
        coefficient_symbol=coefficient,
        coefficient_numeric_available=False,
        action_derived=action_derived,
        **guard_fields(),
    )


def extract_neutral_action_terms(
    repository: str | Path | None = None,
) -> tuple[NeutralActionTerm, ...]:
    root = repository_path(repository)
    return (
        _term(
            root,
            key="neutral_propagation_source",
            status="CONDITIONAL_NEUTRAL_ACTION_STIFFNESS_CANDIDATE",
            equation="S_neutral_prop[Psi_nu,U_nu,R_curv] integrated over dmu_boundary dt",
            role="author-ontology propagation and curvature-response source",
            coefficient="open neutral normalization",
            source="artifacts/BHSM_author_ontology_v0_8.json",
            action_derived=False,
            boundary="The ontology supplies an action source and measure symbol, not their physical normalization.",
            missing="normalized dmu_boundary dt and neutral action coefficients",
        ),
        _term(
            root,
            key="neutral_boundary_tangential_kinetic",
            status="OPEN_MISSING_NEUTRAL_KINETIC_STIFFNESS",
            equation="1/2 chi_nu^{AB} D_A Phi D_B Phi",
            role="conditional neutral boundary kinetic response",
            coefficient="chi_nu^{AB}",
            source="data/bhsm_numerical_input_closure_map.json",
            action_derived=True,
            boundary="The variational form is conditionally derived, but chi_nu values and physical normalization are open.",
            missing="neutral tensor chi_nu^{AB}, support metric, and normalization identifying Z_nu",
        ),
        _term(
            root,
            key="neutral_boundary_normal_coupling",
            status="OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
            equation="lambda_nu Phi n.grad Phi",
            role="normal/collar coupling",
            coefficient="lambda_nu",
            source="data/bhsm_numerical_input_closure_map.json",
            action_derived=False,
            boundary="The term and its variation are localized, but the collar reduction and lambda_nu remain open.",
            missing="lambda_nu, orientation, edge condition, and admissible collar variation data",
        ),
        _term(
            root,
            key="scalar_mass_gap_analogue",
            status="CONDITIONAL_NEUTRAL_ACTION_STIFFNESS_CANDIDATE",
            equation="1/2 lambda (-nabla^2 phi-k_loc)^2",
            role="general scalar curvature-penalty analogue",
            coefficient="lambda (scalar, not A_nu)",
            source="theory/legacy_sources/v1_1/mass_gap.pdf",
            action_derived=True,
            boundary="The scalar penalty supports the action shape but does not determine the neutral A_nu coefficient.",
            missing="operator-to-neutral-action identification and neutral coefficient normalization",
        ),
        _term(
            root,
            key="neutral_collar_measure",
            status="OPEN_MISSING_BOUNDARY_MEASURE_NORMALIZATION",
            equation="dV_collar=J(Y,rho)dA d rho; J=det(I+rho S)",
            role="conditional geometric support measure",
            coefficient="J(Y,rho)",
            source="data/bhsm_numerical_input_closure_map.json",
            action_derived=True,
            boundary="The Jacobian identity is conditionally derived, but BHSM embedding, shape operator, orientation, and units remain open.",
            missing="BHSM boundary embedding, S(Y), orientation, collar width, and physical normalization",
        ),
        _term(
            root,
            key="measurement_interaction_support",
            status="CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE",
            equation="physical boundary interaction support selects non-null neutral response",
            role="response-cone support condition",
            coefficient="support indicator",
            source="artifacts/BHSM_neutral_measurement_support_ontology_v1_4.json",
            action_derived=False,
            boundary="The support condition is author-ontology backed and compatible with boundary action terms, not complete-action derived.",
            missing="variation theorem deriving the response-magnitude map and active cone from the normalized neutral action",
        ),
    )
