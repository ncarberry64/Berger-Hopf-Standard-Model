"""Claims ledger automation for the Berger-Hopf audit repository."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Iterable


class ClaimStatus(StrEnum):
    """Conservative claim status labels."""

    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    VERIFIED_TEST = "VERIFIED_TEST"
    STRONG_SCREEN = "STRONG_SCREEN"
    PROXY_AUDIT = "PROXY_AUDIT"
    OPEN = "OPEN"
    FORBIDDEN = "FORBIDDEN"


@dataclass(frozen=True)
class Claim:
    """Machine-readable record for one scientific or audit claim."""

    id: str
    title: str
    statement: str
    status: ClaimStatus
    dependencies: tuple[str, ...]
    test_modules: tuple[str, ...]
    limitations: tuple[str, ...]


def _claim(
    id: str,
    title: str,
    statement: str,
    status: ClaimStatus,
    *,
    dependencies: Iterable[str] = (),
    test_modules: Iterable[str] = (),
    limitations: Iterable[str],
) -> Claim:
    return Claim(
        id=id,
        title=title,
        statement=statement,
        status=status,
        dependencies=tuple(dependencies),
        test_modules=tuple(test_modules),
        limitations=tuple(limitations),
    )


def build_claims_ledger() -> list[Claim]:
    """Return the current conservative claims ledger."""

    return [
        _claim(
            "sm_gauge_ledger",
            "Standard Model Gauge Ledger",
            "The admitted chiral representation ledger is the anomaly-free Standard Model gauge and matter ledger.",
            ClaimStatus.DERIVED_CONDITIONAL,
            dependencies=("admitted SM chiral representation pattern",),
            test_modules=("tests/test_hypercharges.py", "tests/test_anomalies.py"),
            limitations=("The representation pattern is admitted rather than derived from pure geometry.",),
        ),
        _claim(
            "hypercharge_derivation",
            "Hypercharge Derivation",
            "Hypercharges follow from Yukawa invariance and anomaly cancellation once the chiral pattern and Higgs-selected U(1) are admitted.",
            ClaimStatus.VERIFIED_TEST,
            dependencies=("admitted chiral representation pattern", "Higgs-selected U(1) normalization"),
            test_modules=("tests/test_hypercharges.py",),
            limitations=("This is conditional on the admitted representation pattern and U(1) normalization.",),
        ),
        _claim(
            "anomaly_cancellation",
            "Anomaly Cancellation",
            "One-generation gauge and mixed anomaly residuals vanish in the implemented left-Weyl ledger.",
            ClaimStatus.VERIFIED_TEST,
            dependencies=("hypercharge_derivation",),
            test_modules=("tests/test_anomalies.py",),
            limitations=("The test audits the admitted one-generation ledger; it is not a derivation of the ledger itself.",),
        ),
        _claim(
            "three_generation_index",
            "Three-Generation Index Condition",
            "Three generations are reduced to an index-three twisted Dirac kernel.",
            ClaimStatus.OPEN,
            dependencies=("full twisted Dirac operator construction",),
            test_modules=(),
            limitations=("The index-three kernel has not been computed in this repository.",),
        ),
        _claim(
            "no_fourth_generation",
            "No Fourth Protected Chiral Generation",
            "No fourth protected chiral generation is expected only after the protected kernel computation is completed.",
            ClaimStatus.OPEN,
            dependencies=("three_generation_index", "full protected spectrum computation"),
            test_modules=(),
            limitations=("The protected spectrum is not yet computed, so this remains open.",),
        ),
        _claim(
            "yukawa_overlap_structure",
            "Yukawa Overlap Structure",
            "Charged-sector Yukawa hierarchies are screened by the supplied universal overlap rule and mode ledger.",
            ClaimStatus.STRONG_SCREEN,
            dependencies=("supplied mode ledger", "universal overlap rule"),
            test_modules=("tests/test_mode_selection.py",),
            limitations=("Mode-selection rules are operational audits, not yet derived from the full action; numerical matches are screens, not predictions.",),
        ),
        _claim(
            "charged_sector_mode_ledger",
            "Charged-Sector Mode Ledger",
            "The supplied boundary operators recover the charged-sector mode ledger without mass inputs.",
            ClaimStatus.VERIFIED_TEST,
            dependencies=("supplied boundary operators", "nonnegative Hopf-charge Berger domain"),
            test_modules=("tests/test_mode_selection.py", "tests/test_boundary_derivation.py"),
            limitations=("The boundary operators Omega_f are ACTION_LINKED by symbolic phase factors but are not fully ACTION_DERIVED from variation or spectrum of the twisted Dirac/bundle action.",),
        ),
        _claim(
            "ckm_screen",
            "CKM Screen",
            "CKM mixing is represented as left-handed up/down internal-basis misalignment.",
            ClaimStatus.DERIVED_CONDITIONAL,
            dependencies=("left-handed internal bases",),
            test_modules=(),
            limitations=("No independent CKM fit or dynamical derivation is implemented yet.",),
        ),
        _claim(
            "pmns_effective_extension",
            "PMNS Effective Extension",
            "PMNS mixing is treated only as an effective neutrino-sector extension.",
            ClaimStatus.DERIVED_CONDITIONAL,
            dependencies=("effective neutrino extension",),
            test_modules=(),
            limitations=("Neutrino masses are not part of the minimal Standard Model ledger in this repository.",),
        ),
        _claim(
            "gauge_coupling_screen",
            "Gauge Coupling Matching Screen",
            "The supplied gauge coupling relations are electroweak-scale matching screens with a one-loop RG scaffold.",
            ClaimStatus.STRONG_SCREEN,
            dependencies=("supplied coupling relations",),
            test_modules=("tests/test_couplings.py", "tests/test_rg_matching.py"),
            limitations=("Gate 29B implements one-loop RG matching scaffolding only; full two-/three-loop threshold matching remains OPEN and is not a completed theorem.",),
        ),
        _claim(
            "electroweak_scale_hopf_screen",
            "Electroweak Scale Hopf Screen",
            "The supplied Hopf-scale formula numerically screens the electroweak scale.",
            ClaimStatus.STRONG_SCREEN,
            dependencies=("supplied electroweak scale formula", "reference Planck energy and alpha input"),
            test_modules=("tests/test_higgs_scale.py",),
            limitations=("The calculation is a numerical screen and not an independent prediction.",),
        ),
        _claim(
            "ht_proxy_spectral_gap",
            "H_T Proxy Spectral Gap",
            "The no-extra-light-state condition has executable scalar and twisted-Dirac finite-basis proxy spectral audits, plus a formal sufficient theorem scaffold listing assumptions A1-A7.",
            ClaimStatus.PROXY_AUDIT,
            dependencies=("Berger scalar spectrum proxy", "DIRAC_PROXY_LEVEL_1 finite-basis scaffold", "DIRAC_PROXY_LEVEL_2 matrix scaffold", "natural heat-kernel cutoff", "finite-basis lower-bound inequalities", "finite-basis convergence scan", "sufficient theorem scaffold assumptions A1-A7"),
            test_modules=("tests/test_spectral_gap.py", "tests/test_positivity.py", "tests/test_twisted_dirac_ht.py", "tests/test_twisted_dirac_level2.py", "tests/test_spectral_bounds.py", "tests/test_theorem_scaffold.py"),
            limitations=("Gate 32D formalizes sufficient proxy theorem assumptions A1-A7, but those assumptions are not proven in the full internal action; the theorem remains open.",),
        ),
        _claim(
            "psd_curvature_profile_positivity",
            "PSD Curvature/Profile Positivity",
            "A sufficient positive-semidefinite curvature/profile construction preserves the proxy Hopf gap on H_perp.",
            ClaimStatus.PROXY_AUDIT,
            dependencies=("finite-basis proxy operators", "protected zero-mode projector"),
            test_modules=("tests/test_positivity.py",),
            limitations=("This is a finite-basis proxy construction, not the full curvature/profile operator in the complete action.",),
        ),
        _claim(
            "scalar_decoupling",
            "Scalar Decoupling",
            "Scalar/topographic decoupling has a finite-basis scaffold, but remains to be proven in the full action.",
            ClaimStatus.OPEN,
            dependencies=("full action", "scalar spectrum analysis"),
            test_modules=("tests/test_scalar_decoupling.py",),
            limitations=("Gate 30B implements a scalar/topographic decoupling scaffold only; full action-level scalar decoupling remains OPEN and not proven.",),
        ),
        _claim(
            "trace_u1_topological_condition",
            "Trace U(1) Topological Condition",
            "The trace U(1) topological condition remains an open structural input.",
            ClaimStatus.OPEN,
            dependencies=("topological U(1) construction",),
            test_modules=(),
            limitations=("No independent topological proof is implemented.",),
        ),
        _claim(
            "forbidden_pure_geometry_derivation",
            "Forbidden Pure-Geometry Derivation Claim",
            "The repository must not claim a rigorous first-principles derivation of the Standard Model from pure geometry alone.",
            ClaimStatus.FORBIDDEN,
            dependencies=(),
            test_modules=(),
            limitations=("The current repository is a conditional audit and screen suite.",),
        ),
        _claim(
            "forbidden_confinement_proof",
            "Forbidden Yang-Mills Confinement Claim",
            "The repository must not claim a proof of Yang-Mills confinement.",
            ClaimStatus.FORBIDDEN,
            dependencies=(),
            test_modules=(),
            limitations=("No confinement proof is implemented or audited.",),
        ),
        _claim(
            "forbidden_completed_no_extra_light_theorem",
            "Forbidden Completed No-Extra-Light-State Claim",
            "The repository must not claim the no-extra-light-state theorem is complete before the full H_T spectrum is computed.",
            ClaimStatus.FORBIDDEN,
            dependencies=("full twisted Dirac H_T spectrum",),
            test_modules=(),
            limitations=("Only proxy spectral-gap and positivity audits are implemented.",),
        ),
        _claim(
            "forbidden_neutrino_minimal_sm",
            "Forbidden Minimal-SM Neutrino-Mass Claim",
            "The repository must not claim neutrino masses are part of the minimal Standard Model.",
            ClaimStatus.FORBIDDEN,
            dependencies=(),
            test_modules=(),
            limitations=("Neutrino masses are treated only as an effective extension.",),
        ),
        _claim(
            "forbidden_numerical_predictions",
            "Forbidden Numerical-Prediction Claim",
            "The repository must not claim numerical matches are predictions before independent mode-selection rules are derived.",
            ClaimStatus.FORBIDDEN,
            dependencies=("independent derivation of mode-selection rules",),
            test_modules=(),
            limitations=("Implemented numerical results are screens unless upgraded by future derivations.",),
        ),
    ]


def claims_by_status(status: ClaimStatus | str) -> list[Claim]:
    """Return claims matching a status."""

    resolved = ClaimStatus(status)
    return [claim for claim in build_claims_ledger() if claim.status == resolved]


def _claim_to_jsonable(claim: Claim) -> dict[str, object]:
    data = asdict(claim)
    data["status"] = claim.status.value
    return data


def export_claims_markdown(path: str | Path) -> None:
    """Export claims ledger as manuscript-readable Markdown."""

    claims = build_claims_ledger()
    lines = [
        "# Claims Ledger",
        "",
        "This ledger is generated from `src/claims.py`. It is an audit/control layer, not a proof upgrade.",
        "",
        "| ID | Title | Status | Tests | Limitations |",
        "| --- | --- | --- | --- | --- |",
    ]
    for claim in claims:
        tests = ", ".join(claim.test_modules) if claim.test_modules else "None"
        limitations = "<br>".join(claim.limitations)
        lines.append(
            f"| `{claim.id}` | {claim.title} | `{claim.status.value}` | {tests} | {limitations} |"
        )
    Path(path).write_text("\n".join(lines) + "\n")


def export_claims_json(path: str | Path) -> None:
    """Export claims ledger as machine-readable JSON."""

    data = [_claim_to_jsonable(claim) for claim in build_claims_ledger()]
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
