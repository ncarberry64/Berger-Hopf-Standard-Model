"""Materialize the current-C2 family harmonic-energy pullback audit."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_family_harmonic_energy_pullback import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    harmonic_spectral_pullback,
    physical_mass_ownership_gate,
    positive_energy_killer_test,
)


ARTIFACTS = ROOT / "artifacts"
FLAVOR = ARTIFACTS / "BHSM_aether_hybrid_flavor_spectrum_v15_54.json"
LOCALIZATION = ARTIFACTS / "action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
FAMILY_AUDIT = ARTIFACTS / "action_extension/BHSM_AE3_FAMILY_NONCENTRAL_RETURN_PROVENANCE_AUDIT.json"
RADIUS = ARTIFACTS / "BHSM_aether_diagonal_sp1_m4_attachment_v15_50.json"
TARGET = ARTIFACTS / "action_extension/BHSM_AE3_FAMILY_HARMONIC_ENERGY_PULLBACK_AUDIT.json"
INPUTS = (
    FLAVOR,
    LOCALIZATION,
    FAMILY_AUDIT,
    RADIUS,
    ROOT / "src/bhsm/interface/ae3_family_harmonic_energy_pullback.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    flavor = _load(FLAVOR)
    localization = _load(LOCALIZATION)
    prior_audit = _load(FAMILY_AUDIT)
    radius = _load(RADIUS)
    pullback = harmonic_spectral_pullback()
    killer = positive_energy_killer_test()
    ownership = physical_mass_ownership_gate()
    boundary = claim_boundary()
    expected = {
        "charged_lepton": [0, 35, 99],
        "up": [0, 48, 120],
        "down": [0, 48, 80],
    }
    validation = {
        "historical_scalar_seed_valid": flavor["validation_passed"] is True,
        "same_AE3_C2_family_fibers": localization["family_mode_C2_instantiation"]["certificate_passed"] is True,
        "prior_noncentral_mass_audit_preserved": prior_audit["validation_passed"] is True and prior_audit["claim_boundary"]["family_mass_hierarchy_derived"] is False,
        "action_normalized_reset_radius_valid": radius["validation_passed"] is True,
        "frozen_eigenvalues_reproduced": all(
            [round(value) for value in pullback["sectors"][sector]["dimensionless_R_F_squared_eigenvalues"]] == values
            for sector, values in expected.items()
        ),
        "all_three_pullbacks_noncentral": pullback["spectral_noncentrality_derived"],
        "positive_energy_ordering_kill_test_closes": killer["test_passed"],
        "physical_mass_not_false_promoted": ownership["physical_mass_operator_derived"] is False,
        "old_overlap_not_reused": ownership["old_exponential_overlap_rule_used"] is False,
        "no_empirical_mass_input": ownership["empirical_mass_data_used"] is False and killer["no_measured_mass_used"],
        "no_spectrum_rebuild": boundary["particle_spectrum_rebuilt"] is False,
    }
    return {
        "artifact": "BHSM_AE3_FAMILY_HARMONIC_ENERGY_PULLBACK_AUDIT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "harmonic_spectral_pullback": pullback,
        "positive_energy_killer_test": killer,
        "physical_mass_ownership_gate": ownership,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("family harmonic-energy pullback audit failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
