import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface.aether_forward_c2_local_transfer_germ import (
    local_transfer_cauchy_germ,
    product_dirac_channel_cauchy_generator_jets,
    scalar_channel_cauchy_generator_jets,
)
from bhsm.interface.aether_forward_channel_transfer import (
    product_dirac_channel_transfer_generator,
    scalar_channel_transfer_generator,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_c2_outgoing_local_transfer_germ.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_OUTGOING_LOCAL_TRANSFER_GERM.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("c2_transfer_germ", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generator_cauchy_jets_match_centered_differences() -> None:
    x, rate, h, h_rate, step = -0.07, 0.13, -0.21, 0.09, 1.0e-6
    scalar = scalar_channel_cauchy_generator_jets(
        3.0, x, rate, -1.0, h, h_rate
    )
    product = product_dirac_channel_cauchy_generator_jets(
        1.5, x, rate, -1.0, h, h_rate, chirality=-1
    )
    scalar_parameter_fd = (
        scalar_channel_transfer_generator(3.0, x + step * h, -1.0)
        - scalar_channel_transfer_generator(3.0, x - step * h, -1.0)
    ) / (2.0 * step)
    product_parameter_fd = (
        product_dirac_channel_transfer_generator(
            1.5, x + step * h, -1.0, chirality=-1
        )
        - product_dirac_channel_transfer_generator(
            1.5, x - step * h, -1.0, chirality=-1
        )
    ) / (2.0 * step)
    np.testing.assert_allclose(
        scalar["parameter_first"], scalar_parameter_fd, rtol=1.0e-9
    )
    np.testing.assert_allclose(
        product["parameter_first"], product_parameter_fd, rtol=1.0e-9
    )
    assert local_transfer_cauchy_germ(scalar)[
        "endpoint_condition_imposed"
    ] is False


def test_c2_outgoing_local_transfer_germ_validates() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["actual_C2_birth_and_transfer_germ"] == (
        "DERIVED"
    )
    assert len(payload["reset_quotient_rows"]) == 2
    for row in payload["reset_quotient_rows"]:
        assert len(row["channels"]) == 3
        for channel in row["channels"].values():
            witness = channel["crosscheck"]
            assert 0.11 < witness["value_halving_ratio"] < 0.14
            assert 0.11 < witness["parameter_jet_halving_ratio"] < 0.14
            assert channel["endpoint_condition_imposed"] is False


def test_c2_outgoing_local_transfer_germ_replays() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = RESULT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = RESULT.read_bytes()
    assert first == second
    assert json.loads(first)["validation_passed"] is True
