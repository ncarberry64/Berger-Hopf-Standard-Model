import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ("ckm-boundary-measure-search", "ckm-boundary-measure-source", "ckm-coefficient-normalization", "ckm-action-measure-coefficient-pair", "normalized-ckm-action-candidate", "ckm-projector-sandwich-requirement", "ckm-paired-normalization-rule", "ckm-transport-space-blocker", "ckm-boundary-measure-normalization-report")

def test_v28_cli_is_offline_and_json_parseable():
    env = os.environ.copy(); env["PYTHONPATH"] = str(ROOT / "src")
    for command in COMMANDS:
        r = subprocess.run([sys.executable, "-m", "bhsm.interface", command, "--format", "json"], cwd=ROOT, env=env, capture_output=True, text=True, check=True)
        assert json.loads(r.stdout)

def test_v28_markdown_report():
    env = os.environ.copy(); env["PYTHONPATH"] = str(ROOT / "src")
    r = subprocess.run([sys.executable, "-m", "bhsm.interface", "ckm-boundary-measure-normalization-report", "--format", "markdown"], cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    assert "# CKM Boundary Measure Normalization Audit" in r.stdout
