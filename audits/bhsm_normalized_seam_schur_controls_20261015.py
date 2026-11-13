"""Independent literal full-border mixed-jet controls of the owned seam."""
from pathlib import Path
from hashlib import sha256
from importlib.util import spec_from_file_location, module_from_spec
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
TEST = ROOT/'tests/test_muon_normalized_seam_schur_jets.py'
spec = spec_from_file_location('seam_literal_controls', TEST)
controls = module_from_spec(spec)
spec.loader.exec_module(controls)


def materialize(output):
    out = Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    result = controls.run_independent_controls()
    paths = (ROOT/'src/bhsm/interface/muon_normalized_seam_schur_jets.py',
             TEST, Path(__file__).resolve())
    result.update(scope='off-shell MP64 literal full-seam inverse and mixed derivatives',
                  coupled_matching_corrections=0,
                  physical_outgoing_or_magnetic_response_claimed=False,
                  source_sha256={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest()
                                 for p in paths})
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True,
        allow_nan=False)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(max_MP64_error=max(result['independent_literal_full_seam_MP64_solution_max_errors'].values()),
                         result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    materialize(args.output)
