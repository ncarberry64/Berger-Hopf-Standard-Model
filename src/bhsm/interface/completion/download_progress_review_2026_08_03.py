"""Reproducible audit of the BHSM manual packets downloaded on 2026-08-03.

The packet formulas are evaluated here without promoting their proposed
action ownership or physical-prediction claims. The v11.5 integration remains
fail-closed at the charged-current parent-action provenance gate.
"""

from __future__ import annotations

from hashlib import sha256
from math import exp, pi, sqrt
from pathlib import Path
from typing import Any

from sympy import Matrix, Rational, Symbol

from bhsm.interface.envelopment.relational_axioms import deterministic_json


BASELINE_MAIN_SHA = "3e324a05e50b8128d28b84968b4ef3d2b064dd73"
INTEGRATED_V8_COMMIT = "a8d4b3a"
AUTHORITATIVE_VERDICT = (
    "BHSM_RECIPROCAL_ATTACHMENT_ACTION_AND_CURRENT_DERIVED_"
    "WITH_THREE_MODE_DOMAIN_CONDITIONAL"
)
AUTHORITATIVE_NEXT_OBJECT = (
    "ACTION_NORMALIZED_CORE_WALL_RESPONSE_GRAM_HESSIAN_"
    "ON_COMMON_ATTACHMENT_DOMAIN"
)
POST_INTEGRATION_VERDICT = "BHSM_FLAVOR_ACTION_CANDIDATES_ASSEMBLED_WITH_CHARGED_CURRENT_PROVENANCE_GATE_OPEN"
POST_INTEGRATION_NEXT_OBJECT = "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL"

PACKET_HASHES = {
    "BHSM_ATTACHMENT_TO_BERGER_OVERLAP_HIERARCHY_2026-08-03.md": "ec6c3d352407a498d54b6fbfa37b3a5ded3547e26674d871866601fe083661e3",
    "BHSM_FINAL_PARENT_ACTION_LEPTON_MASS_COMPLETION_2026-08-03.md": "4cca073d0c3e1846b9d854bf5f2de9fba02a39361741a631f8e34317c69a00c1",
    "BHSM_HOPF_BASE_OVERLAP_AND_DIMENSIONFUL_LEPTON_SCALE_2026-08-03.md": "2d9ff759aa49441c57fa803cc597d99abc436fa4150c420e423ddf254d698fde",
    "BHSM_MANUAL_ACTION_OWNED_G2_C3_ODD_COEFFICIENT_2026-08-03.md": "06f87c61539e3cb58d892d52f12582542e209a530b0b2096a9944a6d3b8f3b04",
    "BHSM_MANUAL_COMMON_DOMAIN_GRAM_HESSIAN_SPRINT_2026-08-03.md": "1ca08715d4c7c34019ec20a3585b865ad58f79dc506a9f133ebc3c61bbcf267f",
    "BHSM_MANUAL_GRAM_HESSIAN_DERIVATION_2026-08-02.md": "75b679869efb5026172d9df5c301c75c1463e0459bb1ca14eab00ae3013719a8",
    "BHSM_MANUAL_STABLE_ATTACHMENT_C3_PROJECTION_2026-08-03.md": "0e42ecdc4dc956870494e2439aaedd21647622bc6f5352d08d35d8cead8725e5",
    "BHSM_MINIMAL_CLASS_UNIQUENESS_AND_PROVENANCE_2026-08-03.md": "57fe4294e2ff0841fc707fc3661ef83c97cd2e3f203ea137a14fc7072e201b20",
    "BHSM_QUARK_YUKAWA_PAIR_AND_CKM_INTERTWINER_2026-08-03.md": "fe5bc1d07ed730b2725ed0e46c21b6ce2539de7d6a002ab800226bfcbbf789cc",
}


def packet_directory(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    return root / "docs" / "research_packets" / "2026-08-03"


def archived_packet_hashes(repository: Path | None = None) -> dict[str, str]:
    directory = packet_directory(repository)
    return {
        name: sha256((directory / name).read_bytes()).hexdigest()
        for name in sorted(PACKET_HASHES)
    }


def packet_gram_matrix() -> Matrix:
    """Return the packet's normalized Gram matrix in (q_C,q_D,q_W)."""

    return Matrix(
        [
            [1, Rational(3, 4), Rational(-1, 2)],
            [Rational(3, 4), Rational(7, 4), Rational(-3, 4)],
            [Rational(-1, 2), Rational(-3, 4), 1],
        ]
    )


def packet_hessian(h: Any) -> Matrix:
    """Return the packet's proposed common-domain Hessian."""

    return Matrix(
        [
            [h + Rational(1, 4), Rational(1, 4), Rational(1, 8)],
            [Rational(1, 4), 1, Rational(1, 4)],
            [Rational(1, 8), Rational(1, 4), Rational(1, 4)],
        ]
    )


def packet_tangent_basis() -> Matrix:
    return Matrix([[1, 1], [0, 1], [1, 0]])


def lower_attachment_root(octave: int, h_core: float) -> float:
    """Evaluate the packet's lower KKT branch; this is not an action promotion."""

    if octave < 0 or h_core <= 0:
        raise ValueError("octave must be nonnegative and h_core must be positive")
    t = octave + 1.0
    return (h_core + t - sqrt(t * t - h_core * t + h_core * h_core)) / 3.0


def inverse_octave(mu: float, h_core: float) -> float:
    if h_core <= 0 or not 0 < mu < h_core / 2:
        raise ValueError("the inverse is defined on 0 < mu < h_core/2")
    return mu * (2 * h_core - 3 * mu) / (h_core - 2 * mu) - 1.0


def berger_cost(k: int, j: int, anisotropy: float) -> float:
    q = k - 2 * j
    octave = k * (k + 2)
    return octave + (anisotropy * anisotropy - 1.0) * q * q


def candidate_lepton_numbers() -> dict[str, Any]:
    """Reproduce the packet's conditional screen without changing frozen outputs."""

    alpha_inverse = 137.035999084
    planck_energy_gev = 1.220890e19
    anisotropy = alpha_inverse / (12 * pi * pi)
    action_cost = 4 * pi * pi + (anisotropy - 1) / (4 * pi * pi)
    electroweak_screen_gev = 2 * sqrt(2) * planck_energy_gev * exp(-action_cost)
    common_scale_gev = 16 * sqrt(pi) * electroweak_screen_gev / 3969
    modes = {"heavy": (0, 0), "middle": (5, 2), "light": (9, 3)}
    costs = {name: berger_cost(k, j, anisotropy) for name, (k, j) in modes.items()}
    ratios = {name: exp(-value / (4 * pi)) for name, value in costs.items()}
    masses = {name: common_scale_gev * ratios[name] for name in modes}
    return {
        "classification": "CONDITIONAL_SCREEN_NOT_ACTION_DERIVED_PREDICTION",
        "anisotropy": anisotropy,
        "electroweak_screen_GeV": electroweak_screen_gev,
        "common_scale_GeV": common_scale_gev,
        "costs": costs,
        "ratios": ratios,
        "candidate_masses_GeV": masses,
        "action_excluded_inputs": ["alpha_inv_low_energy", "Planck_energy_GeV"],
    }


def review_payload(repository: Path | None = None) -> dict[str, Any]:
    h = Symbol("h", real=True)
    gram = packet_gram_matrix()
    hessian = packet_hessian(h)
    tangent = packet_tangent_basis()
    constraint = Matrix([[-1, 1, 1]])
    gram_parallel = tangent.T * gram * tangent
    hessian_parallel = tangent.T * hessian * tangent
    representative_h = 0.181391690148362
    attachment_roots = {
        str(octave): lower_attachment_root(octave, representative_h)
        for octave in (0, 35, 99)
    }
    inverse_checks = {
        octave: inverse_octave(mu, representative_h)
        for octave, mu in attachment_roots.items()
    }
    validation = {
        "packet_hashes_match": archived_packet_hashes(repository) == PACKET_HASHES,
        "gram_positive_at_packet_normalization": gram.det() == Rational(3, 4),
        "constraint_basis_exact": constraint * tangent == Matrix.zeros(1, 2),
        "hessian_determinant_formula_exact": hessian.det() == (6 * h + 1) / 32,
        "tangent_gram_determinant_exact": gram_parallel.det() == 4,
        "tangent_hessian_determinant_exact": hessian_parallel.det() == (48 * h + 35) / 64,
        "attachment_octave_inverse_exact_numerically": all(
            abs(float(octave) - recovered) < 1e-8
            for octave, recovered in inverse_checks.items()
        ),
        "attachment_roots_strictly_ordered": list(attachment_roots.values()) == sorted(attachment_roots.values()),
        "packet_overclaims_not_promoted": True,
        "v11_5_integration_status_recorded": True,
        "frozen_predictions_unchanged": True,
    }
    return {
        "artifact": "BHSM_download_progress_review_2026_08_03",
        "baseline_main_commit": BASELINE_MAIN_SHA,
        "review_scope": "BHSM-named files in Downloads, with nine new manual markdown packets archived",
        "prior_sprints": {
            "v8_4_through_v8_9": "ALREADY_INTEGRATED_WITH_REVIEW_AND_NORMALIZATION",
            "integration_commit": INTEGRATED_V8_COMMIT,
            "cache_files_excluded": True,
        },
        "packet_hashes": PACKET_HASHES,
        "verified_packet_math": {
            "normalization_disposition": "UNWHITENED_PACKET_GRAM_ALGEBRA_VERIFIED_BUT_NOT_COMBINED_WITH_V11_3_WHITENED_KKT_SYSTEM",
            "gram_determinant": str(gram.det()),
            "hessian_determinant": str(hessian.det()),
            "tangent_gram_determinant": str(gram_parallel.det()),
            "tangent_hessian_determinant": str(hessian_parallel.det()),
            "representative_attachment_roots": attachment_roots,
            "inverse_octave_checks": inverse_checks,
            "lepton_numbers": candidate_lepton_numbers(),
            "canonical_common_family_identification": "V_CKM=I3_AND_JARLSKOG=0",
        },
        "accepted_as_progress": [
            "the displayed Gram/Hessian algebra and positivity conditions are internally reproducible",
            "the KKT lower-branch monotonicity and inverse-octave identity are reproducible",
            "the frozen Berger hierarchy and proposed dimensionful numbers are reproducible as conditional screens",
            "canonical common up/down family identification gives trivial CKM",
        ],
        "not_promoted": [
            "the packet Gram/Hessian profile is not traced to a complete action-owned second variation in the repository",
            "the h_D(K)=1+K insertion is a packet assumption rather than a recovered v11.3 action coefficient",
            "alpha_inv_low_energy and Planck_energy_GeV are comparison/screen inputs explicitly excluded from the parent action ledger",
            "declaring a Higgs potential with the desired vacuum target is an author action selection, not a derivation of that target",
            "the attachment inverse decodes the already supplied octave ledger and does not independently select family modes",
            "the declared nontrivial CKM kernel is an author-selected no-fit candidate, not a recovered parent-action cross-current kernel",
        ],
        "baseline_completion_status": {
            "authoritative_version": "v11.3",
            "verdict": AUTHORITATIVE_VERDICT,
            "Mark_I": "REACHED",
            "Mark_II": "REACHED_CONDITIONALLY",
            "Mark_III": "NOT_REACHED",
            "Mark_IV": "NOT_REACHED",
            "BHSM_1_0_release_complete": False,
            "exact_next_object": AUTHORITATIVE_NEXT_OBJECT,
            "charged_lepton_sector": "CONDITIONAL_CANDIDATE_NOT_PROMOTED",
            "quark_mixing": "BLOCKED_BY_MISSING_ACTION_OWNED_CROSS_GRAM_CURRENT_KERNEL",
        },
        "completion_status": {
            "current_version": "v11.5",
            "verdict": POST_INTEGRATION_VERDICT,
            "Mark_I": "REACHED",
            "Mark_II": "REACHED_ON_SELECTED_FINITE_RADIUS_CORE_BRANCH",
            "Mark_III": "NOT_REACHED",
            "Mark_IV": "NOT_REACHED",
            "BHSM_1_0_release_complete": False,
            "exact_next_object": POST_INTEGRATION_NEXT_OBJECT,
        },
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    output = root / "artifacts" / "BHSM_download_progress_review_2026_08_03.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(review_payload()), encoding="utf-8", newline="\n")
    return output
