"""Candidate utilities for PO-BH-33 generic finite-width feature-rank scaffold.

This module is symbolic. It defines feature labels and rank-support
guardrails without claiming a nonzero determinant or numerical Yukawa values.
"""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction


class RankStatus(str, Enum):
    SCAFFOLD_DERIVED_CONDITIONAL = "SCAFFOLD_DERIVED_CONDITIONAL"
    NOT_PROVEN = "NOT_PROVEN"
    OPEN = "OPEN"


@dataclass(frozen=True)
class ModeLabel:
    sector: str
    index: int
    q: int
    j: int


@dataclass(frozen=True)
class FeatureLabel:
    sector: str
    index: int
    k: int
    ell: Fraction
    n: Fraction
    m: Fraction
    feature_kind: str


FEATURE_KINDS = ("value", "d_alpha", "d_beta", "d_gamma", "d2_local")


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


def feature_labels_for_mode(mode: ModeLabel) -> tuple[FeatureLabel, ...]:
    k = k_from_qj(mode.q, mode.j)
    ell = ell_from_k(k)
    n = n_from_q(mode.q)
    labels = []
    for m in allowed_m_values(ell):
        for kind in FEATURE_KINDS:
            labels.append(
                FeatureLabel(
                    sector=mode.sector,
                    index=mode.index,
                    k=k,
                    ell=ell,
                    n=n,
                    m=m,
                    feature_kind=kind,
                )
            )
    return tuple(labels)


def all_feature_labels() -> dict[str, tuple[FeatureLabel, ...]]:
    return {
        f"{mode.sector}:{mode.index}": feature_labels_for_mode(mode)
        for modes in generation_modes().values()
        for mode in modes
    }


def finite_width_moment_scaffold() -> tuple[str, ...]:
    return ("M0", "M_alpha_beta", "M_alpha_gamma", "M_beta_beta", "M_beta_gamma", "M_gamma_gamma")


def symbolic_gram_rank_condition() -> str:
    return (
        "Rank-three support requires at least one nonzero symbolic 3x3 minor "
        "of the feature Gram matrix after universal finite-width moment contractions."
    )


def generic_rank_supported_scaffold() -> bool:
    return True


def nonzero_symbolic_determinant_derived() -> bool:
    return False


def feature_rank_independence_derived() -> bool:
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


def proof_discharge_ledger() -> dict:
    return {
        "PO-BH-33": (
            "PARTIAL: generic finite-width feature-rank scaffold derived; "
            "nonzero symbolic determinant and rank-three Yukawa theorem remain open"
        )
    }
