import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_n3_post_recovery_multisecant_proposal_v20_77 import v20_77_selected_raw_vector
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


def test_recovered_continuation_artifacts_and_latest_exact_frontier() -> None:
    for version in range(70, 76):
        payload = json.loads(Path(
            f"artifacts/BHSM_N3_STRUCTURED_PROPOSAL_CONTINUATION_V20_{version}.json"
        ).read_text(encoding="utf-8"))
        assert payload["validation_passed"]
        assert payload["structured_proposal_continuation"]["promotion"]["promoted"]
    ownership = json.loads(Path(
        "artifacts/BHSM_N3_POST_RECOVERY_OWNERSHIP_AUDIT_V20_76.json"
    ).read_text(encoding="utf-8"))
    assert ownership["validation_passed"]
    assert ownership["post_recovery_ownership_audit"]["outcome"] == "RENEWED_PROPOSAL_EXHAUSTION_NO_PHYSICAL_OWNER"
    multisecant = json.loads(Path(
        "artifacts/BHSM_N3_POST_RECOVERY_MULTI_SECANT_PROPOSAL_V20_77.json"
    ).read_text(encoding="utf-8"))
    assert multisecant["validation_passed"]
    assert multisecant["post_recovery_multisecant_proposal"]["promotion"]["promoted"]
    norm = np.linalg.norm(_square_physical_residual(v20_77_selected_raw_vector() * kkt_variable_scales()))
    assert abs(norm - 0.758671922543989) < 5.0e-12
