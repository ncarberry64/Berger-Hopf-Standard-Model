"""Moving-lens HTTP admission, export and replay; invented measurements only."""
import json
import threading
from urllib.error import HTTPError
from urllib.request import Request,urlopen

import pytest
from bhtracker.server import make_server


@pytest.fixture
def service():
    server=make_server(0)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown();server.server_close();server.executor.shutdown(wait=True)


def request(base,path,body=None):
    raw=None if body is None else json.dumps(body).encode('utf-8')
    with urlopen(Request(base+path,data=raw,headers={'Content-Type':'application/json'}),timeout=20) as response:
        return json.loads(response.read())


def test_moving_track_http_export_and_replay(service):
    for route in ('/skytrack','/skytrack/','/skytrack.js','/skytrack.css'):
        with urlopen(service+route,timeout=10) as response:
            assert response.status==200 and len(response.read())>100
            assert "script-src 'self'" in response.headers['Content-Security-Policy']
    example=request(service,'/api/skytrack/example')['dataset_json']
    assert request(service,'/api/skytrack/validate',{'dataset_json':example})['valid']
    returned=request(service,'/api/skytrack/fit',{'dataset_json':example})
    result=json.loads(returned['result_json'])
    assert result['dataset_input_json']==example
    assert result['unavailable']['mass_msun'] is None
    assert result['unavailable']['lens_distance_pc'] is None
    assert 'surface_geometry_interpretation' in result
    replay=request(service,'/api/skytrack/replay',{'result_json':returned['result_json']})
    assert json.loads(replay['result_json'])==result
    exported=request(service,'/api/skytrack/export',{'result_json':returned['result_json']})
    assert exported==result
    assert exported['dataset_input_json']==example
    exported['diagnostics']['chi_square']+=5
    with pytest.raises(HTTPError) as error:
        request(service,'/api/skytrack/replay',{'result':exported})
    assert error.value.code==400


def test_moving_track_rejects_source_direction_and_invented_options(service):
    text=request(service,'/api/skytrack/example')['dataset_json']
    dataset=json.loads(text);dataset['position_role']='SOURCE_EVENT_DIRECTION'
    with pytest.raises(HTTPError) as error:
        request(service,'/api/skytrack/fit',{'dataset':dataset})
    assert error.value.code==400
    with pytest.raises(HTTPError) as error:
        request(service,'/api/skytrack/fit',{'dataset_json':text,'options':{'mass_msun':10}})
    assert error.value.code==400
    duplicate=text.replace('"schema":','"schema":"duplicate", "schema":',1)
    with pytest.raises(HTTPError) as error:
        request(service,'/api/skytrack/validate',{'dataset_json':duplicate})
    assert error.value.code==400
    assert b'duplicate' in error.value.read()


def test_navigation_exposes_the_measured_track_workspace(service):
    for route in ('/','/atlas','/photometry','/joint'):
        with urlopen(service+route,timeout=10) as response:
            assert b'href="/skytrack"' in response.read()
