import json
from pathlib import Path


def test_parallel_jacobian_equivalence_artifact_validates():
    payload = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_parallel_physical_jacobian_v17_32.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["validation_passed"]
