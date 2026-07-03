from bhsm.interface.berger_hodge_component_map.common import ORTHO, RAW
from bhsm.interface.berger_hodge_component_map.hodge_component_map import audit_hodge_component_map

def test_component_map_is_conditional_and_basis_sensitive():
    payload = audit_hodge_component_map()
    assert payload["status"] == "CONDITIONAL_BERGER_HODGE_COMPONENT_MAP"
    assert payload["orthonormal_formula"] == ORTHO
    assert payload["raw_berger_formula"] == RAW
    assert payload["orthonormal_map"] == ORTHO
    assert payload["raw_berger_map"] == RAW
    assert payload["sign_convention"] == "epsilon_123=+1 in the selected orientation"
    assert ORTHO != RAW
    assert "r_fiber/r_base^2" in RAW
