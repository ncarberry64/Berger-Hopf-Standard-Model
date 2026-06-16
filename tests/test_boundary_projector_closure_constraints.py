import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_projector_algebra import (  # noqa: E402
    ProjectorEigenState,
    channel_multiplicity,
    closure_complementarity_passes,
    physical_projector_state_registry,
)


def test_physical_projector_states_obey_closure_complementarity():
    for state in physical_projector_state_registry(include_nu_r=True).values():
        assert closure_complementarity_passes(state)


def test_non_complementary_state_is_reported_false_not_derived():
    assert closure_complementarity_passes(ProjectorEigenState(1, 1, +1, 1)) is False


def test_channel_multiplicity_rule():
    assert channel_multiplicity(0) == 1
    assert channel_multiplicity(1) == 3


def test_closure_constraint_document_contains_candidate_rules():
    text = (ROOT / "theory" / "boundary_projector_closure_constraints.md").read_text()
    assert "P_C + P_ell = I" in text
    assert "C + ell = 1" in text
    assert "d_channel = 1 + 2C" in text
    assert "This is not yet a derivation of SU(3)." in text
