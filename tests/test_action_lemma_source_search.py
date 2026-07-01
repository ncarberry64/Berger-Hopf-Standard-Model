from bhsm.interface.action_lemmas import search_action_lemma_sources


def test_source_search_locates_artifacts_without_inventing_proofs():
    report = search_action_lemma_sources()
    assert all(row["all_present"] for row in report["rows"].values())
    assert report["action_quotient_evidence_found"] is False
    assert report["maximal_bridge_selection_evidence_found"] is False
    assert report["ckm_equivalent_channel_evidence_found"] is False

