from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface.ae3_c2_lorentzian_gauge_ghost_hessian import (
    constraint_ghost_frequency_block,
    current_c2_transverse_frequency_symbol,
    gauge_ghost_hessian_claim_boundary,
    lowest_transverse_residue_witness,
    transverse_frequency_dtn,
)
from scripts.materialize_ae3_c2_lorentzian_gauge_ghost_hessian import (
    TARGET,
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_ae3_c2_lorentzian_gauge_ghost_hessian.py"


def test_continuous_frequency_dtn_is_not_a_cycle_lookup() -> None:
    values = [
        transverse_frequency_dtn(q_squared=q2)
        for q2 in (-0.0013, 0.0, 0.0027)
    ]
    assert values[0] > values[1] > values[2]
    assert abs(values[1] - 1.679557832021) < 2.0e-10


def test_frequency_derivative_and_static_energy_are_same_action_derivatives() -> None:
    result = lowest_transverse_residue_witness()
    assert abs(
        result["static_dimensionless_DtN"]
        - result["static_energy_identity_right_hand_side"]
    ) < 2.0e-10
    assert abs(
        result["d_DtN_d_q_squared_at_zero"]
        - result["centered_difference_derivative"]
    ) < 2.0e-8


def test_transverse_residue_mismatch_is_recorded_not_fitted() -> None:
    result = lowest_transverse_residue_witness()
    assert 0.0 < result["temporal_to_complete_spatial_mode_residue_ratio"] < 1.0
    assert abs(
        result["temporal_to_complete_spatial_mode_residue_ratio"]
        - 0.590609601653
    ) < 2.0e-10
    assert result["one_Lorentzian_residue"] is False


def test_constraint_and_ghost_blocks_obey_the_same_ward_identity() -> None:
    block = constraint_ghost_frequency_block(
        omega=0.37,
        scalar_laplacian=3.0,
        z_temporal=0.25,
        z_spatial=0.42,
    )
    assert block["Maxwell_Ward_residual"] < 1.0e-12
    assert abs(
        block["ghost_Faddeev_Popov_symbol"] - block["expected_ghost_symbol"]
    ) < 1.0e-12
    assert np.allclose(
        block["gauge_fixed_block"], block["gauge_fixed_block"].conj().T
    )
    assert block["BRST_real_degree_weights"] == {
        "temporal_plus_longitudinal_bosons": 2,
        "complex_ghost": -2,
    }


def test_current_c2_symbol_uses_continuous_omega_and_no_free_residue() -> None:
    symbol = current_c2_transverse_frequency_symbol(
        log_radii=np.asarray((0.0, 0.0, 0.0)), omega=0.125
    )
    assert symbol["frequency_domain"] == "CONTINUOUS_REAL_OMEGA__NOT_PERIODIC_CYCLE_MODE"
    assert np.all(symbol["Z_t_over_K_F5"] < symbol["Z_s_over_K_F5"])
    assert symbol["independent_residue_inserted"] is False


def test_claim_boundary_stops_before_photon_and_mixing() -> None:
    claims = gauge_ghost_hessian_claim_boundary()
    assert claims["same_C2_continuous_frequency_gauge_ghost_Hessian_derived"] is True
    assert claims["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"] is False
    assert claims["residue_outcome"] == "MISMATCH_RECORDED__NOT_RENORMALIZED"
    assert claims["physical_photon_derived"] is False
    assert claims["electroweak_neutral_Hessian_derived"] is False


def test_materialized_hessian_is_valid_and_deterministic() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["CURRENT_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN_DERIVED"] is True
    assert payload["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"] is False
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert stored["validation_passed"] is True
