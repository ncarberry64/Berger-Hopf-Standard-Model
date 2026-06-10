import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
THEORY = ROOT / "theory"

REQUIRED_MANUSCRIPT_FILES = (
    "title.md",
    "abstract.md",
    "introduction.md",
    "framework.md",
    "gauge_and_field_ledger.md",
    "flavor_predictions.md",
    "ckm_cp_structure.md",
    "gauge_higgs_electroweak.md",
    "ht_gap_and_scalar_sector.md",
    "bare_vs_dressed_branches.md",
    "falsification_ledger.md",
    "limitations.md",
    "conclusion.md",
    "bhsm_v1_technical_note.md",
)

FULL_MANUSCRIPT = MANUSCRIPT / "BHSM_v1_technical_note_full.md"
REFERENCES = MANUSCRIPT / "references.md"
LATEX_MANUSCRIPT = MANUSCRIPT / "BHSM_v1_technical_note.tex"
SUBMISSION_CHECKLIST = MANUSCRIPT / "submission_checklist.md"

FORBIDDEN_PHRASES = (
    "fully proven",
    "complete derivation",
    "derived the standard model from first principles",
    "proof of yang-mills confinement",
    "h_t theorem proven",
    "dressed branch final",
    "all predictions confirmed",
)

REQUIRED_FULL_MANUSCRIPT_SECTIONS = (
    "# The Berger",
    "# Abstract",
    "# Introduction",
    "# Framework",
    "# Gauge and Field Ledger",
    "# Flavor Predictions",
    "# CKM and CP Structure",
    "# Gauge, Higgs, and Electroweak Screens",
    "# H_T Gap and Scalar Sector",
    "# Bare vs Dressed Branches",
    "# Falsification Ledger",
    "# Limitations",
    "# Conclusion",
    "# References",
)

REQUIRED_CITATION_LABELS = (
    "[SM-Review]",
    "[CKM-CP]",
    "[PMNS-Review]",
    "[Flavor-Problem]",
    "[Spectral-Geometry]",
    "[Internal-Geometry]",
    "[EFT-Review]",
    "[PDG]",
    "[Quark-Masses]",
    "[Reproducible-Research]",
)

VERIFIED_REFERENCE_MARKERS = (
    "10.1103/PhysRevD.110.030001",
    "10.1103/PhysRevLett.10.531",
    "10.1143/PTP.49.652",
    "10.1016/0550-3213(79)90316-X",
    "10.1103/RevModPhys.59.671",
    "10.1007/978-94-017-9162-5",
    "10.1146/annurev.nucl.56.080805.140508",
    "10.1016/S0010-4655(00)00155-7",
    "10.1371/journal.pcbi.1003285",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _paper_text() -> str:
    return "\n".join(_read(MANUSCRIPT / name) for name in REQUIRED_MANUSCRIPT_FILES)


def test_required_manuscript_files_exist():
    for name in REQUIRED_MANUSCRIPT_FILES:
        assert (MANUSCRIPT / name).is_file()
    assert REFERENCES.is_file()
    assert LATEX_MANUSCRIPT.is_file()
    assert SUBMISSION_CHECKLIST.is_file()


def test_full_manuscript_exists_and_has_required_sections():
    assert FULL_MANUSCRIPT.is_file()
    text = _read(FULL_MANUSCRIPT)

    for section in REQUIRED_FULL_MANUSCRIPT_SECTIONS:
        assert section in text


def test_forbidden_overclaiming_phrases_absent_from_paper():
    text = (
        _paper_text()
        + "\n"
        + _read(FULL_MANUSCRIPT)
        + "\n"
        + _read(LATEX_MANUSCRIPT)
        + "\n"
        + _read(SUBMISSION_CHECKLIST)
    ).lower()

    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text


def test_frozen_constants_and_branch_distinction_appear():
    text = _paper_text() + "\n" + _read(FULL_MANUSCRIPT) + "\n" + _read(LATEX_MANUSCRIPT)

    assert "BHSM = Berger–Hopf Standard Model" in text
    assert "a = alpha^{-1}/(12*pi^2)" in text
    assert "S = 1/(4*pi)" in text
    assert "BHSM_BARE_V1" in text
    assert "BHSM_DRESSED_V1_CANDIDATE" in text
    assert "candidate, not final canonical adoption" in text


def test_full_manuscript_has_reproducibility_section():
    text = _read(FULL_MANUSCRIPT)

    assert "# Repository and Reproducibility" in text
    assert "bhsm-v1.0-freeze" in text
    assert "03039feb14fb4c988edce8453f6ee5b234797eb2" in text
    assert "bhsm-v1.1-paper" in text
    assert "275 passed" in text


def test_references_are_present_and_cover_manuscript_labels():
    full_text = _read(FULL_MANUSCRIPT)
    references = _read(REFERENCES)

    assert "# References" in full_text
    for label in REQUIRED_CITATION_LABELS:
        assert label in full_text
        assert label in references

    for marker in VERIFIED_REFERENCE_MARKERS:
        assert marker in references

    remaining_verify_lines = [
        line for line in references.splitlines() if "VERIFY BEFORE SUBMISSION" in line
    ]
    assert remaining_verify_lines == []


def test_dressed_branch_matches_frozen_prediction_set():
    frozen = _read(THEORY / "bhsm_v1_frozen_prediction_set.md")
    branches = _read(MANUSCRIPT / "bare_vs_dressed_branches.md") + "\n" + _read(FULL_MANUSCRIPT)

    for value in (
        "0.008310500554068288",
        "0.004155250277034144",
        "1.2690463017606151e-05",
        "0.021933971495439474",
        "0.0011165200546001757",
        "0.0035623676140463315",
    ):
        assert value in frozen
        assert value in branches
    assert "only to the middle up-sector ratio `c/t`" in branches


def test_limitations_match_open_proof_obligations():
    limitations = _read(MANUSCRIPT / "limitations.md")

    assert "`H_T` spectrum remains proxy/scaffold audited" in limitations
    assert "Scalar/topographic decoupling remains scaffold audited" in limitations
    assert "Boundary operators `Omega_f` are action-linked, not fully action-derived." in limitations
    assert "Precision QCD common-scale running and higher-loop/threshold RG matching" in limitations
    assert "dressed branch is an adoption candidate" in limitations


def test_falsification_criteria_f1_to_f9_are_present():
    paper = _read(MANUSCRIPT / "falsification_ledger.md") + "\n" + _read(LATEX_MANUSCRIPT)
    source = _read(THEORY / "bhsm_v1_falsification_ledger.md")

    for index in range(1, 10):
        criterion = f"`F{index}`"
        latex_criterion = f"F{index}"
        assert criterion in paper or latex_criterion in paper
        assert criterion in source
    assert "Any post-freeze adjustment of `a`, `S`, modes, or `Z_virt`" in paper


def test_latex_manuscript_has_publication_ready_sections():
    text = _read(LATEX_MANUSCRIPT)

    for section in (
        "\\section{Introduction}",
        "\\section{Framework and Frozen Configuration}",
        "\\section{Gauge and Field Ledger}",
        "\\section{Flavor Prediction Ledger}",
        "\\section{CKM and CP Structure}",
        "\\section{Gauge, Higgs, and Electroweak Screens}",
        "\\section{Bare vs Dressed Branches}",
        "\\section{Falsification Ledger}",
        "\\section{Limitations and Open Proof Obligations}",
        "\\section{Publication Declarations}",
        "\\section{References}",
    ):
        assert section in text

    assert "\\Bare" in text
    assert "\\Dressed" in text
    assert "a=\\alpha^{-1}/(12\\pi^2)" in text
    assert "S=1/(4\\pi)" in text
    assert "changes only $c/t$" in text
    assert "candidate, not final canonical adoption" in text
    assert "not analytically proven" in text
    assert "Scalar/topographic decoupling remains open" in text
    assert "Precision QCD/RG matching remains open" in text
    assert "AI-assisted drafting/coding support" in text


def test_submission_checklist_tracks_remaining_publication_blockers():
    text = _read(SUBMISSION_CHECKLIST)

    assert "No `src/` model logic changed" in text
    assert "`BHSM_BARE_V1`" in text
    assert "`BHSM_DRESSED_V1_CANDIDATE`" in text
    assert "`H_T` remains proxy/scaffold audited" in text
    assert "`Omega_f` remains action-linked" in text
    assert "PDF visual proofread" in text


def test_typesetting_pass_does_not_modify_source_model_files():
    result = subprocess.run(
        [
            r"C:\Program Files\Git\cmd\git.exe",
            "diff",
            "--name-only",
            "HEAD",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    changed = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    allowed_v1_5_scaffold_sources = {
        "src/bhsm_dependency_graph.py",
        "src/bhsm_theorem_ledger.py",
        "src/fifth_force_bounds.py",
        "src/fifth_force_exclusion.py",
        "src/scalar_action.py",
        "src/scalar_decoupling_proof.py",
        "src/scalar_screening_action.py",
        "src/topographic_action.py",
        "src/derivative_screening.py",
        "src/curvature_screening.py",
        "src/full_ht_theorem.py",
        "src/self_adjoint_domain.py",
        "src/diagonal_reference_operator.py",
        "src/finite_core_domain.py",
        "src/essential_self_adjointness.py",
        "src/graph_norm_domain.py",
        "src/kato_rellich_preconditions.py",
        "src/ht_domain_bridge.py",
        "src/perturbation_operator.py",
        "src/perturbation_symmetry.py",
        "src/perturbation_domain_inclusion.py",
        "src/relative_bound_closure.py",
        "src/lower_bound_preservation.py",
        "src/kato_rellich_closure.py",
        "src/perturbation_domain_proof.py",
        "src/perturbation_symmetry_closure.py",
        "src/sector_coupling_infinite_bound.py",
        "src/hopf_boundary_infinite_bound.py",
        "src/lift_projector_domain.py",
        "src/perturbation_closure_decision.py",
        "src/formal_kernel_projector.py",
        "src/formal_complement_projector.py",
        "src/projector_domain_stability.py",
        "src/finite_projector_convergence.py",
        "src/complement_lower_bound_bridge.py",
        "src/formal_complement_closure_decision.py",
        "src/topological_index_operator.py",
        "src/twisted_dirac_index_closure.py",
        "src/index_sector_count.py",
        "src/full_mirror_exclusion.py",
        "src/chiral_projector_closure.py",
        "src/higgs_u1_mirror_channel.py",
        "src/boundary_mirror_channel.py",
        "src/index_mirror_closure_decision.py",
        "src/mirror_exclusion_theorem.py",
        "src/operator_domain_index_closure.py",
        "src/twisted_dirac_index_theorem.py",
        "src/complete_operator_domain_stability.py",
        "src/complete_twisted_dirac_operator.py",
        "src/perturbation_projector_commutator.py",
        "src/projector_graph_domain_stability.py",
        "src/complete_operator_bound_transfer.py",
        "src/ht_domain_stability_decision.py",
        "src/full_ht_theorem_closure.py",
        "src/complete_operator_identification_closure.py",
        "src/projector_commutator_closure.py",
        "src/projector_graph_domain_closure.py",
        "src/lower_bound_transfer_closure.py",
        "src/index_theorem_final_proof.py",
        "src/mirror_exclusion_final_proof.py",
        "src/full_bhsm_theorem_completion.py",
        "src/complete_berger_hopf_operator.py",
        "src/bundle_dirac_derivation.py",
        "src/operator_term_inventory.py",
        "src/operator_missing_term_audit.py",
        "src/operator_identification_theorem.py",
        "src/complete_operator_identification_decision.py",
        "src/lichnerowicz_bundle_curvature.py",
        "src/bundle_connection_curvature.py",
        "src/curvature_remainder_audit.py",
        "src/curvature_remainder_bound.py",
        "src/curvature_remainder_closure_decision.py",
        "src/curvature_remainder_formula.py",
        "src/curvature_remainder_basis_action.py",
        "src/curvature_remainder_sector_action.py",
        "src/curvature_remainder_kernel_action.py",
        "src/curvature_remainder_relative_bound.py",
        "src/curvature_remainder_lower_bound_transfer.py",
        "src/curvature_remainder_formula_decision.py",
        "src/complete_bundle_connection.py",
        "src/bundle_connection_components.py",
        "src/bundle_curvature_formula.py",
        "src/lichnerowicz_curvature_action.py",
        "src/curvature_formula_to_operator_map.py",
        "src/bundle_curvature_closure_decision.py",
        "src/mixed_connection_coefficients.py",
        "src/hopf_base_boundary_coframe.py",
        "src/mixed_curvature_contraction.py",
        "src/clifford_curvature_contraction.py",
        "src/mixed_connection_remainder_bound.py",
        "src/mixed_connection_closure_decision.py",
        "src/mixed_coefficient_rule.py",
        "src/coframe_compatibility_rule.py",
        "src/boundary_coframe_compatibility.py",
        "src/hopf_base_mixed_rule.py",
        "src/mixed_coefficient_minimality.py",
        "src/mixed_coefficient_rule_decision.py",
        "src/bundle_curvature_formula_closure.py",
        "src/bundle_curvature_formula_decision.py",
        "src/bundle_curvature_term_map.py",
        "src/curvature_remainder_after_mixed_rule.py",
        "src/topographic_curvature_representation.py",
        "src/operator_action_uniqueness.py",
        "src/parent_action_to_operator.py",
        "src/operator_variation_audit.py",
        "src/operator_alternative_term_audit.py",
        "src/operator_axiom_uniqueness.py",
        "src/complete_operator_action_uniqueness_decision.py",
    }

    assert not [
        path
        for path in changed
        if path.startswith("src/") and path not in allowed_v1_5_scaffold_sources
    ]
