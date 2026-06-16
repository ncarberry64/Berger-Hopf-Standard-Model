from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_closure_selection_status_and_conclusion_language():
    text = (ROOT / "theory" / "closure_spectrum_selection_rule_audit.md").read_text()
    assert (
        "This audit does not fully derive the Standard Model. It tests candidate selection "
        "principles that support the minimal closure spectrum {1,2,3} as the low-energy "
        "fundamental boundary spectrum. The result remains candidate-only unless the "
        "selection conditions are derived directly from the Berger-Hopf boundary action "
        "and the full topographic Hessian problem."
    ) in text
    assert (
        "The audit supports {1,2,3} as the minimal diagnostic closure spectrum compatible "
        "with the current BHSM charge/anomaly bridge, boundary-orientation structure, and "
        "fourth-order branch-count interpretation. It does not uniquely prove that no "
        "higher fundamental closures exist in the full Berger-Hopf theory."
    ) in text


def test_closure_selection_docs_do_not_overclaim():
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "closure spectrum has been uniquely derived",
        "we prove the closure spectrum",
        "full Hessian proof is complete",
        "higher prime closures are impossible",
    ]
    docs = [
        ROOT / "theory" / "closure_spectrum_selection_rule_audit.md",
        ROOT / "theory" / "closure_spectrum_candidate_selection_rules.md",
        ROOT / "theory" / "closure_spectrum_reducibility_screen.md",
        ROOT / "theory" / "closure_spectrum_topographic_branch_screen.md",
        ROOT / "theory" / "closure_spectrum_anomaly_minimality_screen.md",
    ]
    for path in docs:
        text = path.read_text()
        for phrase in forbidden:
            assert phrase not in text
