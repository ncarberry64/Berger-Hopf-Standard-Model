"""Author-defined geometry reporting cannot upgrade a scientific result."""
from copy import deepcopy
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re

import pytest

from bhtracker import surface_geometry_interpretation, with_surface_geometry_interpretation
from bhtracker.interpretation import bhsm_interpretation


ROOT = Path(__file__).resolve().parents[1]
THEORY = ROOT / 'bhtracker/theory'
KEYS = ('definition', 'summary', 'evidence_scope', 'unidentified_scope')


def test_current_contract_is_pinned_to_formal_author_clarification():
    meaning = bhsm_interpretation('gr')
    manifest = meaning['source_provenance']
    entry = next(e for e in manifest['sources'] if e['path'] == meaning['surface_geometry']['source_record'])
    assert entry['commit'] == 'fa4f10a3424aaf21c11cac750892120feaac6dc3'
    assert entry['sha256'] == 'f8dcd3611d71f2acef265bf2f921eb0db5773fc5524266d3a5df63b718c714a3'
    assert entry['url'].startswith(manifest['formal_repository_url'] + '/blob/' + entry['commit'] + '/')
    assert hashlib.sha256((THEORY / entry['path']).read_bytes()).hexdigest() == entry['sha256']
    # The new definition does not rewrite the dated core proposal.
    assert hashlib.sha256((THEORY / 'BHSM_CORE_SURFACE_CONTRACT.json').read_bytes()).hexdigest() == 'a0561d8fe7d1031daa2a56c433d46b99734b20f850e02e16d0e5095b32fc3507'
    assert meaning['core_surface']['core_parameters_fitted'] is False
    assert meaning['core_surface']['new_optical_term_added'] is False


def test_surface_geometry_is_meaning_not_an_extra_term_or_acceptance_gate():
    geometry = surface_geometry_interpretation()
    assert geometry['additional_optical_terms'] == 0
    assert geometry['requires_non_gr_residual'] is False
    assert geometry['fit_alone_validates_gravitational_origin'] is False
    assert geometry['fit_alone_identifies_black_hole'] is False
    assert 'gravitational spacetime geometry' in geometry['definition']
    assert 'support a gravitational origin' in geometry['summary']
    assert 'unique microscopic interface shape' in geometry['unidentified_scope']
    geometry['additional_optical_terms'] = 99
    assert surface_geometry_interpretation()['additional_optical_terms'] == 0


@pytest.mark.parametrize('status', ['PHOTOMETRIC_MODEL_INADEQUATE', 'JOINT_MODEL_NOT_REJECTED', 'FIT_REJECTED', 'TRACKED'])
def test_current_context_preserves_status_native_fields_nulls_and_historical_meaning(status):
    saved = {'status': status, 'parameters': {'mass_msun': None}, 'unavailable': {'horizon': None},
             'investigation_category': 'Potential black hole', 'accepted_black_hole': False,
             'scientific_source_sha256': 'frozen-scientific-source',
             'dataset_input': {'raw_bytes_base64': 'AA==', 'rows': [{'source_row_id': 'native:0001', 'value': -1.0}]},
             'bhsm_interpretation': {'historical_source': 'retained verbatim'}}
    before = deepcopy(saved)
    current = with_surface_geometry_interpretation(saved)
    assert saved == before and current is not saved
    assert set(current) == set(saved) | {'surface_geometry_interpretation'}
    assert {k: v for k, v in current.items() if k != 'surface_geometry_interpretation'} == saved
    assert current['surface_geometry_interpretation'] == surface_geometry_interpretation()


@pytest.mark.parametrize('name', ['index.html', 'photometry.html', 'joint.html', 'atlas.html'])
def test_offline_workspaces_share_exact_contract_and_evidence_qualification(name):
    text = (ROOT / 'bhtracker/web' / name).read_text(encoding='utf8')
    geometry = surface_geometry_interpretation()
    for key in KEYS:
        matches = re.findall(r'<p data-bhsm-surface="' + key + r'">(.*?)</p>', text)
        assert matches == [html.escape(geometry[key])]
    assert 'These observations do not identify a core state, membrane shape, deformation or horizon.' not in text


def test_view_sync_is_idempotent_and_escapes_contract_text(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('sync_interpretation', ROOT / 'scripts/sync_bhsm_interpretation.py')
    sync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sync)
    web = tmp_path / 'web'; web.mkdir()
    for name in ('index.html', 'photometry.html', 'joint.html', 'atlas.html'):
        (web / name).write_text(''.join(f'<p data-bhsm-surface="{key}">old</p>' for key in KEYS), encoding='utf8')
    monkeypatch.setattr(sync, 'ROOT', tmp_path / 'theory')
    contract = {'surface_geometry': {key: '<script>untrusted & text</script>' for key in KEYS}}
    sync.sync_surface_geometry_views(contract)
    first = {p.name: p.read_bytes() for p in web.iterdir()}
    sync.sync_surface_geometry_views(contract)
    assert first == {p.name: p.read_bytes() for p in web.iterdir()}
    assert all(b'<script>' not in raw and b'&lt;script&gt;' in raw for raw in first.values())


def test_current_source_record_and_assets_are_in_installed_content_provenance():
    from bhtracker.provenance import software_provenance
    files = software_provenance()['package_files_sha256']
    for name in ('theory/BHSM_SURFACE_GEOMETRY_CONTRACT.json',
                 'theory/bhsm_sources/BHSM_AUTHOR_SURFACE_GEOMETRY_CLARIFICATION_20261023.md',
                 'theory/bhsm_sources/BHSM_AUTHOR_SURFACE_RECALL_20261023.json'):
        assert files[name] == hashlib.sha256((ROOT / 'bhtracker' / name).read_bytes()).hexdigest()
