"""Read-only acceptance and adversarial checks for the connected identity atlas."""
import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import package_n12_gate7_child_chart_atlas as assembly
import package_n12_gate7_child_chart_interval as interval

BASE = ROOT/'artifacts/flagship_integration'
ATLAS = BASE/'gate7_child_atlas_20260924'


def certificates():
    return [json.loads((p/'certificate.json').read_bytes()) for p in
            [BASE/'gate7_shared_eigenbranch_links_20260923']+
            [ATLAS/f'interval_{n:03d}' for n in range(14, 19)]]


def test_frozen_atlas_exact_chain_and_reproduction():
    assembly.verify_chain(certificates())
    manifest = json.loads((ATLAS/'atlas.json').read_bytes())
    assert manifest['certified_centerline_links'] == 12
    assert manifest['Layer_A_connected_eigenbranch_evaluation_cover'] is True
    for field in ('Layer_B_complete_dense_output_physical_tube',
                  'Layer_C_global_physical_remainder', 'Layer_D_full_Gate7_contraction',
                  'Gate7_closed', 'FULL_BHSM_COMPLETE'):
        assert manifest[field] is False
    for relative, digest in manifest['certificates'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest().upper() == digest
    for n in range(14, 19):
        p = ATLAS/f'interval_{n:03d}'
        first = (p/'certificate.json').read_bytes()
        assert first == (p/'independent_repeat.json').read_bytes()
        r = json.loads((p/'reproduction.json').read_bytes())
        assert r['independent_recomputation'] and r['byte_identical']
        assert hashlib.sha256(first).hexdigest().upper() == r['certificate_SHA256']


@pytest.mark.parametrize('fault', ('missing_interval', 'wrong_order', 'wrong_chart',
                                  'different_endpoint', 'changed_physical_radius'))
def test_disconnected_or_changed_atlas_rejected(fault):
    data = copy.deepcopy(certificates())
    if fault == 'missing_interval':
        data.pop(2)
    elif fault == 'wrong_order':
        data[1], data[2] = data[2], data[1]
    elif fault == 'wrong_chart':
        data[1]['links'][0]['to_domain'] = '.coupled_midpoint_eigenpair_pilot_work/interval_018'
    elif fault == 'different_endpoint':
        source = next(p for p in data[1]['source_SHA256']
                      if p.replace('\\', '/').endswith('/endpoint_014/eigenpair.npz'))
        data[1]['source_SHA256'][source] = '0'*64
    else:
        data[1]['radius_exact'][0] = '1'
    with pytest.raises(ValueError):
        assembly.verify_chain(data)


@pytest.mark.parametrize('fault', ('false_bound', 'zero_gap', 'missing_border_overlap',
                                  'gate_promotion', 'tube_promotion'))
def test_interval_acceptance_fails_closed(fault):
    data = copy.deepcopy(certificates()[-1])
    link = data['links'][0]
    if fault == 'false_bound':
        link['image_radius_ratio_upper']['exact'] = '0'
    elif fault == 'zero_gap':
        link['gap_lower']['exact'] = '0'
    elif fault == 'missing_border_overlap':
        link['both_frozen_eigenpair_boxes_contained'] = False
    elif fault == 'gate_promotion':
        data['Gate7_closed'] = True
    else:
        data['whole_continuous_history_tube_covered'] = True
    with pytest.raises(ValueError):
        interval.verify(data)


def test_historical_source_reconciliation_is_explicit():
    data = json.loads((ATLAS/'atlas.json').read_bytes())
    for row in data['interval13_source_reconciliation']:
        if row['reconciliation'] == 'CRLF_LF_ONLY_EXPLICIT_EQUIVALENCE':
            raw = (ATLAS/row['historical_bytes_archive']).read_bytes()
            assert hashlib.sha256(raw).hexdigest().upper() == row['original_SHA256']
            # Locate the current source portably, without requiring old checkout paths.
            relative = row['active_path'].replace('\\', '/').split('/Berger-Hopf-Standard-Model/', 1)[1]
            assert raw.replace(b'\r\n', b'\n') == (ROOT/relative).read_bytes().replace(b'\r\n', b'\n')
