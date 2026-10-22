import json
import threading
import time
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import pytest
from io import BytesIO
import zipfile
from bhtracker.server import make_server

@pytest.fixture
def service():
    server=make_server(0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown();server.server_close();server.executor.shutdown(wait=True)

def request(base,path,body=None,headers=None):
    data=None if body is None else json.dumps(body).encode()
    req=Request(base+path,data=data,headers={'Content-Type':'application/json',**(headers or {})})
    with urlopen(req,timeout=20) as response:return response.status,response.read(),response.headers

def test_app_full_flow(service):
    for path in ['/','/app.js','/style.css']:
        status,body,headers=request(service,path);assert status==200 and len(body)>100
    _,body,_=request(service,'/api/examples');examples=json.loads(body);assert len(examples)>=3
    _,body,_=request(service,'/api/examples/nearby_motion');dataset=json.loads(body)
    _,body,_=request(service,'/api/validate',{'dataset':dataset});assert json.loads(body)['valid']
    status,body,_=request(service,'/api/fit',{'dataset':dataset,'family':'gr','nuisance':'shear','starts':1})
    assert status==202;job=json.loads(body)['job_id']
    deadline=time.monotonic()+20
    while time.monotonic()<deadline:
        _,body,_=request(service,'/api/jobs/'+job);out=json.loads(body)
        if out['status'] not in ('pending','running'):break
        time.sleep(.02)
    assert out['status']=='complete',out
    result=out['result'];assert result['status']=='TRACKED'
    from bhtracker.interpretation import bhsm_interpretation
    assert result['bhsm_interpretation']==bhsm_interpretation('gr',result['estimates'],result['uncertainty'],result['model'],result['status'])
    _,body,_=request(service,'/api/report',{'result':result});report=json.loads(body)['html']
    assert '<html' in report and 'TRACKED' in report and 'known' in report
    assert result['data_summary']['provenance']['kind']=='synthetic'
    _,body,headers=request(service,'/api/export',{'result':result})
    assert headers['Content-Type']=='application/zip'
    with zipfile.ZipFile(BytesIO(body)) as archive:
        assert json.loads(archive.read('dataset.json'))==result['dataset_input']
        assert json.loads(archive.read('result.json'))['bhsm_interpretation']==result['bhsm_interpretation']
    _,body,headers=request(service,'/api/examples/nearby_motion/bundle')
    with zipfile.ZipFile(BytesIO(body)) as archive:
        assert {'dataset.json','measurements.csv','metadata.json','full_covariance.csv'}<=set(archive.namelist())

def test_bad_covariance_rejected(service):
    _,body,_=request(service,'/api/examples/nearby_motion');dataset=json.loads(body)
    dataset['covariance'][0][0]=0
    with pytest.raises(HTTPError) as error:request(service,'/api/validate',{'dataset':dataset})
    assert error.value.code==400
    with pytest.raises(HTTPError) as error:
        request(service,'/api/validate',{'dataset_json':'{"schema_version":1,"schema_version":1}'})
    assert 'duplicate field' in json.loads(error.value.read())['error']

def test_cross_origin_and_path_rejected(service):
    with pytest.raises(HTTPError) as error:request(service,'/api/health',headers={'Origin':'https://example.com'})
    assert error.value.code==403
    with pytest.raises(HTTPError) as error:request(service,'/../pyproject.toml')
    assert error.value.code==404
