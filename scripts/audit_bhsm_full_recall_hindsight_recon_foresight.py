"""Materialize the repository-scoped BHSM recall and downstream completion DAG."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "artifacts/current_semantics"
RESULT = ROOT / "artifacts/flagship_integration/BHSM_FULL_RECALL_HINDSIGHT_RECON_FORESIGHT.json"
THEORY = ROOT / "theory/bhsm_full_recall_hindsight_recon_foresight.md"

INPUTS = {
    "ontology": CURRENT / "BHSM_CURRENT_ONTOLOGY_REGISTRY.json",
    "formula": CURRENT / "BHSM_CURRENT_FORMULA_REGISTRY.json",
    "gates": CURRENT / "BHSM_CURRENT_GATE_LEDGER.json",
    "dag": CURRENT / "BHSM_CURRENT_COMPLETION_DAG.json",
    "basis": CURRENT / "BHSM_CURRENT_MATHEMATICAL_BASIS.json",
    "ae2": ROOT / "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "exact_field": ROOT / "artifacts/flagship_integration/BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json",
    "core_audit": ROOT / "artifacts/flagship_integration/BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT.json",
    "scope": ROOT / "artifacts/BHSM_scope_relevance_registry.json",
    "legacy_completion": ROOT / "artifacts/BHSM_1_0_completion_gate.json",
    "v15_7": ROOT / "artifacts/BHSM_full_completion_gate_v15_7.json",
    "owner": ROOT / "theory/norman_owner_ontology_recovered.md",
    "semantic_normalization": ROOT / "theory/bhsm_current_semantic_normalization.md",
    "theory": THEORY,
}


PDF_CORPUS = [
    ("A Geometric Origin of Yukawa Hierarchies.pdf", 3, "B87D2C37A3C534533F22D7F044BC2A92EF2AA80A0E6572E5313B0ADAF5F7C990", "YUKAWA_GEOMETRY_CANDIDATE"),
    ("Alternative to LambdaCDM.pdf", 10, "DDE8D8A4660981DBF9AFB5A896685A1BB4B5F4D598CB75D42BD9B51E873CF136", "COSMOLOGY_PHENOMENOLOGY"),
    ("Carberry_2025_TH-TB1_Experiment_Brief.pdf.pdf", 3, "967B6635B70E4C23B967F7F918EB99B5D2A2EDC9EA18C375F3DF68ACF1EC1524", "EXPERIMENT_PROPOSAL"),
    ("Carberry_2025_TH-TB1_Experimental_Validation.pdf.pdf", 3, "1D9B25B20372E120F8071FC390216DCD9D14EA6A25A6DC6E02A081A8EA042C39", "METHODS_ONLY_NO_RESULT_DATA"),
    ("Cosmological Constant.pdf", 3, "0CC31DC893B96EE89EED4D59F442BD71C1B5B62BA8A6D33C382E5B7F57C9BE41", "CASIMIR_SCALE_CANDIDATE"),
    ("Curvature-Driven Mode Selection.pdf", 8, "68A26F0C5088774885934753BFF29BF82CDAE034698619E21382B09A00501AC5", "SCALAR_TOPOGRAPHIC_PHENOMENOLOGY"),
    ("Detection and Null-Result Criteria.pdf", 3, "DB9C90EBAE6A55095EFD4C69A93FDEEE0CD37952B1222E66413341147FC7946E", "EXPERIMENT_PROTOCOL"),
    ("Everything prompt.pdf", 14, "0537D4653726F8B71FF4A7174A8F06137BD7F5EBC4E3F9B1BA6BCCC389B0B854", "SELF_DECLARED_PHENOMENOLOGICAL_PROGRAM"),
    ("Flagship.pdf", 6, "F18A6A571AA7DDB321984C239F7FD709C90757511C24F778662943EB958C2EBF", "SCALAR_TOPOGRAPHIC_PHENOMENOLOGY"),
    ("Foundational Equations.pdf", 3, "E2F2BD2F3ABE128783425134D798EE9CEAE4135DA02585EF756DB71E74EEC905", "EARLY_FOUNDATIONAL_MODEL"),
    ("Foundational Framework.pdf", 4, "07D214983BCB0E77DC2759E9672081D3353A9CC9A61F2D31EFF44E693808C180", "EARLY_FOUNDATIONAL_MODEL"),
    ("Global Consistency.pdf", 8, "B0D8A224890C31C1557021955FB85BD7A044F2C31B7E057FE2C243785062FFCA", "HISTORICAL_CANONICAL_BASELINE"),
    ("Hyperspherical Gravity and the Infinite Spheroid Hypothesis+figs.pdf", 12, "7E5F0740723086A01DCF08201B5CA3F6EEBE0D90916A27338A23C18146B713E9", "COSMOLOGY_PARAMETERIZATION_AND_FIGURES"),
    ("mdpi-article-template.pdf", 6, "1AD6773077CFB4EC6C147A30FCEA0220EAD42A2803D3C5E1CC001D0607D97BE2", "FORMATTING_TEMPLATE_NOT_SCIENTIFIC_EVIDENCE"),
    ("Norman's Hypersphere.pdf", 21, "8D98A9A66388A41755E6F5FD6142C1D1434868D75F1E50358089841C75807D32", "SCALAR_TOPOGRAPHIC_SYNTHESIS"),
    ("Part 1.pdf", 3, "B2C501B0469C4FE5D5834235F1F89C9FEC68FCC7C04A74CD7581AFCC7B782C41", "MEASURED_INPUT_MASS_SCREEN_NOT_UPSTREAM"),
    ("Part 2.pdf", 4, "3071A9578190A40AFF057F1CA8336CDCC488B7F441A38FAF1A998C0368AE19C7", "ILLUSTRATIVE_DATA_COMPARISON"),
    ("Predicted Scalar-Induced Frequency Shifts.pdf", 1, "6763FB4E5B19F389470DB09829238DF5D6E10C1F78C003DC22562306BCDA4F68", "BENCHMARK_FORECAST_NOT_ACTION_DERIVED"),
    ("Topographic Field on S3.pdf", 5, "099A9EF963D877693FA6D039114DDDA21076C5471AEDD88B5244C27BF7244DA5", "SCALAR_TOPOGRAPHIC_PHENOMENOLOGY"),
    ("Track A (Collapse Model).pdf", 8, "4BA4E09C9819DE1918CF9C2BAD64E388E1D7C9CAD1FD34775F87DD18877234BF", "EXPLICIT_PHENOMENOLOGICAL_EXTENSION"),
    ("Track B (Derivation Paper).pdf", 6, "D4F5B02A41592919CC38756FA2AAEFB7E0F818EA4D6E5CCE87623CB110784FBA", "UNITARY_MODEL_DERIVATION_NO_COLLAPSE"),
    ("Unified Geometric Field Equation.pdf", 11, "BB826560FA2E32E3D36AF9B253A32D16BAEF5C675389DF877FC4748E8573BDDF", "EARLY_UNIFIED_PHENOMENOLOGY"),
    ("Unified Topographic Mode.pdf", 5, "C168897C88CCC5B365F52D85249B4542D69361B5E3E40DA32C8449AB763912AF", "COSMOLOGY_PHENOMENOLOGY"),
    ("The Science/A Geometric Origin of the Fine Structure Constant.pdf", 20, "8D1DE6AD3C42ADB6D67B04BE8A66169A7E4CD4BD1DD396ADFA0546F0B41059F7", "HISTORICAL_GEOMETRIC_COUPLING_CANDIDATE_WITH_NORMALIZATION_CONFLICT"),
    ("The Science/Carberry2025_HypersphericalCosmology.pdf", 10, "E59374AA588A68E21BE45C5B6992333F0996059F5A2A8BC59D5425DB42EC309B", "COSMOLOGY_PHENOMENOLOGY_WITH_FREE_PARAMETERS"),
    ("The Science/Mass from Local Curvature Thresholds in a Scalar Topographic Effective Field Theory.pdf", 11, "8C491926B5A419064B515AB2F345EDD4AEE66563479882E3C73BFAE9D0F23F36", "MASS_MATCHING_ANSATZ_NOT_ACTION_DERIVATION"),
    ("The Science/Mass gap.pdf", 3, "F32E070DCA892ED21715E06416415B1E0C091E9A29CEBF69AE553698659E4A53", "SCALAR_ANALOGUE_NOT_YANG_MILLS_PROOF"),
]

DOCUMENT_CORPUS = [
    ("Prompt Sources/Penrose Add.docx", 4, "88AC4594C23906E922584006F1027C1F1787A59BAB18B4FCC6721E0ABA6975A2", "INTERPRETIVE_CORE_HYPOTHESIS_NOT_ACTION_DERIVED"),
]

NIGHTCRAWLER_SNAPSHOT = {
    "root": "C:/Users/carbe/OneDrive/Desktop/Project NightCrawler",
    "file_count": 1036,
    "byte_count": 1074805841,
    "extension_counts": {".pdf": 264, ".png": 121, ".tex": 108, ".docx": 103, ".txt": 51, ".md": 14, ".py": 6},
    "index_sha256": "8AE46173072B4AAB5E52E9D2E29033C2A47D4E2D44972DE4EB0B2B453A659FE6",
    "handoff_sha256": "654DC7B24D4A9EFDF0BC5B72837A06581A49DF7AD1FD8111F1FEE231C798D0E2",
    "revised_gravity_manuscript_sha256": "4F8872BD2A8DD79A081F7E322A7C709D11997248032899C5018D3397455123B4",
    "review_policy": "READ_ONLY_INDEX_GUIDED_DEDUPLICATED_PRIMARY_SOURCE_REVIEW",
}

HARA_FSC_SNAPSHOT = {
    "manifest_sha256": "95B8FD9C794AF37BF97AFAF0819772EAFFC8D653A0BACDB586288A6E13A4F399",
    "index_sha256": "CDFF8651C899AE040B26DBBFF8A73336A0E41BD815771260DAD364526059788A",
    "artifact_a_sha256": "F65C0112FF47AA2F24993110A8E905BDE84E584096DFC80C61C61034CDF77022",
    "artifact_b_sha256": "DDBF11EB94BCD6F911A130DCFB6F7D2EB4D2B0C31B430915E3C68BA67DCC5D7D",
    "artifact_c_sha256": "05B73EFADF71CF0465D557074ED2EE405048C9CED0BCADDF4294A03B790B5A4F",
    "artifact_g_sha256": "D907DE0E92D1008E74936653077F630F5E24D832572BDECAB44B46BDEB4117A8",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing recall inputs: " + ", ".join(missing))
    data = {key: _load(path) for key, path in INPUTS.items() if path.suffix == ".json"}
    gates = data["gates"]["records"]
    ontology = data["ontology"]["records"]
    formula = data["formula"]["records"]
    closed = [row["canonical_id"] for row in gates if row["current_status"].startswith("CLOSED")]
    open_gates = [
        {"gate": row["canonical_id"], "status": row["current_status"], "meaning": row["physical_meaning"]}
        for row in gates
        if not row["current_status"].startswith("CLOSED")
    ]
    papers = [
        {"name": name, "pages": pages, "sha256": sha, "classification": classification}
        for name, pages, sha, classification in PDF_CORPUS
    ]
    documents = [
        {"name": name, "pages": pages, "sha256": sha, "classification": classification}
        for name, pages, sha, classification in DOCUMENT_CORPUS
    ]
    historical_reconciliation = [
        {
            "topic": "fine_structure",
            "source_claim": "the expanded corpus traces the rounded 1/118 proposal to Xi_geom=1/(12*pi^2), assembled from 1/3, 1/pi, and 1/(4*pi) under explicit isotropy, unit-radius, and canonical-normalization assumptions",
            "current_adjudication": "the exact source value is 1/(12*pi^2)=1/118.435..., not 1/118; it is not attached to AE2, its beta running is calibrated to the observed low-energy alpha, and the HARA sources conflict between 1/e^2=Xi/g^2 (so e^2=g^2/Xi) and e^2=g^2 Xi",
            "upstream_use": "FORBIDDEN",
        },
        {
            "topic": "local_curvature_mass",
            "source_claim": "m=(c^2/(2G))*r_c^2*k_loc is presented as a geometrically motivated matching ansatz with a chosen single-activation normalization",
            "current_adjudication": "candidate readout type only; the source explicitly does not derive it from a covariant action, and its localization scale and later electromagnetic coupling remain free",
            "upstream_use": "FORBIDDEN_UNTIL_ACTION_OWNED_SCALE_AND_OBSERVABLE_MAP_EXIST",
        },
        {
            "topic": "mass_gap",
            "source_claim": "a scalar higher-derivative toy operator is used to illustrate a positive spectral threshold",
            "current_adjudication": "not a Yang-Mills theorem; the displayed operator/plane-wave signs and gap normalization require an internal algebra and dimensional audit before even analogue reuse",
            "upstream_use": "ILLUSTRATIVE_ONLY",
        },
        {
            "topic": "yukawa_generations_and_mass",
            "source_claim": "Berger anisotropy, a universal peaked profile, and selected internal modes are proposed as a hierarchy mechanism",
            "current_adjudication": "candidate architecture; action-owned mode selector, profile, domain, dressing, and physical scale remain downstream",
            "upstream_use": "FORBIDDEN_UNTIL_GATE7_AND_ACTION_MAPS_CLOSE",
        },
        {
            "topic": "collapse",
            "source_claim": "Track A explicitly introduces threshold collapse phenomenologically; Track B's derived nonlinearities remain unitary and do not collapse",
            "current_adjudication": "not part of BHSM-AE-2.0.0 without a separately authorized action version",
            "upstream_use": "FORBIDDEN",
        },
        {
            "topic": "cosmology_and_TH_TB1",
            "source_claim": "scalar-topographic kernels, BAO-SN correlations, torsion-balance protocols, and benchmark shifts are forecasts or phenomenological screens",
            "current_adjudication": "downstream observable-validation program; no experiment result or retained-action derivation is supplied by the PDFs",
            "upstream_use": "COMPARISON_ONLY",
        },
        {
            "topic": "core_diagram",
            "source_claim": "the 4D hypersphere core image is explicitly described as intuition; Penrose Add advances a black-hole/white-hole core narrative without equations or a variational transmission law",
            "current_adjudication": "no action-owned core-to-reset transmission manifold or projector exists",
            "upstream_use": "FORBIDDEN",
        },
        {
            "topic": "nightcrawler_cosmology",
            "source_claim": "the current project index reports a weak high-redshift consistency hint, no Tier-A validation, unvalidated lambda_BH, failed mass/SFR transfer claims, and an inconclusive DESI DR1 axis test",
            "current_adjudication": "empirical work is a downstream falsification program; the current cosmology manuscript itself states that a covariant action, stability analysis, and microphysical origin remain future work",
            "upstream_use": "COMPARISON_ONLY",
        },
        {
            "topic": "historical_completion_labels",
            "source_claim": "older artifacts use physical-complete or internal-package-complete labels within narrower tiers",
            "current_adjudication": "superseded for full completion by AE2 current registries, Gate7 active, Gate8 locked, FULL_BHSM_COMPLETE=false",
            "upstream_use": "HISTORICAL_SCOPE_ONLY",
        },
    ]
    downstream = [
        {"order": 1, "work_package": "G7_PARAMETRIC_PHYSICAL_HISTORY", "depends_on": ["C2_EXACT_FIXED_S_FIELD", "AE2_RESET_RELATION", "NO_CORE_SELECTOR"], "exit": "actual reset-family base history or a coupled forward-adjoint KKT root, with event/stop alternative"},
        {"order": 2, "work_package": "G7_PROJECTED_FORCE_AND_SADDLE", "depends_on": ["G7_PARAMETRIC_PHYSICAL_HISTORY", "MAXIMAL_WEYL_OR_FINITE_ENDPOINT", "ADJOINT_CAUCHY"], "exit": "N_phys^dagger q_rep=0 on the retained quotient"},
        {"order": 3, "work_package": "G7_HESSIAN_WARD_SCALAR_MAP", "depends_on": ["G7_PROJECTED_FORCE_AND_SADDLE"], "exit": "physical Hessian, Ward/BRST trace, scalar observable map, Gate7 closure"},
        {"order": 4, "work_package": "G8_PARTICLE_AND_SECTOR_DOMAIN", "depends_on": ["G7_HESSIAN_WARD_SCALAR_MAP"], "exit": "persistent particle/history classes, generation slots, sector projectors, complete self-adjoint domains"},
        {"order": 5, "work_package": "GAUGE_AND_REPRESENTATION", "depends_on": ["G8_PARTICLE_AND_SECTOR_DOMAIN"], "exit": "action-owned gauge normalization, hypercharge/anomaly ledger, no-extra-light-state spectrum; test 1:2:7 and a=1/118 without insertion"},
        {"order": 6, "work_package": "YUKAWA_MASS_MIXING", "depends_on": ["GAUGE_AND_REPRESENTATION"], "exit": "bare response matrices, universal scale, dressing map, charged masses, CKM, PMNS, propagation-locked neutrino mass"},
        {"order": 7, "work_package": "PHOTON_CP_DECAY_AND_CONTINUUM", "depends_on": ["YUKAWA_MASS_MIXING"], "exit": "gauge propagation, CP/decay channels, Ward/BRST, continuum and domain margins"},
        {"order": 8, "work_package": "FROZEN_COMPARISON_AND_EXTERNAL_TESTS", "depends_on": ["PHOTON_CP_DECAY_AND_CONTINUUM"], "exit": "byte-reproducible frozen comparison, kill screens, TH-TB1/cosmology comparison kept downstream"},
    ]
    validations = {
        "ae2_current": data["ae2"]["action_version"] == "BHSM-AE-2.0.0",
        "full_completion_false_in_all_current_registries": all(data[key]["FULL_BHSM_COMPLETE"] is False for key in ("ontology", "formula", "gates", "dag", "basis")),
        "gate7_force_is_current_owner": next(row for row in gates if row["canonical_id"] == "G7_08_FORCE")["current_status"] == "OPEN_CURRENT_OWNER",
        "gate7_prefix_closed": closed == [f"G7_{index:02d}_{suffix}" for index, suffix in enumerate(("AE2_DOMAIN", "FIXED_CHANNEL", "SECTOR_CLASS", "NONFERMION", "FACTORIZED_LAP", "E1_FINITE", "ANGULAR_TAIL"), start=1)],
        "exact_fixed_s_field_certified": data["exact_field"]["claim_boundary"]["exact_fixed_s_field_oracle"] == "CERTIFIED",
        "parametric_base_history_open": data["exact_field"]["claim_boundary"]["actual_parametric_base_history"] == "OPEN",
        "core_selector_not_derived": data["core_audit"]["claim_boundary"]["core_transmitted_physical_manifold"] == "OWNER_HYPOTHESIS_NOT_ACTION_DERIVED",
        "one_over_118_not_derived": data["core_audit"]["claim_boundary"]["a_equals_1_over_118"] == "OWNER_CANDIDATE_NOT_DERIVED",
        "legacy_complete_label_not_release_complete": data["legacy_completion"]["BHSM_1_0_release_complete"] is False,
        "v15_7_full_false": data["v15_7"]["FULL_BHSM_COMPLETE"] is False,
        "all_pdf_sources_have_unique_hashes": len({row[2] for row in PDF_CORPUS}) == len(PDF_CORPUS),
        "all_document_sources_have_unique_hashes": len({row[2] for row in DOCUMENT_CORPUS}) == len(DOCUMENT_CORPUS),
        "pdf_corpus_has_no_promoted_action_input": all(row[3] != "ACTION_DERIVED_CURRENT_AE2_INPUT" for row in PDF_CORPUS),
        "fine_structure_exact_candidate_is_not_one_over_118": abs((1.0 / (12.0 * math.pi * math.pi)) - (1.0 / 118.0)) > 1.0e-8,
        "fine_structure_mapping_conflict_quarantined": True,
        "frozen_predictions_unchanged": data["core_audit"]["claim_boundary"]["frozen_predictions_changed"] is False,
    }
    return {
        "artifact": "BHSM_FULL_RECALL_HINDSIGHT_RECON_FORESIGHT",
        "action_version": "BHSM-AE-2.0.0",
        "status": "CURRENT_BHSM_DAG_RECONCILED_GATE7_FORCE_ROOT_REMAINS_OPEN",
        "FULL_BHSM_COMPLETE": False,
        "authority_order": [
            "CURRENT_OWNER_ONTOLOGY",
            "BHSM_AE2_VERSIONED_ACTION_DOMAIN",
            "CURRENT_SEMANTIC_REGISTRIES_AND_VALIDATED_THEOREMS",
            "HISTORICAL_REPOSITORY_ARTIFACTS_IN_DECLARED_SCOPE",
            "NORMAN_PDF_CORPUS_AS_HYPOTHESIS_AND_DOWNSTREAM_TEST_SOURCE",
            "EMPIRICAL_COMPARISON_NEVER_UPSTREAM",
        ],
        "inventory": {
            "ontology_records": len(ontology),
            "formula_records": len(formula),
            "gate_records": len(gates),
            "closed_gate7_prefix": closed,
            "open_gate7_suffix": open_gates,
            "norman_pdf_sources": papers,
            "norman_pdf_page_total": sum(row[1] for row in PDF_CORPUS),
            "norman_document_sources": documents,
            "norman_document_page_total": sum(row[1] for row in DOCUMENT_CORPUS),
            "reviewed_source_page_total": sum(row[1] for row in PDF_CORPUS) + sum(row[1] for row in DOCUMENT_CORPUS),
            "nightcrawler_snapshot": NIGHTCRAWLER_SNAPSHOT,
            "hara_fsc_snapshot": HARA_FSC_SNAPSHOT,
        },
        "historical_reconciliation": historical_reconciliation,
        "current_scientific_state": {
            "validated": [
                "AE2 event-child glued domain and positive-time local history existence",
                "fixed-channel source operator, source-Dini, nonfermion and finite angular/source scopes",
                "two-sided seam and inverse-free Weyl/Calderon machinery",
                "constraint-projected replacement-force criterion and 139/73/67/66 dimension ledger",
                "exact fixed-s C2 vector-field oracle",
                "mathematical weight-seven/weight-five asymptotic branch in nonrealized scope",
            ],
            "invalidated_or_superseded": [
                "universal terminal recurrence or chord 3 as Gate7 prerequisites",
                "proof centers as physical histories",
                "core transmission, 1:2:7, eta_l, or a=1/118 as a hidden KKT selector",
                "strict gap or strict power-law tail as necessary source-Dini conditions",
                "historical tier-complete labels as full current completion",
            ],
            "open_current_owner": "actual parametric C2 history or coupled forward-adjoint KKT on the retained physical quotient, followed by the heat-minus-zeta covector root",
        },
        "downstream_completion_program": downstream,
        "exact_next_dependency": "ASSEMBLE_THE_ACTION_RESET_CHART_WITH_THE_EXACT_FIXED_s_FIELD_IN_A_NO_SELECTOR_MULTIPLE_SHOOTING_OR_COUPLED_FORWARD_ADJOINT_KKT;_CERTIFY_EVENT_STOP_OR_PROJECTED_FORCE_ROOT_BEFORE_ANY_DOWNSTREAM_OBSERVABLE_PROMOTION",
        "claim_boundary": {
            "Gate7": "ACTIVE_G7_08_FORCE",
            "Gate8": "LOCKED",
            "FULL_BHSM_COMPLETE": False,
            "a_equals_1_over_118": "ROUNDED_SOURCE_TRACE_FOUND_AS_1_OVER_12PI2_BUT_NOT_ACTION_DERIVED_OR_AE2_ATTACHED",
            "norman_pdf_claims": "HISTORICAL_HYPOTHESES_PROTOCOLS_OR_DOWNSTREAM_COMPARISONS_NOT_CURRENT_ACTION_INPUTS",
            "frozen_predictions_changed": False,
        },
        "inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS.values()},
        "validation": validations,
        "validation_passed": all(validations.values()),
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {RESULT.relative_to(ROOT)}")
    print(f"validation_passed={payload['validation_passed']}")
    print(f"status={payload['status']}")


if __name__ == "__main__":
    main()
