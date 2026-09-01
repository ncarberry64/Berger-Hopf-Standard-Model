"""Regenerate the exploratory CKM mixing dressing candidate audit."""

from pathlib import Path

from ckm_mixing_dressing_audit import (
    export_ckm_mixing_dressing_audit_json,
    export_ckm_mixing_dressing_audit_markdown,
)


def main() -> None:
    root = Path(__file__).resolve().parent
    export_ckm_mixing_dressing_audit_markdown(
        root / "ckm_mixing_dressing_candidate_audit.md"
    )
    export_ckm_mixing_dressing_audit_json(
        root / "ckm_mixing_dressing_candidate_audit.json"
    )


if __name__ == "__main__":
    main()
