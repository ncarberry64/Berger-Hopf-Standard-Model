import importlib.util
from pathlib import Path

import numpy as np

from bhsm.interface.action_extension_global_spin_reset_ae2 import (
    ACTION_VERSION,
    brst_transmission_residual,
    independent_phase_twist_distance,
    opposite_normal_green_residual,
    transmission_graph_certificate,
    transmit_trace,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_bhsm_action_ae2_global_spin_reset.py"


def _materializer():
    spec = importlib.util.spec_from_file_location("ae2_materializer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _unitary() -> np.ndarray:
    raw = np.array(
        [
            [1, 1j, 0, 0],
            [1j, 1, 0, 0],
            [0, 0, 1, -1j],
            [0, 0, -1j, 1],
        ],
        dtype=complex,
    )
    return raw / np.sqrt(2.0)


def test_global_spin_reset_graph_is_self_adjoint_and_brst_covariant() -> None:
    lift = _unitary()
    form = np.diag([1.0, 1.0, -1.0, -1.0])
    psi = np.array([1 + 2j, -0.5j, 3.0, -2.0 + 0.25j])
    phi = np.array([-1j, 2.0, 0.75 + 0.5j, 1.0])
    ghost_seed = np.arange(16, dtype=float).reshape(4, 4)
    ghost = ghost_seed - ghost_seed.T

    assert np.allclose(transmit_trace(psi, lift), lift @ psi)
    assert opposite_normal_green_residual(psi, phi, form, lift) < 1.0e-12
    certificate = transmission_graph_certificate(form, lift)
    assert certificate["maximal_isotropic"] is True
    assert brst_transmission_residual(psi, lift, ghost) < 1.0e-12
    assert independent_phase_twist_distance(lift, 0.4) > 0.0


def test_ae2_payloads_close_only_the_matter_domain() -> None:
    action, gate7 = _materializer().build_payloads()
    assert action["action_version"] == ACTION_VERSION
    assert action["decision_report"]["NORMAN_SELECTED_OPTION"] == "A"
    assert action["validation_passed"] is True
    assert action["action_definition"]["independent_Cayley_phase"] is None
    assert action["claim_boundary"]["unchanged_action_completed"] is False
    assert gate7["validation_passed"] is True
    assert gate7["source_domain"]["fermion_W_phys_local_surface_block"] == 0
    assert gate7["source_domain"]["Cayley_phase_family"] is None
    assert gate7["adjudication"]["Gate7"] == "ACTIVE_NOT_CLOSED"
    assert gate7["FULL_BHSM_COMPLETE"] is False


def test_ae2_materialization_is_byte_deterministic() -> None:
    module = _materializer()
    first = module.build_payloads()
    second = module.build_payloads()
    assert module.deterministic_bytes(first[0]) == module.deterministic_bytes(second[0])
    assert module.deterministic_bytes(first[1]) == module.deterministic_bytes(second[1])
