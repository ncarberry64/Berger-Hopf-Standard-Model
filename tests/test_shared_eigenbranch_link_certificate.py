"""Read-only exact acceptance checks for the new local certificate."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/'artifacts/flagship_integration/gate7_shared_eigenbranch_links_20260923'
spec = importlib.util.spec_from_file_location('link_package', ROOT/'scripts/package_n12_gate7_shared_eigenbranch_links.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def certificate():
    return json.loads((PACKAGE/'certificate.json').read_bytes())


def test_exact_certificate_and_independent_reproduction():
    checker.verify(certificate())
    first, repeat = [(PACKAGE/name).read_bytes() for name in ('certificate.json', 'independent_repeat.json')]
    receipt = json.loads((PACKAGE/'reproduction.json').read_bytes())
    assert first == repeat
    assert hashlib.sha256(first).hexdigest().upper() == receipt['certificate_SHA256']
    assert receipt['independent_recomputation'] is True


@pytest.mark.parametrize('change', ('false_zero_image', 'gate_promotion', 'missing_link',
                                   'continuous_tube', 'zero_gap', 'missing_overlap'))
def test_incomplete_or_overpromoted_certificates_fail_closed(change):
    data = copy.deepcopy(certificate())
    if change == 'false_zero_image':
        data['links'][0]['image_radius_ratio_upper']['exact'] = '0'
    elif change == 'gate_promotion':
        data['Gate7_closed'] = True
    elif change == 'missing_link':
        data['links'].pop()
    elif change == 'continuous_tube':
        data['whole_continuous_history_tube_covered'] = True
    elif change == 'zero_gap':
        data['links'][0]['gap_lower']['exact'] = '0'
    else:
        data['links'][0]['both_frozen_eigenpair_boxes_contained'] = False
    with pytest.raises(ValueError):
        checker.verify(data)


def test_original_physical_radii_are_unchanged():
    ledger = json.loads((ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json').read_bytes())
    assert certificate()['radius_exact'] == [row['radius']['exact'] for row in ledger['rows']]
