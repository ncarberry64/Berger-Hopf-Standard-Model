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
    }

    assert not [
        path
        for path in changed
        if path.startswith("src/") and path not in allowed_v1_5_scaffold_sources
    ]
