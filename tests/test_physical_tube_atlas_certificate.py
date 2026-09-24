"""The physical atlas must cover every closed cell, not selected samples."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
from flint import ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from package_n12_gate7_physical_tube_atlas import validate_cells


def operands():
    package=ROOT/'artifacts/flagship_integration/gate7_physical_tube_20260924/interval_013'
    read=lambda p:json.loads(p.read_bytes())
    chunks=[read(package/f'interval13_cubic8_cells{i}_{i+1}_first.json') for i in range(0,8,2)]
    aug=read(package/'interval13_augmented_first.json')
    frozen=read(ROOT/'artifacts/flagship_integration/gate7_shared_eigenbranch_links_20260923/certificate.json')
    return chunks,aug,frozen


def test_reproduced_closed_atlas_and_augmented_domain():
    ctx.prec=512
    chunks,aug,frozen=operands()
    cells=validate_cells(chunks,aug,frozen)
    assert len(cells)==8
    assert cells[3]['tau_exact'][1]==cells[4]['tau_exact'][0]=='1/2'


@pytest.mark.parametrize('failure',('gap','duplicate','radius','inverse','norm'))
def test_atlas_rejects_missing_domain_or_missing_authority(failure):
    ctx.prec=512
    chunks,aug,frozen=deepcopy(operands())
    if failure=='gap':chunks.pop()
    elif failure=='duplicate':chunks[0]['evaluated_cells'][1]=chunks[0]['evaluated_cells'][0]
    elif failure=='radius':chunks[0]['radius_exact'][0]='0'
    elif failure=='inverse':chunks[0]['evaluated_cells'][0]['q']['exact']='2'
    else:aug['cells'][0]['physical_norm_lower_exact']='0'
    with pytest.raises(ValueError):validate_cells(chunks,aug,frozen)
