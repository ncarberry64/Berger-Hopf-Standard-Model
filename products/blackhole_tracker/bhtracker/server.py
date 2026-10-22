"""Loopback-only app. Measurements stay in memory; no remote service used."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json
import hashlib
import threading
import uuid
import webbrowser
import base64
from .data import load_dataset,read_json
from .examples import example_names,make_example
from .inference import fit,profile
from .report import report_html,export_analysis_bundle
from .provenance import VERSION, project_citation

WEB=Path(__file__).resolve().parent/'web'
PHOTOMETRY_DATASET_LIMIT=32_000_000

def photometry_dataset(raw):
    from .observations import UnresolvedPhotometry
    if not isinstance(raw,dict):raise ValueError('unresolved dataset must be a versioned JSON object')
    if not isinstance(raw.get('rows'),list) or any(not isinstance(row,dict) for row in raw['rows']):
        raise ValueError('unresolved rows must be an array of measurement objects')
    instruments=raw.get('instruments')
    if not isinstance(instruments,dict) or any(not isinstance(item,dict) or not isinstance(item.get('time'),dict) for item in instruments.values()):
        raise ValueError('instruments require calibration objects and explicit time metadata')
    if not isinstance(raw.get('metadata',{}),dict):raise ValueError('dataset metadata must be a JSON object')
    if len(json.dumps(raw,allow_nan=False).encode())>PHOTOMETRY_DATASET_LIMIT:
        raise ValueError('Unresolved dataset JSON must contain at most 32 MB')
    return UnresolvedPhotometry.from_dict(raw)

def photometry_summary(dataset):
    return {'rows':len(dataset.rows),'sha256':dataset.sha256,'schema':dataset.document['schema'],
            'instruments':dataset.document['instruments'],'sources':dataset.document.get('sources',[]),
            'metadata':dataset.document.get('metadata',{}),'common_numeric_origin_jd':dataset.common_origin_jd,
            'transformations':dataset.document.get('transformations',[]),
            'noise':'published magnitude errors retained; diagonal independence is an explicit likelihood assumption',
            'unavailable':['mass','distance','absolute proper motion','theta_E','pi_E','horizon','core state']}

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
        def submit_job(self,key,operation):
            with lock:
                prior=fingerprints.get(key)
                if prior and jobs[prior]['status'] in ('pending','running'):
                    self.send_json({'job_id':prior,'duplicate_prevented':True},202);return
                if len(jobs)>=64:raise ValueError('Session limit reached; restart the local app to clear in-memory results')
                name=uuid.uuid4().hex;jobs[name]={'status':'pending'};fingerprints[key]=name
            def work():
                with lock:jobs[name]={'status':'running'}
                try:item={'status':'complete','result':operation()}
                except Exception as error:item={'status':'failed','error':str(error)}
                with lock:jobs[name]=item
            pool.submit(work);self.send_json({'job_id':name},202)
        def do_GET(self):
            if not self.local_request():self.send_json({'error':'Local origin required'},403);return
            if self.path=='/api/health':self.send_json({'status':'ready','product':'BHSM Blackhole Tracker','version':VERSION,'project_citation':project_citation(),'dataset_file_limit_bytes':8_000_000,'photometry_dataset_file_limit_bytes':PHOTOMETRY_DATASET_LIMIT,'request_limit_bytes':40_000_000});return
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
            path={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css',
                  '/photometry':'photometry.html','/photometry/':'photometry.html','/photometry.js':'photometry.js'}.get(self.path)
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
                if not 0<size<=40_000_000:raise ValueError('Request must contain at most 40 MB of JSON (resolved dataset files: 8 MB; unresolved JSON: 32 MB)')
                data=read_json(self.rfile.read(size))
                if not isinstance(data,dict):raise ValueError('request body must be a JSON object')
                if self.path=='/api/validate':
                    raw=read_json(data['dataset_json']) if 'dataset_json' in data else data['dataset']
                    dataset=load_dataset(raw);self.send_json({'valid':True,'summary':dataset.summary()});return
                if self.path=='/api/report':self.send_json({'html':report_html(data['result'])});return
                if self.path=='/api/export':
                    self.send_zip(export_analysis_bundle(data['result']),'Blackhole_Tracker_analysis.zip');return
                if self.path=='/api/photometry/import':
                    from .observations import parse_ogle_photometry,parse_benchmark_photometry
                    files=data['files'];metadata=data.get('metadata',{})
                    if not isinstance(metadata,dict):raise ValueError('metadata must be a JSON object')
                    if not isinstance(files,list) or not 1<=len(files)<=2:raise ValueError('provide one OGLE-III file or one/two distinct benchmark instrument files')
                    decoded=[]
                    for item in files:
                        if not isinstance(item,dict) or not isinstance(item.get('name'),str) or not isinstance(item.get('content_base64'),str):
                            raise ValueError('each native file requires its name and content_base64 bytes')
                        decoded.append((item,base64.b64decode(item['content_base64'],validate=True)))
                    if sum(len(content) for _,content in decoded)>24_000_000:raise ValueError('native files must total at most 24 MB before base64 encoding')
                    if data.get('format')=='ogle3':
                        if len(decoded)!=1:raise ValueError('OGLE-III import requires exactly one optimized light-curve file')
                        item,content=decoded[0]
                        dataset=parse_ogle_photometry(content,source_name=item['name'],metadata=metadata)
                    elif data.get('format')=='benchmark':
                        inputs={}
                        for item,content in decoded:
                            instrument=item.get('instrument')
                            if instrument not in ('OGLE','MOA') or instrument in inputs:raise ValueError('benchmark files require distinct OGLE or MOA instruments')
                            inputs[instrument]={'content':content,'source_name':item['name']}
                        dataset=parse_benchmark_photometry(inputs,metadata=metadata)
                    else:raise ValueError('native format must be ogle3 or benchmark; other formats require versioned calibrated JSON')
                    dataset=photometry_dataset(dataset.to_dict())
                    self.send_json({'valid':True,'dataset':dataset.to_dict(),'summary':photometry_summary(dataset)});return
                if self.path=='/api/photometry/validate':
                    raw=read_json(data['dataset_json']) if 'dataset_json' in data else data['dataset']
                    dataset=photometry_dataset(raw);self.send_json({'valid':True,'summary':photometry_summary(dataset)});return
                if self.path=='/api/photometry/fit':
                    from .photometry import fit_photometry
                    dataset=photometry_dataset(data['dataset']);options=data.get('options',{})
                    if not isinstance(options,dict) or set(options)-{'starts','max_nfev','noise_scale','equal_instrument_weight','allow_negative_blend'}:
                        raise ValueError('unsupported photometry options')
                    starts=options.get('starts',12);maximum=options.get('max_nfev',1500)
                    if isinstance(starts,bool) or not isinstance(starts,int) or not 1<=starts<=12:raise ValueError('photometry starts must be an integer from 1 to 12')
                    if isinstance(maximum,bool) or not isinstance(maximum,int) or not 1<=maximum<=1500:raise ValueError('photometry max_nfev must be an integer from 1 to 1500')
                    for key in ['equal_instrument_weight','allow_negative_blend']:
                        if key in options and not isinstance(options[key],bool):raise ValueError(key+' must be true or false')
                    if 'noise_scale' in options and (isinstance(options['noise_scale'],bool) or not isinstance(options['noise_scale'],(int,float)) or not .1<=options['noise_scale']<=10):
                        raise ValueError('noise_scale must be a finite value from 0.1 to 10')
                    options={'starts':starts,'max_nfev':maximum,**options}
                    key=hashlib.sha256(json.dumps(['unresolved_photometry_v1',dataset.sha256,options],sort_keys=True).encode()).hexdigest()
                    self.submit_job(key,lambda:fit_photometry(dataset,**options));return
                if self.path=='/api/fit':
                    dataset=load_dataset(data['dataset'])
                    key=hashlib.sha256(json.dumps([dataset.sha256,data.get('family','gr'),data.get('nuisance','shear'),data.get('starts',2)],sort_keys=True).encode()).hexdigest()
                    self.submit_job(key,lambda:fit(dataset,family=data.get('family','gr'),nuisance=data.get('nuisance','shear'),starts=data.get('starts',2)));return
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
