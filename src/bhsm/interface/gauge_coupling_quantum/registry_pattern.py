"""Audit the registered 1:2:7 gauge-coupling pattern."""

from .common import STATUS_REGISTRY, input_guard


def audit_gauge_coupling_registry_pattern() -> dict[str, object]:
    return {
        "alpha1_expression": "1/(6*pi^2)",
        "alpha2_expression": "2/(6*pi^2)",
        "alpha3_expression": "7/(6*pi^2)",
        "base_quantum": "1/(6*pi^2)",
        "weights": {"w1": 1, "w2": 2, "w3": 7},
        "source_locations": [
            "src/gauge_couplings.py",
            "src/charged_lepton_eta_derivation.py",
            "tests/test_rg_matching.py",
        ],
        "is_registry_pattern": True,
        "is_action_derivation": False,
        "evidence_for": ["all three supplied screens share the exact denominator and integer weights"],
        "evidence_against": ["the registry calls them supplied matching screens, not action coefficients"],
        "status": STATUS_REGISTRY,
        "claim_boundary": "Registered coupling expressions are not action derivations.",
        **input_guard(),
    }
