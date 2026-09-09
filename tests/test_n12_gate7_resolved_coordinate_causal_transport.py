from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_resolved_coordinate_causal_transport as report


def complete_record():
    return dict(artifact='BHSM_N12_GATE7_MIDPOINT_COORDINATE_PULLBACK',
                validation_passed=True,
                scope='COORDINATE_ERROR_THROUGH_EXACT_STORED_BINARY64_TENSOR_ONLY',
                coverage=dict(verified_midpoints=370, required_midpoints=370, complete=True),
                rows=[dict(interval=i) for i in range(370)])


def test_complete_ordered_coordinate_records_required():
    record = complete_record()
    assert len(report._coordinate_rows(record)) == 370
    record['rows'][3]['interval'] = 4
    with pytest.raises(RuntimeError, match='ordered'):
        report._coordinate_rows(record)


def test_wrong_scope_or_incomplete_coverage_is_rejected():
    for key, value in [('scope', 'PHYSICAL_HESSIAN'), ('validation_passed', False),
                       ('coverage', dict(complete=False))]:
        record = complete_record()
        record[key] = value
        with pytest.raises(RuntimeError, match='Complete'):
            report._coordinate_rows(record)


def test_changed_historical_target_is_not_accepted_by_tolerance():
    operands = dict(basis=np.eye(2), target=np.ones((2, 2)))
    hashes = {n: report.old.coordinate._array_hash(v) for n, v in operands.items()}
    row = dict(interval=4, operand_binary64_SHA256=hashes)
    assert report._verify_operands(row, operands) == hashes
    operands['target'][0, 0] = np.nextafter(1., 2.)
    with pytest.raises(RuntimeError, match='changed'):
        report._verify_operands(row, operands)


def test_input_binding_rejects_modified_file(monkeypatch, tmp_path):
    monkeypatch.setattr(report, 'ROOT', tmp_path)
    path = tmp_path/'operand.txt'
    path.write_bytes(b'original')
    record = dict(inputs={'operand.txt': report.center._sha(path)})
    assert report._verified_inputs(record) == record['inputs']
    path.write_bytes(b'modified')
    with pytest.raises(RuntimeError, match='changed'):
        report._verified_inputs(record)


def test_missing_input_bindings_rejected():
    with pytest.raises(RuntimeError, match='no input'):
        report._verified_inputs({})
