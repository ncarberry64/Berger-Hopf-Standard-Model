"""The existing monitor must display certificate operands, never demo fallback."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "museum_engines", ROOT / "docs/assets/generate_bhsm_museum_engines.py"
)
engines = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engines)


def test_monitor_values_match_outward_converted_certificate_arrays():
    data = engines.load_residual_certificate()
    with np.load(ROOT / data["source_data"]) as source:
        expected = np.nextafter(source["local_projected_HS_second_residual_norm_upper"], np.inf)
    np.testing.assert_array_equal(data["local_residual_norm_upper"], expected)
    assert np.argmax(expected) == 8
    assert max(expected) == 0.08778167488957692
    assert data["FULL_BHSM_COMPLETE"] is False


def test_monitor_rejects_tampered_or_missing_input(tmp_path):
    path = tmp_path / "input.json"
    with pytest.raises(FileNotFoundError):
        engines.load_residual_certificate(path)
    original = engines.CERTIFICATE_DATA.read_bytes()
    path.write_bytes(original.replace(b"0.00028879232303009324", b"0.99928879232303009324"))
    with pytest.raises(ValueError, match="hash mismatch"):
        engines.load_residual_certificate(path)


def test_monitor_accepts_git_line_ending_conversion(tmp_path):
    path = tmp_path / "input.json"
    original = engines.CERTIFICATE_DATA.read_bytes().replace(b"\r\n", b"\n")
    path.write_bytes(original.replace(b"\n", b"\r\n"))
    assert engines.load_residual_certificate(path) == engines.load_residual_certificate()
