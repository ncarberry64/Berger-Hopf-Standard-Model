import math

from bhsm.interface.aether_common_gauge_hs_pushforward_v16_05 import (
    combine_common_responses,
    sm_trace_ledger,
)


MATTER = {
    "proper_duration": 2.0 * math.pi,
    "U1_delta_K_magnetic_seed": 11.0,
    "U1_delta_K_electric_seed": 7.0,
    "HS_delta_Z_per_normalized_pair_seed": 0.25,
    "rows": [{
        "Weyl_U1_constant": 8.0,
        "Weyl_U1_first_frequency": 11.0,
        "HS_U1_constant": 3.0,
        "HS_U1_first_frequency": 7.0,
    }],
}
ADJOINT = {"unit_adjoint_delta_KB": -2.0, "unit_adjoint_delta_KE": -1.0}
DENSE = {"proper_cycle_K_magnetic": 100.0, "proper_cycle_K_electric": 200.0}


def test_fixed_sm_trace_ledger_has_no_free_normalization():
    ledger = sm_trace_ledger()
    assert ledger["three_family_Weyl_trace_T2"] == {"U1": 10.0, "SU2": 6.0, "SU3": 6.0}
    assert ledger["adjoint_C_A"] == {"U1": 0.0, "SU2": 2.0, "SU3": 3.0}
    assert not ledger["new_continuous_coefficient"]


def test_one_combination_generates_gauge_and_hs_residues():
    result = combine_common_responses(MATTER, ADJOINT, DENSE)
    assert set(result["group_residues"]) == {"U1", "SU2", "SU3"}
    assert result["HS_channel_kinetic_matrix"] == {
        "up": 2.25, "down": 2.25, "charged_lepton": 0.75, "neutrino": 0.75,
    }
    assert result["unit_EC_LR_vertex"] == 1.0
    assert not result["physical_HS_direction_selected"]
    assert result["same_geometry_same_regulator_same_direct_sum_operator"]


def test_nonabelian_groups_receive_matter_and_adjoint_blocks():
    result = combine_common_responses(MATTER, ADJOINT, DENSE)["group_residues"]
    assert math.isclose(result["SU2"]["delta_KB_common_heat_operator"], 0.6 * 8.0 + 3.0 - 4.0)
    assert math.isclose(result["SU3"]["delta_KB_common_heat_operator"], 0.6 * 8.0 - 6.0)
    assert result["U1"]["delta_KB_common_heat_operator"] == 11.0
