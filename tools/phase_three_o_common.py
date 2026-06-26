from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from phase_three_n_common import ROOT, guardrails, runtime_report, write_json


RELEASE_BASIS = "v1.0.1"
PHASE = "PHASE_THREE_O_RUNTIME_ASSETS_HEP_HANDOFF"

OFFICIAL_FEYNRULES_URL = "https://feynrules.irmp.ucl.ac.be/"
OFFICIAL_MADGRAPH_URL = "https://launchpad.net/mg5amcnlo"


def env_path(name: str) -> str | None:
    value = os.environ.get(name)
    if value and Path(value).exists():
        return value
    return None


def asset_entry(
    asset_id: str,
    asset_name: str,
    required_for: list[str],
    required_or_optional: str,
    legal_source_policy: str,
    download_allowed: bool,
    install_allowed: bool,
    detected: bool,
    version: str,
    path: str,
    source_url_if_known: str,
    checksum_if_available: str,
    license_notes: str,
    status: str,
    blocks_validation_if_missing: bool,
    notes: list[str],
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "required_for": required_for,
        "required_or_optional": required_or_optional,
        "legal_source_policy": legal_source_policy,
        "download_allowed": download_allowed,
        "install_allowed": install_allowed,
        "detected": detected,
        "version": version,
        "path": path,
        "source_url_if_known": source_url_if_known,
        "checksum_if_available": checksum_if_available,
        "license_notes": license_notes,
        "status": status,
        "blocks_validation_if_missing": blocks_validation_if_missing,
        "notes": notes,
    }


def runtime_asset_manifest() -> dict[str, Any]:
    runtime = runtime_report()
    assets = [
        asset_entry(
            "python",
            "Python",
            ["repository tests", "artifact exporters", "setup scripts"],
            "required",
            "system/package-manager/user-managed",
            False,
            False,
            runtime["python_detected"],
            "current interpreter",
            runtime["python_path"],
            "https://www.python.org/",
            "not_recorded",
            "Open-source runtime already provided by environment.",
            "DETECTED" if runtime["python_detected"] else "MISSING",
            True,
            ["Basic repository tests require Python."],
        ),
        asset_entry(
            "wolframscript",
            "WolframScript",
            ["scripted FeynRules execution"],
            "required",
            "licensed/authorized Wolfram runtime only",
            False,
            False,
            runtime["wolframscript_detected"],
            runtime["wolframscript_version"],
            runtime["wolframscript_path"],
            "https://www.wolfram.com/",
            "not_available",
            "Requires licensed or otherwise authorized Wolfram runtime; no automatic download.",
            "DETECTED" if runtime["wolframscript_detected"] else "MISSING_LICENSED_EXTERNAL_RUNTIME",
            True,
            ["May be supplied with WOLFRAMSCRIPT_PATH."],
        ),
        asset_entry(
            "wolfram_kernel",
            "WolframKernel",
            ["Mathematica/FeynRules model loading"],
            "required",
            "licensed/authorized Wolfram runtime only",
            False,
            False,
            runtime["wolfram_kernel_detected"],
            runtime["wolfram_kernel_version"],
            runtime["wolfram_kernel_path"],
            "https://www.wolfram.com/",
            "not_available",
            "Requires licensed or otherwise authorized Wolfram runtime; no license bypass.",
            "DETECTED" if runtime["wolfram_kernel_detected"] else "MISSING_LICENSED_EXTERNAL_RUNTIME",
            True,
            ["May be supplied with WOLFRAM_KERNEL_PATH."],
        ),
        asset_entry(
            "mathematica",
            "Mathematica",
            ["FeynRules notebook/package runtime"],
            "required",
            "licensed/authorized Wolfram installation only",
            False,
            False,
            runtime["mathematica_detected"],
            "not_detected",
            runtime["mathematica_path"],
            "https://www.wolfram.com/mathematica/",
            "not_available",
            "Restricted proprietary runtime; user/institution must provide legal install.",
            "DETECTED" if runtime["mathematica_detected"] else "MISSING_LICENSED_EXTERNAL_RUNTIME",
            True,
            ["May be supplied with MATHEMATICA_PATH."],
        ),
        asset_entry(
            "feynrules",
            "FeynRules",
            ["FeynRules validation", "UFO export"],
            "required",
            "official/legal FeynRules source only",
            True,
            True,
            runtime["feynrules_detected"],
            runtime["feynrules_version_if_available"],
            runtime["feynrules_path"],
            OFFICIAL_FEYNRULES_URL,
            "not_recorded",
            "Use only official/legal FeynRules package; load test still requires Wolfram.",
            "DETECTED" if runtime["feynrules_detected"] else "MISSING",
            True,
            ["May be supplied with FEYNRULES_PATH."],
        ),
        asset_entry(
            "feynarts_optional",
            "FeynArts/FormCalc",
            ["optional diagram checks"],
            "optional",
            "official/legal source only",
            True,
            True,
            False,
            "not_detected",
            "not_detected",
            "https://feynarts.de/",
            "not_recorded",
            "Optional; not required for Phase Three-O validation gates.",
            "OPTIONAL_NOT_DETECTED",
            False,
            ["Not needed for the bounded minimal validation chain."],
        ),
        asset_entry(
            "madgraph",
            "MadGraph5_aMC",
            ["UFO import", "MadGraph smoke test"],
            "required_for_smoke",
            "official public MadGraph source only",
            True,
            True,
            runtime["madgraph_detected"],
            runtime["madgraph_version_if_available"],
            runtime["madgraph_path"],
            OFFICIAL_MADGRAPH_URL,
            "not_recorded",
            "Open public HEP software; use official distribution only.",
            "DETECTED" if runtime["madgraph_detected"] else "MISSING",
            True,
            ["May be supplied with MADGRAPH_PATH or MG5AMC_PATH."],
        ),
        asset_entry(
            "hepmc_optional",
            "HepMC",
            ["optional event-output validation"],
            "optional",
            "official/legal package source only",
            True,
            True,
            False,
            "not_detected",
            "not_detected",
            "https://hepmc.web.cern.ch/",
            "not_recorded",
            "Optional until event-generation evidence exists.",
            "OPTIONAL_NOT_DETECTED",
            False,
            ["No HepMC readiness is claimed."],
        ),
        asset_entry(
            "root_optional",
            "ROOT",
            ["optional analysis checks"],
            "optional",
            "official/legal package source only",
            True,
            True,
            False,
            "not_detected",
            "not_detected",
            "https://root.cern/",
            "not_recorded",
            "Optional analysis runtime.",
            "OPTIONAL_NOT_DETECTED",
            False,
            ["No ROOT dependency is required for repository tests."],
        ),
        asset_entry(
            "lhapdf_optional",
            "LHAPDF",
            ["optional collider phenomenology extensions"],
            "optional",
            "official/legal package source only",
            True,
            True,
            False,
            "not_detected",
            "not_detected",
            "https://lhapdf.hepforge.org/",
            "not_recorded",
            "Optional future phenomenology dependency.",
            "OPTIONAL_NOT_DETECTED",
            False,
            ["Not required for the bounded CKM/PMNS validation gate."],
        ),
    ]
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "environment_variables_supported": [
            "WOLFRAMSCRIPT_PATH",
            "WOLFRAM_KERNEL_PATH",
            "MATHEMATICA_PATH",
            "FEYNRULES_PATH",
            "MADGRAPH_PATH",
            "MG5AMC_PATH",
            "BHSM_RUNTIME_DIR",
            "BHSM_OUTPUT_DIR",
        ],
        "assets": assets,
        **guardrails(),
    }


def download_attempts(attempt_downloads: bool = False) -> dict[str, Any]:
    attempts = []
    for asset_id, url, allowed, note in [
        ("wolfram_runtime", "user_provided_only", False, "Restricted runtime; no automatic download."),
        ("feynrules", OFFICIAL_FEYNRULES_URL, True, "Official/legal source only; not downloaded by default."),
        ("madgraph", OFFICIAL_MADGRAPH_URL, True, "Official public source only; not downloaded by default."),
    ]:
        attempts.append(
            {
                "asset_id": asset_id,
                "source_url": url,
                "download_attempted": False if not attempt_downloads else False,
                "download_succeeded": False,
                "destination": "external/ or .cache/bhsm_runtime/ when explicitly requested",
                "checksum_if_available": "not_recorded",
                "license_note": note,
                "failure_reason": "automatic downloads disabled by default to avoid large/unreviewed runtime artifacts",
            }
        )
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "download_policy": "legal sources only; no Wolfram automatic download; large assets not committed by default",
        "attempt_downloads_requested": attempt_downloads,
        "downloaded_assets_committed_to_repo": False,
        "attempts": attempts,
        **guardrails(),
    }


def wolfram_mapping_status() -> dict[str, Any]:
    runtime = runtime_report()
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "mapping_attempted": True,
        "wolframscript_detected": runtime["wolframscript_detected"],
        "wolframscript_path": runtime["wolframscript_path"],
        "wolframscript_version": runtime["wolframscript_version"],
        "wolfram_kernel_detected": runtime["wolfram_kernel_detected"],
        "wolfram_kernel_path": runtime["wolfram_kernel_path"],
        "wolfram_kernel_version": runtime["wolfram_kernel_version"],
        "mathematica_detected": runtime["mathematica_detected"],
        "mathematica_path": runtime["mathematica_path"],
        "environment_variables_checked": ["WOLFRAMSCRIPT_PATH", "WOLFRAM_KERNEL_PATH", "MATHEMATICA_PATH"],
        "common_paths_checked": ["PATH", "C:/Program Files/Wolfram Research", "/Applications/Mathematica.app"],
        "ready_for_feynrules": runtime["environment_ready_for_feynrules_validation"],
        "license_notes": ["Requires licensed/authorized Wolfram runtime; no bypass attempted."],
        "missing_if_not_ready": [item for item in ["wolframscript", "wolfram_kernel_or_mathematica"] if item in runtime["missing_components"]],
        "notes": ["Provide paths by environment variables or install through institutional license."],
        **guardrails(),
    }


def feynrules_installation_status() -> dict[str, Any]:
    runtime = runtime_report()
    wolfram_ready = runtime["wolframscript_detected"] and (runtime["wolfram_kernel_detected"] or runtime["mathematica_detected"])
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "installation_or_mapping_attempted": True,
        "download_attempted": False,
        "download_succeeded": False,
        "source_url": OFFICIAL_FEYNRULES_URL,
        "destination_path": "external/feynrules or FEYNRULES_PATH when explicitly supplied",
        "feynrules_detected": runtime["feynrules_detected"],
        "feynrules_path": runtime["feynrules_path"],
        "feynrules_version_if_available": runtime["feynrules_version_if_available"],
        "load_test_attempted": False,
        "load_test_passed": False,
        "requires_wolfram_runtime": True,
        "ready_for_validation": runtime["environment_ready_for_feynrules_validation"],
        "failure_reason_if_any": "none" if runtime["environment_ready_for_feynrules_validation"] else ("Wolfram runtime unavailable" if not wolfram_ready else "FeynRules package unavailable"),
        "notes": ["FeynRules can be mapped via FEYNRULES_PATH; load testing requires Wolfram."],
        **guardrails(),
    }


def madgraph_installation_status() -> dict[str, Any]:
    runtime = runtime_report()
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "installation_or_mapping_attempted": True,
        "download_attempted": False,
        "download_succeeded": False,
        "source_url": OFFICIAL_MADGRAPH_URL,
        "destination_path": "external/madgraph or MADGRAPH_PATH/MG5AMC_PATH when explicitly supplied",
        "madgraph_detected": runtime["madgraph_detected"],
        "madgraph_path": runtime["madgraph_path"],
        "madgraph_version_if_available": runtime["madgraph_version_if_available"],
        "import_test_attempted": False,
        "import_test_passed": False,
        "ready_for_smoke_test": runtime["environment_ready_for_madgraph_smoke"],
        "failure_reason_if_any": "none" if runtime["environment_ready_for_madgraph_smoke"] else "MadGraph missing or UFO loadability unavailable",
        "notes": ["Smoke test remains gated by UFO export/loadability."],
        **guardrails(),
    }


def handoff_manifest() -> dict[str, Any]:
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "package_name": "BHSM Phase Three-O CERN-like institutional HEP handoff package",
        "package_scope": "bounded minimal collider-interface subset",
        "is_official_cern_integration": False,
        "is_complete_bhsm_4d_lagrangian": False,
        "is_minimal_collider_interface_subset": True,
        "included_physics": [
            "CKM charged-current bounded collider-interface target",
            "PMNS charged-current bounded collider-interface target",
            "BHSM-derived CKM/PMNS source matrices",
            "runtime/scheme parameters for simulation only",
        ],
        "excluded_physics": [
            "charged_boundary_response_matrix",
            "neutral_operator_kernel_BH",
            "standalone cp_holonomy_phase_attachment",
            "complete BHSM 4D Lagrangian",
            "pure no-fit mass-width closure",
            "renormalization closure",
        ],
        "runtime_dependencies": ["Python", "licensed Wolfram runtime", "FeynRules", "MadGraph for smoke tests"],
        "validation_chain": [
            "repo integrity",
            "runtime preflight",
            "FeynRules load validation",
            "Feynman rule generation",
            "UFO export",
            "UFO loadability",
            "MadGraph smoke test",
        ],
        "entrypoint_commands": [
            "python scripts/setup/check_bhsm_hep_environment.py",
            "python scripts/setup/run_full_bhsm_hep_validation_chain.py",
        ],
        "expected_outputs": ["artifacts/*_v1_7.json", "runs/phase_three_n/ logs if real runtime is executed"],
        "gated_readiness_claims": ["FeynRules validation", "UFO export/loadability", "MadGraph smoke", "event generation"],
        "forbidden_claims": ["CERN-ready", "CERN-approved", "empirically validated", "complete BHSM collider model"],
        "reviewer_quickstart_docs": [
            "docs/institutional_hep_quickstart.md",
            "docs/institutional_validation_protocol.md",
            "docs/bhsm_collider_interface_model_card.md",
        ],
        "model_files": ["models/feynrules/BHSM_Minimal_Collider_Interface.fr.disabled"],
        "artifacts": [
            "artifacts/BHSM_runtime_asset_manifest_v1_7.json",
            "artifacts/BHSM_phase_three_o_gate_status_v1_7.json",
        ],
        "known_blockers": ["licensed Wolfram runtime", "FeynRules package mapping", "UFO export/loadability"],
        "recommended_institutional_review_steps": ["install/map legal runtime", "run preflight", "run validation chain", "inspect logs"],
        "notes": ["This is a handoff package, not a production experiment integration."],
        **guardrails(),
    }


def validation_protocol() -> dict[str, Any]:
    steps = []
    for step_id, purpose, command in [
        ("step_0_repo_integrity", "Run repository tests and guardrail audits", "python -m pytest -q"),
        ("step_1_runtime_preflight", "Detect legal runtime dependencies", "python tools/check_runtime_provisioning_v1_6.py"),
        ("step_2_feynrules_load_validation", "Load minimal model in FeynRules", "python scripts/feynrules/run_live_feynrules_validation.py"),
        ("step_3_feynman_rules_generation", "Generate Feynman rules for bounded subset", "same FeynRules validation wrapper"),
        ("step_4_ufo_export", "Export UFO after FeynRules validation", "python scripts/feynrules/run_ufo_export_if_validated.py"),
        ("step_5_ufo_loadability", "Check required UFO files/loadability", "file/loadability checks after export"),
        ("step_6_madgraph_import", "Import UFO in MadGraph", "python scripts/madgraph/run_minimal_ufo_smoke_if_available.py"),
        ("step_7_minimal_smoke_process", "Run minimal planned processes", "MadGraph smoke script"),
        ("step_8_event_output_optional", "Optional event output after smoke pass", "institution-defined"),
        ("step_9_detector_software_boundary_review", "External detector software boundary review", "institution-defined"),
    ]:
        steps.append(
            {
                "step_id": step_id,
                "purpose": purpose,
                "required_inputs": ["BHSM repository", "prior gates passed as applicable"],
                "command_or_script": command,
                "success_criteria": "corresponding artifact gate records true with real logs",
                "failure_criteria": "missing runtime, nonzero command exit, missing expected outputs, or forbidden claim boundary",
                "outputs": ["JSON artifact", "local logs if command actually runs"],
                "gates_unlocked_if_passed": ["next validation step"],
                "gates_remain_closed_if_failed": ["all downstream readiness claims"],
                "notes": "Do not promote readiness without live evidence.",
            }
        )
    return {"release_basis": RELEASE_BASIS, "phase": PHASE, "steps": steps, **guardrails()}


def collider_model_card() -> dict[str, Any]:
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "model_name": "BHSM_Minimal_Collider_Interface",
        "model_scope": "bounded minimal CKM/PMNS collider-interface subset",
        "physics_status": "internal boundary no-fit package complete/exported; external comparison separate/open",
        "software_status": "handoff package; runtime validation gated",
        "included_vertices": ["q_charged_current_CKM_BH", "lepton_charged_current_PMNS_BH"],
        "excluded_vertices": ["charged_boundary_response_matrix", "neutral_operator_kernel_BH", "standalone cp_holonomy_phase_attachment"],
        "parameters": ["BHSM-derived CKM/PMNS sources", "runtime/scheme placeholders for simulation only"],
        "runtime_parameters": ["g2_BH_runtime", "W_mass_runtime", "W_width_runtime", "fermion_masses_runtime", "fermion_widths_runtime"],
        "derived_BHSM_sources": ["CKM_BH_source_matrix", "PMNS_BH_source_matrix"],
        "not_derived_runtime_inputs": ["masses", "widths", "renormalization scale", "detector cards"],
        "mass_width_policy": "runtime collider-interface inputs only; not BHSM derivation inputs",
        "renormalization_policy": "open production scheme gate",
        "validation_status": "not FeynRules/UFO/MadGraph ready unless live artifacts pass",
        "known_limitations": ["complete BHSM 4D Lagrangian excluded", "unresolved vertex families excluded", "Wolfram/FeynRules runtime external"],
        "appropriate_uses": [
            "reviewing BHSM collider-interface structure",
            "checking reproducibility of minimal CKM/PMNS bounded subset",
            "attempting FeynRules/UFO/MadGraph validation in licensed HEP software environment",
        ],
        "inappropriate_uses": [
            "claiming complete BHSM collider model",
            "claiming official CERN integration",
            "claiming empirical validation",
            "using runtime PDG values as BHSM derivation inputs",
            "using excluded vertices as validated production vertices",
        ],
        "citation_files": ["CITATION.cff"],
        "contact_or_repository": "https://github.com/ncarberry64/Berger-Hopf-Standard-Model",
        "notes": ["CERN-like institutional HEP handoff package; not production readiness."],
        **guardrails(),
    }


def phase_three_o_gate_status() -> dict[str, Any]:
    runtime = runtime_report()
    n_status = json.loads((ROOT / "artifacts" / "BHSM_phase_three_n_gate_status_v1_6.json").read_text(encoding="utf-8"))
    manifest = handoff_manifest()
    downloads = download_attempts(False)
    wolfram = wolfram_mapping_status()
    feynrules = feynrules_installation_status()
    madgraph = madgraph_installation_status()
    return {
        "release_basis": RELEASE_BASIS,
        "phase": PHASE,
        "runtime_asset_manifest_exported": True,
        "runtime_download_attempts_exported": True,
        "wolfram_runtime_mapping_status_exported": True,
        "feynrules_installation_status_exported": True,
        "madgraph_installation_status_exported": True,
        "institutional_hep_handoff_manifest_exported": True,
        "institutional_validation_protocol_exported": True,
        "collider_interface_model_card_exported": True,
        "python_detected": runtime["python_detected"],
        "wolframscript_detected": runtime["wolframscript_detected"],
        "wolfram_kernel_detected": runtime["wolfram_kernel_detected"],
        "mathematica_detected": runtime["mathematica_detected"],
        "feynrules_detected": runtime["feynrules_detected"],
        "madgraph_detected": runtime["madgraph_detected"],
        "wolfram_runtime_ready": wolfram["ready_for_feynrules"],
        "feynrules_ready_for_validation": feynrules["ready_for_validation"],
        "madgraph_ready_for_smoke": madgraph["ready_for_smoke_test"],
        "allowed_assets_downloaded": any(item["download_succeeded"] for item in downloads["attempts"]),
        "downloaded_assets_committed_to_repo": False,
        "environment_ready_for_feynrules_validation": runtime["environment_ready_for_feynrules_validation"],
        "feynrules_validation_attempted": n_status["feynrules_validation_attempted"],
        "feynrules_syntax_validated": n_status["feynrules_syntax_validated"],
        "feynrules_model_load_validated": n_status["feynrules_model_load_validated"],
        "minimal_feynrules_model_enabled": n_status["minimal_feynrules_model_enabled"],
        "production_feynrules_file_exported": n_status["production_feynrules_file_exported"],
        "ufo_export_attempted": n_status["ufo_export_attempted"],
        "ufo_export_passed": n_status["ufo_export_passed"],
        "ufo_loadability_tested": n_status["ufo_loadability_tested"],
        "ufo_loadability_passed": n_status["ufo_loadability_passed"],
        "madgraph_smoke_test_attempted": n_status["madgraph_smoke_test_attempted"],
        "madgraph_smoke_test_passed": n_status["madgraph_smoke_test_passed"],
        "lhe_generation_ready": n_status["lhe_generation_ready"],
        "hepmc_generation_ready": n_status["hepmc_generation_ready"],
        "athena_ready": False,
        "cmssw_ready": False,
        "institutional_hep_handoff_package_ready": True,
        "is_official_cern_integration": manifest["is_official_cern_integration"],
        "is_complete_bhsm_4d_lagrangian": manifest["is_complete_bhsm_4d_lagrangian"],
        "is_minimal_collider_interface_subset": manifest["is_minimal_collider_interface_subset"],
        **guardrails(),
        "remaining_blockers": runtime["missing_components"]
        + ["live FeynRules validation", "UFO export/loadability", "MadGraph smoke test", "Athena/CMSSW boundary"],
        "recommended_status_language": (
            "BHSM Phase Three-O packages the runtime asset provisioning layer and CERN-like institutional HEP handoff bundle for the bounded minimal collider-interface subset. "
            "The repository can now guide external reviewers through dependency mapping, FeynRules validation, UFO export, and MadGraph smoke testing. "
            "Wolfram/FeynRules execution remains a gated external runtime requirement, and no official CERN integration or production readiness is claimed."
        ),
    }


def all_artifacts() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_runtime_asset_manifest_v1_7.json": runtime_asset_manifest(),
        "BHSM_runtime_download_attempts_v1_7.json": download_attempts(False),
        "BHSM_wolfram_runtime_mapping_status_v1_7.json": wolfram_mapping_status(),
        "BHSM_feynrules_installation_status_v1_7.json": feynrules_installation_status(),
        "BHSM_madgraph_installation_status_v1_7.json": madgraph_installation_status(),
        "BHSM_institutional_hep_handoff_manifest_v1_7.json": handoff_manifest(),
        "BHSM_institutional_validation_protocol_v1_7.json": validation_protocol(),
        "BHSM_collider_interface_model_card_v1_7.json": collider_model_card(),
        "BHSM_phase_three_o_gate_status_v1_7.json": phase_three_o_gate_status(),
    }


def write_all_artifacts() -> None:
    for name, payload in all_artifacts().items():
        write_json(ROOT / "artifacts" / name, payload)

