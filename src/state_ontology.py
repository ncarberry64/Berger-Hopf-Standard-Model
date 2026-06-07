"""BHSM v1.3F state ontology and particle/mode classification ledger.

This module separates observable particles from internal modes, virtual
excitations, dressing contributions, composite states, lifted modes, screened
topographic states, and forbidden extra-light states. It is semantic/audit
infrastructure only; it does not change BHSM predictions or H_T logic.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class StateCategory(StrEnum):
    """Allowed BHSM state ontology categories."""

    ON_SHELL_SM_PARTICLE = "ON_SHELL_SM_PARTICLE"
    COMPOSITE_QCD_STATE = "COMPOSITE_QCD_STATE"
    INTERNAL_BERGER_HOPF_MODE = "INTERNAL_BERGER_HOPF_MODE"
    VIRTUAL_EXCITATION = "VIRTUAL_EXCITATION"
    DRESSING_CONTRIBUTION = "DRESSING_CONTRIBUTION"
    HEAVY_LIFTED_STATE = "HEAVY_LIFTED_STATE"
    SCREENED_TOPOGRAPHIC_STATE = "SCREENED_TOPOGRAPHIC_STATE"
    FORBIDDEN_EXTRA_LIGHT_STATE = "FORBIDDEN_EXTRA_LIGHT_STATE"
    OPEN_UNCLASSIFIED = "OPEN_UNCLASSIFIED"


@dataclass(frozen=True)
class BHSMState:
    """A state or contribution in the BHSM ontology."""

    id: str
    name: str
    sector: str
    description: str
    sm_field: bool = False
    on_shell: bool = False
    composite: bool = False
    internal_mode: bool = False
    virtual: bool = False
    dressing: bool = False
    above_ht_gap: bool = False
    screened: bool = False
    higgs_projected: bool = False
    experimentally_identified: bool = False
    couples_as_observable: bool = False
    light: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StateClassification:
    """Classification result for one BHSM state."""

    state_id: str
    category: StateCategory
    observable_particle: bool
    virtual_or_dressing: bool
    forbidden_extra_light: bool
    rationale: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class StateOntologyRule:
    """One ontology rule used for state classification."""

    id: str
    statement: str
    category: StateCategory | None
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class StateOntologyLedger:
    """Ledger of states, rules, and classifications."""

    rules: tuple[StateOntologyRule, ...]
    states: tuple[BHSMState, ...]
    classifications: tuple[StateClassification, ...]
    theorem_complete: bool


@dataclass(frozen=True)
class StateOntologyReport:
    """BHSM v1.3F state ontology report."""

    title: str
    ledger: StateOntologyLedger
    category_counts: dict[str, int]
    claim_boundary: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def state_ontology_rules() -> tuple[StateOntologyRule, ...]:
    """Return the BHSM v1.3F state ontology rules R1-R8."""

    return (
        StateOntologyRule(
            id="R1",
            statement="Standard Model elementary particles are real/on-shell particle states only if they correspond to the accepted SM field ledger.",
            category=StateCategory.ON_SHELL_SM_PARTICLE,
            limitations=("This ontology does not derive the SM field ledger.",),
        ),
        StateOntologyRule(
            id="R2",
            statement="Composite hadrons, mesons, baryons, resonances, and bound states are downstream QCD composite states, not elementary BHSM ledger entries.",
            category=StateCategory.COMPOSITE_QCD_STATE,
            limitations=("Composite classification is semantic and does not solve QCD confinement.",),
        ),
        StateOntologyRule(
            id="R3",
            statement="Internal Berger-Hopf eigenmodes are not automatically observable particles.",
            category=StateCategory.INTERNAL_BERGER_HOPF_MODE,
            limitations=("The full internal spectrum remains under H_T audit.",),
        ),
        StateOntologyRule(
            id="R4",
            statement="Virtual charm, top, quark, lepton, gauge, or scalar contributions are virtual excitations or dressing contributions unless they correspond to on-shell states.",
            category=StateCategory.VIRTUAL_EXCITATION,
            limitations=("Loop/dressing language is an ontology distinction, not a new numerical prediction.",),
        ),
        StateOntologyRule(
            id="R5",
            statement="Virtual-environment corrections such as Z_virt^{u,2}=1/2 are dressing contributions, not new particles.",
            category=StateCategory.DRESSING_CONTRIBUTION,
            limitations=("The dressed branch remains a candidate branch, not canonical adoption.",),
        ),
        StateOntologyRule(
            id="R6",
            statement="Any additional internal mode below the H_T gap that couples as an observable on-shell state is a forbidden extra-light state unless experimentally identified.",
            category=StateCategory.FORBIDDEN_EXTRA_LIGHT_STATE,
            limitations=("The full H_T no-extra-light theorem remains scaffolded, not proven.",),
        ),
        StateOntologyRule(
            id="R7",
            statement="Heavy internal modes above the Hopf/H_T lift scale are heavy lifted states.",
            category=StateCategory.HEAVY_LIFTED_STATE,
            limitations=("The full H_T spectrum is still open.",),
        ),
        StateOntologyRule(
            id="R8",
            statement="Scalar/topographic modes are allowed only if Higgs-projected, heavy, derivative-filtered, curvature-filtered, or screened; otherwise they are forbidden extra-light states.",
            category=StateCategory.SCREENED_TOPOGRAPHIC_STATE,
            limitations=("Full scalar/topographic decoupling from the action remains open.",),
        ),
    )


def standard_model_state_ledger() -> tuple[BHSMState, ...]:
    """Return representative on-shell SM field states."""

    return (
        BHSMState(
            id="electron",
            name="electron",
            sector="charged_leptons",
            description="Accepted on-shell Standard Model charged-lepton field state.",
            sm_field=True,
            on_shell=True,
            experimentally_identified=True,
            couples_as_observable=True,
            light=True,
        ),
        BHSMState(
            id="charm_quark_field",
            name="charm quark field excitation",
            sector="up_quarks",
            description="Accepted SM charm field state when treated as a real field excitation.",
            sm_field=True,
            on_shell=True,
            experimentally_identified=True,
            couples_as_observable=True,
        ),
        BHSMState(
            id="photon",
            name="photon",
            sector="gauge",
            description="Accepted on-shell SM gauge field state.",
            sm_field=True,
            on_shell=True,
            experimentally_identified=True,
            couples_as_observable=True,
            light=True,
        ),
    )


def internal_mode_state_ledger() -> tuple[BHSMState, ...]:
    """Return representative internal and lifted mode examples."""

    return (
        BHSMState(
            id="lepton_internal_mode_5_2",
            name="charged-lepton internal mode (5,2)",
            sector="charged_leptons",
            description="Berger-Hopf internal mode used in the charged-lepton ledger.",
            internal_mode=True,
            notes=("Internal mode label is not automatically an on-shell particle.",),
        ),
        BHSMState(
            id="non_sm_light_internal_mode",
            name="non-SM light internal mode below H_T gap",
            sector="internal",
            description="Hypothetical light internal mode below the H_T gap that couples as an observable on-shell state.",
            internal_mode=True,
            on_shell=True,
            light=True,
            couples_as_observable=True,
            experimentally_identified=False,
        ),
        BHSMState(
            id="heavy_complement_mode",
            name="heavy internal complement mode above 4 pi^2 v",
            sector="internal",
            description="Internal complement mode lifted above the Hopf/H_T scale.",
            internal_mode=True,
            above_ht_gap=True,
        ),
        BHSMState(
            id="screened_topographic_scalar",
            name="screened topographic scalar mode",
            sector="scalar_topographic",
            description="Scalar/topographic mode allowed through screening rather than as an extra light direct-coupled state.",
            internal_mode=True,
            screened=True,
            light=True,
        ),
    )


def virtual_environment_state_ledger() -> tuple[BHSMState, ...]:
    """Return virtual/dressing examples, including the charm-sector effect."""

    return (
        BHSMState(
            id="temporary_charm_sector_dressing",
            name="temporary charm-sector loop/dressing effect",
            sector="up_quarks",
            description="Temporary charm-sector contribution treated as virtual/off-shell or dressing structure.",
            virtual=True,
            light=False,
            notes=("Not an additional on-shell particle.",),
        ),
        BHSMState(
            id="z_virt_u2_half",
            name="Z_virt^{u,2}=1/2",
            sector="up_quarks",
            description="Virtual-environment dressing contribution for the pure-fiber middle-up mode.",
            dressing=True,
            notes=("Dressing contribution changes only c/t in the dressed candidate branch.",),
        ),
    )


def composite_qcd_state_ledger() -> tuple[BHSMState, ...]:
    """Return representative QCD composite states."""

    return (
        BHSMState(
            id="proton",
            name="proton",
            sector="qcd_composite",
            description="QCD baryon composite state.",
            composite=True,
            on_shell=True,
            experimentally_identified=True,
            couples_as_observable=True,
        ),
        BHSMState(
            id="neutron",
            name="neutron",
            sector="qcd_composite",
            description="QCD baryon composite state.",
            composite=True,
            on_shell=True,
            experimentally_identified=True,
            couples_as_observable=True,
        ),
        BHSMState(
            id="pion",
            name="pion",
            sector="qcd_composite",
            description="QCD meson composite state.",
            composite=True,
            on_shell=True,
            experimentally_identified=True,
            couples_as_observable=True,
        ),
    )


def classify_state(state: BHSMState) -> StateClassification:
    """Classify one BHSM state according to rules R1-R8."""

    rationale: list[str] = []
    limitations = ("State ontology is semantic; it does not change model predictions.",)
    if state.composite:
        category = StateCategory.COMPOSITE_QCD_STATE
        rationale.append("R2: QCD bound states are composite, not elementary BHSM ledger entries.")
    elif state.dressing:
        category = StateCategory.DRESSING_CONTRIBUTION
        rationale.append("R5: virtual-environment corrections are dressing contributions, not particles.")
    elif state.virtual:
        category = StateCategory.VIRTUAL_EXCITATION
        rationale.append("R4: off-shell temporary contributions are virtual excitations unless on-shell.")
    elif state.sm_field and state.on_shell and state.experimentally_identified:
        category = StateCategory.ON_SHELL_SM_PARTICLE
        rationale.append("R1: accepted on-shell SM field state.")
    elif state.internal_mode and state.above_ht_gap:
        category = StateCategory.HEAVY_LIFTED_STATE
        rationale.append("R7: internal complement mode is above the Hopf/H_T lift scale.")
    elif state.screened or state.higgs_projected:
        category = StateCategory.SCREENED_TOPOGRAPHIC_STATE
        rationale.append("R8: scalar/topographic mode is Higgs-projected or screened.")
    elif (
        state.internal_mode
        and state.light
        and state.on_shell
        and state.couples_as_observable
        and not state.experimentally_identified
    ):
        category = StateCategory.FORBIDDEN_EXTRA_LIGHT_STATE
        rationale.append("R6: unrecognized light observable internal state is forbidden.")
    elif state.internal_mode:
        category = StateCategory.INTERNAL_BERGER_HOPF_MODE
        rationale.append("R3: internal Berger-Hopf modes are not automatically particles.")
    else:
        category = StateCategory.OPEN_UNCLASSIFIED
        rationale.append("No ontology rule conclusively classifies this state.")

    return StateClassification(
        state_id=state.id,
        category=category,
        observable_particle=category in {StateCategory.ON_SHELL_SM_PARTICLE, StateCategory.COMPOSITE_QCD_STATE},
        virtual_or_dressing=category in {StateCategory.VIRTUAL_EXCITATION, StateCategory.DRESSING_CONTRIBUTION},
        forbidden_extra_light=category == StateCategory.FORBIDDEN_EXTRA_LIGHT_STATE,
        rationale=tuple(rationale),
        limitations=limitations,
    )


def is_observable_particle(state: BHSMState) -> bool:
    """Return whether ``state`` is an observable particle/composite state."""

    return classify_state(state).observable_particle


def is_virtual_or_dressing(state: BHSMState) -> bool:
    """Return whether ``state`` is virtual or dressing structure."""

    return classify_state(state).virtual_or_dressing


def is_forbidden_extra_light_state(state: BHSMState) -> bool:
    """Return whether ``state`` is a forbidden extra-light state."""

    return classify_state(state).forbidden_extra_light


def _all_example_states() -> tuple[BHSMState, ...]:
    return (
        standard_model_state_ledger()
        + composite_qcd_state_ledger()
        + internal_mode_state_ledger()
        + virtual_environment_state_ledger()
    )


def build_state_ontology_ledger(model: object | None = None) -> StateOntologyLedger:
    """Build the state ontology ledger.

    ``model`` is accepted for API symmetry with other BHSM ledgers but is not
    inspected; ontology classification must not depend on residuals or outputs.
    """

    del model
    states = _all_example_states()
    return StateOntologyLedger(
        rules=state_ontology_rules(),
        states=states,
        classifications=tuple(classify_state(state) for state in states),
        theorem_complete=False,
    )


def state_ontology_report(model: object | None = None) -> StateOntologyReport:
    """Return the v1.3F state ontology report."""

    ledger = build_state_ontology_ledger(model)
    counts: dict[str, int] = {category.value: 0 for category in StateCategory}
    for classification in ledger.classifications:
        counts[classification.category.value] += 1
    return StateOntologyReport(
        title="BHSM v1.3F State Ontology and Particle/Mode Classification Ledger",
        ledger=ledger,
        category_counts=counts,
        claim_boundary=(
            "BHSM v1.3F clarifies that internal modes and virtual dressing "
            "contributions are not automatically new observable particles. "
            "Extra observable light states remain forbidden unless identified "
            "experimentally or lifted/screened by the H_T/scalar-sector mechanisms."
        ),
        theorem_complete=False,
        limitations=(
            "This is a semantic and structural ontology layer, not a model-output change.",
            "It does not compute the full H_T spectrum or prove the no-extra-light theorem.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, StateCategory):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_state_ontology_json(path: str | Path) -> None:
    """Export the state ontology report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(state_ontology_report()), indent=2, sort_keys=True) + "\n")


def export_state_ontology_markdown(path: str | Path) -> None:
    """Export the state ontology report as Markdown."""

    report = state_ontology_report()
    lines = [
        "# BHSM v1.3F State Ontology",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        report.claim_boundary,
        "",
        "## Categories",
        "",
        "| Category | Count |",
        "| --- | --- |",
    ]
    for category, count in report.category_counts.items():
        lines.append(f"| `{category}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "| Rule | Category | Statement |",
            "| --- | --- | --- |",
        ]
    )
    for rule in report.ledger.rules:
        category = rule.category.value if rule.category else "OPEN"
        lines.append(f"| `{rule.id}` | `{category}` | {rule.statement} |")
    lines.extend(
        [
            "",
            "## Example Classifications",
            "",
            "| State | Category | Observable particle | Virtual/dressing | Forbidden extra-light |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    classification_by_id = {item.state_id: item for item in report.ledger.classifications}
    for state in report.ledger.states:
        classification = classification_by_id[state.id]
        lines.append(
            f"| `{state.id}` | `{classification.category.value}` | `{classification.observable_particle}` | `{classification.virtual_or_dressing}` | `{classification.forbidden_extra_light}` |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
