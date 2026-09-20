from flint import arb,arb_mat,ctx
import importlib.util
from pathlib import Path
import io
import json
import pytest


@pytest.mark.parametrize("producer",["certify_n12_gate7_full_input_transport.py","certify_n12_gate7_coupled_vector_transport.py","certify_n12_gate7_base_cancelled_transport.py","certify_n12_gate7_pretransport_base_cancellation.py","certify_n12_gate7_refined_directional_transport.py"])
def test_signed_anchor_transport_is_same_complete_input_operator(producer):
    path=Path(__file__).resolve().parents[1]/'scripts'/producer
    spec=importlib.util.spec_from_file_location('full_input_transport',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    ctx.prec=256
    QP=arb_mat([[1,2,-1],[2,-3,1]])
    Q=arb_mat([[1,0],[0,1]])
    E=arb_mat([[1,2],[3,1],[-1,2]])
    M=arb_mat([[1,2,0],[0,1,-2],[-1,0,3]])
    A0=arb_mat([[2,1],[-3,1],[1,-2]])
    A=arb_mat([[3,-1],[2,4],[0,3]])
    U=arb_mat([[1,-1],[2,-2],[3,-3]])
    B=arb_mat([[1,3],[-2,2]])
    h=arb(3)/8
    fixed,coefficient=module.transport_coefficients(QP,Q,E,M,h,A0,U)
    grouped=fixed+B+coefficient*(A-A0)
    original=Q-QP*E+QP*A*(h/6)+B+QP*M*(E/2-A*(h/8)-U)*(2*h/3)
    assert grouped==original
    pivot=[arb(2),arb(-3),arb(4)]
    row=[arb(5),arb(7),arb(-2)]
    ratio,complement=module.eliminate_descriptor(row,pivot)
    state=[arb(3),arb(-2),arb(5)]
    projected=module.dot(pivot,state)
    assert ratio*projected+module.dot(complement,state[:-1])==module.dot(row,state)


def test_coefficient_archive_streaming_keeps_rows_across_chunk_boundaries():
    path=Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_full_input_transport.py'
    spec=importlib.util.spec_from_file_location('streamed_full_input_transport',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows=[[[str(i*j),'1/128'] for j in range(17)] for i in range(23)]
    encoded=json.dumps(rows,indent=2)
    assert list(module.json_array_rows(io.StringIO(encoded),13))==rows
    with pytest.raises(ValueError,match='trailing'):
        list(module.json_array_rows(io.StringIO(encoded+'false'),17))


@pytest.fixture(autouse=True)
def restore_arb_precision():
    previous = ctx.prec
    try:
        yield
    finally:
        ctx.prec = previous
