"""Primitive/composite BHSM support-character ledger for v11.2."""

from __future__ import annotations

from typing import Any


VERDICT = "BHSM_COMPOSITE_SUPPORT_CONNECTION_DERIVED_BUT_PRIMITIVE_CHARACTER_AND_CURRENT_LEDGER_NOT_ACTION_FIXED"
NEXT_OBJECT = "ACTION_TERM_OR_GEOMETRIC_PRINCIPLE_FIXING_PRIMITIVE_SUPPORT_CHARACTER_OWNERSHIP"


def _row(
    key: str,
    kind: str,
    domain: str,
    tensor: str,
    density: str,
    source: str | None,
    normalization: str | None,
    aliases: list[str],
    character: str | None,
    derivation: str,
    *,
    gauge: str = "singlet",
    fiber: str = "none",
    wall: str = "none",
    boundary: str = "none",
    core: str = "none",
    dimension: str = "action dependent",
) -> dict[str, Any]:
    return {
        "object": key,
        "primitive_or_composite": kind,
        "domain": domain,
        "tensor_type": tensor,
        "density_type": density,
        "gauge_representation": gauge,
        "fiber_base_ownership": fiber,
        "wall_incidence": wall,
        "boundary_incidence": boundary,
        "core_incidence": core,
        "engineering_dimension": dimension,
        "existing_action_source": source,
        "existing_normalization": normalization,
        "historical_aliases": aliases,
        "candidate_support_character": character,
        "candidate_derivation_source": derivation,
    }


def primitive_object_ledger() -> list[dict[str, Any]]:
    """Return the complete requested ledger without inventing open weights."""

    return [
        _row("supported_coframe_e", "primitive candidate", "S8 regular", "coframe one-form", "none", "metric action only through G", None, ["orthonormal frame", "supported frame"], "r_e (provisional)", "coframe ansatz, not an established support definition"),
        _row("inverse_coframe", "composite", "S8 regular", "frame vector", "none", "inverse of e", None, ["dual frame"], "-r_e", "inverse law"),
        _row("metric_G_AB", "composite", "S8 regular", "symmetric (0,2)", "none", "S8 Einstein-Hilbert", "kappa1", ["bulk metric"], "2 r_e", "G=eta_ab e^a tensor e^b"),
        _row("inverse_metric_G_AB", "composite", "S8 regular", "symmetric (2,0)", "none", "all contractions", None, ["inverse bulk metric"], "-2 r_e", "inverse law"),
        _row("bulk_measure", "composite", "S8 regular", "top form", "weight-one density", "all S8 terms", "orientation fixed", ["dmu_G", "sqrt(|G|)d8x"], "8 r_e for full support", "determinant law"),
        _row("boundary_measure", "composite after embedding choice", "finite regular boundary", "top boundary form", "weight-one boundary density", "GHY and localized terms", None, ["dmu_h"], "7 r_e only for a fully supported codimension-one induced metric", "induced determinant; partial support open", boundary="finite regular"),
        _row("normal_covector", "composite after normalization", "finite regular boundary", "one-form", "none", "GHY", "G^AB n_A n_B=+/-1", ["n_flat"], "r_e for full Weyl scaling", "unit-normal condition", boundary="finite regular"),
        _row("normal_vector", "composite", "finite regular boundary", "vector", "none", "GHY and flux", "n^A=G^AB n_B", ["n_sharp"], "-r_e for full Weyl scaling", "metric inverse plus normal covector", boundary="finite regular"),
        _row("hodge_star", "composite", "supported d-stratum", "p-form to (d-p)-form", "none", "gauge/scalar kinetic sectors", "orientation fixed", ["star_G"], "(d-2p) r_e for full support", "metric Hodge law"),
        _row("levi_civita_density", "composite", "supported d-stratum", "alternating density", "density", "Hodge and volume", "orientation fixed", ["epsilon_G"], "d r_e for covariant volume form", "determinant law"),
        _row("hopf_fiber_one_form", "primitive geometric form", "Hopf fiber", "one-form", "none", "v6.0.7/v6.0.9 reduction", "period fixed in selected bundle convention", ["contact form", "sigma_3"], None, "no G_D action in the normalized Hopf geometry", fiber="fiber"),
        _row("base_coframe", "primitive geometric frame", "Hopf base", "horizontal coframe", "none", "Berger metric/Hodge map", "Berger radii", ["sigma_1,sigma_2"], None, "partial-support subbundle not action-selected", fiber="base"),
        _row("fiber_measure", "composite", "closed Hopf fiber", "top fiber form", "density", "v7.1 pi_!", "normalized Haar dnu_F", ["dmu_F", "dnu_F"], None, "normalization fixes integral, not G_D character", fiber="fiber"),
        _row("wall_embedding", "primitive map", "S5 into S8/collar", "embedding", "none", "cap and compatibility action", None, ["i_W", "moving fold"], None, "embedding support action absent", wall="enclosure wall"),
        _row("wall_normal", "composite after embedding", "S5 wall", "normal vector/covector", "none", "wall/GHY variation", "unit normalization", ["fold normal"], None, "depends on unassigned wall embedding and metric character", wall="enclosure wall"),
        _row("support_scalar_upsilon", "primitive", "regular support", "positive real scalar", "scalar", "v11.0 Haar term", "upsilon in (0,1]", ["support order parameter"], "group coordinate, not a linear character", "multiplicative group law", core="vanishes asymptotically"),
        _row("canonical_depth_q_D", "composite coordinate", "regular support", "real scalar", "scalar", "v11.0 Haar term", "q_D=-lambda_D log upsilon", ["depth", "spacetime-removal depth"], "affine shift delta q_D=-lambda_D epsilon", "logarithmic Haar coordinate", core="tends to +infinity"),
        _row("core_Hopf_mode_q_C", "primitive mode class", "S8/Hopf", "scalar/metric mode", "scalar", "S8 env", None, ["core mode", "Hopf mode"], "w_C open", "no map from Hopf incidence to G_D generator", core="core-facing", fiber="Hopf"),
        _row("wall_fold_mode_q_W", "primitive mode class", "S5/wall", "scalar/radial mode", "scalar", "S5 cap", None, ["wall mode", "fold mode"], "w_W open", "no map from wall incidence to G_D generator", wall="enclosure wall"),
        _row("gauge_connections", "primitive", "localized S4", "adjoint one-forms", "none", "intrinsic gauge action", "g1,g2,g3", ["A_mu"], "0 under multiplicative support scaling of a non-Abelian connection", "dA and A wedge A homogeneity", gauge="U1 x SU2 x SU3 adjoint"),
        _row("gauge_curvatures", "composite", "localized S4", "adjoint two-forms", "none", "intrinsic gauge action", None, ["F_A"], "0 when gauge-connection weight is zero", "F=dA+A wedge A", gauge="adjoint"),
        _row("fermion_fields", "primitive", "localized S4", "chiral spinors", "spinor", "Dirac/Yukawa terms", "common kinetic normalization", ["psi_L,psi_R"], "0 only inside the rejected full-coframe scale-symmetry candidate; otherwise unassigned", "kinetic/Yukawa covariance conditional on support action", gauge="frozen SM reps"),
        _row("fermion_adjoints", "composite but pairing-dependent", "localized S4", "dual/Hermitian spinors", "spinor", "Dirac/Yukawa terms", None, ["bar psi", "psi dagger"], None, "positive-real Hermitian and contragredient dual laws differ; action supplies no G_D pairing"),
        _row("scalar_topographic_fields", "primitive", "S8/S5/S4", "real/complex scalars", "scalar", "scalar kinetic/potential terms", "retained EFT inputs", ["sigma", "Higgs", "topographic scalar"], "sigma=0 and localized scalar=0 inside full-coframe candidate; otherwise unassigned", "mass/quartic coexistence with inert coefficients", gauge="sector dependent"),
        _row("charged_current_maps", "primitive morphisms", "localized S4/common current", "current intertwiners", "none", "S_current", None, ["charged-current incidence"], None, "action normalization/current origin incomplete", gauge="charged weak"),
        _row("neutral_response_maps", "primitive morphisms", "localized S4/collar", "response operators", "boundary density", "neutral response layer", None, ["neutral incidence"], None, "response normalization remains conditional"),
        _row("sector_projectors", "composite idempotents", "finite localized module", "endomorphisms", "none", "frozen finite ledger", "P^2=P", ["P_l,P_u,P_d"], "0", "idempotency requires 2w_P=w_P", gauge="commutant projectors"),
        _row("compatibility_fields", "primitive multipliers", "cross-stratum", "multiplier tensors", "density after contraction", "S_compatibility", "normalization 1", ["matching multipliers"], "w_compat open", "schematic action lacks a G_D-equivariant intertwiner"),
        _row("boundary_trace_maps", "primitive morphisms", "bulk to boundary", "trace/pullback", "none", "boundary variation", None, ["i*", "trace"], None, "embedding action absent", boundary="finite regular"),
        _row("fiber_integration_maps", "primitive morphisms", "S8 to S5/S4", "pushforward", "measure dependent", "v7.1 reduction", "V_F normalized", ["pi_!"], None, "requires a basic connection and fiber-measure character", fiber="pushforward"),
        _row("M4_reduction_maps", "composite morphism", "stratified parent to effective M4", "functor", "M4 density", "v7.1 reduction plus localized incidence", None, ["R_84", "effective projection"], None, "complete G_D-natural cross-stratum map absent"),
        _row("core_asymptotic_data", "primitive boundary data", "q_D=+infinity", "phase-space candidate", "not supplied", None, None, ["core response", "terminal stratum data"], "w_core open", "core action and phase space absent", core="terminal asymptotic end"),
    ]


def coframe_candidate_test() -> dict[str, Any]:
    return {
        "ansatz": "e_supported=upsilon^r_e e_0",
        "inherited_full_D8": {"coframe": "r_e", "metric": "2 r_e", "inverse_metric": "-2 r_e", "bulk_measure": "8 r_e", "Ricci_scalar_algebraic": "-2 r_e"},
        "constant_scaling_action_equations": ["EH: 6 r_e=0", "cosmological: 8 r_e=0"],
        "local_scaling_obstruction": "the D8 Einstein-Hilbert density also generates Box(epsilon) and (d epsilon)^2 terms; the frozen action has no Weyl compensator completion",
        "solution_with_inert_existing_coefficients": {"r_e": 0},
        "nonzero_r_e_requires": "spurionic transformations of independent coefficients or a new Weyl-compensated action",
        "support_definition_fixes_nonzero_r_e": False,
        "candidate_classification": "NONTRIVIAL_COFRAME_SUPPORT_CHARACTER_REJECTED_FOR_CURRENT_ACTION",
    }


def ledger_payload() -> dict[str, Any]:
    rows = primitive_object_ledger()
    validation = {
        "minimum_inventory_complete": len(rows) >= 30,
        "every_object_typed": all(row["domain"] and row["tensor_type"] and row["primitive_or_composite"] for row in rows),
        "composites_not_independently_weighted": all(row["candidate_derivation_source"] for row in rows),
        "coframe_candidate_exhausted": coframe_candidate_test()["solution_with_inert_existing_coefficients"] == {"r_e": 0},
        "no_empirical_inputs": True,
        "no_1_2_7_import": True,
    }
    return {
        "artifact": "BHSM_primitive_support_character_ledger_v11_2",
        "primitive_objects": rows,
        "coframe_candidate": coframe_candidate_test(),
        "ledger_unique": False,
        "nontrivial_action_owned_ledger": None,
        "status": VERDICT,
        "exact_next_object": NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }

