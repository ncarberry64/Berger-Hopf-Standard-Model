"""A center derivative or missing descriptor column cannot establish uniform HS blocks."""
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_uniform_physical_local_defects as pilot


@pytest.mark.parametrize('alteration',[
    {'uniform_physical_first_derivatives_enclosed':False},
    {'weighted_augmented_basis_columns':98},
    {'full_descriptor_direction_included':False},
    {'actual_HS_midpoint_domain_enclosed':False},
])
def test_incomplete_or_wrong_domain_derivative_is_rejected(tmp_path,alteration):
    producer=SimpleNamespace(load_inputs=lambda index:dict(binding={}),WORK=tmp_path,ALGORITHM='test')
    directory=tmp_path/'interval_013';directory.mkdir()
    report=dict(validation_passed=True,uniform_physical_first_derivatives_enclosed=True,
        weighted_augmented_basis_columns=99,full_descriptor_direction_included=True,
        actual_HS_midpoint_domain_enclosed=True)
    report.update(alteration)
    (directory/'record.json').write_text(json.dumps(dict(binding={},algorithm='test',interval=13,report=report)))
    (directory/'reproduction.json').write_text('{}')
    with pytest.raises(RuntimeError,match='matching physical domain'):
        pilot.read_derivative(producer,13,'midpoint')
