"""Import reviewed retained-response components without rerunning ancestors.

The original archives remain immutable provenance. Only selected reusable source,
one set of inputs, compact outputs and scope records enter the maintained tree.
Existing different files are never overwritten by this importer.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
ART = REPO / 'artifacts/muon_retained_response_20261018'
SRC = REPO / 'src/bhsm/interface/retained_response'
PACKAGES = {
    'compatible_source': 'BHSM_compatible_source_application_20261016',
    'cascade_connection': 'BHSM_daughter_cascade_magnetic_connection_20261017',
    'probe_connection': 'BHSM_cascade_photon_projection_20261017',
    'action_magnetic_kernel': 'BHSM_action_magnetic_insertion_20261017',
    'retained_magnetic_application': 'BHSM_magnetic_retained_application_20261017',
    'odd_response_bridge': 'BHSM_magnetic_odd_response_connection_20261017',
    'forced_canonical_source': 'BHSM_forced_canonical_source_20261017',
    'integrated_source': 'BHSM_integrated_magnetic_source_20261017',
    'integrated_magnetic_hessian': 'BHSM_integrated_magnetic_source_20261017',
    'port_response': 'BHSM_port_preserving_retarded_response_20261017',
    'build_higgs_response': 'BHSM_higgs_wall_coupled_response_20261017',
    'graph_action': 'BHSM_normal_graph_field_response_20261017',
    'finite_time_response': 'BHSM_finite_time_spin_response_20261017',
    'field_spin_connection': 'BHSM_field_to_spin_response_20261018',
}
LIVE_OWNERS = (
    'muon_native_dirac_hamiltonian.py', 'muon_native_product_factor_graph.py',
    'muon_intrinsic_higgs_weak_action.py', 'muon_intrinsic_higgs_gauge_action.py',
    'muon_intrinsic_m4_normal_pullback.py', 'muon_intrinsic_lepton_primal.py',
    'muon_material_higgs_gauge_action.py', 'muon_parent_gauge_geometry_correction.py',
    'ae31_c2_intrinsic_m4_lepton_action.py', 'ae3_c2_hopf_semigroup_transport.py',
    'muon_baton_zoo_original_validation.py',
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f'Preserving different file: {path}')
    else:
        path.write_bytes(data)


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def replace_function(text, name, replacement):
    node = next(n for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+replacement+'\n'+''.join(lines[node.end_lineno:])


def adapt(name, text):
    text = text.replace('\r\n', '\n')
    text = re.sub(r'^sys\.path\.insert\(.*\)\n', '', text, flags=re.M)
    for module in PACKAGES:
        text = re.sub(r'^from '+module+r' import ', 'from .'+module+' import ', text, flags=re.M)
    text = text.replace('ROOT=Path(__file__).resolve().parent',
        "ROOT=Path(__file__).resolve().parents[4]/'artifacts/muon_retained_response_20261018'")
    if name == 'compatible_source':
        text = replace_function(text, 'retained_representation', '''def retained_representation():
    """Live unit-Tr16 full18 owner; no state or pole is selected."""
    from ..muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from ..muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    G=lepton_unit_trace_gauge_representation()['generators']
    alpha=lepton_current_hilbert_representation()['alpha']
    action=np.zeros((5,4,18,18),complex)
    action[0]=1j*G
    action[2:]=1j*np.einsum('aij,cjk->acik',alpha,G)
    return G,alpha,action
''')
    if name == 'finite_time_response':
        start, end = text.index('YUKAWA='), text.index("LABELS=['lo'")
        text = text[:start]+'''from ..muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
YUKAWA=np.diag(lepton_current_hilbert_representation()['family_Y']).copy()
'''+text[end:]
        text = replace_function(text, 'full18_point', '''def full18_point(raw):
    """Live material-clock Hamiltonian; convert At to proper time exactly once."""
    from ..muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
    raw=np.asarray(raw,float);d=wall_data(raw);G,alpha,_=retained_representation()
    H=raw[260:262]+1j*raw[262:264]
    connection=np.einsum('fc,cij->fij',d['connection'][[0,2,3,4]],G)
    connection[0]/=d['lapse']
    owned=canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
        spatial_derivative_map=np.zeros((1,3,18,18)),H=H[None],
        R4=d['R4'],gauge_connection=connection[None])
    return d,d['lapse']*owned['hamiltonian_map'][0],G,alpha
''')
        text = text.replace("'inputs/metadata.json'", "'inputs/history_metadata.json'")
        text = text.replace("f'{side}.npz'", "f'{side}_history.npz'")
    if name == 'field_spin_connection':
        old = '    return meta\n'
        new = '''    for name,expected in meta['maintained_source_sha256'].items():
        if hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('maintained source changed: '+name)
    repo=Path(__file__).resolve().parents[4]
    for name,expected in meta['live_owner_lf_sha256'].items():
        payload=(repo/name).read_bytes().replace(b'\\r\\n',b'\\n')
        if hashlib.sha256(payload).hexdigest()!=expected:
            raise ValueError('live owner changed; review affected cached applications: '+name)
    return meta
'''
        text = text.replace(old, new, 1)
        text = text.replace("    root=Path(result_directory)\n", "    root=Path(result_directory)\n    verify_application_result(root)\n", 1)
        text += '''

def verify_application_result(result_directory):
    """Reject stale owners, source, inputs or modified evaluated output arrays."""
    verify_inputs()
    root=Path(result_directory)
    binding=json.loads((root/'BINDING.json').read_text())
    if binding['input_manifest_sha256']!=hashlib.sha256((ROOT/'inputs/PROVENANCE.json').read_bytes()).hexdigest():
        raise ValueError('application input binding changed; review affected result')
    for name,expected in binding['files'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('evaluated result changed: '+name)
    return binding
'''
    if name == 'graph_action':
        text = text.replace('import torch\n', '')
        text = text.replace('torch.set_default_dtype(torch.float64)\n', '')
        text = text.replace('torch.set_num_threads(1)\n', '')
        text = text.replace('x=torch.zeros(104,requires_grad=True)',
                            'x=torch.zeros(104,dtype=torch.float64,requires_grad=True)')
        text = text.replace('torch.eye(3)', 'torch.eye(3,dtype=x.dtype,device=x.device)')
        # Only the automatic Hessian producers need this optional dependency.
        lines=text.splitlines(keepends=True)
        tree=ast.parse(text)
        for node in reversed(tree.body):
            if isinstance(node,ast.FunctionDef) and node.name in ('torch_action','blocks'):
                first=node.body[0]
                at=first.end_lineno if isinstance(first,ast.Expr) and isinstance(first.value,ast.Constant) and isinstance(first.value.value,str) else node.lineno
                lines.insert(at, '    import torch\n')
        text=''.join(lines)
    return text


def main(handoff):
    extracted = handoff/'extracted'
    latest = extracted/'BHSM_field_to_spin_response_20261018'
    records = {}
    for module, package in PACKAGES.items():
        original = extracted/package/(module+'.py')
        raw = original.read_bytes()
        maintained = adapt(module, raw.decode('utf-8-sig')).encode()
        ast.parse(maintained)
        put(SRC/(module+'.py'), maintained)
        records[module+'.py'] = dict(package=package, original_sha256=sha(raw),
            maintained_sha256=sha(maintained), modifications='relative imports and artifact root; live lepton owner adapters where applicable')
    put(SRC/'__init__.py', b'"""Scoped retained-history response components; physical feedback remains open."""\n')
    put(SRC/'.gitattributes', b'*.py text eol=lf\n')
    put(ART/'.gitattributes', b'** -text whitespace=cr-at-eol\n')
    for f in (latest/'inputs').iterdir():
        if f.is_file() and f.name!='PROVENANCE.json':
            put(ART/'inputs'/f.name, f.read_bytes())
    meta = json.loads((latest/'inputs/PROVENANCE.json').read_text())
    meta['original_source_dependencies'] = {k:v for k,v in meta['files'].items() if k.startswith('dependencies/')}
    meta['files'] = {k:v for k,v in meta['files'].items() if k.startswith('inputs/')}
    meta['maintained_source_sha256'] = {k:v['maintained_sha256'] for k,v in records.items()}
    meta['live_owner_lf_sha256'] = {
        'src/bhsm/interface/'+name:sha((REPO/'src/bhsm/interface'/name).read_bytes().replace(b'\r\n',b'\n'))
        for name in LIVE_OWNERS}
    put(ART/'inputs/PROVENANCE.json', encode(meta))
    for f in (latest/'replay_A').iterdir():
        if f.is_file(): put(ART/'supplied'/f.name, f.read_bytes())
    graph = extracted/'BHSM_normal_graph_field_response_20261017'
    for f in (graph/'replay_A').iterdir():
        if f.is_file(): put(ART/'normal_graph'/f.name, f.read_bytes())
    archives = []
    for f in sorted((handoff/'sources').glob('*.zip')):
        payload=f.read_bytes();target=ART/'provenance'/f.name
        put(target, payload)
        archives.append(dict(path=target.relative_to(REPO).as_posix(),canonical_bytes=len(payload),sha256=sha(payload)))
    for package in sorted(extracted.iterdir()):
        for name in ('DERIVATION.md','CHECKPOINT.json','VERIFICATION.json'):
            f=package/name
            if f.exists(): put(ART/'scope_records'/package.name/name, f.read_bytes())
    put(ART/'BUNDLE_MANIFEST.json',(handoff/'BUNDLE_MANIFEST.json').read_bytes())
    put(ART/'source_map.json',encode(dict(source_revision=meta['source_revision'],
        maintained_modules=records,archives=archives,
        scope='retained provisional history maps and mathematical controls; no physical admission')))
    runner=(latest/'run_connection.py').read_text(encoding='utf-8-sig')
    runner=runner.replace('from field_spin_connection import *','from bhsm.interface.retained_response.field_spin_connection import *')
    runner=runner.replace('from retained_magnetic_application import FRAME','from bhsm.interface.retained_response.retained_magnetic_application import FRAME')
    runner=runner.replace("    if not packet['all_scoped_checks_pass']:", '''    json_write(out/'BINDING.json',dict(
        input_manifest_sha256=hashlib.sha256((ROOT/'inputs/PROVENANCE.json').read_bytes()).hexdigest(),
        files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.glob('*.npz'))}))
    if not packet['all_scoped_checks_pass']:''')
    put(REPO/'scripts/evaluate_muon_retained_field_spin.py',runner.encode())
    ledger=REPO/'data/retained_large_research_artifacts.json'
    registry=json.loads(ledger.read_text())
    paths={r['path'] for r in registry['artifacts']}
    for record in archives:
        if record['canonical_bytes']>10*1024**2 and record['path'] not in paths:
            registry['artifacts'].append(record)
    ledger.write_bytes((json.dumps(registry,indent=2)+'\n').encode())
    print(json.dumps(dict(modules=len(records),input_files=len(meta['files']),archives=len(archives))))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('handoff',type=Path)
    main(parser.parse_args().handoff)
