"""Local native-observation API, actual asynchronous fitting/export and guards."""
import base64
from hashlib import sha256
from io import BytesIO
import json
import threading
import time
import zipfile
from urllib.error import HTTPError

import numpy as np
import pytest

from test_local_app import service, request


def native_injection():
    # Independent image-summed PSPL equation, not an implementation predictor.
    times=np.r_[np.linspace(1000,1150,45),np.linspace(1300,1450,75),np.linspace(1650,1900,60)]
    u2=.28**2+((times-1375)/72)**2
    amplification=(u2+2)/np.sqrt(u2*(u2+4))
    magnitudes=18-2.5*np.log10(1+.65*(amplification-1))
    return ('\n'.join(f'{t:.9f} {m:.12f} .008' for t,m in zip(times,magnitudes))+'\n').encode('ascii')


def upload(service, content=None):
    content=content or native_injection()
    _,body,_=request(service,'/api/photometry/import',{'format':'ogle3',
        'files':[{'name':'SYNTHETIC_native.dat','content_base64':base64.b64encode(content).decode()}],
        'metadata':{'synthetic':True,'event_id':'SYNTHETIC-API-REGRESSION'}})
    return json.loads(body)


def finished(service,job):
    deadline=time.monotonic()+25
    while time.monotonic()<deadline:
        _,body,_=request(service,'/api/jobs/'+job);output=json.loads(body)
        if output['status'] not in ('pending','running'):return output
        time.sleep(.02)
    pytest.fail('native photometry job did not finish within bounded test deadline')


def test_native_app_complete_job_export_and_replay(service,tmp_path):
    for path in ['/photometry','/photometry/','/photometry.js']:
        status,body,headers=request(service,path)
        assert status==200 and len(body)>100
    _,body,_=request(service,'/')
    assert b'href="/photometry"' in body
    _,body,_=request(service,'/api/health');health=json.loads(body)
    assert health['dataset_file_limit_bytes']==8_000_000
    assert health['photometry_dataset_file_limit_bytes']==32_000_000
    assert health['request_limit_bytes']==40_000_000
    imported=upload(service);dataset=imported['dataset']
    assert imported['summary']['rows']==180
    assert dataset['sources'][0]['sha256']==sha256(native_injection()).hexdigest()
    assert dataset['instruments']['OGLE-III']['time']['clock_scale']=='UNSPECIFIED'
    _,body,_=request(service,'/api/photometry/validate',{'dataset':dataset})
    assert json.loads(body)['summary']['sha256']==imported['summary']['sha256']
    status,body,_=request(service,'/api/photometry/fit',{'dataset':dataset,'options':{'starts':3,'max_nfev':500}})
    assert status==202
    output=finished(service,json.loads(body)['job_id']);assert output['status']=='complete',output
    result=output['result']
    assert result['parameters']['tE_days']==pytest.approx(72.,rel=1e-5)
    assert result['point_count']==180 and result['excluded_point_count']==0
    assert result['mass_status']=='MASS_UNRESOLVED'
    assert result['unresolved_quantities']['mass_msun'] is None
    assert result['unresolved_quantities']['resolved_image_positions'] is None
    assert result['row_ids']==[row['source_row_id'] for row in dataset['rows']]
    assert result['dataset_input']==dataset
    assert {'numerical_convergence','observational_adequacy','physical_admission','uncertainty'}<=result.keys()
    _,body,_=request(service,'/api/report',{'result':result})
    html=json.loads(body)['html']
    assert 'BHSM' in html and 'MASS_UNRESOLVED' in html and '180' in html
    _,body,headers=request(service,'/api/export',{'result':result})
    assert headers['Content-Type']=='application/zip'
    with zipfile.ZipFile(BytesIO(body)) as archive:
        assert json.loads(archive.read('dataset.json'))==dataset
        assert len(archive.read('native_observations.csv').splitlines())==181
        assert {'predictions.csv','report.html','manifest.json'}<=set(archive.namelist())
    bundle=tmp_path/'native.zip';bundle.write_bytes(body)
    from bhtracker.report import replay_analysis
    replay=replay_analysis(bundle,tmp_path/'replay')
    assert replay['passed'] and replay['same_native_row_identities_and_order']
    assert replay['maximum_prediction_difference_in_supplied_sigma']<.001


def test_native_annotation_and_benchmark_time_origin_preserved(service):
    content=b'3 18 .1\nERROR: data not sorted in HJD!\n1 19 .2\n1 20 .3\n'
    response=upload(service,content)
    assert [r['native_time'] for r in response['dataset']['rows']]==[3,1,1]
    assert [r['source_line'] for r in response['dataset']['rows']]==[1,3,4]
    assert response['dataset']['sources'][0]['annotations'][0]['line']==2
    status,body,_=request(service,'/api/photometry/import',{'format':'benchmark','files':[
        {'name':'OGLE.dat','instrument':'OGLE','content_base64':base64.b64encode(b'hjd mag mag_err\n2451234 18 .1\n').decode()},
        {'name':'MOA.dat','instrument':'MOA','content_base64':base64.b64encode(b'hjd mag mag_err\n2451235 19 .2\n').decode()}]})
    assert status==200
    dataset=json.loads(body)['dataset']
    assert [r['native_time'] for r in dataset['rows']]==[2451234,2451235]
    assert dataset['instruments']['MOA']['time']['numeric_origin_jd']==0
    assert dataset['metadata']['relative_time_combination_assumption']


@pytest.mark.parametrize('mutation',[
    {'format':'ogle3','files':[{'name':'broken.dat','content_base64':'%%%'}]},
    {'format':'ogle3','files':[{'name':'broken.dat','content_base64':base64.b64encode(b'1 bright .1').decode()}]},
    {'format':'benchmark','files':[{'name':'a','instrument':'HST','content_base64':'MQ=='}]},
])
def test_native_upload_errors_are_actionable(service,mutation):
    with pytest.raises(HTTPError) as error:request(service,'/api/photometry/import',mutation)
    assert error.value.code==400
    assert json.loads(error.value.read())['error']


def test_native_job_guard_and_invalid_options(service,monkeypatch):
    import bhtracker.photometry as module
    dataset=upload(service)['dataset']
    with pytest.raises(HTTPError) as error:
        request(service,'/api/photometry/fit',{'dataset':dataset,'options':{'starts':True}})
    assert error.value.code==400
    with pytest.raises(HTTPError) as error:
        request(service,'/api/photometry/validate',{'dataset_json':'{"schema":1,"schema":2}'})
    assert 'duplicate field' in json.loads(error.value.read())['error']
    with pytest.raises(HTTPError) as error:
        request(service,'/api/photometry/validate',{'dataset':[]})
    assert error.value.code==400
    release=threading.Event();entered=threading.Event();original=module.fit_photometry
    def slow(*args,**kwargs):
        entered.set();assert release.wait(5)
        return original(*args,**kwargs)
    monkeypatch.setattr(module,'fit_photometry',slow)
    body={'dataset':dataset,'options':{'starts':2,'max_nfev':500}}
    try:
        _,first,_=request(service,'/api/photometry/fit',body)
        assert entered.wait(3)
        _,second,_=request(service,'/api/photometry/fit',body)
        a,b=json.loads(first),json.loads(second)
        assert b['job_id']==a['job_id'] and b['duplicate_prevented']
    finally:release.set()
    assert finished(service,a['job_id'])['status']=='complete'
