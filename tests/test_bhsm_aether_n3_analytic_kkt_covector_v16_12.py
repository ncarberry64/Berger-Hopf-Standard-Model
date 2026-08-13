import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    chain_rule_directional_witness,
    replacement_action_covector,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    pack_reduced,
)


def test_chain_rule_covector_matches_complete_action_direction():
    witness = chain_rule_directional_witness()
    assert witness["relative_residual"] < 2.0e-5


def test_covector_rejects_wrong_base_dimension():
    with np.testing.assert_raises(ValueError):
        replacement_action_covector(np.zeros(376))
