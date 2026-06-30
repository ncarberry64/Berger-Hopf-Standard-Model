"""Reviewer-facing BHSM Engine/Physics status and reproduction reports."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .action_derivation_gates import build_action_derivation_report
from .engine_invariants import build_engine_invariant_report


ROOT = Path(__file__).resolve().parents[3]
ENGINE_PHYSICS_BOUNDARY = (
    "BHSM Engine validation does not constitute empirical validation of BHSM as new particle physics."
)


def engine_physics_status() -> dict[str, object]:
    return {
        "version": "1.9",
        "engine_validated_capabilities": [
            "high-throughput precision-gated four-vector coordinate transformations",
            "synthetic boundary-stress validation",
            "published CMS dimuon four-vector kinematics validation",
            "CERN ROOT 6.30.06 compile and runtime smoke gate",
            "deterministic invariant-preservation tests",
        ],
        "engine_excluded_capabilities": [
            "detector track reconstruction",
            "magnetic-field or material propagation",
            "track fitting",
            "empirical validation of BHSM particle physics",
            "CMS, CERN, or ATLAS endorsement",
        ],
        "physics_current_status": "integrated conditional Berger-Hopf boundary-mode framework",
        "physics_open_blockers": [
            "complete action derivations",
            "transport theorems",
            "physical normalization and unit maps",
            "gauge/scalar normalization",
            "physical neutrino mass closure",
            "external runtime/export gates",
        ],
        "claim_boundaries": [
            ENGINE_PHYSICS_BOUNDARY,
            "BHSM does not claim full Standard Model derivation or physical eV/GeV neutrino mass closure.",
        ],
        "validated_data_sources": [
            {
                "name": "CMS 2010 dimuon derived education dataset",
                "record": 303,
                "doi": "10.7483/OPENDATA.CMS.4M97.3SQ9",
                "scope": "four-vector coordinate transformations only",
            }
        ],
        "runtime_gates": {
            "root": "CI_COMPILED_RUNTIME_GATED",
            "native_pmu": "PERF_COUNTERS_UNAVAILABLE_OR_PERMISSION_DENIED_ON_HOSTED_RUNNER",
            "feynrules_ufo_madgraph": "RUNTIME_GATED",
        },
    }


def minimal_theorem_core() -> dict[str, object]:
    action = build_action_derivation_report()
    rows = [
        ("CORE-01", "Unified boundary/action principle", "CONDITIONAL", "complete normalized action"),
        ("CORE-02", "Sector projectors and admissible domains", "ARTIFACT_BACKED", "complete-action uniqueness"),
        ("CORE-03", "Charged Omega_f operators", action["omega_f"]["status"], "complete twisted Dirac/bundle action"),
        ("CORE-04", "rho_ch threshold structure", action["rho_ch"]["status"], "action selection of rho_ch"),
        ("CORE-05", "Charged bridge and beta hierarchy", "CONDITIONAL", "4/3 overlap action source"),
        ("CORE-06", "Common-16 generator candidate", "CONDITIONAL", "shared action generator"),
        ("CORE-07", "CKM exponent", "OPEN_MISSING_ACTION_DERIVATION", "reciprocal transport theorem"),
        ("CORE-08", "PMNS/neutrino structure", "CONDITIONAL", "physical basis and unit map"),
        ("CORE-09", "Neutral propagation", "CONDITIONAL", "dimensionful transport normalization"),
        ("CORE-10", "Neutral positivity", "CONDITIONAL", "complete-action admissible cone"),
        ("CORE-11", "Boundary measure/collar transport", "OPEN_MISSING_TRANSPORT_THEOREM", "normalized physical measure"),
        ("CORE-12", "Gauge/scalar normalization", "OPEN_MISSING_PHYSICAL_NORMALIZATION", "action normalization"),
        ("CORE-13", "Runtime/export gates", "RUNTIME_GATED", "live external tool validation"),
    ]
    return {
        "version": "1.9",
        "full_completion_claimed": False,
        "core_items": [
            {
                "core_id": core_id,
                "name": name,
                "statement": f"BHSM repository status for {name}.",
                "inputs_or_axioms": ["local BHSM artifacts", "author ontology where labeled conditional"],
                "derived_objects": [name],
                "proof_route": "artifact and executable-gate audit",
                "artifact_sources": ["STATUS.md", "CLAIMS.md", "ARTIFACT_INDEX.md"],
                "test_sources": ["tests/test_minimal_theorem_core.py"],
                "status": status,
                "remaining_blockers": [blocker],
                "claim_boundary": "Status is evidence-gated and is not empirical confirmation.",
            }
            for core_id, name, status, blocker in rows
        ],
    }


def falsification_table() -> dict[str, object]:
    rows = [
        ("ENG-01", "CERN open-data four-vector accuracy", "ENGINE", "ARTIFACT_BACKED", "scale-aware error exceeds declared bound"),
        ("ENG-02", "SIMD/control speedup", "ENGINE", "ENVIRONMENT_SPECIFIC", "independent matched implementation is not faster"),
        ("ENG-03", "ROOT implicit multithreading scaling", "ENGINE", "NEGATIVE_HOSTED_RESULT", "no scaling or regression; current 2-thread run is 0.940x"),
        ("ENG-04", "Native PMU explanation", "ENGINE", "RUNTIME_GATED", "PMU counters contradict proposed mechanism"),
        ("ENG-05", "Lorentz invariant preservation", "ENGINE", "ARTIFACT_BACKED", "declared backward-error gate fails"),
        ("ENG-06", "Round-trip coordinate transformation", "ENGINE", "ARTIFACT_BACKED", "inverse fails scale-aware tolerance"),
        ("PHY-01", "Frozen prediction integrity", "PHYSICS", "ESTABLISHED", "frozen artifact hash changes unexpectedly"),
        ("PHY-02", "Charged projectors", "PHYSICS", "ARTIFACT_BACKED", "projector identities or ledger mapping fail"),
        ("PHY-03", "Common-16 generator", "PHYSICS", "CONDITIONAL", "no shared action generator exists"),
        ("PHY-04", "CKM exponent", "PHYSICS", "OPEN", "action-derived transport yields a different exponent"),
        ("PHY-05", "PMNS structure", "PHYSICS", "CONDITIONAL", "derived basis map conflicts with frozen structure"),
        ("PHY-06", "Neutral propagation", "PHYSICS", "CONDITIONAL", "complete action lacks propagation response"),
        ("PHY-07", "Neutral positivity", "PHYSICS", "CONDITIONAL", "admissible cone contains a negative direction"),
        ("PHY-08", "Physical neutrino mass", "PHYSICS", "OPEN", "no unit-safe physical map or external bounds conflict after one is derived"),
        ("PHY-09", "Omega_f action derivation", "PHYSICS", "CONDITIONAL", "complete action does not generate sector functional"),
        ("PHY-10", "rho_ch action derivation", "PHYSICS", "OPEN", "action selects a value other than 3"),
        ("PHY-11", "Boundary-measure normalization", "PHYSICS", "OPEN", "normalized measure cannot be constructed"),
        ("PHY-12", "Gauge/scalar normalization", "PHYSICS", "OPEN", "complete action gives incompatible normalization"),
        ("PHY-13", "External HEP runtime readiness", "PHYSICS", "RUNTIME_GATED", "live toolchain validation fails"),
    ]
    return {
        "version": "1.9",
        "rows": [
            {
                "claim_id": claim_id,
                "claim": claim,
                "track": track,
                "current_status": status,
                "prediction_or_requirement": claim,
                "what_would_falsify_it": falsifier,
                "dataset_or_calculation_required": "independent matched reproduction or named complete-action calculation",
                "current_test_or_artifact": "see ARTIFACT_INDEX.md and reviewer reproduction manifest",
                "claim_boundary": ENGINE_PHYSICS_BOUNDARY if track == "ENGINE" else "Internal theorem status is not empirical confirmation.",
            }
            for claim_id, claim, track, status, falsifier in rows
        ],
    }


def reviewer_manifest() -> dict[str, object]:
    commands = {
        "reviewer-smoke": "python -m pytest -q tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py",
        "reviewer-full": "python -m pytest -q",
        "reviewer-cern-open-data": "python -m bhsm.interface.benchmarks.cern_open_data_benchmark --download --summary",
        "reviewer-invariants": "python -m bhsm.interface engine-invariants --format json",
        "reviewer-claims-audit": "python tools/audit_forbidden_claims.py",
        "reviewer-engine-report": "python -m bhsm.interface engine-status --format markdown",
        "reviewer-physics-status": "python -m bhsm.interface physics-status --format markdown",
    }
    return {
        "version": "1.9",
        "commands": commands,
        "expected_outputs": {key: "exit code 0 or an explicit documented runtime/data gate" for key in commands},
        "expected_artifacts": [
            "artifacts/BHSM_engine_invariant_preservation_v1_9.json",
            "artifacts/cern_open_data_benchmark/results.json",
        ],
        "expected_test_counts": {"baseline_before_v1_9": 2277, "exact_post_v1_9_count": "reported by CI"},
        "data_requirements": {"reviewer-cern-open-data": "requires_network_or_cached_data", "all_other_commands": "offline"},
        "runtime_requirements": {"python": ">=3.10", "root": "containerized CI for ROOT-specific checks"},
        "time_estimates": {"smoke": "under 5 minutes", "full": "about 5 minutes", "cern": "network and host dependent"},
        "failure_interpretation": "A failed gate falsifies or blocks only its named claim; it does not validate or invalidate unrelated BHSM Physics claims.",
        "claim_boundaries": [ENGINE_PHYSICS_BOUNDARY, "No detector reconstruction is included."],
    }


def external_reproduction_packet() -> dict[str, object]:
    manifest = reviewer_manifest()
    return {
        "version": "1.9",
        "recommended_reproducer_profile": [
            "computational HEP user",
            "ROOT/CMS open-data user",
            "numerical methods person",
            "scientific software engineer",
            "mathematical physicist comfortable with code",
        ],
        "scope": "reproduce BHSM Engine CERN open-data four-vector precision and throughput",
        "not_in_scope": ["detector reconstruction", "validation of BHSM Physics", "institutional endorsement"],
        "commands_to_run": manifest["commands"],
        "expected_outputs": manifest["expected_outputs"],
        "data_requirements": manifest["data_requirements"],
        "hardware_notes": "Report CPU, compiler, SIMD flags, thread count, and PMU permissions; unfavorable results are valid results.",
        "how_to_report_results": "Attach command output, generated JSON, hardware metadata, and deviations from the protocol.",
        "claim_boundaries": manifest["claim_boundaries"],
        "draft_message": "Can you reproduce the BHSM Engine CERN open-data four-vector validation and confirm the precision/performance claims?",
        "contact_performed": False,
    }


def markdown_report(title: str, payload: dict[str, object]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"


def run_reviewer_command(name: str) -> int:
    command = reviewer_manifest()["commands"].get(name)
    if command is None:
        raise KeyError(name)
    return subprocess.call(command, cwd=ROOT, shell=True)


def payload_for_command(command: str) -> dict[str, object]:
    mapping: dict[str, Any] = {
        "engine-status": engine_physics_status,
        "physics-status": engine_physics_status,
        "reviewer-reproduction": reviewer_manifest,
        "engine-invariants": build_engine_invariant_report,
        "minimal-theorem-core": minimal_theorem_core,
        "omega-f-action-audit": lambda: build_action_derivation_report()["omega_f"],
        "rho-ch-action-audit": lambda: build_action_derivation_report()["rho_ch"],
        "falsification-table": falsification_table,
        "external-reproduction-packet": external_reproduction_packet,
    }
    return mapping[command]()


def emit_hardening_payload(command: str, output_format: str) -> None:
    payload = payload_for_command(command)
    if command == "physics-status":
        payload = {
            "physics_current_status": payload["physics_current_status"],
            "physics_open_blockers": payload["physics_open_blockers"],
            "claim_boundaries": payload["claim_boundaries"],
        }
    elif command == "engine-status":
        payload = {
            "engine_validated_capabilities": payload["engine_validated_capabilities"],
            "engine_excluded_capabilities": payload["engine_excluded_capabilities"],
            "runtime_gates": payload["runtime_gates"],
            "claim_boundaries": payload["claim_boundaries"],
        }
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown_report(command.replace("-", " ").title(), payload), end="")
