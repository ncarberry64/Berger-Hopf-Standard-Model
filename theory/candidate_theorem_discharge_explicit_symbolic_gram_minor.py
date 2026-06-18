"""Candidate utilities for PO-BH-34 explicit symbolic Gram/minor audit.

This module constructs explicit symbolic feature matrices and 3x3 minor
candidates from the Wigner/Hopf labels already present in the theorem-discharge
chain. It does not claim a nonzero determinant, numerical Yukawa values, CKM,
PMNS, or replacement readiness.
"""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import combinations


class GramMinorStatus(str, Enum):
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    PARTIAL = "PARTIAL"
    OPEN = "OPEN"


@dataclass(frozen=True)
class ModeLabel:
    sector: str
    index: int
    q: int
    j: int


@dataclass(frozen=True)
class HarmonicLabel:
    k: int
    ell: Fraction
    n: Fraction
    m: Fraction


@dataclass(frozen=True)
class FeatureAtom:
    name: str
    derivative: str
    m_selector: str


@dataclass(frozen=True)
class MatrixEntry:
    row: FeatureAtom
    column: ModeLabel
    harmonic: HarmonicLabel
    expression: str


FEATURE_ATOMS = (
    FeatureAtom("value_lowest", "value", "lowest"),
    FeatureAtom("value_center", "value", "center"),
    FeatureAtom("value_highest", "value", "highest"),
    FeatureAtom("d_alpha_lowest", "d_alpha", "lowest"),
    FeatureAtom("d_beta_center", "d_beta", "center"),
    FeatureAtom("d_gamma_highest", "d_gamma", "highest"),
    FeatureAtom("d2_local_center", "d2_local", "center"),
)


def k_from_qj(q: int, j: int) -> int:
    return q + 2 * j


def ell_from_k(k: int) -> Fraction:
    return Fraction(k, 2)


def n_from_q(q: int) -> Fraction:
    return Fraction(q, 2)


def allowed_m_values(ell: Fraction) -> tuple[Fraction, ...]:
    return tuple(-ell + i for i in range(int(2 * ell) + 1))


def generation_modes() -> dict[str, tuple[ModeLabel, ...]]:
    return {
        "reference_charged": (
            ModeLabel("reference_charged", 0, 0, 0),
            ModeLabel("reference_charged", 1, 1, 2),
            ModeLabel("reference_charged", 2, 3, 3),
        ),
        "reference_neutral": (
            ModeLabel("reference_neutral", 0, 0, 0),
            ModeLabel("reference_neutral", 1, 3, 0),
            ModeLabel("reference_neutral", 2, 1, 1),
        ),
        "cyclic_upper": (
            ModeLabel("cyclic_upper", 0, 0, 0),
            ModeLabel("cyclic_upper", 1, 6, 0),
            ModeLabel("cyclic_upper", 2, 8, 1),
        ),
        "cyclic_lower": (
            ModeLabel("cyclic_lower", 0, 0, 0),
            ModeLabel("cyclic_lower", 1, 0, 3),
            ModeLabel("cyclic_lower", 2, 4, 2),
        ),
    }


def harmonic_label_for_mode(mode: ModeLabel, atom: FeatureAtom) -> HarmonicLabel:
    k = k_from_qj(mode.q, mode.j)
    ell = ell_from_k(k)
    n = n_from_q(mode.q)
    m_values = allowed_m_values(ell)
    if atom.m_selector == "lowest":
        m = m_values[0]
    elif atom.m_selector == "highest":
        m = m_values[-1]
    elif atom.m_selector == "center":
        m = n if n in m_values else m_values[len(m_values) // 2]
    else:
        raise ValueError(f"unknown m selector: {atom.m_selector}")
    return HarmonicLabel(k=k, ell=ell, n=n, m=m)


def wigner_jet_expression(h: HarmonicLabel, derivative: str) -> str:
    base = (
        f"D^({h.ell})_({h.m},{h.n})(y0)"
        f"=exp(-i*{h.m}*alpha0)*d^({h.ell})_({h.m},{h.n})(beta0)"
        f"*exp(-i*{h.n}*gamma0)"
    )
    if derivative == "value":
        return base
    return f"{derivative}[{base}]"


def feature_matrix(sector: str) -> tuple[tuple[MatrixEntry, ...], ...]:
    modes = generation_modes()[sector]
    rows: list[tuple[MatrixEntry, ...]] = []
    for atom in FEATURE_ATOMS:
        row = []
        for mode in modes:
            harmonic = harmonic_label_for_mode(mode, atom)
            row.append(
                MatrixEntry(
                    row=atom,
                    column=mode,
                    harmonic=harmonic,
                    expression=wigner_jet_expression(harmonic, atom.derivative),
                )
            )
        rows.append(tuple(row))
    return tuple(rows)


def symbolic_minor_candidates(sector: str, max_candidates: int = 5) -> tuple[dict, ...]:
    matrix = feature_matrix(sector)
    candidates = []
    for row_indexes in combinations(range(len(matrix)), 3):
        row_names = tuple(matrix[i][0].row.name for i in row_indexes)
        determinant = "det(" + ",".join(row_names) + f"; columns=g0,g1,g2; sector={sector})"
        candidates.append(
            {
                "sector": sector,
                "row_indexes": row_indexes,
                "row_names": row_names,
                "determinant_symbol": determinant,
                "entries_tied_to_wigner_labels": True,
                "nonzero_proven": False,
                "status": GramMinorStatus.PARTIAL.value,
            }
        )
        if len(candidates) >= max_candidates:
            break
    return tuple(candidates)


def all_symbolic_minor_candidates() -> dict[str, tuple[dict, ...]]:
    return {sector: symbolic_minor_candidates(sector) for sector in generation_modes()}


def global_peter_weyl_independence_supported() -> bool:
    """Distinct matrix coefficients are globally independent in the scaffold."""
    return True


def local_jet_injectivity_proven() -> bool:
    return False


def wigner_hopf_jet_independence_derived() -> bool:
    return False


def explicit_nonzero_3x3_minor_derived() -> bool:
    return False


def finite_width_moment_non_degeneracy_condition_defined() -> bool:
    return True


def finite_width_moment_non_degeneracy_derived() -> bool:
    return False


def generic_rank_three_support_condition_defined() -> bool:
    return True


def generic_rank_three_support_derived() -> bool:
    return False


def finite_width_rank_three_derived() -> bool:
    return False


def numerical_yukawa_values_derived() -> bool:
    return False


def ckm_values_derived() -> bool:
    return False


def pmns_values_derived() -> bool:
    return False


def replacement_claim_ready() -> bool:
    return False


def status() -> GramMinorStatus:
    if explicit_nonzero_3x3_minor_derived() and wigner_hopf_jet_independence_derived():
        return GramMinorStatus.DERIVED_CONDITIONAL
    return GramMinorStatus.PARTIAL


def degenerate_loci() -> tuple[str, ...]:
    return (
        "axis collapse such as beta0=0 without a derived finite-width rescue term",
        "vanishing universal finite-width second-moment block",
        "local Wigner/Hopf jet map not injective at y0",
        "coincident reduced-Wigner beta factors across the three generation labels",
        "moment contractions projecting all three columns onto a lower-dimensional subspace",
    )


def non_tautology_guardrails() -> tuple[str, ...]:
    return (
        "minor entries are Wigner/Hopf jet expressions tied to k, ell, n, and m labels",
        "nonzero determinant is not asserted from independent formal variables alone",
        "beta0 is not chosen to fit masses or mixing",
        "finite-width moments are universal and not generation-fitted",
        "CKM, PMNS, and numerical Yukawa values are not imported",
    )


def proof_discharge_ledger() -> dict[str, str]:
    return {
        "PO-BH-34": (
            "PARTIAL: explicit symbolic feature matrices and minor candidates "
            "constructed; nonzero symbolic minor and Wigner/Hopf jet-independence "
            "theorem remain open"
        )
    }

