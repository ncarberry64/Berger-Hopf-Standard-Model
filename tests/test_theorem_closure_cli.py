import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, "-m", "bhsm.interface", *args], cwd=ROOT, text=True, capture_output=True, check=True, timeout=60).stdout


def test_closure_report_and_individual_attempts_work_offline():
    report = json.loads(run("theorem-closure-report", "--format", "json"))
    assert report["internet_required"] is False
    assert report["promotions_allowed"] == []
    for key in ("X_ch", "neutrino_basis_scale", "cp_o_int"):
        attempt = json.loads(run("close-theorem", key, "--format", "json"))
        gates = json.loads(run("theorem-proof-gates", key))
        assert attempt["promotion_allowed"] is False
        assert len(gates["proof_gates"]) == 17
    assert "narrative plausibility is not enough" in run("theorem-closure-report", "--format", "markdown")
