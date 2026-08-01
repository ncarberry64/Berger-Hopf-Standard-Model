from __future__ import annotations

import hashlib
import json

from bhsm.interface.envelopment import relational_axioms as axioms


def test_exact_author_json_round_trips_without_semantic_mutation():
    encoded = axioms.doctrine_bytes()
    assert json.loads(encoded) == axioms.AUTHOR_DOCTRINE
    assert hashlib.sha256(encoded).hexdigest() == axioms.doctrine_sha256()
    assert axioms.AUTHOR_DOCTRINE["foundational_axiom"] == (
        "The whole determines the permitted local differentials, and the local differentials continually reshape the whole."
    )


def test_status_vocabulary_is_exact_and_typed():
    values = {status.value for status in axioms.DoctrineStatus}
    assert values == {
        "AUTHOR_AXIOM", "AUTHOR_ONTOLOGY", "HARD_ARCHITECTURAL_CONSTRAINT",
        "DERIVED", "DERIVED_CONDITIONAL", "STRUCTURAL_POSTULATE", "CANDIDATE",
        "PROXY_ONLY", "INVALIDATED", "OPEN", "BLOCKED_EXACT_OBJECT_PROVED",
    }


def test_every_doctrine_record_has_required_fields_and_no_axiom_is_derived():
    ledger = axioms.constraint_ledger()
    assert ledger["validation_passed"] is True
    assert all(row["current_status"] != "DERIVED" for row in ledger["doctrine_records"])
    assert {row["qualification_status"] for row in ledger["doctrine_records"]} == {
        "HARD_ARCHITECTURAL_CONSTRAINT", "OPEN_ACTION_DERIVATION", "OPEN_PHYSICAL_EQUIVALENCE"
    }
    assert len(ledger["hard_architectural_invariants"]) == 10
    assert all(row["status"] == "HARD_ARCHITECTURAL_CONSTRAINT" for row in ledger["hard_architectural_invariants"])


def test_serialization_and_hash_are_stable():
    assert axioms.doctrine_bytes() == axioms.doctrine_bytes()
    assert axioms.doctrine_sha256() == axioms.doctrine_sha256()
    assert len(axioms.doctrine_sha256()) == 64
    assert axioms.doctrine_sha256() == "f981a6501526a3ff324cbf5cb4f1e26b1f7d3ecd0c7b2759c200f6aa1ee184b0"
