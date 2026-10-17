"""Freeze independent MP64 controls of the conditional seam transfer."""
from pathlib import Path
from hashlib import sha256
import argparse
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def evaluate(output):
    out = Path(output)
    if not out.is_absolute():
        out = ROOT / out
    if out.exists():
        raise FileExistsError('Preserve each independent MP64 application')
    path = ROOT / 'tests/test_muon_isotropic_seam_transfer.py'
    spec = importlib.util.spec_from_file_location('literal_seam_controls', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run_independent_controls()
    result['classification'] = 'INDEPENDENT_LITERAL_MP64_MOVING_SEAM_CONTROLS'
    names = [path, Path(__file__).resolve(), ROOT / 'src/bhsm/interface/muon_isotropic_seam_transfer.py']
    result['source_sha256'] = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in names}
    out.mkdir(parents=True)
    dest = out / 'result.json'
    dest.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(sha256=sha256(dest.read_bytes()).hexdigest(), errors=result['independent_literal_MP64_Cayley_errors'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    evaluate(parser.parse_args().output)
