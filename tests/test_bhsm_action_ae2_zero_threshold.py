import importlib.util
from pathlib import Path

import numpy as np

from bhsm.interface.action_extension_ae2_zero_threshold import (
    constant_channel_zero_transport,
    piecewise_constant_zero_transport,
    two_sided_ae2_zero_transport,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_gate7_ae2_zero_threshold.py"


def _audit():
    spec = importlib.util.spec_from_file_location("ae2_zero_threshold", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_zero_transport_makes_factorized_collar_lower_bound_sharp() -> None:
    witness = constant_channel_zero_transport(2.75, 0.4, 1.0 - 0.5j)
    assert witness["terminal_trace"] == (1.0 - 0.5j) * np.exp(-1.1)
    assert witness["factorized_form_energy"] == 0.0
    assert witness["zero_energy_weyl_value"] == 0.0

    variable = piecewise_constant_zero_transport(
        [2.0, -1.0, 0.5], [0.1, 0.2, 0.3], 1.0
    )
    assert variable["maximum_transport_residual"] == 0.0
    assert variable["factorized_form_energy"] == 0.0


def test_ae2_reset_graph_does_not_turn_local_zero_conormals_positive() -> None:
    lift = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    witness = two_sided_ae2_zero_transport(
        1.5, -1.5, 0.2, 0.3, lift, [1.0, 2.0j]
    )
    assert witness["trace_graph_residual"] == 0.0
    assert witness["two_sided_zero_energy_wronskian"] == 0.0
    assert witness["strict_positive_margin_from_local_collars"] is False


def test_ae2_zero_threshold_audit_is_deterministic_and_conservative() -> None:
    module = _audit()
    first = module.build_payload()
    second = module.build_payload()
    assert first["validation_passed"] is True
    assert first["claim_boundary"]["physical_maximal_exterior_has_zero_mode"] == (
        "NOT_CLAIMED"
    )
    assert first["claim_boundary"]["Gate7"] == "ACTIVE_NOT_CLOSED"
    assert module.deterministic_bytes(first) == module.deterministic_bytes(second)
