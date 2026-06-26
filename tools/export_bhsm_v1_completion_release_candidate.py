from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import bhsm_external_comparison_package as completion


INTERNAL_CLOSED_BLOCKERS = {
    "r",
    "r_internal_profile",
    "kappa_H",
    "Z_H",
    "boundary-derived tau/sigma",
    "charged outputs at boundary tau",
    "common-scale boundary transport",
    "neutral no-fit output export",
    "PMNS no-fit output export",
    "CKM no-fit output export",
    "CP no-fit output export",
    "boundary no-fit prediction package",
    "profile normalization theorem identifying Z_H with unit norm",
    "S_eff^(H) Higgs/profile effective action",
    "H_H Higgs saddle Hessian",
    "boundary potential curvature coefficients",
    "INTERNAL_BERGER_RADIUS_SELECTION_THEOREM",
    "internal/profile Berger radius normalization theorem",
}

EXTERNAL_OPEN_ITEMS = [
    "external empirical comparison transport",
    "external target data population",
    "comparison covariance",
    "published-scheme comparison results",
    "actual DESI directional anisotropy data",
]


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _guard(payload: dict) -> dict:
    payload.update(completion.guardrails())
    return payload


def _append_or_update_claim(payload: dict, row: dict) -> None:
    for entry in payload["claim_statuses"]:
        if entry["claim"] == row["claim"]:
            entry.update(row)
            return
    payload["claim_statuses"].append(row)


def _clean_open_blockers(items: list[str]) -> list[str]:
    result = [item for item in items if item not in INTERNAL_CLOSED_BLOCKERS]
    for item in EXTERNAL_OPEN_ITEMS:
        if item not in result:
            result.append(item)
    return result


def update_prediction_package(path: Path) -> None:
    payload = _guard(load_json(path))
    payload["package_status"] = "BHSM_COMPLETE_V1_RELEASE_CANDIDATE"
    payload["profile_scale"] = completion.INTERNAL_COMPLETE
    payload["charged_boundary_outputs"] = completion.INTERNAL_COMPLETE
    payload["common_boundary_transport"] = completion.INTERNAL_COMPLETE
    payload["neutral_boundary_output"] = completion.INTERNAL_COMPLETE
    payload["PMNS_boundary_output"] = completion.INTERNAL_COMPLETE
    payload["CKM_boundary_output"] = completion.INTERNAL_COMPLETE
    payload["CP_boundary_output"] = completion.INTERNAL_COMPLETE
    payload["BHSM_boundary_no_fit_prediction_package"] = completion.INTERNAL_COMPLETE
    payload["external_empirical_comparison_package"] = completion.COMPARISON_LAYER
    payload["external_empirical_comparison_result"] = completion.DATA_ABSENT
    for name in ("charged_same_sector_ratios", "PMNS_angles_and_phase", "CKM_angles_and_phase", "CP_Jarlskog_invariants"):
        if name in payload["sections"]:
            payload["sections"][name]["comparison_ready"] = False
            payload["sections"][name]["uses_empirical_input"] = False
    payload["sections"]["open_boundary_parameters"]["status"] = completion.INTERNAL_COMPLETE
    payload["sections"]["open_boundary_parameters"]["open_blockers"] = []
    payload["sections"]["external_empirical_comparison"] = {
        "status": completion.COMPARISON_LAYER,
        "source_artifact": "artifacts/BHSM_external_empirical_comparison_package_v1.json",
        "uses_empirical_input": False,
        "comparison_ready": True,
        "comparison_result": completion.DATA_ABSENT,
        "open_blockers": EXTERNAL_OPEN_ITEMS,
    }
    write_json(path, payload)


def update_open_gate_ledger(path: Path) -> None:
    payload = _guard(load_json(path))
    payload["public_status"] = "structural architecture integrated conditional; numerical closure open"
    payload["statuses"].update(
        {
            "BHSM_COMPLETE_V1_RELEASE_CANDIDATE": "EXPORTED",
            "BHSM_boundary_no_fit_prediction_package": completion.INTERNAL_COMPLETE,
            "BHSM_internal_boundary_package": completion.INTERNAL_COMPLETE,
            "external_empirical_comparison_package": completion.COMPARISON_LAYER,
            "external_empirical_comparison_status": "DATA_OPTIONAL_OR_DATA_ABSENT",
            "external_target_data_population": completion.DATA_ABSENT,
            "external_comparison_transport": "OPEN_COMPARISON_LAYER",
            "comparison_covariance": completion.DATA_ABSENT,
            "published_scheme_comparison_results": completion.DATA_ABSENT,
            "tau_from_boundary_geometry": "DERIVED_CONDITIONAL",
            "sigma_from_boundary_geometry": "DERIVED_CONDITIONAL",
            "charged_no_fit_outputs": "NO_FIT_OUTPUT_CANDIDATE_EXPORTED",
            "common_scale_boundary_transport": "DERIVED_FIXED_IDENTITY_AT_BHSM_BOUNDARY_SCALE",
            "neutral_boundary_operator": "CLOSED_AS_BOUNDARY_SEED",
            "PMNS_boundary_no_fit_output": "CLOSED_UNDER_CANONICAL_MINIMAL_CHARGED_DIAGONAL_CONVENTION",
            "CKM_full_boundary_no_fit_output": "CLOSED_BY_TAU_SUPPRESSED_HIGHER_CHANNEL_THEOREM",
            "CP_boundary_holonomy": "CLOSED",
            "official_predictions": "UNCHANGED",
            "empirical_derivation_inputs_used": False,
        }
    )
    payload["remaining_open_blockers"] = _clean_open_blockers(payload.get("remaining_open_blockers", []))
    write_json(path, payload)


def update_claim_status(path: Path) -> None:
    payload = _guard(load_json(path))
    payload["public_status"] = "structural architecture integrated conditional; numerical closure open"
    for row in (
        {
            "claim": "BHSM complete v1 release candidate",
            "status": "BHSM_COMPLETE_V1_RELEASE_CANDIDATE",
            "boundary": (
                "Internal boundary no-fit package complete/exported; external empirical comparison "
                "implemented as a separate comparison-only layer and data-optional."
            ),
        },
        {
            "claim": "External empirical comparison package",
            "status": completion.COMPARISON_LAYER,
            "boundary": "Comparison-only layer; cannot modify derivation constants or internal boundary predictions.",
        },
        {
            "claim": "External empirical validation",
            "status": "DATA_ABSENT",
            "boundary": "No empirical validation is claimed without external target data and comparison artifacts.",
        },
    ):
        _append_or_update_claim(payload, row)
    payload["official_predictions_changed"] = False
    write_json(path, payload)


def update_current_status(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## BHSM v1 Completion Release Candidate"
    section = f"""
{marker}

BHSM v1 now contains a complete internal no-fit boundary prediction package. The
profile scale, charged boundary outputs, neutral/PMNS/CKM/CP boundary outputs,
and boundary-scale transport identity are exported as machine-readable
artifacts.

External empirical comparison is implemented as a separate comparison-only
layer. Empirical data are not used to derive BHSM constants or boundary
predictions. If comparison data are absent, the package remains internally
complete but externally unevaluated.

Current split:

- `BHSM_internal_boundary_package = COMPLETE_EXPORTED`
- `BHSM_boundary_no_fit_prediction_package = COMPLETE_EXPORTED`
- `external_empirical_comparison_package = IMPLEMENTED_COMPARISON_ONLY_LAYER`
- `external_empirical_comparison_status = DATA_OPTIONAL_OR_DATA_ABSENT`
"""
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    path.write_text(text, encoding="utf-8")


def append_doc_section(path: Path, title: str, body: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else f"# {title}\n"
    marker = f"## {title}"
    section = f"{marker}\n\n{body.strip()}\n"
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section
    else:
        text = text.rstrip() + "\n\n" + section
    path.write_text(text, encoding="utf-8")


def update_docs() -> None:
    status_text = (
        "BHSM v1 now contains a complete internal no-fit boundary prediction package. "
        "The external empirical comparison layer is implemented as a separate comparison-only layer. "
        "Empirical data are not derivation inputs, and absent external data produce "
        "`DATA_ABSENT`, not an internal-package failure."
    )
    append_doc_section(ROOT / "docs" / "claim_boundaries.md", "BHSM v1 Release-Candidate Boundary", status_text)
    append_doc_section(
        ROOT / "docs" / "falsification_criteria.md",
        "BHSM v1 Comparison Gates",
        (
            "The internal profile-scale identities and no-empirical-derivation gate are internal gates. "
            "Charged-sector, CKM/PMNS/CP, and DESI checks are comparison-only gates and are "
            "`NOT_EVALUATED_DATA_ABSENT` until target data are supplied."
        ),
    )
    append_doc_section(
        ROOT / "docs" / "reproducibility.md",
        "BHSM v1 Release Candidate",
        (
            "Run `python -m pytest -q` to reproduce the internal boundary no-fit package and "
            "comparison-layer guardrails. The final manifest is "
            "`artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json`."
        ),
    )

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## BHSM v1 Completion Release Candidate"
    section = f"""
{marker}

BHSM v1 now contains a complete internal no-fit boundary prediction package. The
profile scale, charged boundary outputs, neutral/PMNS/CKM/CP boundary outputs,
and boundary-scale transport identity are exported as machine-readable artifacts.

External empirical comparison is implemented as a separate comparison-only
layer. Empirical data are not used to derive BHSM constants or boundary
predictions. If comparison data are absent, the package remains internally
complete but externally unevaluated.
"""
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + "\n\n" + section.strip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + section.strip() + "\n"
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    artifacts = ROOT / "artifacts"
    write_json(artifacts / "BHSM_external_comparison_target_schema_v1.json", completion.build_external_target_schema())
    write_json(
        artifacts / "BHSM_external_transport_layer_v1.json",
        completion.transport_boundary_predictions_to_external_scheme_if_possible(ROOT),
    )
    write_json(artifacts / "BHSM_falsification_gates_v1.json", completion.evaluate_falsification_gates(ROOT))
    write_json(
        artifacts / "BHSM_external_empirical_comparison_package_v1.json",
        completion.build_external_comparison_artifact(ROOT),
    )
    write_json(artifacts / "BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json", completion.build_completion_manifest(ROOT))

    update_prediction_package(artifacts / "BHSM_prediction_package_skeleton_v1.json")
    update_open_gate_ledger(artifacts / "full_BHSM_open_gate_ledger_v2.json")
    update_claim_status(artifacts / "full_BHSM_claim_status_table_v2.json")
    update_current_status(ROOT / "docs" / "current_status.md")
    update_docs()


if __name__ == "__main__":
    main()
