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


def test_candidate_atlas_bundled_assets_and_navigation(service):
    import hashlib
    for page in ('/atlas','/atlas/','/atlas.html'):
        status,body,headers=request(service,page)
        assert status==200 and b'Candidate atlas' in body and b'href="/joint"' in body
        assert headers['Content-Type'].startswith('text/html')
    for name in ('atlas.css','atlas.js','atlas-core.js','atlas_data.json','atlas_manifest.json'):
        _,raw,_=request(service,'/'+name)
        _,nested,_=request(service,'/atlas/'+name)
        assert raw==nested and len(raw)>100
    _,data,headers=request(service,'/atlas_data.json')
    _,manifest,_=request(service,'/atlas_manifest.json')
    assert headers['Content-Type'].startswith('application/json')
    assert hashlib.sha256(data).hexdigest()==json.loads(manifest)['inventory_utf8_sha256']
    from bhtracker.candidate_atlas import validate_inventory
    inventory=validate_inventory(json.loads(data))
    assert len(inventory['events'])==155 and len(inventory['benchmarks'])==1
    assert all(e['lens']['mass_msun'] is None for e in inventory['events'])
    for page in ('/','/photometry','/joint'):
        _,body,_=request(service,page)
        assert b'href="/atlas"' in body


def test_named_workspace_open_is_local_and_closes_server():
    from unittest.mock import Mock,patch
    from bhtracker.server import serve
    server=Mock(server_port=9999);server.serve_forever.side_effect=KeyboardInterrupt
    with patch('bhtracker.server.make_server',return_value=server),patch('bhtracker.server.webbrowser.open') as browser:
        serve(9999,True,'atlas')
    browser.assert_called_once_with('http://127.0.0.1:9999/atlas')
    server.server_close.assert_called_once()
    with patch('bhtracker.server.make_server') as maker,pytest.raises(ValueError):serve(9999,True,'https://example.invalid')
    maker.assert_not_called()
