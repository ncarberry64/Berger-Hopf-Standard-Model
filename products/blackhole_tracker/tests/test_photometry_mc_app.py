"""Loopback/CLI engineering on invented records; all analysis is explicitly mocked."""
from contextlib import contextmanager,redirect_stdout
from io import BytesIO,StringIO
import base64,json,os
from pathlib import Path
import tempfile,threading,time,unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request,urlopen
import zipfile
import http.client,hashlib

from bhtracker import photometry_mc as mc
from bhtracker.cli import main
from bhtracker.server import make_server
from test_photometry_mc_workflow import data_fixture,mocked_mc


def request(server,path,body=None,origin=None):
    headers={}
    if origin is not None:headers['Origin']=origin
    data=None if body is None else json.dumps(body,allow_nan=False).encode()
    if data is not None:headers['Content-Type']='application/json'
    req=Request(f'http://127.0.0.1:{server.server_port}'+path,data=data,headers=headers)
    with urlopen(req,timeout=10) as response:return response.status,response.read(),response.headers


@contextmanager
def service():
    server=make_server(0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield server
    finally:
        server.mc_jobs.shutdown();server.shutdown();server.server_close();server.executor.shutdown(wait=True,cancel_futures=True);thread.join(5)


def input_body():
    data,_=data_fixture(1.,True)
    original=(json.dumps(data.to_dict(),ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode()
    return {'input_base64':base64.b64encode(original).decode(),'grids':{'tE_days':[25.]},'entropy':[8675309]},original


def inline_mocked_supervisor(workspace):
    result=workspace._execute();mc.save(workspace.directory/'result.json',result)
    workspace._progress(status=result['status'],stage='TERMINAL_AUDIT_RETAINED')
    return result


class MCAppControls(unittest.TestCase):
    def setUp(self):
        base=os.environ.get('BHSM_MC_APP_TEST_ARTIFACT_DIR')
        if base:self.root=Path(tempfile.mkdtemp(prefix=self._testMethodName+'_',dir=base))
        else:
            self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)

    def test_01_static_route_nav_and_local_origin(self):
        with service() as server:
            for path in ('/photometry-mc','/photometry-mc/','/photometry-mc.js','/photometry-mc.css'):
                status,blob,_=request(server,path);self.assertEqual(status,200);self.assertGreater(len(blob),100)
            _,blob,_=request(server,'/photometry');self.assertIn(b'/photometry-mc',blob)
            with self.assertRaises(HTTPError) as error:request(server,'/api/photometry-mc/plan',input_body()[0],origin='https://external.invalid')
            self.assertEqual(error.exception.code,403)

    def test_02_plan_preserves_originalbytes_and_never_starts_analysis(self):
        body,original=input_body()
        with service() as server,patch.object(mc,'monte_carlo_ordinate',side_effect=AssertionError('plan cannot analyze')):
            _,blob,_=request(server,'/api/photometry-mc/plan',body);value=json.loads(blob)
        self.assertEqual(value['summary']['input_utf8_sha256'],mc.digest(original))
        self.assertEqual(value['request']['nodes'][0]['value'],25.)
        self.assertEqual(value['request']['method'],mc.METHOD)

    def test_03_async_mocked_job_export_and_fullnumerical_replay(self):
        body,original=input_body()
        with service() as server,patch.object(mc.MCWorkspace,'run',inline_mocked_supervisor),patch.object(mc,'monte_carlo_ordinate',side_effect=mocked_mc):
            status,blob,_=request(server,'/api/photometry-mc/start',body);self.assertEqual(status,202);identity=json.loads(blob)['job_id']
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                _,blob,_=request(server,'/api/photometry-mc/jobs/'+identity);value=json.loads(blob)
                if value['status'] in ('complete','failed','cancelled'):break
                time.sleep(.02)
            self.assertEqual(value['status'],'complete',value)
            self.assertEqual(len(value['summary']['nodes']),1);self.assertEqual(value['summary']['nodes'][0]['decision'],'UNRESOLVED')
            self.assertTrue(value['workspace_path'])
            _,bundle,headers=request(server,'/api/photometry-mc/jobs/'+identity+'/export',{})
            self.assertEqual(headers['Content-Type'],'application/zip')
            with zipfile.ZipFile(BytesIO(bundle)) as archive:self.assertEqual(archive.read('input.original.utf8.json'),original)
            _,blob,_=request(server,'/api/photometry-mc/replay',{'bundle_base64':base64.b64encode(bundle).decode(),'mode':'numerical'})
            verification=json.loads(blob)
            self.assertEqual(verification['verification']['mode'],'NUMERICAL_SAVED_STATE_REPLAY')
            self.assertGreater(verification['verification']['exact_vector_states_evaluated'],0)
            self.assertEqual(verification['evidence_scope']['validation_status'],'PENDING')

    def test_04_queued_duplicate_and_cancel_keep_every_unknown(self):
        body,_=input_body();release=threading.Event();entered=threading.Event()
        with service() as server:
            blocker=server.executor.submit(lambda:(entered.set(),release.wait(5)))
            self.assertTrue(entered.wait(2))
            try:
                _,first,_=request(server,'/api/photometry-mc/start',body);a=json.loads(first)
                _,second,_=request(server,'/api/photometry-mc/start',body);b=json.loads(second)
                self.assertEqual(a['job_id'],b['job_id']);self.assertTrue(b['duplicate_prevented'])
                _,blob,_=request(server,'/api/photometry-mc/jobs/'+a['job_id']+'/cancel',{});value=json.loads(blob)
                self.assertEqual(value['status'],'cancelled');self.assertEqual(value['summary']['nodes'][0]['decision'],'UNRESOLVED')
                self.assertEqual(value['summary']['nodes'][0]['unknown'],199)
            finally:release.set();blocker.result(timeout=5)

    def test_05_bad_options_and_archive_are_actionable(self):
        body,_=input_body()
        with service() as server:
            for mutation in ({**body,'slots':5},{**body,'entropy':[True]},{**body,'grids':{'mass_msun':[7.]}}):
                with self.assertRaises(HTTPError) as error:request(server,'/api/photometry-mc/plan',mutation)
                self.assertEqual(error.exception.code,400);self.assertTrue(json.loads(error.exception.read())['error'])
            with self.assertRaises(HTTPError) as error:request(server,'/api/photometry-mc/replay',{'bundle_base64':base64.b64encode(b'badzip').decode(),'mode':'numerical'})
            self.assertEqual(error.exception.code,400)

    def test_06_cli_export_replay_and_fresh_output_guard(self):
        body,original=input_body();source=self.root/'original.json';source.write_bytes(original);workspace=self.root/'audit'
        with patch.object(mc.MCWorkspace,'run',inline_mocked_supervisor),patch.object(mc,'monte_carlo_ordinate',side_effect=mocked_mc),redirect_stdout(StringIO()):
            main(['mc-photometry','run',str(source),'--timescales','25','--entropy','8675309','--output',str(workspace)])
        bundle=self.root/'portable.zip';check=self.root/'numerical.json'
        with redirect_stdout(StringIO()):
            main(['mc-photometry','export',str(workspace),'--output',str(bundle),'--max-archive-bytes','536870912'])
            main(['mc-photometry','replay',str(bundle),'--mode','numerical','--output',str(check)])
        value=json.loads(check.read_bytes());self.assertTrue(value['verification']['passed'])
        before=check.read_bytes()
        with redirect_stdout(StringIO()),self.assertRaises(SystemExit):main(['mc-photometry','replay',str(bundle),'--mode','integrity','--output',str(check)])
        self.assertEqual(check.read_bytes(),before)

    def test_07_binary_replay_above_legacy40MB_preserves_bytes_without_base64(self):
        # Transfer engineering only: replay is mocked, no ZIP/model/native analysis.
        size=40_000_123;block=b'INVENTED_LARGE_TRANSFER\x00\r\n'*4096
        expected=hashlib.sha256();remaining=size;seen={}
        def checking(path,*,mode):
            self.assertIsInstance(path,Path);self.assertEqual(mode,'integrity')
            seen.update(mc.file_pin(path));seen['owned_path']=str(path)
            return {'verification':{'passed':True,'mode':'INTEGRITY_ONLY','requested_mode':mode},'summary':{'nodes':[]},'engineering_mock':True}
        with service() as server,patch('bhtracker.photometry_mc_replay.replay_bundle',side_effect=checking):
            connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=30)
            connection.putrequest('POST','/api/photometry-mc/replay-file?mode=integrity')
            connection.putheader('Content-Type','application/zip');connection.putheader('Content-Length',str(size));connection.endheaders()
            while remaining:
                value=block[:min(len(block),remaining)];expected.update(value);connection.send(value);remaining-=len(value)
            response=connection.getresponse();payload=response.read();self.assertEqual(response.status,200,payload);value=json.loads(payload);connection.close()
        self.assertEqual(seen['bytes'],size);self.assertEqual(seen['sha256'],expected.hexdigest())
        self.assertFalse(Path(seen['owned_path']).exists());self.assertTrue(value['engineering_mock'])
        mc.save(self.root/'LARGE_STREAM_TRANSFER_CHECK.json',{'bytes':size,'sha256':expected.hexdigest(),'base64_used':False,'analysis_mocked':True,'passed':True})

    def test_08_terminal_result_waits_for_worker_exit_before_export(self):
        body,original=input_body();entered=threading.Event();release=threading.Event()
        def held_supervisor(workspace):
            result=inline_mocked_supervisor(workspace);entered.set()
            if not release.wait(10):raise TimeoutError('Invented supervisor release was not received')
            return result
        with service() as server,patch.object(mc.MCWorkspace,'run',held_supervisor),patch.object(mc,'monte_carlo_ordinate',side_effect=mocked_mc):
            _,blob,_=request(server,'/api/photometry-mc/start',body);identity=json.loads(blob)['job_id']
            try:
                self.assertTrue(entered.wait(10))
                _,blob,_=request(server,'/api/photometry-mc/jobs/'+identity);value=json.loads(blob)
                self.assertEqual(value['status'],'finalizing',value)
                self.assertEqual(value['recorded_result_status'],'complete');self.assertFalse(value['export_ready'])
                with self.assertRaises(HTTPError) as error:request(server,'/api/photometry-mc/jobs/'+identity+'/export',{})
                self.assertEqual(error.exception.code,400)
                self.assertIn('wait for terminal audit',json.loads(error.exception.read())['error'])
            finally:release.set()
            server.mc_jobs._job(identity)['future'].result(timeout=10)
            _,blob,_=request(server,'/api/photometry-mc/jobs/'+identity);value=json.loads(blob)
            self.assertEqual(value['status'],'complete');self.assertTrue(value['export_ready'])
            _,bundle,_=request(server,'/api/photometry-mc/jobs/'+identity+'/export',{})
            with zipfile.ZipFile(BytesIO(bundle)) as archive:self.assertEqual(archive.read('input.original.utf8.json'),original)
