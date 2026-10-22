"""The exported analysis must replay without access to its original input path."""
from io import BytesIO
import json
import zipfile
import numpy as np
import pytest
from bhtracker import fit,load_dataset
from bhtracker.examples import make_example
from bhtracker.report import export_analysis_bundle,replay_analysis

def test_complete_export_replay_and_tamper_detection(tmp_path):
    raw,_=make_example('nearby_motion')
    raw['analysis']['external_calibration_note']='supplied frame and parallax calibration retained'
    result=fit(raw,starts=1)
    bundle=export_analysis_bundle(result)
    source=tmp_path/'analysis with spaces.zip';source.write_bytes(bundle)
    with zipfile.ZipFile(BytesIO(bundle)) as archive:
        saved=json.loads(archive.read('dataset.json'))
        assert saved==load_dataset(raw).raw
        assert json.loads(archive.read('analysis_config.json'))==result['analysis_configuration']
        assert json.loads(archive.read('result.json'))['bhsm_interpretation']==result['bhsm_interpretation']
        for name in ('measurements_and_model.png','track_and_residuals.png','report.html','REPRODUCE.md','software_provenance.json'):
            assert len(archive.read(name))>100
        files={name:archive.read(name) for name in archive.namelist()}
    destination=tmp_path/'replayed'
    check=replay_analysis(source,destination)
    assert check['passed'] and check['same_status'] and check['same_package_content']
    assert check['same_interpretation'] and check['original_interpretation_schema_version']==check['current_interpretation_schema_version']==2
    replay=json.loads((destination/'result.json').read_text())
    np.testing.assert_allclose(replay['predictions'],result['predictions'],rtol=2e-11,atol=1e-12)
    assert replay['bhsm_interpretation']==result['bhsm_interpretation']
    files['dataset.json']=files['dataset.json'].replace(b'2026',b'2027',1)
    with zipfile.ZipFile(source,'w') as archive:
        for name,blob in files.items():archive.writestr(name,blob)
    with pytest.raises(ValueError,match='hash mismatch for dataset.json'):replay_analysis(source,tmp_path/'tampered')

@pytest.mark.parametrize('field,value,match',[
    ('geometry',None,'geometry must be an object'),('analysis',[], 'analysis must be an object'),
    ('provenance',[], 'provenance must be an object')])
def test_nested_input_errors_are_useful(field,value,match):
    raw,_=make_example('nearby_motion');raw[field]=value
    with pytest.raises(ValueError,match=match):load_dataset(raw)

def test_bad_cells_and_duplicate_json_are_identified(tmp_path):
    raw,_=make_example('nearby_motion');raw['observations'][1][2]='not-a-measurement'
    with pytest.raises(ValueError,match='observations row 2, column 3'):load_dataset(raw)
    path=tmp_path/'duplicate.json';path.write_text('{"schema_version":1,"schema_version":1}')
    with pytest.raises(ValueError,match='duplicate field'):load_dataset(path)
