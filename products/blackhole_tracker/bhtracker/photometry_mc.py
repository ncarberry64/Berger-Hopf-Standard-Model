"""Researcher orchestration for the unchanged nonregular magnitude MC method.

Validation is PENDING. Fixed-node decisions remain approximate with fitted
nuisance; this workspace does not identify a black hole or continuous endpoints.
"""
from copy import deepcopy
from fractions import Fraction
import base64
import gzip
import hashlib
from io import BytesIO
import json
import math
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import zipfile

from .data import read_json
from .observations import UnresolvedPhotometry
from .photometry_inference import _seed_slots,monte_carlo_ordinate,rank_p_bounds,confidence_set_from_ordinates
from . import _photometry_mc_store as store
from .provenance import project_citation,software_provenance

SCHEMA='bhsm.photometry_mc_workspace.v1'
MAX_INPUT_BYTES=32_000_000
MAX_NODES=17
MAX_EXPORT_BYTES=128*1024**2
MAX_WORKSPACE_BYTES=512*1024**2
METHOD={'slots':199,'starts':12,'max_nfev':1500,'noise_scale':1.,'confidence_level':.95,
        'lazy':True,'search_method':'NULL12_FREE1','seed_policy':'NULL_RAW_PEAK_WIDTH12_V1'}
UNAVAILABLE={'mass_msun':None,'lens_distance_pc':None,'theta_E_mas':None,'pi_E':None,
             'absolute_lens_proper_motion':None,'horizon':None,'core_state':None}
EVIDENCE={'validation_status':'PENDING','fitted_nuisance_bootstrap':'APPROXIMATE',
    'global_optimum_certified':False,'continuous_endpoints_available':False,
    'interpretation':'One image-summed optical exterior interpreted as BHSM gravitational surface topography; no extra optical potential.',
    'physical_identification':UNAVAILABLE,'project_citation':project_citation()}


def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
def digest(b):return hashlib.sha256(b).hexdigest()
def file_pin(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return {'bytes':path.stat().st_size,'sha256':h.hexdigest()}
def method_pins():
    root=Path(__file__).resolve().parent
    return {name:file_pin(root/name) for name in ('photometry_inference.py','photometry.py','observations.py',
        '_photometry_mc_store.py','_photometry_mc_trace.py','_photometry_mc_worker.py','photometry_mc.py','photometry_mc_replay.py')}
def write_new(path,blob):
    with Path(path).open('xb') as stream:stream.write(blob);stream.flush();os.fsync(stream.fileno())
def save(path,value):write_new(path,canonical(value))
def workspace_bytes(root):
    total=0
    for path in Path(root).iterdir():
        try:
            if path.is_file():total+=path.stat().st_size
        except FileNotFoundError:continue
    return total
def _integer(value,name,low,high):
    if isinstance(value,bool) or not isinstance(value,int) or not low<=value<=high:raise ValueError(f'{name} must be an integer in {low}..{high}')
    return value
def _number(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError(name+' must be finite numeric')
    return float(value)
def input_bytes(value):
    if isinstance(value,Path):value=value.read_bytes()
    elif isinstance(value,str):value=value.encode('utf-8')
    if not isinstance(value,bytes) or not 0<len(value)<=MAX_INPUT_BYTES:raise ValueError('Provide UTF-8 versioned unresolved JSON, at most32MB')
    value.decode('utf-8-sig')
    data=UnresolvedPhotometry.from_dict(read_json(value))
    return value,data


def make_request(original,grids,entropy,*,wall_seconds=600,max_saved_bytes=256*1024**2):
    blob,data=input_bytes(original)
    if not isinstance(grids,dict) or not grids or set(grids)-{'tE_days','u0'}:raise ValueError('Provide tE_days and/or u0 node arrays')
    if any(not isinstance(values,list) or not values for values in grids.values()):raise ValueError('Every requested grid requires at least1node')
    if not 1<=sum(len(values) for values in grids.values())<=MAX_NODES:raise ValueError(f'Provide1..{MAX_NODES}total fixed nodes; no adaptive insertion')
    if not isinstance(entropy,(list,tuple)) or not 1<=len(entropy)<=16:raise ValueError('Provide1..16 explicit seed words')
    words=[_integer(x,'seed word',0,2**32-1) for x in entropy]
    wall=_integer(wall_seconds,'wall_seconds',1,3600)
    budget=_integer(max_saved_bytes,'max_saved_bytes',1024**2,MAX_WORKSPACE_BYTES)
    nodes=[]
    for pindex,parameter in enumerate(('tE_days','u0')):
        if parameter not in grids:continue
        values=grids[parameter]
        if not isinstance(values,list) or not values:raise ValueError('Every requested grid requires at least1node')
        values=[_number(x,'grid value') for x in values]
        lower,upper=(.1,10000.) if parameter=='tE_days' else (.0001,10.)
        if any(not lower<=v<=upper for v in values) or any(b<=a for a,b in zip(values,values[1:])):
            raise ValueError(f'{parameter} nodes must strictly increase in the numerical domain {lower}..{upper}; caps are not confidence limits')
        for index,value in enumerate(values):
            ent=words+[pindex,index];identity=f'{parameter}_{index:03d}'
            nodes.append({'node_id':identity,'parameter':parameter,'value':value,'entropy':ent,
                'all199_seed_slots':_seed_slots(ent,parameter,value,199),'numerical_cap_ordinate':value in (lower,upper)})
    if not 1<=len(nodes)<=MAX_NODES:raise ValueError(f'Provide1..{MAX_NODES}total fixed nodes; no adaptive insertion')
    return {'schema':SCHEMA,'kind':'FIXED_NODE_MC_REQUEST','input_utf8_sha256':digest(blob),'input_bytes':len(blob),
        'canonical_input_sha256':data.sha256,'nodes':nodes,'entropy':words,'method':METHOD.copy(),
        'method_source_pins':method_pins(),'resources':{'wall_seconds':wall,'max_saved_bytes':budget},
        'evidence_scope':deepcopy(EVIDENCE),'native_rows':len(data.rows),'excluded_rows':0}


def _unknown(node,input_sha,reason):
    return {'schema':SCHEMA,'kind':'UNATTEMPTED_OR_FAILED_UNKNOWN','input_sha256':input_sha,
        'parameter':node['parameter'],'value':node['value'],'confidence_level':.95,
        'rank_bounds':rank_p_bounds(0,199),'observed_profile':None,'audit_failure':reason,
        'slots':[{'slot':i,'seed':seed,'status':'NOT_ATTEMPTED_UNKNOWN'} for i,seed in enumerate(node['all199_seed_slots'])],
        'physical_identification':deepcopy(UNAVAILABLE),'coverage_claim':False}


def _compact_child(document,parent,seed):
    child=UnresolvedPhotometry.from_dict(document)
    token=digest(json.dumps(seed,separators=(',',':')).encode())[:24]
    if child.document.get('metadata',{}).get('parent_input_sha256')!=parent.sha256 or len(child.rows)!=len(parent.rows):raise ValueError('generated child lineage differs')
    if child.times.tolist()!=parent.times.tolist() or child.errors.tolist()!=parent.errors.tolist():raise ValueError('generated child time/error sampling changed')
    for i,(row,old) in enumerate(zip(child.rows,parent.rows)):
        if row['source_row_id']!=f'SYNTHETIC:BOOTSTRAP:{token}:{i}' or row.get('bootstrap_parent_source_row_id')!=old['source_row_id']:raise ValueError('generated child row identity differs')
    return {'input_sha256':child.sha256,'parent_input_sha256':parent.sha256,'magnitudes':child.magnitudes.tolist(),
        'row_count':len(child.rows),'seed':seed,'parent_row_id_order_sha256':digest(canonical([r['source_row_id'] for r in parent.rows]))}


class MCWorkspace:
    """One local run. Cancellation/budget failures preserve unknowns; never retry."""
    def __init__(self,original,grids,entropy,directory,**limits):
        self.original,self.data=input_bytes(original)
        self.request=make_request(self.original,grids,entropy,**limits)
        if len(self.original)+len(canonical(self.request))>self.request['resources']['max_saved_bytes']:
            raise ValueError('Workspace byte budget is smaller than the immutable input/request')
        self.directory=Path(directory).resolve();self.directory.mkdir(parents=True,exist_ok=False)
        self.cancel_event=threading.Event();self.lock=threading.Lock()
        self.progress={'status':'pending','completed_nodes':0,'planned_nodes':len(self.request['nodes']),
            'committed_bootstrap_fits':0,'current_node':None,'stage':'REQUEST_DURABLE','evidence_scope':deepcopy(EVIDENCE)}
        write_new(self.directory/'input.original.utf8.json',self.original)
        save(self.directory/'request.json',self.request)
        save(self.directory/'provenance.json',{'project_citation':project_citation(),'software':software_provenance(),
            'scope':'Local pending research workflow; one BHSM optical exterior; hashes are consistency/provenance, not independent calibration.'})
        save(self.directory/'initial_unknown_nodes.json',[_unknown(n,self.data.sha256,'NOT_ATTEMPTED') for n in self.request['nodes']])

    def status(self):
        try:
            saved=read_json((self.directory/'progress.json').read_bytes())
            if not isinstance(saved,dict):raise ValueError('invalid progress')
        except (OSError,ValueError):saved={}
        with self.lock:return {**deepcopy(self.progress),**saved}
    def cancel(self):
        self.cancel_event.set()
        with self.lock:self.progress['cancellation_requested']=True
        return self.status()
    def _progress(self,**values):
        with self.lock:self.progress.update(values);value=deepcopy(self.progress)
        path=self.directory/f'.progress_{os.getpid()}_{threading.get_ident()}.tmp'
        with path.open('wb') as stream:stream.write(canonical(value));stream.flush();os.fsync(stream.fileno())
        # Windows readers may momentarily deny replacement. The authoritative
        # SQLite audit is already durable; retry only this transient UI race.
        for attempt in range(10):
            try:os.replace(path,self.directory/'progress.json');break
            except PermissionError:
                if attempt==9:raise
                time.sleep(.005)
    @classmethod
    def _open_worker(cls,directory,request_sha256):
        root=Path(directory).resolve();request=read_json((root/'request.json').read_bytes())
        if digest(canonical(request))!=request_sha256:raise ValueError('Worker request binding changed')
        original,data=input_bytes((root/'input.original.utf8.json').read_bytes())
        grids={}
        for node in request['nodes']:grids.setdefault(node['parameter'],[]).append(node['value'])
        rebuilt=make_request(original,grids,request['entropy'],**request['resources'])
        if canonical(request)!=canonical(rebuilt):raise ValueError('Worker method/input/seed plan changed')
        obj=object.__new__(cls);obj.original=original;obj.data=data;obj.request=request;obj.directory=root
        obj.cancel_event=threading.Event();obj.lock=threading.Lock()
        obj.progress={'status':'running','completed_nodes':0,'planned_nodes':len(request['nodes']),
            'committed_bootstrap_fits':0,'current_node':None,'stage':'REQUEST_DURABLE','evidence_scope':deepcopy(EVIDENCE)}
        return obj
    def _execute(self):
        start=time.monotonic();nodes=self.request['nodes'];outcomes={n['node_id']:_unknown(n,self.data.sha256,'NOT_ATTEMPTED') for n in nodes}
        database=self.directory/'audit.sqlite';writer=None;failure=None;cancelled=False;integrity=None
        self._progress(status='running',stage='AUDIT_REQUESTS')
        def check():
            if self.cancel_event.is_set():raise RuntimeError('CANCELLED_COOPERATIVELY_BEFORE_NEXT_STAGE')
            if time.monotonic()-start>self.request['resources']['wall_seconds']:raise TimeoutError('DECLARED_WALL_BUDGET')
            total=workspace_bytes(self.directory)
            if total>self.request['resources']['max_saved_bytes']:raise OSError('DECLARED_WORKSPACE_BUDGET')
        try:
            if method_pins()!=self.request['method_source_pins']:raise ValueError('Scientific method source changed after request')
            writer=store.AuditStore(database,digest(canonical(self.request)),[(n['node_id'],n['parameter']) for n in nodes],max_database_bytes=self.request['resources']['max_saved_bytes'])
            for node in nodes:writer.put(node['node_id'],node['parameter'],-1,'REQUEST',node)
            for node in nodes:
                check();self._progress(current_node=node['node_id'],stage='OBSERVED_FIT')
                def callback(stage,slot,payload):
                    check()
                    value=_compact_child(payload,self.data,node['all199_seed_slots'][slot]) if stage=='GENERATED' else payload
                    writer.put(node['node_id'],node['parameter'],slot,stage,value)
                    if stage=='FITTED':
                        with self.lock:self.progress['committed_bootstrap_fits']+=1
                    self._progress(stage=stage)
                from ._photometry_mc_trace import capture_evaluation_states
                with capture_evaluation_states():
                    result=monte_carlo_ordinate(self.data,node['parameter'],node['value'],entropy=node['entropy'],audit_callback=callback,**METHOD)
                writer.put(node['node_id'],node['parameter'],-1,'FINAL_ORDINATE',result)
                outcomes[node['node_id']]=result
                self._progress(completed_nodes=self.status()['completed_nodes']+1)
                if result.get('audit_failure'):raise RuntimeError('Permanent audit/cancel/budget latch: '+result['audit_failure'])
            integrity=writer.seal();writer=None
        except Exception as exc:
            failure=type(exc).__name__+': '+str(exc);cancelled=self.cancel_event.is_set()
            if writer is not None:
                writer.close();writer=None
            if database.exists():
                try:integrity=store.verify(database,include_record_metadata=False)
                except Exception as error:integrity={'integrity_ok':False,'error':str(error)}
        finally:
            if writer is not None:writer.close()
        try:changed=method_pins()!=self.request['method_source_pins']
        except OSError:changed=True
        status='cancelled' if cancelled else 'failed' if failure or changed else 'complete'
        result={'schema':SCHEMA,'kind':'FIXED_GRID_DECISION_RESULTS','status':status,'request_sha256':digest(canonical(self.request)),
            'input_utf8_sha256':self.request['input_utf8_sha256'],'canonical_input_sha256':self.data.sha256,
            'all_node_ids':[n['node_id'] for n in nodes],'nodes':outcomes,'failure':failure,'method_source_changed':changed,
            'elapsed_seconds':time.monotonic()-start,'audit_database':'audit.sqlite','audit_verification':integrity,'evidence_scope':deepcopy(EVIDENCE)}
        save(self.directory/'worker_result.json',result)
        self._progress(status='running',stage='WORKER_FINISHED_AWAITING_SUPERVISOR',failure=failure,workspace=str(self.directory))
        return result

    def _committed_terminal_progress(self,database,*,require_sealed=False):
        """Authoritative terminal counters; never reuse a parent's stale cache."""
        store.verify(database,expected_protocol_sha256=digest(canonical(self.request)),require_sealed=require_sealed,include_record_metadata=False)
        expected={(node['node_id'],node['parameter']) for node in self.request['nodes']}
        final=set();fitted=set()
        con=sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)
        try:
            for case,parameter,slot,stage in con.execute("SELECT case_id,parameter,slot,stage FROM records WHERE stage IN ('FINAL_ORDINATE','FITTED')"):
                if (case,parameter) not in expected:raise ValueError('Progress record outside exact request nodes')
                if stage=='FINAL_ORDINATE':
                    if type(slot) is not int or slot!=-1:raise ValueError('Final progress record has a bootstrap slot')
                    final.add((case,parameter))
                else:
                    if type(slot) is not int or not 0<=slot<199:raise ValueError('Fitted progress slot outside fixed199 roster')
                    fitted.add((case,parameter,slot))
        finally:con.close()
        return {'completed_nodes':len(final),'committed_bootstrap_fits':len(fitted),
          'progress_counts_available':True,'progress_counts_source':'VERIFIED_COMMITTED_SQLITE_STAGES',
          'progress_audit_database':Path(database).name}

    def _recover_stopped(self,reason,elapsed):
        outcomes={n['node_id']:_unknown(n,self.data.sha256,reason) for n in self.request['nodes']}
        database=self.directory/'audit.sqlite';integrity=None;chosen=None;recovery=None
        request_sha256=digest(canonical(self.request))
        if database.exists():
            try:integrity=store.verify(database,expected_protocol_sha256=request_sha256,include_record_metadata=False);chosen=database
            except Exception:
                try:
                    target=self.directory/'audit.recovered.sqlite';recovery=store.recover_copy(database,target)
                    integrity=store.verify(target,expected_protocol_sha256=request_sha256,include_record_metadata=False);chosen=target
                except Exception as exc:integrity={'integrity_ok':False,'error':type(exc).__name__+': '+str(exc)}
        if chosen is not None:
            con=sqlite3.connect(chosen.as_uri()+'?mode=ro',uri=True)
            try:
                for key,parameter,length,raw_sha,comp_sha,blob in con.execute("SELECT case_id,parameter,canonical_bytes,canonical_sha256,compressed_sha256,payload FROM records WHERE stage='FINAL_ORDINATE'"):
                    if key not in outcomes:raise ValueError('Recovered record outside fixed plan')
                    value=store._decode(blob,length,raw_sha,comp_sha,store.MAX_PAYLOAD)
                    node=next(n for n in self.request['nodes'] if n['node_id']==key)
                    if parameter!=node['parameter'] or canonical([value['parameter'],value['value'],value.get('input_sha256')])!=canonical([parameter,node['value'],self.data.sha256]):
                        raise ValueError('Recovered node/request/input identity changed')
                    outcomes[key]=value
            finally:con.close()
        counts={'completed_nodes':None,'committed_bootstrap_fits':None,'progress_counts_available':False,
          'progress_counts_source':'NO_VERIFIED_COMMITTED_DATABASE','progress_audit_database':None}
        if chosen is not None:
            try:counts=self._committed_terminal_progress(chosen)
            except Exception as exc:counts['progress_count_error']=type(exc).__name__+': '+str(exc)
        result={'schema':SCHEMA,'kind':'FIXED_GRID_DECISION_RESULTS','status':'cancelled' if self.cancel_event.is_set() else 'failed',
            'request_sha256':digest(canonical(self.request)),'input_utf8_sha256':self.request['input_utf8_sha256'],
            'canonical_input_sha256':self.data.sha256,'all_node_ids':[n['node_id'] for n in self.request['nodes']],
            'nodes':outcomes,'failure':reason,'elapsed_seconds':elapsed,'audit_database':None if chosen is None else chosen.name,
            'audit_verification':integrity,'recovery_of_fresh_copy_only':recovery,'committed_progress':counts,'evidence_scope':deepcopy(EVIDENCE)}
        if not (self.directory/'result.json').exists():save(self.directory/'result.json',result)
        self._progress(**counts,status=result['status'],stage='TERMINAL_AUDIT_RETAINED',failure=reason,workspace=str(self.directory))
        return result

    def run(self):
        """Hard supervisor; no automatic resume/refit if this run was attempted."""
        started=time.monotonic();marker=self.directory/'WORKER_STARTED.json'
        save(marker,{'request_sha256':digest(canonical(self.request)),'automatic_retry':False})
        command=[sys.executable,'-I','-B',str(Path(__file__).with_name('_photometry_mc_worker.py')),
            str(self.directory),digest(canonical(self.request))]
        environment=os.environ.copy()
        for name in ('PYTHONHOME','PYTHONPATH'):environment.pop(name,None)
        environment.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        reason=None;child=None
        with (self.directory/'worker.log').open('xb') as log:
            try:
                if self.cancel_event.is_set():reason='CANCELLED_BEFORE_WORKER'
                else:child=subprocess.Popen(command,env=environment,stdout=log,stderr=subprocess.STDOUT)
                while child is not None and child.poll() is None:
                    if self.cancel_event.is_set():reason='CANCELLED_HARD_SUPERVISOR'
                    elif time.monotonic()-started>self.request['resources']['wall_seconds']:reason='HARD_WALL_BUDGET'
                    elif workspace_bytes(self.directory)>self.request['resources']['max_saved_bytes']:reason='WORKSPACE_BUDGET'
                    if reason:child.terminate();break
                    time.sleep(.1)
            except KeyboardInterrupt:
                self.cancel_event.set();reason='CANCELLED_BY_LOCAL_INTERRUPT'
                if child is not None and child.poll() is None:child.terminate()
            except Exception as exc:
                reason=type(exc).__name__+': '+str(exc)
                if child is not None and child.poll() is None:child.terminate()
            finally:
                if child is not None:
                    try:child.wait(timeout=10)
                    except subprocess.TimeoutExpired:child.kill();child.wait()
        if reason is None:
            if self.cancel_event.is_set():reason='CANCELLED_AFTER_WORKER_EXIT'
            elif time.monotonic()-started>self.request['resources']['wall_seconds']:reason='HARD_WALL_BUDGET_AFTER_WORKER_EXIT'
            elif workspace_bytes(self.directory)>self.request['resources']['max_saved_bytes']:reason='WORKSPACE_BUDGET_AFTER_WORKER_EXIT'
        if reason is None and child is not None and child.returncode==0 and (self.directory/'worker_result.json').is_file():
            result=read_json((self.directory/'worker_result.json').read_bytes())
            if result['request_sha256']!=digest(canonical(self.request)) or result['all_node_ids']!=[n['node_id'] for n in self.request['nodes']]:
                return self._recover_stopped('WORKER_RESULT_IDENTITY_MISMATCH',time.monotonic()-started)
            if result['status']=='complete':
                try:
                    fresh=store.verify(self.directory/'audit.sqlite',expected_protocol_sha256=digest(canonical(self.request)),require_sealed=True,include_record_metadata=False)
                    if canonical(fresh)!=canonical(result['audit_verification']):raise ValueError('Worker seal receipt mismatch')
                except Exception as exc:return self._recover_stopped('WORKER_RESULT_AUDIT_REFUSED: '+str(exc),time.monotonic()-started)
            result['supervisor']={'worker_returncode':child.returncode,'wall_seconds':time.monotonic()-started,
                'worker_result_pin':file_pin(self.directory/'worker_result.json'),'no_automatic_retry':True}
            try:counts=self._committed_terminal_progress(self.directory/'audit.sqlite',require_sealed=result['status']=='complete')
            except Exception as exc:return self._recover_stopped('WORKER_PROGRESS_AUDIT_REFUSED: '+str(exc),time.monotonic()-started)
            result['committed_progress']=counts
            save(self.directory/'result.json',result)
            self._progress(**counts,**{k:result[k] for k in ('status','failure')},stage='TERMINAL_AUDIT_RETAINED',workspace=str(self.directory))
            return result
        return self._recover_stopped(reason or 'WORKER_FAILED_OR_RESULT_UNAVAILABLE',time.monotonic()-started)


def workspace_status(directory):
    root=Path(directory);request=read_json((root/'request.json').read_bytes())
    if (root/'result.json').is_file():
        value=read_json((root/'result.json').read_bytes())
        return {'status':value['status'],'planned_nodes':len(request['nodes']),'result':value,'evidence_scope':deepcopy(EVIDENCE)}
    return {'status':'UNTERMINATED_OR_RUNNING','planned_nodes':len(request['nodes']),
        'qualification':'No terminal result exists; all missing states remain unknown. No automatic resume or refit.','evidence_scope':deepcopy(EVIDENCE)}


def request_from_body(body):
    allowed={'input_base64','dataset_json','grids','entropy','wall_seconds','max_saved_bytes'}
    if not isinstance(body,dict) or set(body)-allowed:raise ValueError('Unsupported MC request fields')
    if ('input_base64' in body)==('dataset_json' in body):raise ValueError('Provide original input_base64 or dataset_json exactly once')
    if 'input_base64' in body:
        encoded=body['input_base64']
        if not isinstance(encoded,str) or len(encoded)>44_000_000:raise ValueError('Original JSON upload exceeds32MB')
        original=base64.b64decode(encoded,validate=True)
    else:
        if not isinstance(body['dataset_json'],str):raise ValueError('dataset_json must preserve the original UTF-8 text')
        original=body['dataset_json'].encode('utf-8')
    limits={k:body[k] for k in ('wall_seconds','max_saved_bytes') if k in body}
    request=make_request(original,body.get('grids'),body.get('entropy'),**limits)
    return original,request,limits


def plan(body):
    original,request,_=request_from_body(body);_,data=input_bytes(original)
    return {'request':request,'summary':{'rows':len(data.rows),'input_utf8_sha256':request['input_utf8_sha256'],
        'canonical_input_sha256':data.sha256,'instruments':data.document['instruments'],
        'common_numeric_origin_jd':data.common_origin_jd,'evidence_scope':deepcopy(EVIDENCE)},
        'analysis_optimizer_or_RNG_calls':0}


class MCJobs:
    """Local job registry; immutable inputs and audit directories remain on disk."""
    def __init__(self,executor,directory=None):
        self.executor=executor;self.directory=Path(directory) if directory is not None else Path(tempfile.mkdtemp(prefix='BHSM_photometry_MC_'))
        if directory is not None:self.directory.mkdir(parents=True,exist_ok=False)
        self.jobs={};self.fingerprints={};self.lock=threading.Lock()
    def submit(self,body):
        original,request,limits=request_from_body(body);key=digest(canonical(request))
        with self.lock:
            prior=self.fingerprints.get(key)
            if prior and not self.jobs[prior]['future'].done():return {'job_id':prior,'duplicate_prevented':True}
            if len(self.jobs)>=16:raise ValueError('MC session limit reached; export retained audits before starting a new local session')
            identity=uuid.uuid4().hex
            workspace=MCWorkspace(original,body['grids'],body['entropy'],self.directory/identity,**limits)
            future=self.executor.submit(workspace.run)
            self.jobs[identity]={'workspace':workspace,'future':future};self.fingerprints[key]=identity
            return {'job_id':identity,'duplicate_prevented':False}
    def _job(self,identity):
        with self.lock:
            if identity not in self.jobs:raise ValueError('Unknown local MC job')
            return self.jobs[identity]
    def status(self,identity):
        job=self._job(identity);workspace=job['workspace'];progress=workspace.status()
        value={'job_id':identity,'status':progress['status'],'progress':progress,'workspace_path':str(workspace.directory),
            'evidence_scope':deepcopy(EVIDENCE)}
        if job['future'].done() and not job['future'].cancelled() and job['future'].exception() is not None:
            value.update(status='failed',error=str(job['future'].exception()))
        if (workspace.directory/'result.json').is_file():
            from .photometry_mc_replay import summary
            result=read_json((workspace.directory/'result.json').read_bytes());value['summary']=summary(workspace.request,result);value['status']=result['status']
        return value
    def cancel(self,identity):
        job=self._job(identity);workspace=job['workspace'];workspace.cancel()
        if job['future'].cancel():workspace._recover_stopped('CANCELLED_WHILE_QUEUED',0.)
        return {**self.status(identity),'cancellation_requested':True}
    def export(self,identity,output=None):
        job=self._job(identity)
        if not job['future'].done():raise ValueError('Cancel and wait for terminal audit before exporting')
        from .photometry_mc_replay import export_workspace
        return export_workspace(job['workspace'].directory,output)
    def shutdown(self):
        for identity in list(self.jobs):
            try:self.cancel(identity)
            except (ValueError,OSError):pass
