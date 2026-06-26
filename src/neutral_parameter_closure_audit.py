from __future__ import annotations

from fractions import Fraction
from typing import Dict

import neutral_bridge_pmns_source as bridge
import neutral_minimal_hessian as hessian


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build_neutral_parameter_closure_or_obstruction_artifact() -> Dict[str, object]:
    diag = bridge.diagnostic()
    hdiag = hessian.diagnostic()
    return {
        "public_status_before_gate": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "observed_neutrino_data_used": False,
        "PMNS_data_used": False,
        "gate": "neutral_parameters",
        "status": "STRONGLY_SUPPORTED_CANDIDATE",
        "neutral_parameter_final_derivation": "OPEN_LOCALIZABLE",
        "neutral_eta_beta_kappa": "STRONGLY_SUPPORTED_CANDIDATE",
        "candidate_values": {
            "eta_nu": _fraction_string(diag.eta_nu),
            "g_nu": _fraction_string(diag.g_nu),
            "beta_nu": _fraction_string(diag.beta_nu),
            "kappa_nu": _fraction_string(diag.kappa_nu),
            "K_nu": [[_fraction_string(value) for value in row] for row in diag.K_nu],
            "H_nu": [list(row) for row in hdiag.matrix],
            "det_H_nu": hdiag.determinant,
            "N_nu_3_0": hdiag.cost_3_0,
            "N_nu_1_1": hdiag.cost_1_1,
            "v_nu_H_v_nu": hdiag.tangent_norm,
        },
        "source_trace": {
            "neutral_minimal_hessian": "src/neutral_minimal_hessian.py",
            "neutral_bridge_pmns_source": "src/neutral_bridge_pmns_source.py",
        },
        "missing_objects": [
            "action/source derivation of eta_nu",
            "action/source derivation of beta_nu",
            "action/source derivation of kappa_nu",
            "neutral threshold operator",
        ],
        "obstruction": (
            "The repo contains a strong neutral Hessian/bridge candidate, but the final "
            "action/source derivation and neutral threshold rules remain open."
        ),
    }
