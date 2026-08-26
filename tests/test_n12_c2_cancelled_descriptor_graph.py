from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_c2_cancelled_descriptor_graph.py"


def test_cancelled_descriptor_is_an_invariant_graph_not_an_independent_tube() -> None:
    spec = importlib.util.spec_from_file_location("descriptor_graph", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.build_payload()
    assert payload["validation_passed"] is True
    assert payload["dimension"]["invariant_descriptor_graph_dimension"] == 98
    assert payload["dimension"]["extra_physical_degree_of_freedom_added"] is False
    assert all(row["descriptor_graph_defect_rate"] == 0.0 for row in payload["witnesses"])
    assert payload["adjudication"]["physical_stop_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False

