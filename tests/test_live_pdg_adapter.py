import json
from pathlib import Path
from bhsm.interface.live_pdg import LivePDGProvider
ROOT=Path(__file__).resolve().parents[1]
def test_offline_fallback_is_reference_only(tmp_path):
    provider=LivePDGProvider(); provider.cache.directory=tmp_path
    w=provider.fetch_particle_reference("W_boson",offline_ok=True)
    nu=provider.fetch_particle_reference("electron_neutrino",offline_ok=True)
    assert w.reference_only and not w.derivation_input
    assert nu.reference.reference_kind=="upper_limit" and nu.fallback_used
def test_live_pdg_policy_artifacts():
    policy=json.loads((ROOT/"artifacts/BHSM_live_pdg_fetch_policy_v0_2.json").read_text())
    assert policy["live_pdg_optional"] is True
    assert policy["internet_required_for_tests"] is False
    assert policy["pdg_package_required_for_tests"] is False
    assert "never BHSM derivation inputs" in policy["reference_vs_derivation_policy"]
