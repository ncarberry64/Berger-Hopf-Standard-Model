"""Audit what Weyl/resolvent data the retained heat functional requires."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_common_source_frechet_response_v15_99 import (  # noqa: E402
    regulated_trace,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
)
SUPERDET = ARTIFACTS / "BHSM_aether_common_quantum_superdeterminant_v15_96.json"
FRECHET = ARTIFACTS / "BHSM_aether_common_source_frechet_response_v15_99.json"
WEYL = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
)
SCALAR = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
)
DIRAC = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
)
TAIL = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_SOURCE_TAIL_OWNERSHIP_AUDIT.json"
)
WEAK_HEAT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_WEAK_HEAT_VARIATIONS.json"
)
MODULE = ROOT / "src/bhsm/interface/aether_common_source_frechet_response_v15_99.py"
INPUTS = (SUPERDET, FRECHET, WEYL, SCALAR, DIRAC, TAIL, WEAK_HEAT, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _fraction(value: Fraction) -> dict[str, Any]:
    return {"exact": f"{value.numerator}/{value.denominator}", "decimal": float(value)}


def _single_probe_counterexample() -> dict[str, Any]:
    # M(z)=a-z-b^2/(d-z).  These positive matrices have the same M(-1)
    # but different spectra and therefore different retained heat functionals.
    first = {
        "a": Fraction(2),
        "b": Fraction(1),
        "d": Fraction(3),
    }
    second = {
        "a": Fraction(29, 12),
        "b": Fraction(2),
        "d": Fraction(5),
    }
    z = Fraction(-1)

    def weyl(record: dict[str, Fraction]) -> Fraction:
        return record["a"] - z - record["b"] ** 2 / (record["d"] - z)

    def matrix(record: dict[str, Fraction]) -> np.ndarray:
        return np.asarray(
            [
                [float(record["a"]), float(record["b"])],
                [float(record["b"]), float(record["d"])],
            ]
        )

    matrices = (matrix(first), matrix(second))
    traces = [regulated_trace(value, heat_length=1.0) for value in matrices]
    eigenvalues = [np.linalg.eigvalsh(value).tolist() for value in matrices]
    determinants = [np.linalg.det(value) for value in matrices]
    return {
        "Weyl_formula": "M(z)=a-z-b^2/(d-z)",
        "z": -1.0,
        "first_matrix": [[2.0, 1.0], [1.0, 3.0]],
        "second_matrix": [[29.0 / 12.0, 2.0], [2.0, 5.0]],
        "common_Weyl_value": _fraction(weyl(first)),
        "second_Weyl_value": _fraction(weyl(second)),
        "positive_matrix_determinants": determinants,
        "spectra": eigenvalues,
        "regulated_trace_minus_half_E1": traces,
        "regulated_trace_difference": traces[1] - traces[0],
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all resolvent/heat synthesis inputs are required")
    records = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in INPUTS
        if path.suffix == ".json"
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all resolvent/heat synthesis inputs must validate")
    superdet = records[SUPERDET.name]
    frechet = records[FRECHET.name]
    weyl = records[WEYL.name]
    scalar = records[SCALAR.name]
    dirac = records[DIRAC.name]
    tail = records[TAIL.name]
    weak_heat = records[WEAK_HEAT.name]
    witness = _single_probe_counterexample()

    validation = {
        "all_inputs_validated": True,
        "retained_functional_is_E1_heat_regulated": superdet[
            "regulated_free_superdeterminant_seed"
        ]["definition"].startswith("Gamma_1^R=-(1/2)*STr*E1"),
        "same_operator_Frechet_pair_contact_engine_is_retained": frechet[
            "validation"
        ]["all_responses_from_one_operator"]
        is True,
        "native_Weyl_parameter_is_not_momentum_squared": weyl[
            "operator_family"
        ]["z_identified_with_momentum_squared"]
        is False,
        "current_concrete_channel_rows_use_one_probe": (
            scalar["spectral_probe"]["z"] == -1.0
            and dirac["spectral_probe"]["z"] == -1.0
        ),
        "counterexample_matrices_are_positive": all(
            value > 0.0 for value in witness["positive_matrix_determinants"]
        )
        and all(min(values) > 0.0 for values in witness["spectra"]),
        "counterexample_has_identical_single_probe_Weyl_value": witness[
            "common_Weyl_value"
        ]["exact"]
        == witness["second_Weyl_value"]["exact"],
        "counterexample_heat_functionals_differ": abs(
            witness["regulated_trace_difference"]
        )
        > 1.0e-6,
        "weak_heat_variations_require_functional_calculus_not_one_probe": (
            "int_" in weak_heat["weak_variation_theorem"][
                "integrated_contact_bound"
            ]
            and "exp(-sP)" in weak_heat["weak_variation_theorem"][
                "contact_trace_bound"
            ]
        ),
        "source_angular_or_relative_trace_tail_remains_open": tail[
            "adjudication"
        ]["pair_contact_continuum_or_relative_trace"]
        == "OPEN",
        "no_p2_profile_endpoint_reference_subtraction_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT",
        "status": "SINGLE_NEGATIVE_z_PROBE_NOT_SUFFICIENT_FOR_RETAINED_HEAT_FUNCTIONAL",
        "classification": (
            "THE_RETAINED_GATE7_QUANTUM_FUNCTIONAL_IS_MINUS_ONE_HALF_STr_"
            "E1(ell_kappa_squared_P),_WHOSE_FIRST_AND_SECOND_VARIATIONS_"
            "REQUIRE_CONTROLLED_FUNCTIONAL_CALCULUS_OVER_THE_SPECTRUM;_THE_"
            "NATIVE_WEYL_FAMILY_CAN_ENCODE_THAT_DATA_BUT_A_BROAD_ENCLOSURE_"
            "AT_THE_SINGLE_PROBE_z_MINUS_1_DOES_NOT_DETERMINE_OR_ENCLOSE_THE_"
            "HEAT_FORCE_OR_PAIR_PLUS_CONTACT_HESSIAN"
        ),
        "retained_functional_calculus": {
            "functional": "Gamma_heat(P)=-(1/2)*STr*E1(ell_kappa^2*P)",
            "first_variation": (
                "D_Gamma_heat[P_h]=(1/2)*integral_(ell_kappa^2)^infinity_"
                "STr(exp(-sP)*P_h)_ds"
            ),
            "commuting_spectral_multiplier": (
                "f_prime(lambda)=(1/2)*exp(-ell_kappa^2*lambda)/lambda"
            ),
            "second_variation": (
                "ONE_NONCOMMUTING_DUHamel_PAIR_TERM_PLUS_THE_SEAGULL_CONTACT_"
                "TERM_FROM_THE_SAME_P"
            ),
            "equivalent_data_sufficient_in_principle": [
                "THE_ACTION_OWNED_SPECTRAL_MEASURE_WITH_INTEGRABLE_VARIATION_BOUNDS",
                "THE_WEYL_FAMILY_ON_A_REGION_SUFFICIENT_FOR_A_CONTROLLED_CONTOUR_OR_STIELTJES_SYNTHESIS",
                "THE_HEAT_SEMIGROUP_VARIATION_DIRECTLY_WITH_RELATIVE_TRACE_CONTROL",
            ],
            "one_resolvent_probe_sufficient": False,
        },
        "single_probe_counterexample": witness,
        "current_channel_result_scope": {
            "parametric_formulas_accept_every_real_z_less_than_zero": True,
            "materialized_numeric_rows": "z=-1_ONLY",
            "base_and_weak_bounds_at_z_minus_1": "DERIVED_BROADLY",
            "controlled_E1_functional_synthesis": "OPEN",
            "pair_contact_angular_or_relative_trace_tail": "OPEN",
            "zero_source_weak_geometry_force": "OPEN",
        },
        "adjudication": {
            "z_identified_with_p_squared": False,
            "z_minus_1_rows_retracted": False,
            "z_minus_1_rows_promoted_to_Gamma_heat": False,
            "exterior_Weyl_compression_route": "VALID_REQUIRES_SPECTRAL_SYNTHESIS",
            "Gate7_zero_source_force_evaluable_from_current_rows": False,
        },
        "exact_next_dependency": (
            "DERIVE_A_CONTROLLED_ACTION_OWNED_FUNCTIONAL_CALCULUS_SYNTHESIS_"
            "OF_THE_E1_HEAT_VARIATIONS_FROM_THE_MAXIMAL_FORWARD_WEYL_OR_"
            "SPECTRAL_FAMILY_TOGETHER_WITH_THE_COMMON_SOURCE_BRST_ANGULAR_"
            "RELATIVE_TRACE_TAIL;_THEN_ASSEMBLE_THE_ZERO_SOURCE_WEAK_FORCE"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "single_probe_sufficient": payload[
                    "retained_functional_calculus"
                ]["one_resolvent_probe_sufficient"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
