"""BHSM topographic action scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from scalar_action import CURVATURE_SCREENED, DERIVATIVE_SCREENED, VIRTUAL_ONLY


@dataclass(frozen=True)
class TopographicActionTerm:
    """One symbolic topographic action term."""

    id: str
    expression: str
    channel: str
    derivative_order: int
    curvature_filtered: bool
    virtual_only: bool
    suppresses_fifth_force: bool
    status: str
    limitations: tuple[str, ...]


def topographic_action_terms() -> tuple[TopographicActionTerm, ...]:
    """Return symbolic topographic action terms."""

    return (
        TopographicActionTerm(
            id="TA1",
            expression="(nabla_mu T_loc)^2 / Lambda_T^2",
            channel=DERIVATIVE_SCREENED,
            derivative_order=2,
            curvature_filtered=False,
            virtual_only=False,
            suppresses_fifth_force=True,
            status="DERIVATIVE_SCREENING_SCAFFOLD",
            limitations=("Low-energy derivative suppression must be derived from full topographic action.",),
        ),
        TopographicActionTerm(
            id="TA2",
            expression="K[rho_Phi] T_loc^2",
            channel=CURVATURE_SCREENED,
            derivative_order=0,
            curvature_filtered=True,
            virtual_only=False,
            suppresses_fifth_force=True,
            status="CURVATURE_SCREENING_SCAFFOLD",
            limitations=("Curvature/profile positivity must be proven in the complete action.",),
        ),
        TopographicActionTerm(
            id="TA3",
            expression="off-shell T_loc exchange",
            channel=VIRTUAL_ONLY,
            derivative_order=0,
            curvature_filtered=False,
            virtual_only=True,
            suppresses_fifth_force=True,
            status="VIRTUAL_ONLY_ONTOLOGY_LINKED",
            limitations=("Virtual-only classification is ontology-linked, not a full path-integral proof.",),
        ),
    )
