import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("institutional_check", ROOT / "tools/institutional_check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def test_core_readiness_requires_frozen_integrity_and_keeps_physics_open():
    report = check.check()
    assert report["passed"]
    assert report["scientific_status"] == "GATE7_ACTIVE__PHYSICAL_COMPLETION_OPEN"
    assert not report["network_or_proof_campaign_started"]
    assert not report["smoke"]["executed"]


def test_missing_source_snapshot_fails_without_running_tests(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "ROOT", tmp_path)
    report = check.check(smoke=True)
    assert not report["passed"]
    assert not report["checks"]["frozen_prediction_integrity"]
    assert not report["checks"]["current_system_map_present_and_valid"]
    assert not report["smoke"]["executed"]


def test_missing_optional_exact_arithmetic_does_not_block_core(monkeypatch):
    original = check.importlib.metadata.version

    def version(name):
        if name == "python-flint":
            raise check.importlib.metadata.PackageNotFoundError(name)
        return original(name)

    monkeypatch.setattr(check.importlib.metadata, "version", version)
    assert check.check("core")["passed"]
    assert not check.check("rigorous")["passed"]


def test_source_archive_guard_protects_scientific_files_without_git(tmp_path, monkeypatch):
    import conftest
    monkeypatch.setattr(conftest, "ROOT", tmp_path)
    (tmp_path / "src").mkdir()
    source = tmp_path / "src/example.py"
    source.write_text("x = 1\n")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv/unrelated.py").write_text("x = 2\n")
    assert conftest._tracked_paths() == (source.resolve(),)
