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
    "[EFT-Review]",
    "[PDG]",
    "[Quark-Masses]",
    "[Reproducible-Research]",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _paper_text() -> str:
    return "\n".join(_read(MANUSCRIPT / name) for name in REQUIRED_MANUSCRIPT_FILES)


def test_required_manuscript_files_exist():
    for name in REQUIRED_MANUSCRIPT_FILES:
        assert (MANUSCRIPT / name).is_file()
    assert REFERENCES.is_file()


def test_full_manuscript_exists_and_has_required_sections():
    assert FULL_MANUSCRIPT.is_file()
    text = _read(FULL_MANUSCRIPT)

    for section in REQUIRED_FULL_MANUSCRIPT_SECTIONS:
        assert section in text


def test_forbidden_overclaiming_phrases_absent_from_paper():
    text = (_paper_text() + "\n" + _read(FULL_MANUSCRIPT)).lower()

    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in text


def test_frozen_constants_and_branch_distinction_appear():
    text = _paper_text() + "\n" + _read(FULL_MANUSCRIPT)

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


def test_references_scaffold_and_citation_placeholders_exist():
    full_text = _read(FULL_MANUSCRIPT)
    references = _read(REFERENCES)

    assert "# References" in full_text
    assert "VERIFY BEFORE SUBMISSION" in references
    for label in REQUIRED_CITATION_LABELS:
        assert label in full_text
        assert label in references


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
    paper = _read(MANUSCRIPT / "falsification_ledger.md")
    source = _read(THEORY / "bhsm_v1_falsification_ledger.md")

    for index in range(1, 10):
        criterion = f"`F{index}`"
        assert criterion in paper
        assert criterion in source
    assert "Any post-freeze adjustment of `a`, `S`, modes, or `Z_virt`" in paper
