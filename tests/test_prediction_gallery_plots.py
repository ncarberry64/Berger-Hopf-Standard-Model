import json
from pathlib import Path
from bhsm.interface.plotting import generate_gallery_plots
ROOT=Path(__file__).resolve().parents[1]
def test_plot_dry_run_and_committed_svgs_are_claim_safe():
    assert len(generate_gallery_plots(dry_run=True)["plots"])==3
    manifest=json.loads((ROOT/"artifacts/BHSM_prediction_gallery_plot_manifest_v0_2.json").read_text())
    for row in manifest["plots"]:
        path=ROOT/row["path"]; assert path.is_file() and path.stat().st_size<100_000
        text=path.read_text(encoding="utf-8"); assert "not empirical validation" in text
        assert row["speculative_included"] is False
