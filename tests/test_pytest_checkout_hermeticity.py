from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
THEORY = ROOT / "theory"


TRACKED_EXPORTS = (
    THEORY / "derived_active_scalar_orientation_doublet.md",
    THEORY / "derived_scalar_conjugate_doublet.md",
    THEORY / "theorem_discharge_higgs_scalar_boundary_mechanism.md",
)


def test_generator_test_cannot_rewrite_tracked_theory_files():
    before = {path: path.read_bytes() for path in TRACKED_EXPORTS}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_derived_active_scalar_orientation_doublet.py",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    after = {path: path.read_bytes() for path in TRACKED_EXPORTS}
    assert result.returncode == 0, result.stdout + result.stderr
    assert after == before
