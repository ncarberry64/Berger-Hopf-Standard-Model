import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "theory" / "candidate_theorem_discharge_explicit_symbolic_gram_minor.py"


def load_mod():
    spec = importlib.util.spec_from_file_location("explicit_minor", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_generation_labels_and_matrix_shape():
    mod = load_mod()
    sectors = mod.generation_modes()
    assert set(sectors) == {"reference_charged", "reference_neutral", "cyclic_upper", "cyclic_lower"}
    for sector in sectors:
        matrix = mod.feature_matrix(sector)
        assert len(matrix) == len(mod.FEATURE_ATOMS)
        assert all(len(row) == 3 for row in matrix)


def test_entries_are_tied_to_wigner_labels():
    mod = load_mod()
    matrix = mod.feature_matrix("cyclic_upper")
    entry = matrix[0][1]
    assert entry.column.q == 6
    assert entry.harmonic.k == 6
    assert entry.harmonic.ell == 3
    assert entry.harmonic.n == 3
    assert "D^" in entry.expression
    assert "beta0" in entry.expression

