"""Exact lifting identities and completeness checks for the physical vector."""
import importlib.util
import json
from pathlib import Path
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('vector_lift',ROOT/'scripts/certify_n12_gate7_projected_vector_lift.py')
lift=importlib.util.module_from_spec(spec)
spec.loader.exec_module(lift)


def test_descriptor_elimination_with_nonunit_projector():
    ctx.prec=128
    a=arb_mat([[arb(1)/2],[arb(1)/4]])
    Q=arb_mat([[1,0],[0,1]])-a*a.transpose()
    L=Q*arb_mat([[1,2,3],[4,5,6]])
    f=arb_mat([[2],[-3],[7]])
    original=L*f
    for i in range(2):
        v=L[i,2]/L[1,2]
        recovered=v*original[1,0]+sum((L[i,j]-v*L[1,j])*f[j,0] for j in range(2))
        assert recovered.contains(original[i,0])
    assert not (a.transpose()*a)[0,0].contains(1)


def test_exact_ball_roundtrip_does_not_drop_radius():
    ctx.prec=512
    for rad in ['639795933/'+str(2**571),'1/8','0']:
        value=lift.restore(['3/4',rad])
        assert str(value.mid().fmpq())=='3/4'
        assert value.rad().fmpq()==arb(rad).fmpq()


def test_materialized_vector_has_all_rows_and_shared_parameters():
    ctx.prec=512
    record=json.loads((ROOT/'artifacts/gate7/GATE7_PROJECTED_VECTOR_CERTIFICATE_v1.json').read_bytes())
    assert len(record['components'])==len(record['shared_models'])==74
    assert record['parameters']==497
    assert [r['component'] for r in record['components']]==[f'projected_row_{i:02d}' for i in range(74)]
    assert all(len(m)==499 for m in record['shared_models'])
    radii=[arb(r['total_radius']['exact']) for r in record['components']]
    assert lift.norm(radii)<=arb(record['vector_norm']['anchor_deviation']['exact'])
    assert record['all_output_rows_retained'] is True
    assert record['complete_local_column_certified'] is False
    assert record['Gate7_closed'] is False
