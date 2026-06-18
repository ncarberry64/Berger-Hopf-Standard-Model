import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_projector_algebra import physical_projector_charge_table  # noqa: E402
from candidate_finite_boundary_algebra import (  # noqa: E402
    anomaly_closure_bridge_confirmed,
    physical_boundary_algebra_charge_table,
)


def test_finite_algebra_registry_matches_projector_charge_bridge():
    finite = physical_boundary_algebra_charge_table(include_nu_r=True)
    projector = physical_projector_charge_table(include_nu_r=True)

    for field, projector_row in projector.items():
        assert finite[field]["T3"] == projector_row["T3"]
        assert finite[field]["Y"] == projector_row["Y"]
        assert finite[field]["Q"] == projector_row["Q"]


def test_anomaly_closure_bridge_remains_confirmed_diagnostic():
    assert anomaly_closure_bridge_confirmed() is True
