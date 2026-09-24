import gzip
import importlib.util
from pathlib import Path
from flint import arb,arb_mat,ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor


def test_streamed_input_archive_is_complete_canonical_and_deterministic(tmp_path):
    path=Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_full_input_output.py'
    spec=importlib.util.spec_from_file_location('full_input_output_archive',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    ctx.prec=256
    domain=TaylorDomain([(0,2,'euclidean')],2)
    models=[InputLinearTaylor(domain,arb_mat([[arb(1, '1e-20'),arb(2)]]),arb_mat([[3,4],[5,6]]),arb('1e-12')),
            InputLinearTaylor(domain,arb_mat([[0,0]]),arb_mat(2,2))]
    a,b=tmp_path/'a.gz',tmp_path/'b.gz'
    assert module.write_models_archive(a,models)==module.write_models_archive(b,models)
    assert a.read_bytes()==b.read_bytes()
    assert gzip.decompress(a.read_bytes())==module.saved.encoded([module.encode(v) for v in models])

import pytest


@pytest.fixture(autouse=True)
def restore_arb_precision():
    previous = ctx.prec
    try:
        yield
    finally:
        ctx.prec = previous
