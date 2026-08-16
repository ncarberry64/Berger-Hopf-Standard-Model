import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_n3_controlled_structured_shake_recovery_v20_69 import v20_69_selected_raw_vector
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


def test_shake_is_removed_and_original_f376_decides() -> None:
    payload = json.loads(Path("artifacts/BHSM_N3_CONTROLLED_STRUCTURED_SHAKE_RECOVERY_V20_69.json").read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["controlled_structured_shake_recovery"]
    assert result["prospective_exact_search"]["candidate_origin_is_unshaken_v20_66"]
    assert result["prospective_exact_search"]["exact_original_f376_authoritative"]
    assert not result["physical_equations_changed"]
    assert result["promotion"]["promoted"]
    assert abs(np.linalg.norm(_square_physical_residual(v20_69_selected_raw_vector() * kkt_variable_scales())) - 0.764419585850328) < 5.0e-12
