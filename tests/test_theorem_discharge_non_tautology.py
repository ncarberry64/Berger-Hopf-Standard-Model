from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_discharge_docs_do_not_import_sm_charge_labels_into_closure_derivation():
    docs = [
        ROOT / "theory" / "derived_hopf_phase_closure.md",
        ROOT / "theory" / "derived_orientation_involution.md",
        ROOT / "theory" / "derived_minimal_cyclic_channel.md",
        ROOT / "theory" / "derived_closure_spectrum_123.md",
    ]
    forbidden_imports = [
        "hypercharge",
        "quark",
        "lepton",
        "CKM",
        "Yukawa",
        "anomaly sums force",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden_imports:
            assert phrase not in text


def test_main_discharge_doc_states_non_tautology_basis():
    text = (ROOT / "theory" / "theorem_discharge_phase_orientation_cyclic.md").read_text()
    assert "does not use SM charge labels" in text
    assert "Hopf phase single-valuedness" in text
    assert "involution order" in text
    assert "cyclic-order hierarchy" in text

