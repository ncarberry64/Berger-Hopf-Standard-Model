"""Loopback-only app. Measurements stay in memory; no remote service used."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json
import hashlib
import threading
import uuid
import webbrowser
from .data import load_dataset,read_json
from .examples import example_names,make_example
from .inference import fit,profile
from .report import report_html,export_analysis_bundle
from .provenance import VERSION

WEB=Path(__file__).resolve().parent/'web'

def make_server(port=8765):
    pool=ThreadPoolExecutor(max_workers=1)
    jobs={};fingerprints={};lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send_json(self,value,status=200):
            blob=json.dumps(value,allow_nan=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(blob)));self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(blob)
        def send_zip(self,blob,filename):
            self.send_response(200);self.send_header('Content-Type','application/zip')
            self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
            self.send_header('Content-Length',str(len(blob)));self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(blob)
        def local_request(self):
            hosts={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
            if self.headers.get('Host') not in hosts:return False
            origin=self.headers.get('Origin')
            return origin is None or origin in {f'http://{h}' for h in hosts}
        def do_GET(self):
            if not self.local_request():self.send_json({'error':'Local origin required'},403);return
            if self.path=='/api/health':self.send_json({'status':'ready','product':'BHSM Blackhole Tracker','version':VERSION,'dataset_file_limit_bytes':8_000_000,'request_limit_bytes':40_000_000});return
            if self.path=='/api/examples':self.send_json(example_names());return
            if self.path.startswith('/api/examples/'):
                try:
                    if self.path.endswith('/bundle'):
                        from .sample_bundle import build_sample_bundle
                        name=self.path.split('/')[-2]
                        self.send_zip(build_sample_bundle(make_example(name)[0]),'Blackhole_Tracker_'+name+'_example.zip')
                    else:self.send_json(make_example(self.path.rsplit('/',1)[1])[0])
                except ValueError as error:self.send_json({'error':str(error)},404)
                return
            if self.path.startswith('/api/jobs/'):
                name=self.path.rsplit('/',1)[1]
                with lock:item=jobs.get(name)
                self.send_json(item or {'error':'Unknown job'},200 if item else 404);return
            path={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css'}.get(self.path)
            if not path:self.send_json({'error':'Not found'},404);return
            blob=(WEB/path).read_bytes();self.send_response(200)
            self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'text/javascript','css':'text/css'}[path.rsplit('.',1)[1]])
            self.send_header('Content-Length',str(len(blob)));self.send_header('Cache-Control','no-store')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
            self.end_headers();self.wfile.write(blob)
        def do_POST(self):
            if not self.local_request():self.send_json({'error':'Local origin required'},403);return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=40_000_000:raise ValueError('Request must contain at most 40 MB of JSON (dataset files: 8 MB)')
                data=read_json(self.rfile.read(size))
                if not isinstance(data,dict):raise ValueError('request body must be a JSON object')
                if self.path=='/api/validate':
                    raw=read_json(data['dataset_json']) if 'dataset_json' in data else data['dataset']
                    dataset=load_dataset(raw);self.send_json({'valid':True,'summary':dataset.summary()});return
                if self.path=='/api/report':self.send_json({'html':report_html(data['result'])});return
                if self.path=='/api/export':
                    self.send_zip(export_analysis_bundle(data['result']),'Blackhole_Tracker_analysis.zip');return
                if self.path=='/api/fit':
                    dataset=load_dataset(data['dataset'])
                    key=hashlib.sha256(json.dumps([dataset.sha256,data.get('family','gr'),data.get('nuisance','shear'),data.get('starts',2)],sort_keys=True).encode()).hexdigest()
                    with lock:
                        prior=fingerprints.get(key)
                        if prior and jobs[prior]['status'] in ('pending','running'):
                            self.send_json({'job_id':prior,'duplicate_prevented':True},202);return
                        if len(jobs)>=64:raise ValueError('Session limit reached; restart the local app to clear in-memory results')
                        name=uuid.uuid4().hex;jobs[name]={'status':'pending'};fingerprints[key]=name
                    def work():
                        with lock:jobs[name]={'status':'running'}
                        try:
                            result=fit(dataset,family=data.get('family','gr'),nuisance=data.get('nuisance','shear'),starts=data.get('starts',2))
                            item={'status':'complete','result':result}
                        except Exception as error:item={'status':'failed','error':str(error)}
                        with lock:jobs[name]=item
                    pool.submit(work);self.send_json({'job_id':name},202);return
                self.send_json({'error':'Not found'},404)
            except (ValueError,KeyError,TypeError) as error:self.send_json({'error':str(error)},400)
    try:server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    except OSError as error:
        pool.shutdown(wait=False)
        raise OSError(f'Cannot open local port {port}: {error}. Close the other app or choose another port, for example --port 8766') from error
    server.executor=pool
    return server

def serve(port=8765,open_browser=False):
    server=make_server(port)
    url=f'http://127.0.0.1:{server.server_port}/'
    print('Blackhole Tracker ready at '+url,flush=True)
    print('Local-only research app. Ctrl+C stops the server; inputs/results stay in this process.',flush=True)
    if open_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();server.executor.shutdown(wait=False,cancel_futures=True)
