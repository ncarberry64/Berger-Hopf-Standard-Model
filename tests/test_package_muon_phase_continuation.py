import importlib.util
import json
from hashlib import sha256
from pathlib import Path
import numpy as np
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def test_stage_package_preserves_every_array_and_replays_identically(tmp_path):
    source=tmp_path/'source';source.mkdir()
    arrays=dict(stage_indices=np.array([0,1]),initial_raw=np.arange(7.),
        stage_unknowns=np.arange(14.).reshape(2,7),stage_jacobian=np.arange(98.).reshape(2,7,7),
        stage_0000_iteration_right_vectors=np.arange(49.).reshape(1,7,7),
        stage_0001_iteration_left_source_projections=np.array([[1.,2.,3.]]))
    _compressed_npz(source/'application.npz',arrays)
    r=dict(numerical_sha256=sha256((source/'application.npz').read_bytes()).hexdigest(),steps=2)
    (source/'result.json').write_text(json.dumps(r),encoding='utf8')
    script=Path(__file__).parents[1]/'scripts/package_muon_phase_continuation.py'
    spec=importlib.util.spec_from_file_location('phase_packager',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    results=[m.package_phase_application(source,tmp_path/name) for name in ('first','second')]
    assert results[0]==results[1]
    for f in (tmp_path/'first').iterdir():assert f.read_bytes()==(tmp_path/'second'/f.name).read_bytes()
    receipt=json.loads((tmp_path/'first/result.json').read_bytes())
    assert receipt['array_count']==len(arrays)
    assert receipt['all_arrays_bit_identical']
