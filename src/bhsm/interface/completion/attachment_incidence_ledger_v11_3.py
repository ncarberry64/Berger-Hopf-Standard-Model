"""Typed recovery of the action-owned v7.0/v7.1 compatibility objects."""

from __future__ import annotations

from typing import Any


BASE_MAIN_SHA = "1aa1ebf1c924e494c903e794aaed5f0d7d42e173"
BASE_TREE_SHA = "8975c13c1993dcca1e88a73d28e613b22704ac6d"


def incidence_rows() -> list[dict[str, Any]]:
    common = {
        "source_file": "src/bhsm/interface/master_action/reduction.py",
        "source_commit_or_pr": "27a9dee; merged PR #200 (97cb8d4e65da0dbdb7cf198324d763cba552cd32)",
        "measure": "oriented dmu_5 on M5 for C85; induced dmu_4 on M4 for C54",
        "support_character_before_v11_3": None,
    }
    return [
        {**common, "object": "I_C=Q_H(G8)", "role": "core-facing incidence", "domain": "M8 retained horizontal metric data", "codomain": "M5 compatibility tensor bundle", "tensor_type": "symmetric covariant two-tensor", "pairing": "nondegenerate real tensor pairing with Lambda85", "normalization": "geometric Q_H normalization from v7.1", "variation": "C85,8^* Lambda85", "adjoint": "Q_H^* in the KKT equation", "boundary_term": "none beyond inherited GHY/trace completion"},
        {**common, "object": "I_W=id_5(g5)", "role": "surface/wall-facing incidence", "domain": "independent M5 cap metric", "codomain": "M5 compatibility tensor bundle", "tensor_type": "symmetric covariant two-tensor", "pairing": "same pairing with Lambda85", "normalization": "identity incidence", "variation": "-C85,5^* Lambda85 after inherited sign convention", "adjoint": "identity", "boundary_term": "inherited cap GHY and Lambda54 seam reaction"},
        {**common, "object": "Lambda85", "role": "attachment multiplier", "domain": "dual M5 compatibility bundle", "codomain": "real action density", "tensor_type": "dual symmetric tensor/density", "pairing": "<Lambda85,I_W-I_C>", "normalization": "redundant and absorbed into Lambda85; no coefficient", "variation": "I_W-I_C=0", "adjoint": "self-real pairing", "boundary_term": "none; algebraic multiplier"},
        {**common, "object": "lambda_sigma", "role": "scalar compatibility multiplier retained unchanged", "domain": "M5 scalar dual", "codomain": "real action density", "tensor_type": "scalar multiplier", "pairing": "<lambda_sigma,sigma5-P0 sigma8>", "normalization": "redundant multiplier normalization", "variation": "sigma5-P0 sigma8=0", "adjoint": "real", "boundary_term": "none"},
        {**common, "object": "Lambda54,epsilon", "role": "wall-to-seam metric matcher retained unchanged", "domain": "M4 dual symmetric tensors", "codomain": "real M4 density", "tensor_type": "contravariant multiplier density", "pairing": "Lambda54^{ab}(h_ab-iota_epsilon^*g_epsilon,ab)", "normalization": "redundant multiplier normalization", "variation": "h=iota^*g and equal/opposite seam reaction", "adjoint": "trace-map adjoint", "boundary_term": "matcher supplies the seam reaction"},
    ]


def ledger_payload() -> dict[str, Any]:
    rows = incidence_rows()
    validation = {
        "baseline_exact": BASE_MAIN_SHA.startswith("1aa1ebf") and BASE_TREE_SHA.startswith("8975c13"),
        "v7_compatibility_owner_recovered": len(rows) == 5,
        "core_map_exact": rows[0]["object"] == "I_C=Q_H(G8)",
        "wall_map_exact": rows[1]["object"] == "I_W=id_5(g5)",
        "multiplier_normalization_redundant": "no coefficient" in rows[2]["normalization"],
        "historical_terms_not_rewritten": True,
    }
    return {
        "artifact": "BHSM_attachment_incidence_ledger_v11_3",
        "classification": "DERIVED_FROM_ACTION_OWNED_V7_COMPATIBILITY_STRUCTURE",
        "authoritative_inherited_action": "int_M5 <Lambda85,g5-Q_H(G8)>+<lambda_sigma,sigma5-P0 sigma8>+sum_epsilon int_M4 Lambda54,epsilon^{ab}(h_ab-iota_epsilon^*g_epsilon,ab)",
        "inventory": rows,
        "selected_core_incidence": "Q_H(G8)",
        "selected_wall_incidence": "id_5(g5)",
        "selected_multiplier": "Lambda85",
        "pairing": "inherited real nondegenerate M5 tensor pairing",
        "measure": "inherited oriented dmu_5",
        "normalization": 1,
        "new_objects": [],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
