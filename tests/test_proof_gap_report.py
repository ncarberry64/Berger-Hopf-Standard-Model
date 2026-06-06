import json
from pathlib import Path

from boundary_derivation import DerivationStatus, default_boundaries
from claims import ClaimStatus, claims_by_status, build_claims_ledger


ROOT = Path(__file__).parents[1]


def test_all_four_proof_gaps_present_in_markdown_and_json():
    markdown = ROOT.joinpath("theory", "proof_gap_report.md").read_text()
    data = json.loads(ROOT.joinpath("theory", "proof_gap_report.json").read_text())
    gap_ids = {item["gap_id"] for item in data}

    assert "Full Twisted Dirac / H_T Spectrum" in markdown
    assert "Boundary Operators Omega_f" in markdown
    assert "RG Matching" in markdown
    assert "Scalar/Topographic Decoupling" in markdown
    assert gap_ids == {"ht_full_spectrum", "boundary_operators", "rg_matching", "scalar_decoupling"}


def test_no_proof_gap_is_marked_complete():
    data = json.loads(ROOT.joinpath("theory", "proof_gap_report.json").read_text())

    assert all("COMPLETE" not in item["status"] for item in data)
    assert all("Do not claim" in item["claim_forbidden"] for item in data)


def test_five_forbidden_claims_remain_present():
    forbidden = claims_by_status(ClaimStatus.FORBIDDEN)

    assert len(forbidden) == 5


def test_ht_claim_remains_proxy_audit():
    claim = next(claim for claim in build_claims_ledger() if claim.id == "ht_proxy_spectral_gap")

    assert claim.status == ClaimStatus.PROXY_AUDIT


def test_boundary_operators_are_not_action_derived():
    boundaries = default_boundaries()

    assert all(boundary.derivation_status != DerivationStatus.ACTION_DERIVED for boundary in boundaries.values())


def test_rg_matching_not_marked_complete():
    data = json.loads(ROOT.joinpath("theory", "proof_gap_report.json").read_text())
    rg = next(item for item in data if item["gap_id"] == "rg_matching")

    assert rg["status"] == "ONE_LOOP_SCAFFOLD"
    assert "complete" in rg["claim_forbidden"].lower()


def test_scalar_decoupling_remains_open():
    claim = next(claim for claim in build_claims_ledger() if claim.id == "scalar_decoupling")

    assert claim.status == ClaimStatus.OPEN
