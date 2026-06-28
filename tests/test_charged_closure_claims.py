from __future__ import annotations

import hashlib
from pathlib import Path

from bhsm.interface.charged_closure import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "artifacts/CKM_no_fit_operator_output_v1.json": "9c354e8812682c75187c00becb90ff44b5dcc74aef10992103df28b34321d757",
}


def test_charged_docs_contain_required_exact_statements() -> None:
    report = (ROOT / "docs/charged_closure_report.md").read_text(encoding="utf-8")
    for statement in REQUIRED_STATEMENTS:
        assert statement in report


def test_charged_docs_do_not_promote_open_sources() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in ROOT.joinpath("docs").glob("*charged*audit.md")
    )
    for forbidden in (
        "charged stiffness is action-derived",
        "eta_l is fully derived",
        "ckm 1/16 exponent is action-derived",
        "bhsm is empirically validated",
    ):
        assert forbidden not in combined


def test_frozen_and_ckm_artifacts_are_unchanged() -> None:
    for path, expected in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
