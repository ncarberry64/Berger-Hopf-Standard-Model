from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(output_format: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "neutrino-closure-status", "--format", output_format],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_neutrino_closure_status_json_is_split_and_mass_free() -> None:
    result = run_cli("json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["dimensionless_propagation_closure_status"] == "CONDITIONAL_DIMENSIONLESS_PROPAGATION_CLOSURE"
    assert payload["neutral_spectral_mass_theorem_status"] == "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE"
    assert payload["measurement_supported_admissible_positivity_status"].startswith("CONDITIONAL_")
    assert payload["action_derived_response_cone_status"] == "CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE"
    assert payload["dimensionful_ev_gev_mass_closure_status"] == "DIMENSIONFUL_MASS_NOT_AVAILABLE"
    assert payload["physical_mass_emitted"] is False
    assert not any(key in payload for key in ("mass_ev", "mass_gev", "mass_kg"))


def test_neutrino_closure_status_markdown_names_every_open_object() -> None:
    result = run_cli("markdown")
    assert result.returncode == 0, result.stderr
    for text in (
        "numeric sqrt(A_nu/Z_nu) in metres",
        "physical K_neutral,eff in m^-2",
        "complete-action derivation of the admissible response cone",
        "No physical eV/GeV neutrino mass is emitted.",
    ):
        assert text in result.stdout
