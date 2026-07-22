from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "bhsm_in_plain_language.md",
    ROOT / "docs" / "bhsm_scientific_contribution_ledger.md",
    ROOT / "docs" / "cern_toy_model_in_plain_language.md",
    ROOT / "docs" / "cern_open_data_benchmark.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.split())


def test_plain_language_entrypoints_are_prominent_and_indexed():
    readme = read(ROOT / "README.md")
    docs_index = read(ROOT / "docs" / "README.md")
    for relative in (
        "docs/bhsm_in_plain_language.md",
        "docs/bhsm_scientific_contribution_ledger.md",
        "docs/cern_toy_model_in_plain_language.md",
    ):
        assert relative in readme
        assert (ROOT / relative).is_file()
    for filename in (
        "bhsm_in_plain_language.md",
        "bhsm_scientific_contribution_ledger.md",
        "cern_toy_model_in_plain_language.md",
    ):
        assert filename in docs_index


def test_lay_docs_preserve_engine_physics_and_completion_boundaries():
    combined = normalized("\n".join(read(path) for path in PUBLIC_DOCS))
    assert "FULL_BHSM_NOT_COMPLETE" in combined
    assert "Engine validation, not BHSM Physics validation" in combined
    assert "does not currently prove the Standard Model" in combined
    forbidden = (
        "BHSM is experimentally validated",
        "BHSM derives all particle masses",
        "BHSM derives the Standard Model from pure geometry",
        "CERN endorses BHSM",
        "CMS endorses BHSM",
        "full BHSM completion is achieved",
    )
    assert not any(phrase in combined for phrase in forbidden)


def test_cern_lay_explanation_states_the_data_flow_and_nonphysics_scope():
    text = normalized(read(ROOT / "docs" / "cern_toy_model_in_plain_language.md"))
    for required in (
        "200,000 unique muon four-vectors",
        "2,000,000 vector",
        "map projection",
        "none of this establishes BHSM as particle physics",
        "CERN_OPEN_DATA_FOUR_VECTOR_BENCHMARK_NOT_TRACK_RECONSTRUCTION",
    ):
        assert required in text


def test_contribution_ledger_records_merged_frontier_without_preclaiming_active_work():
    text = read(ROOT / "docs" / "bhsm_scientific_contribution_ledger.md")
    assert "positive mathematical derivation" in text
    assert "obstruction or kill test" in text
    assert "[#153]" in text
    assert "[#154]" in text
    assert "[#156]" in text
    assert "latest result on `main` is PR #156" in text
    assert "not listed as an achievement before review" in text
    assert "does not assert" in text


def test_new_local_markdown_links_resolve():
    link_pattern = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    for source in PUBLIC_DOCS:
        for target in link_pattern.findall(read(source)):
            if target.startswith(("http://", "https://", "#")):
                continue
            target_path = target.split("#", 1)[0]
            assert (source.parent / target_path).resolve().exists(), f"{source}: {target}"
