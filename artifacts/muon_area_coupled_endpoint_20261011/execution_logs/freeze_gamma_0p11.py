"""Pin the completed independently replayed positive-area action family member."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
target = Path(__file__).resolve().parents[1]
groups = [(target, 'gamma_0p11')]
for side in ('incoming', 'outgoing'):
    groups.extend([(target, f'gamma_0p11_{side}_phase'),
                   (target, f'gamma_0p11_{side}_boundary')])
groups.append((ROOT/'artifacts/muon_common_normal_boundary_form_20261011', 'gamma_0p11'))
files = []; pairs = []; dependencies = {}
for folder, stem in groups:
    first, second = (folder/f'{stem}_run_{i}' for i in (1, 2))
    for name in ('result.json', 'application.npz'):
        a, b = (first/name).read_bytes(), (second/name).read_bytes()
        if a != b:
            raise ValueError('independent replay differs: '+str(first/name))
        pairs.append(dict(application=stem, filename=name, bytes=len(a),
                          sha256=sha256(a).hexdigest(), byte_identical=True))
        files.extend((first/name, second/name))
    dependencies.update(json.loads((first/'result.json').read_text())['input_hashes'])
for name, digest in dependencies.items():
    if sha256((ROOT/name).read_bytes()).hexdigest() != digest:
        raise ValueError('consumed owner changed: '+name)
for prefix in ('gamma_0p11_action', 'gamma_0p11_replay'):
    files.append(target/f'{prefix}_verification.json')
files.extend(sorted((target/'execution_logs').glob('gamma_0p11*')))
files.extend(target/'execution_logs'/name for name in (
    'run_gamma_0p11_action.py', 'run_gamma_0p11_replay.py', 'freeze_gamma_0p11.py'))
pair_path = target/'gamma_0p11_pair_verification.json'
manifest_path = target/'gamma_0p11_publication_manifest.json'
if pair_path.exists() or manifest_path.exists():
    raise FileExistsError('preserve the frozen independent replay evidence')
pair_path.write_text(json.dumps(dict(pairs=pairs,
    scope='same finite action parameter-trial member; independent binary64 byte replays',
    physical_formation_or_mode_or_cutoff_selected=False), indent=2, sort_keys=True)+'\n',
    encoding='utf8', newline='\n')
files.append(pair_path); pins = {}
for path in sorted(set(files)):
    data = path.read_bytes()
    if len(data) > 10*1024**2:
        raise ValueError('publication cap: '+str(path))
    if path.suffix in ('.py', '.txt', '.json') and b'\r\n' in data:
        raise ValueError('noncanonical LF: '+str(path))
    pins[path.relative_to(ROOT).as_posix()] = dict(bytes=len(data), sha256=sha256(data).hexdigest())
manifest_path.write_text(json.dumps(dict(
    classification='FROZEN_POSITIVE_AREA_COUPLED_BASE_PHASE_AND_SHARED_NORMAL_APPLICATION',
    files=pins, dependencies=dependencies, parameter_trial=dict(gamma=.11, nu_squared_action=4.),
    scope='full finite represented birth rows and chronological action kernels with recorded numerical outer canonical faces',
    physical_surface_gamma_or_normal_section_or_E0_or_local_R_I_c_selected=False,
    no_static_boundary_pairing_promoted_to_event_drive=True), indent=2, sort_keys=True)+'\n',
    encoding='utf8', newline='\n')
print(json.dumps(dict(files=len(pins), pairs=len(pairs),
    manifest_sha256=sha256(manifest_path.read_bytes()).hexdigest()), sort_keys=True))
