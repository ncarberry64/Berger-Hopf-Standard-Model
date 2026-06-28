import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args): return subprocess.run([sys.executable,"-m","bhsm.interface",*args],cwd=ROOT,text=True,capture_output=True,check=True,timeout=30).stdout
def test_gallery_and_status_commands_offline():
    assert len(json.loads(run("gallery","--format","json"))["entries"])==10
    assert "BHSM Prediction Gallery" in run("gallery","--format","markdown")
    assert json.loads(run("pdg-status"))["internet_required"] is False
    assert json.loads(run("speculative","list"))["enabled_by_default_count"]==0
    assert len(json.loads(run("theorem-blockers"))["blockers"])==3
def test_new_cli_help_and_plot_dry_run():
    assert len(json.loads(run("plot-gallery","--dry-run"))["plots"])==3
    for cmd in ("gallery","plot-gallery","notebook-pack","pdg-fetch","speculative","theorem-attempt"):
        assert "usage:" in run(cmd,"--help")
