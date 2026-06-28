"""Assemble and export the admissible neutral positivity verdict."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..neutrino_scale.common import repository_path
from .admissible_domain import derive_or_load_neutral_admissible_domain
from .common import NeutralPositivityReport, NeutralPositivityVerdict
from .neutral_quadratic_form import _base_payload, audit_neutral_kernel_exact
from .positivity_counterexample import search_admissible_positivity_counterexample
from .positivity_proof import prove_neutral_positivity_on_domain
from .projected_kernel import build_projected_neutral_kernel
from ..neutrino_closure_status import PUBLIC_REPO_STATUS


PUBLIC_STATUS = PUBLIC_REPO_STATUS
FINAL_STATUS = "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE"
ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_neutral_positivity_manifest_v1_4.json",
    "exact": "artifacts/BHSM_neutral_kernel_exact_audit_v1_4.json",
    "domain": "artifacts/BHSM_neutral_admissible_domain_v1_4.json",
    "projected": "artifacts/BHSM_neutral_projected_kernel_v1_4.json",
    "proof": "artifacts/BHSM_neutral_positivity_proof_v1_4.json",
    "counterexample": "artifacts/BHSM_neutral_positivity_counterexample_v1_4.json",
    "report": "artifacts/BHSM_neutral_positivity_report_v1_4.json",
    "claims": "artifacts/BHSM_neutral_positivity_claim_policy_v1_4.json",
}

REQUIRED_STATEMENTS = (
    "The raw neutral kernel is not assumed to be positive semidefinite.",
    "BHSM distinguishes raw kernel positivity, projected/admissible positivity, and thresholded response nonnegativity.",
    "Thresholding a response to be nonnegative is not a proof that the underlying kernel is positive.",
    "Admissible neutral positivity requires both an explicit admissible domain and a proof that x^T K_nu x is nonnegative on that domain.",
    "Admissible neutral positivity is proven only on the stated admissible domain and is not a raw-kernel PSD claim.",
    "BHSM treats the neutrino mass contribution as interaction-supported and propagation-locked. Measurement supplies a physical boundary/interaction condition that can prevent the neutral response from nulling out.",
)


def build_neutral_positivity_report(
    repository: str | Path | None = None,
) -> NeutralPositivityReport:
    root = repository_path(repository)
    exact = audit_neutral_kernel_exact(root)
    domain = derive_or_load_neutral_admissible_domain(root)
    projected = build_projected_neutral_kernel(root)
    proof = prove_neutral_positivity_on_domain(root)
    counterexample = search_admissible_positivity_counterexample(root)
    conditional = (
        domain.admissible_domain_defined
        and proof.positivity_proven_without_thresholding
        and not counterexample.counterexample_found
    )
    status = FINAL_STATUS if conditional else (
        "ADMISSIBLE_POSITIVITY_COUNTEREXAMPLE_FOUND"
        if counterexample.counterexample_found
        else "THRESHOLDED_RESPONSE_ONLY_NO_POSITIVITY_PROOF"
    )
    payload = _base_payload(exact)
    for key in (
        "admissible_domain_defined",
        "admissible_domain_constraints",
        "projection_matrix",
        "projected_kernel",
        "projected_eigenvalues",
        "projected_psd",
        "minimum_on_admissible_domain",
        "counterexample",
        "thresholding_used",
        "positivity_proven_without_thresholding",
        "counterexample_found",
    ):
        payload.pop(key)
    common = dict(
        status=status,
        admissible_domain_defined=domain.admissible_domain_defined,
        admissible_domain_constraints=domain.admissible_domain_constraints,
        projection_matrix=None,
        projected_kernel=None,
        projected_eigenvalues=(),
        projected_psd=None,
        minimum_on_admissible_domain=proof.minimum_on_admissible_domain,
        counterexample=counterexample.counterexample,
        thresholding_used=False,
        positivity_proven_without_thresholding=proof.positivity_proven_without_thresholding,
        counterexample_found=counterexample.counterexample_found,
        claim_boundary=(
            "Exact copositivity is established on the author-ontology measurement-supported response cone. "
            "The cone identification remains conditional and the raw kernel remains indefinite."
        ),
        remaining_missing_object="complete-action derivation of the measurement-supported response cone",
        **payload,
    )
    verdict = NeutralPositivityVerdict(
        candidate_key="neutral_admissible_positivity_verdict",
        domain_artifact_backed=False,
        domain_ontology_conditional=True,
        **common,
    )
    return NeutralPositivityReport(
        candidate_key="neutral_positivity_report",
        exact_audit=exact,
        domain=domain,
        projected=projected,
        proof=proof,
        counterexample_search=counterexample,
        verdict=verdict,
        public_status=PUBLIC_STATUS,
        frozen_predictions_changed=False,
        production_physics_model_logic_changed=False,
        internet_required=False,
        external_hep_tools_required=False,
        libreoffice_required=False,
        **common,
    )


def neutral_positivity_report_to_markdown(report: NeutralPositivityReport) -> str:
    lines = [
        "# BHSM Admissible Neutral Positivity",
        "",
        f"Final status: `{report.status}`.",
        "",
        *REQUIRED_STATEMENTS,
        "",
        "| Question | Result |",
        "| --- | --- |",
        f"| Raw PSD | {'yes' if report.raw_psd else 'no'} |",
        f"| Admissible domain defined | {'yes' if report.admissible_domain_defined else 'no'} |",
        "| Linear projected-subspace PSD | not applicable; the restriction is a cone |",
        f"| Positivity without thresholding | {'yes' if report.positivity_proven_without_thresholding else 'no'} |",
        f"| Admissible counterexample | {'yes' if report.counterexample_found else 'no'} |",
        "",
        f"Quadratic form: `{report.quadratic_form}`.",
        f"Raw eigenvalues: `{list(report.raw_eigenvalues_numeric)}`.",
        f"Remaining object: {report.remaining_missing_object}.",
        "",
    ]
    return "\n".join(lines)


def _claim_policy() -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Neutral Positivity Claim Policy",
        "version": "1.4",
        "allowed": [
            "BHSM has audited the raw neutral kernel exactly.",
            "BHSM distinguishes raw kernel PSD, projected/admissible positivity, and thresholded nonnegative response.",
            "BHSM does not claim raw neutral-kernel PSD if the raw kernel has a negative eigenvalue.",
            "BHSM claims conditional admissible positivity only on the explicit measurement-supported response cone.",
        ],
        "forbidden": [
            "The raw neutral kernel is positive semidefinite if its smallest eigenvalue is negative.",
            "Threshold clipping is a proof of kernel positivity.",
            "Admissible positivity is proven without an admissible domain.",
            "A projected positivity result applies to the full raw vector space.",
            "The neutrino does not exist at all unless someone observes it.",
            "BHSM empirically validates neutrino mass.",
            "BHSM centrally measures electron-neutrino mass.",
            "PDG/reference values are theorem inputs.",
            "W calibration is used.",
            "Legacy particle tables are derivation inputs.",
        ],
        "required_statements": list(REQUIRED_STATEMENTS),
        "frozen_predictions_changed": False,
    }


def write_neutral_positivity_artifacts(
    repository: str | Path | None = None,
) -> NeutralPositivityReport:
    root = repository_path(repository)
    report = build_neutral_positivity_report(root)
    payloads: dict[str, Any] = {
        "manifest": {
            "artifact_name": "BHSM Neutral Positivity Manifest",
            "version": "1.4",
            "artifact_paths": list(ARTIFACT_PATHS.values()),
            "status": report.status,
            "frozen_predictions_changed": False,
        },
        "exact": report.exact_audit.to_dict(),
        "domain": report.domain.to_dict(),
        "projected": report.projected.to_dict(),
        "proof": report.proof.to_dict(),
        "counterexample": report.counterexample_search.to_dict(),
        "report": report.to_dict(),
        "claims": _claim_policy(),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
