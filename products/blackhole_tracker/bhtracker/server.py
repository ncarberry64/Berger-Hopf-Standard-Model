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
from io import BytesIO
import tempfile
import zipfile
from .data import load_dataset,read_json
from .examples import example_names,make_example
from .inference import fit,profile
from .report import report_html,export_analysis_bundle
from .provenance import VERSION, project_citation

WEB=Path(__file__).resolve().parent/'web'
PHOTOMETRY_DATASET_LIMIT=32_000_000
JOINT_SOURCEPACK_SHA256='71d36a03e4ba275e91bea62f4784a5193f34ad32d3777b637453f91151bafa99'

def import_joint_sourcepack(content):
    """Import only the reviewed source pack; never execute archived helpers."""
    if hashlib.sha256(content).hexdigest()!=JOINT_SOURCEPACK_SHA256:
        raise ValueError('Known-system source pack hash differs from the reviewed 2023 data version; use the accompanying unchanged SourcePack_v1.zip')
    from .joint_benchmark_v2 import import_2023_benchmark
    with zipfile.ZipFile(BytesIO(content)) as archive, tempfile.TemporaryDirectory(prefix='bhtracker native sources ') as temporary:
        infos=archive.infolist()
        if len(infos)>110 or sum(item.file_size for item in infos)>5_000_000:
            raise ValueError('Known-system source pack exceeds its reviewed inventory bounds')
        if len({i.filename for i in infos})!=len(infos):raise ValueError('Source pack contains duplicate filenames')
        root=Path(temporary).resolve()
        for item in infos:
            if '\\' in item.filename or ':' in item.filename:raise ValueError('Source pack contains a nonportable path')
            target=(root/item.filename).resolve()
            if not target.is_relative_to(root):raise ValueError('Source pack path is outside its temporary import directory')
            if item.is_dir():target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(archive.read(item))
        return import_2023_benchmark(root/'portable_2023_benchmark_v1')

def joint_module(version):
    if version=='v1':
        from . import joint_mass
        return joint_mass
    if version=='v2':
        from . import joint_mass_v2
        return joint_mass_v2
    raise ValueError('joint scientific_version must be explicitly v1 or v2')

def joint_dataset(raw):
    from .joint_mass_v2 import JointData
    if not isinstance(raw,dict):raise ValueError('joint dataset must be a versioned JSON object')
    if not isinstance(raw.get('metadata'),dict):raise ValueError('joint metadata must document its native clocks and reference frame')
    if 'analysis' in raw and not isinstance(raw['analysis'],dict):raise ValueError('joint analysis bounds and initial guesses must be a JSON object')
    if len(json.dumps(raw,allow_nan=False).encode())>PHOTOMETRY_DATASET_LIMIT:
        raise ValueError('Joint dataset JSON must contain at most 32 MB')
    if not all(isinstance(raw.get(key),list) and all(isinstance(row,dict) for row in raw[key]) for key in ('photometry','astrometry')):
        raise ValueError('joint photometry and astrometry must be native measurement object arrays')
    return JointData(raw)

def joint_summary(dataset):
    d=dataset.document
    analysis_ready=bool(str(d.get('data_version','')).startswith('OGLE-Mroz2022-corrected_LamLu2023v2') or d.get('analysis'))
    effective_bounds=None
    if analysis_ready:
        import math
        module=joint_module('v2' if dataset.__class__.__module__.endswith('_v2') else 'v1')
        model=module.JointModel(d)
        center=getattr(model,'time_origin_jd_tdb',2450000.)
        declared=getattr(model,'analysis_bounds',{})
        effective_bounds={'t0_jd_tdb':[center+model.lower[0],center+model.upper[0]],
                          'tE_days':[math.exp(model.lower[1]),math.exp(model.upper[1])],
                          'u0_heliocentric':[model.lower[2],model.upper[2]],'pi_E':[model.lower[4],model.upper[4]],
                          'theta_E_mas':declared.get('theta_E_mas',[.01,40.]),
                          'relative_frame_source_parallax_mas':declared.get('relative_frame_source_parallax_mas',[-1.,1.]),
                          'qualification':'Declared search domains; artificial caps are not observational limits.'}
    return {'schema':d['schema'],'sha256':dataset.sha256,'target':d.get('target'),
            'input_hash_algorithm':('bhtracker.canonical_numeric_json.v2' if dataset.__class__.__module__.endswith('_v2') else 'archived_v1_json_numeric_spelling'),
            'photometry_rows':len(d['photometry']),'astrometry_rows':len(d['astrometry']),
            'time_coordinate':d['time_coordinate'],'metadata':d['metadata'],
            'data_version':d.get('data_version'),'analysis':d.get('analysis'),'bounds':d.get('bounds'),
            'fit_readiness':'DECLARED_ANALYSIS_DOMAIN' if analysis_ready else 'ANALYSIS_BOUNDS_AND_INITIAL_GUESSES_REQUIRED',
            'effective_physical_search_bounds':effective_bounds,
            'unavailable':['absolute source parallax','absolute lens proper motion','lens distance','horizon','core state']}

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
        def submit_job(self,key,operation,*,lossless_json=False):
            with lock:
                prior=fingerprints.get(key)
                if prior and jobs[prior]['status'] in ('pending','running'):
                    self.send_json({'job_id':prior,'duplicate_prevented':True},202);return
                if len(jobs)>=64:raise ValueError('Session limit reached; restart the local app to clear in-memory results')
                name=uuid.uuid4().hex;jobs[name]={'status':'pending'};fingerprints[key]=name
            def work():
                with lock:jobs[name]={'status':'running'}
                try:
                    value=operation()
                    # A JSON string preserves numeric spelling for archived v1
                    # hashes through a JavaScript browser's number conversion.
                    item={'status':'complete',('result_json' if lossless_json else 'result'):
                          json.dumps(value,allow_nan=False) if lossless_json else value}
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
                  '/photometry':'photometry.html','/photometry/':'photometry.html','/photometry.js':'photometry.js',
                  '/joint':'joint.html','/joint/':'joint.html','/joint.js':'joint.js',
                  '/atlas':'atlas.html','/atlas/':'atlas.html','/atlas.html':'atlas.html',
                  '/atlas.js':'atlas.js','/atlas-core.js':'atlas-core.js','/atlas.css':'atlas.css',
                  '/atlas_data.json':'atlas_data.json','/atlas_manifest.json':'atlas_manifest.json'}.get(self.path)
            if self.path.startswith('/atlas/'):
                asset=self.path[len('/atlas/'):]
                if asset in ('atlas.js','atlas-core.js','atlas.css','atlas_data.json','atlas_manifest.json'):path=asset
            if not path:self.send_json({'error':'Not found'},404);return
            blob=(WEB/path).read_bytes();self.send_response(200)
            self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'text/javascript','css':'text/css','json':'application/json; charset=utf-8'}[path.rsplit('.',1)[1]])
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
                if 'result_json' in data:
                    if 'result' in data:raise ValueError('provide result or lossless result_json, not both')
                    data['result']=read_json(data['result_json'])
                if self.path=='/api/validate':
                    raw=read_json(data['dataset_json']) if 'dataset_json' in data else data['dataset']
                    dataset=load_dataset(raw);self.send_json({'valid':True,'summary':dataset.summary()});return
                if self.path=='/api/report':self.send_json({'html':report_html(data['result'])});return
                if self.path=='/api/export':
                    self.send_zip(export_analysis_bundle(data['result']),'Blackhole_Tracker_analysis.zip');return
                if self.path=='/api/joint/validate':
                    raw=read_json(data['dataset_json']) if 'dataset_json' in data else data['dataset']
                    dataset=joint_dataset(raw);self.send_json({'valid':True,'summary':joint_summary(dataset)});return
                if self.path=='/api/joint/import-benchmark':
                    encoded=data.get('content_base64')
                    if not isinstance(encoded,str) or len(encoded)>4_000_000:raise ValueError('provide the reviewed known-system source ZIP, at most 3 MB before base64 encoding')
                    dataset=import_joint_sourcepack(base64.b64decode(encoded,validate=True))
                    self.send_json({'valid':True,'summary':joint_summary(dataset),
                                    'sourcepack_sha256':JOINT_SOURCEPACK_SHA256,
                                    'dataset_json':json.dumps(dataset.document,allow_nan=False)});return
                if self.path in ('/api/joint/result','/api/joint/replay'):
                    from .joint_report import validate_result
                    dataset,_,checked=validate_result(data['result'])
                    self.send_json({'valid':True,'summary':joint_summary(dataset),'replay':checked,
                                    'dataset_json':json.dumps(dataset.document,allow_nan=False)});return
                if self.path=='/api/joint/fit':
                    version=data.get('scientific_version')
                    module=joint_module(version)
                    raw=read_json(data['dataset_json']) if 'dataset_json' in data else data['dataset']
                    dataset=joint_dataset(raw)
                    options=data.get('options',{})
                    allowed={'starts','max_nfev','gp','cross_filter_correlation','astrometric_jitter_mas',
                             'source_parallax_prior','free_filter_offsets','astrometric_lens_light','exposure_time_choice','noise_model'}
                    if not isinstance(options,dict) or set(options)-allowed:raise ValueError('unsupported joint fit options')
                    starts=options.get('starts',16);maximum=options.get('max_nfev',600)
                    if isinstance(starts,bool) or not isinstance(starts,int) or not 1<=starts<=16:raise ValueError('joint starts must be an integer from 1 to 16')
                    if isinstance(maximum,bool) or not isinstance(maximum,int) or not 1<=maximum<=2000:raise ValueError('joint max_nfev must be an integer from 1 to 2000')
                    for key in ['gp','free_filter_offsets','astrometric_lens_light']:
                        if key in options and not isinstance(options[key],bool):raise ValueError(key+' must be true or false')
                    for key in ['cross_filter_correlation','astrometric_jitter_mas']:
                        if key in options and (isinstance(options[key],bool) or not isinstance(options[key],(int,float))):raise ValueError(key+' must be numeric')
                    options={'starts':starts,'max_nfev':maximum,**options}
                    model_options={k:v for k,v in options.items() if k not in ('starts','max_nfev')}
                    # Validate the declared likelihood before accepting a long job.
                    module.JointModel(dataset.document,**model_options)
                    key=hashlib.sha256(json.dumps(['native_joint_mass',version,dataset.sha256,options],sort_keys=True).encode()).hexdigest()
                    def joint_fit_operation():
                        from .provenance import software_provenance
                        result=module.fit_joint(dataset.document,**options)
                        result['software_provenance']=software_provenance()
                        return result
                    self.submit_job(key,joint_fit_operation,lossless_json=True);return
                if self.path=='/api/joint/profile':
                    from .joint_report import validate_result
                    result=data['result'];dataset,_,_=validate_result(result)
                    module=joint_module('v2' if result['schema'].endswith('.v2') else 'v1')
                    masses=data.get('masses');maximum=data.get('max_nfev',600)
                    if not isinstance(masses,list) or not 3<=len(masses)<=61 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not .05<=v<=200 for v in masses):raise ValueError('profile requires 3 to 61 finite masses in .05..200 solar masses')
                    if any(b<=a for a,b in zip(masses,masses[1:])):raise ValueError('profile masses must increase strictly')
                    if isinstance(maximum,bool) or not isinstance(maximum,int) or not 1<=maximum<=2000:raise ValueError('profile max_nfev must be an integer from 1 to 2000')
                    # Profiling uses the likelihood, reference objective and all
                    # retained start states, not just the best forward state.
                    # Preserve the parsed lossless result's numeric semantics.
                    profile_identity=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
                    key=hashlib.sha256(json.dumps(['joint_profile',profile_identity,masses,maximum],sort_keys=True).encode()).hexdigest()
                    self.submit_job(key,lambda:module.profile_joint_mass(dataset.document,result,masses,max_nfev=maximum));return
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
            except ImportError:
                self.send_json({'error':'The joint astrometry route requires the optional astrometry dependencies. Install the matching local wheel with its [astrometry] extra, including Astropy.'},400)
            except (ValueError,KeyError,TypeError) as error:self.send_json({'error':str(error)},400)
    try:server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    except OSError as error:
        pool.shutdown(wait=False)
        raise OSError(f'Cannot open local port {port}: {error}. Close the other app or choose another port, for example --port 8766') from error
    server.executor=pool
    return server

def serve(port=8765,open_browser=False,page='resolved'):
    route={'resolved':'/','photometry':'/photometry','joint':'/joint','atlas':'/atlas'}.get(page)
    if route is None:raise ValueError('Unknown local workspace page')
    server=make_server(port)
    url=f'http://127.0.0.1:{server.server_port}{route}'
    print('Blackhole Tracker ready at '+url,flush=True)
    print('Local-only research app. Ctrl+C stops the server; inputs/results stay in this process.',flush=True)
    if open_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();server.executor.shutdown(wait=False,cancel_futures=True)
