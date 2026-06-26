from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

NEUTRINO_SECTOR_EQUATION = "q + 2j = 3"
NEUTRINO_LEDGER: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]] = (
    (0, 0),
    (3, 0),
    (1, 1),
)
NEUTRINO_TANGENT = (-2, 1)

NEUTRAL_OPERATOR_SYMBOLIC = "NEUTRAL_OPERATOR_SYMBOLIC"
NEUTRAL_OPERATOR_UNIT_DIAGNOSTIC = "NEUTRAL_OPERATOR_UNIT_DIAGNOSTIC"
NEUTRAL_OPERATOR_TOPOGRAPHIC_MIXED_DIAGNOSTIC = "NEUTRAL_OPERATOR_TOPOGRAPHIC_MIXED_DIAGNOSTIC"

STATUS_TABLE = {
    "neutral_sector_operator_kernel_v1": "STRUCTURALLY_MOTIVATED_CANDIDATE",
    "neutrino_mode_ledger": "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
    "neutral_Hessian_symbolic_form": "OPEN_LOCALIZABLE",
    "neutral_Hessian_branch_N0_isotropic": "NEUTRAL_HESSIAN_BRANCH_CANDIDATE",
    "neutral_Hessian_branch_N1_charged_like": "STRUCTURALLY_POSSIBLE_NOT_DERIVED",
    "neutral_Hessian_branch_N2_topographic_mixed": "STRUCTURALLY_MOTIVATED_CANDIDATE",
    "neutral_Hessian_branch_N3_tangent_adapted": "OPEN_LOCALIZABLE",
    "neutral_eta_source": "OPEN_LOCALIZABLE",
    "neutral_beta_bridge_source": "OPEN_LOCALIZABLE",
    "neutral_kappa_bridge_source": "OPEN_LOCALIZABLE",
    "neutral_threshold_operator": "OPEN",
    "PMNS_structural_source": "STRUCTURALLY_MOTIVATED_CANDIDATE",
    "PMNS_numerical_closure": "OPEN",
    "neutral_numerical_closure": "OPEN",
    "numerical_closure": "OPEN",
}

FORBIDDEN_DERIVATION_INPUTS = (
    "observed neutrino masses",
    "neutrino mass splittings",
    "PMNS data",
    "observed charged masses",
    "measured alpha",
    "empirical target ratios",
    "cosmological neutrino bounds",
    "post-comparison residuals",
)


@dataclass(frozen=True)
class NeutralHessianBranch:
    branch_id: str
    name: str
    a: Fraction
    b: Fraction
    c: Fraction
    status: str
    notes: str


@dataclass(frozen=True)
class HessianPositivityDiagnostic:
    branch_id: str
    a_positive: bool
    c_positive: bool
    determinant: Fraction
    positive_semidefinite: bool
    positive_definite: bool


@dataclass(frozen=True)
class NeutralCostDiagnostic:
    branch_id: str
    mode: Tuple[int, int]
    cost: Fraction


@dataclass(frozen=True)
class TangentNormDiagnostic:
    branch_id: str
    tangent: Tuple[int, int]
    norm_sq: Fraction


@dataclass(frozen=True)
class NeutralOperatorTemplate:
    readout_mode: str
    topology_edges: Tuple[Tuple[int, int], ...]
    direct_0_2_bridge_enabled: bool
    eta_nu: str
    beta_nu: str
    kappa_nu: str
    matrix_template: Tuple[Tuple[str, str, str], Tuple[str, str, str], Tuple[str, str, str]]
    status: str
    physical_prediction: bool


@dataclass(frozen=True)
class NeutralThresholdRecord:
    slot: int
    mode: Tuple[int, int]
    is_reference_slot: bool
    status: str
    threshold_factor: Fraction | None
    insertion: str | None


@dataclass(frozen=True)
class PMNSStructuralPlaceholder:
    formula: str
    charged_source: str
    neutral_source: str
    structural_status: str
    numerical_status: str


@dataclass(frozen=True)
class NeutralSectorVerdict:
    neutral_sector_status: str
    selected_hessian_branch: str | None
    neutral_numerical_closure: str
    PMNS_numerical_closure: str
    theorem_complete: bool


def fraction_string(value: Fraction | None) -> str | None:
    if value is None:
        return None
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _convert(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, tuple):
        return [_convert(item) for item in value]
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    return value


def neutrino_sector_equation_value(q: int, j: int) -> int:
    return q + 2 * j


def nonzero_neutrino_modes() -> Tuple[Tuple[int, int], Tuple[int, int]]:
    return NEUTRINO_LEDGER[1:]


def tangent_difference() -> Tuple[int, int]:
    first, second = nonzero_neutrino_modes()
    return second[0] - first[0], second[1] - first[1]


def neutral_hessian_symbolic_form() -> Dict[str, str]:
    return {
        "matrix": "[[a,b],[b,c]]",
        "cost": "N_nu(q,j)=a q^2 + 2b qj + c j^2",
        "PSD_conditions": "a>0, c>0, ac-b^2>=0",
    }


def neutral_hessian_branches() -> Tuple[NeutralHessianBranch, ...]:
    return (
        NeutralHessianBranch(
            branch_id="N0",
            name="diagonal isotropic neutral Hessian",
            a=Fraction(1),
            b=Fraction(0),
            c=Fraction(1),
            status=STATUS_TABLE["neutral_Hessian_branch_N0_isotropic"],
            notes="No-fit isotropic diagnostic branch.",
        ),
        NeutralHessianBranch(
            branch_id="N1_rho_1",
            name="charged-like neutral Hessian rho_ch=1 placeholder",
            a=Fraction(1),
            b=Fraction(0),
            c=Fraction(1),
            status=STATUS_TABLE["neutral_Hessian_branch_N1_charged_like"],
            notes="Charged-like reuse is not preferred unless an action source identifies neutral and charged stiffness.",
        ),
        NeutralHessianBranch(
            branch_id="N1_rho_2",
            name="charged-like neutral Hessian rho_ch=2 placeholder",
            a=Fraction(1),
            b=Fraction(0),
            c=Fraction(2),
            status=STATUS_TABLE["neutral_Hessian_branch_N1_charged_like"],
            notes="Charged-like reuse is not preferred unless an action source identifies neutral and charged stiffness.",
        ),
        NeutralHessianBranch(
            branch_id="N1_rho_3",
            name="charged-like neutral Hessian rho_ch=3 placeholder",
            a=Fraction(1),
            b=Fraction(0),
            c=Fraction(3),
            status=STATUS_TABLE["neutral_Hessian_branch_N1_charged_like"],
            notes="Charged-like reuse is not preferred unless an action source identifies neutral and charged stiffness.",
        ),
        NeutralHessianBranch(
            branch_id="N2",
            name="topographic mixed neutral Hessian",
            a=Fraction(1),
            b=Fraction(1),
            c=Fraction(2),
            status=STATUS_TABLE["neutral_Hessian_branch_N2_topographic_mixed"],
            notes="Neutral/topographic sector permits q-j mixing; this is a diagnostic candidate.",
        ),
    )


def positivity_diagnostic(branch: NeutralHessianBranch) -> HessianPositivityDiagnostic:
    determinant = branch.a * branch.c - branch.b * branch.b
    return HessianPositivityDiagnostic(
        branch_id=branch.branch_id,
        a_positive=branch.a > 0,
        c_positive=branch.c > 0,
        determinant=determinant,
        positive_semidefinite=branch.a > 0 and branch.c > 0 and determinant >= 0,
        positive_definite=branch.a > 0 and branch.c > 0 and determinant > 0,
    )


def neutral_cost(q: int, j: int, branch: NeutralHessianBranch) -> Fraction:
    return branch.a * q * q + 2 * branch.b * q * j + branch.c * j * j


def cost_diagnostics() -> Tuple[NeutralCostDiagnostic, ...]:
    rows = []
    for branch in neutral_hessian_branches():
        for mode in nonzero_neutrino_modes():
            rows.append(
                NeutralCostDiagnostic(
                    branch_id=branch.branch_id,
                    mode=mode,
                    cost=neutral_cost(mode[0], mode[1], branch),
                )
            )
    return tuple(rows)


def tangent_norm(branch: NeutralHessianBranch) -> Fraction:
    q, j = NEUTRINO_TANGENT
    return neutral_cost(q, j, branch)


def tangent_norm_diagnostics() -> Tuple[TangentNormDiagnostic, ...]:
    return tuple(
        TangentNormDiagnostic(
            branch_id=branch.branch_id,
            tangent=NEUTRINO_TANGENT,
            norm_sq=tangent_norm(branch),
        )
        for branch in neutral_hessian_branches()
    )


def neutral_operator_template(
    readout_mode: str = NEUTRAL_OPERATOR_SYMBOLIC,
) -> NeutralOperatorTemplate:
    if readout_mode == NEUTRAL_OPERATOR_SYMBOLIC:
        eta, beta, kappa = "eta_nu_OPEN", "beta_nu_OPEN", "kappa_nu_OPEN"
        lam1, lam2 = "eta_nu N_nu(3,0)", "eta_nu N_nu(1,1)"
        status = "SYMBOLIC_OPEN"
        physical = False
    elif readout_mode == NEUTRAL_OPERATOR_UNIT_DIAGNOSTIC:
        eta, beta, kappa = "1_DIAGNOSTIC", "0_DIAGNOSTIC", "0_DIAGNOSTIC"
        lam1, lam2 = "N_nu(3,0)", "N_nu(1,1)"
        status = "UNIT_DIAGNOSTIC_NOT_PHYSICAL_PREDICTION"
        physical = False
    elif readout_mode == NEUTRAL_OPERATOR_TOPOGRAPHIC_MIXED_DIAGNOSTIC:
        eta, beta, kappa = "1_DIAGNOSTIC", "0_DIAGNOSTIC", "0_DIAGNOSTIC"
        lam1, lam2 = "N2(3,0)=9", "N2(1,1)=5"
        status = "TOPOGRAPHIC_MIXED_DIAGNOSTIC_NOT_PHYSICAL_PREDICTION"
        physical = False
    else:
        raise ValueError(f"unknown neutral readout mode: {readout_mode}")
    return NeutralOperatorTemplate(
        readout_mode=readout_mode,
        topology_edges=((0, 1), (1, 2)),
        direct_0_2_bridge_enabled=False,
        eta_nu=eta,
        beta_nu=beta,
        kappa_nu=kappa,
        matrix_template=(
            ("0", beta, "0"),
            (beta, lam1, kappa),
            ("0", kappa, lam2),
        ),
        status=status,
        physical_prediction=physical,
    )


def neutral_threshold_records() -> Tuple[NeutralThresholdRecord, ...]:
    rows = []
    for slot, mode in enumerate(NEUTRINO_LEDGER):
        is_reference = slot == 0 or mode == (0, 0)
        rows.append(
            NeutralThresholdRecord(
                slot=slot,
                mode=mode,
                is_reference_slot=is_reference,
                status=(
                    "REFERENCE_SLOT_NOT_THRESHOLD_TARGET"
                    if is_reference
                    else "NO_THRESHOLD_SOURCE_FOUND"
                ),
                threshold_factor=None,
                insertion=None,
            )
        )
    return tuple(rows)


def PMNS_placeholder() -> PMNSStructuralPlaceholder:
    return PMNSStructuralPlaceholder(
        formula="U_PMNS = U_l^dagger U_nu",
        charged_source="charged-lepton K_l",
        neutral_source="neutral K_nu",
        structural_status=STATUS_TABLE["PMNS_structural_source"],
        numerical_status=STATUS_TABLE["PMNS_numerical_closure"],
    )


def verdict() -> NeutralSectorVerdict:
    return NeutralSectorVerdict(
        neutral_sector_status=STATUS_TABLE["neutral_sector_operator_kernel_v1"],
        selected_hessian_branch=None,
        neutral_numerical_closure=STATUS_TABLE["neutral_numerical_closure"],
        PMNS_numerical_closure=STATUS_TABLE["PMNS_numerical_closure"],
        theorem_complete=False,
    )


def _dataclass_rows(rows):
    out = []
    for row in rows:
        item = asdict(row)
        out.append({key: _convert(value) for key, value in item.items()})
    return out


def report_as_dict() -> Dict[str, object]:
    branches = neutral_hessian_branches()
    return {
        "id": "PO-BH-neutral-sector-operator-kernel-v1",
        "title": "Neutral Sector Operator Kernel v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "sector_equation": NEUTRINO_SECTOR_EQUATION,
        "ledger": [list(mode) for mode in NEUTRINO_LEDGER],
        "ledger_status": STATUS_TABLE["neutrino_mode_ledger"],
        "tangent_generator": list(NEUTRINO_TANGENT),
        "hessian_symbolic_form": neutral_hessian_symbolic_form(),
        "hessian_branches": _dataclass_rows(branches),
        "positivity_diagnostics": _dataclass_rows(
            tuple(positivity_diagnostic(branch) for branch in branches)
        ),
        "cost_diagnostics": _dataclass_rows(cost_diagnostics()),
        "tangent_norm_diagnostics": _dataclass_rows(tangent_norm_diagnostics()),
        "neutral_operator_templates": {
            mode: {key: _convert(value) for key, value in asdict(neutral_operator_template(mode)).items()}
            for mode in (
                NEUTRAL_OPERATOR_SYMBOLIC,
                NEUTRAL_OPERATOR_UNIT_DIAGNOSTIC,
                NEUTRAL_OPERATOR_TOPOGRAPHIC_MIXED_DIAGNOSTIC,
            )
        },
        "threshold_records": _dataclass_rows(neutral_threshold_records()),
        "PMNS_placeholder": {key: _convert(value) for key, value in asdict(PMNS_placeholder()).items()},
        "statuses": STATUS_TABLE,
        "verdict": {key: _convert(value) for key, value in asdict(verdict()).items()},
        "claim_boundary": (
            "Neutral sector operator kernel is a symbolic/candidate scaffold; "
            "no neutrino mass or PMNS numerical closure is claimed."
        ),
    }
