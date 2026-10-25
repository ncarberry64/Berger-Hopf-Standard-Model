"""Portable fixed-node MC audit export and explicit saved-state numerical replay.

Numerical replay evaluates stored exact vectors. It never optimizes, profiles,
resamples data, estimates coverage or upgrades the PENDING validation label.
"""
from copy import deepcopy
from fractions import Fraction
import gzip
from io import BytesIO
import json
import math
from pathlib import Path
import sqlite3
import tempfile
import time
import zipfile

from . import photometry_mc as mc
from .data import read_json
from .observations import UnresolvedPhotometry
from ._photometry_mc_trace import evaluate_saved_state

FILES={'input.original.utf8.json','request.json','provenance.json','initial_unknown_nodes.json','result.json',
       'worker_result.json','audit.sqlite','audit.sqlite-journal','audit.recovered.sqlite','README.txt','manifest.json'}
REQUIRED={'input.original.utf8.json','request.json','provenance.json','initial_unknown_nodes.json','result.json','README.txt','manifest.json'}
ATOL=1e-8
RTOL=1e-11


def summary(request,result):
    nodes=[];groups={}
    for node in request['nodes']:
        value=result.get('nodes',{}).get(node['node_id'])
        bounds=value.get('rank_bounds',{}) if isinstance(value,dict) else {}
        state=bounds.get('decision','UNRESOLVED')
        row={'node_id':node['node_id'],'parameter':node['parameter'],'value':node['value'],'decision':state,
             'p_lower':bounds.get('p_lower'),'p_upper':bounds.get('p_upper'),'unknown':bounds.get('unknown',199),
             'attempted_slots':0 if not value else value.get('attempted_slots',0),'numerical_cap_ordinate':node['numerical_cap_ordinate']}
        nodes.append(row)
        groups.setdefault(node['parameter'],[]).append({'input_sha256':request['canonical_input_sha256'],'parameter':node['parameter'],
            'value':node['value'],'confidence_level':.95,'kind':'FIXED_NODE_APPROXIMATE_PLUGIN_DECISIONS','rank_bounds':{'decision':state}})
    return {'status':result['status'],'nodes':nodes,'sampled_grid_summaries':{k:mc.confidence_set_from_ordinates(v) for k,v in groups.items()},
        'failure':result.get('failure'),'evidence_scope':deepcopy(mc.EVIDENCE),
        'qualification':'Requested-node test decisions only. Unknowns/gaps and outside-domain behavior are unassessed; no continuous endpoint or black-hole identity.'}


def export_workspace(directory,output=None,*,max_archive_bytes=mc.MAX_EXPORT_BYTES):
    mc._integer(max_archive_bytes,'max_archive_bytes',1,2*1024**3)
    root=Path(directory).resolve()
    if not (root/'result.json').is_file():raise ValueError('Cancel and wait for terminal audit before export; no automatic resume/refit')
    request=read_json((root/'request.json').read_bytes());result=read_json((root/'result.json').read_bytes())
    payloads={p.name:p for p in root.iterdir() if p.is_file() and p.name in FILES-{'README.txt','manifest.json'}}
    if not REQUIRED-{'README.txt','manifest.json'}<=set(payloads):raise ValueError('Workspace lacks mandatory input/request/result evidence')
    readme=('BHSM PHOTOMETRY MONTE CARLO AUDIT\nValidation:PENDING; fitted-nuisance approximation; finite requested grid.\n'
        'One ordinary optical exterior interpreted as BHSM surface topography. Mass/distance/angular scale/parallax/horizon/core are unavailable.\n'
        'INTEGRITY_ONLY verifies bytes/identities/ranks, not scientific reproduction. NUMERICAL_SAVED_STATE_REPLAY also re-evaluates every stored finite exact vector/objective and contrast; no optimization or random draws.\n'
        'Cancellation/failures/unattempted slots remain unknown. A recovered SQLite copy never changes the original DB/journal.\n'
        'Repository:https://github.com/ncarberry64/Berger-Hopf-Standard-Model\n').encode('utf-8')
    entries={name:mc.file_pin(path) for name,path in payloads.items()};entries['README.txt']={'bytes':len(readme),'sha256':mc.digest(readme)}
    manifest={'schema':'bhsm.photometry_mc.audit_bundle.v1','files':entries,'input_utf8_sha256':request['input_utf8_sha256'],
        'canonical_input_sha256':request['canonical_input_sha256'],'method_source_pins':request['method_source_pins'],
        'evidence_scope':deepcopy(mc.EVIDENCE),'hashes_are_authenticity_or_coverage_certificate':False}
    class CappedArchive:
        def __init__(self,stream):self.stream=stream;self.limit=max_archive_bytes
        def write(self,block):
            if self.stream.tell()+len(block)>self.limit:raise ValueError('Archive byte cap exceeded; original workspace retained. Use CLI/file export with an explicit larger cap')
            return self.stream.write(block)
        def __getattr__(self,name):return getattr(self.stream,name)
    def write_archive(target):
        target=CappedArchive(target)
        with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for name in sorted(entries):
                info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                with archive.open(info,'w') as destination:
                    if name=='README.txt':destination.write(readme)
                    else:
                        with payloads[name].open('rb') as source:
                            for block in iter(lambda:source.read(1024*1024),b''):destination.write(block)
            info=zipfile.ZipInfo('manifest.json',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,mc.canonical(manifest))
    if output is None:
        with tempfile.TemporaryFile() as stream:
            write_archive(stream);stream.seek(0);blob=stream.read()
        if len(blob)>max_archive_bytes:raise ValueError('Bundle exceeds browser export limit; export the durable workspace with the CLI/file API')
        return blob
    path=Path(output)
    with path.open('xb') as stream:write_archive(stream)
    if path.stat().st_size>max_archive_bytes:raise ValueError('Export exceeds declared archive limit; unaccepted file retained for audit')
    return {'path':str(path.resolve()),**mc.file_pin(path),'scope':'Portable saved audit; no new scientific validation'}


def restore_bootstrap(parent,compact):
    if compact.get('parent_input_sha256')!=parent.sha256 or compact.get('row_count')!=len(parent.rows) or len(compact.get('magnitudes',[]))!=len(parent.rows):
        raise ValueError('Missing/changed generated observation data')
    if compact['parent_row_id_order_sha256']!=mc.digest(mc.canonical([r['source_row_id'] for r in parent.rows])):raise ValueError('Parent row identity order changed')
    seed=compact['seed'];token=mc.digest(json.dumps(seed,separators=(',',':')).encode())[:24]
    document=parent.to_dict();document['sources']=[]
    document['metadata']={'synthetic':True,'kind':'PARAMETRIC_BOOTSTRAP_MAGNITUDES','parent_input_sha256':parent.sha256}
    if 'relative_time_combination_assumption' in parent.document.get('metadata',{}):
        document['metadata']['relative_time_combination_assumption']=deepcopy(parent.document['metadata']['relative_time_combination_assumption'])
    document['metadata']['inherited_instrument_metadata_role']='Parent time/error/calibration context only; every child brightness is synthetic and original source files remain with the immutable parent.'
    document['transformations']=[{'operation':'SYNTHETIC_MAGNITUDE_REPLACEMENT','parent_input_sha256':parent.sha256,'all_rows_replaced':True,'original_source_files_embedded':False}]
    for index,(row,y) in enumerate(zip(document['rows'],compact['magnitudes'])):
        row['bootstrap_parent_source_row_id']=row['source_row_id'];row['source_row_id']=f'SYNTHETIC:BOOTSTRAP:{token}:{index}'
        for key in ('native_fields','source_file','source_line','source_sha256'):row.pop(key,None)
        row['magnitude']=y;row['quality_flags']=[*row.get('quality_flags',[]),'SYNTHETIC_MAGNITUDE']
    child=UnresolvedPhotometry(document)
    if child.sha256!=compact['input_sha256']:raise ValueError('Generated input canonical hash changed')
    return child


def _same(a,b):return mc.canonical(a)==mc.canonical(b)
def _close(a,b):return abs(a-b)<=ATOL+RTOL*max(abs(a),abs(b))


def numerical_profile(data,profile,*,deadline,max_states=100000):
    if profile.get('input_sha256')!=data.sha256:raise ValueError('Profile/input hash mismatch')
    seen={};count=0;maxdiff=0.;exact=0
    def visit(value):
        nonlocal count,maxdiff,exact
        if time.monotonic()>deadline:raise TimeoutError('Numerical replay wall budget reached; no complete numerical certificate')
        if isinstance(value,dict):
            if value.get('objective_chi_square') is not None and 'parameters' in value:
                expected=mc._number(value['objective_chi_square'],'saved objective')
                trace=value.get('saved_numerical_state')
                if not isinstance(trace,dict):raise ValueError('Finite saved objective lacks exact numerical state; numerical replay refused')
                identity=(trace.get('search_call_index'),trace.get('trial_index'))
                if any(type(v) is not int or v<0 for v in identity):raise ValueError('Exact state/trial binding missing')
                if 'start' in value and value['start']!=identity[1]:raise ValueError('State belongs to a different optimizer trial')
                payload=(trace,value['parameters'])
                if identity in seen:
                    if not _same(seen[identity][0],payload):raise ValueError('Ambiguous state binding changed')
                    actual=seen[identity][1]
                else:
                    if count>=max_states:raise ValueError('Numerical replay state-count cap reached')
                    actual=evaluate_saved_state(data,trace,value['parameters']);seen[identity]=(payload,actual);count+=1
                difference=abs(actual-expected);maxdiff=max(maxdiff,difference);exact+=int(actual==expected)
                if not _close(actual,expected):raise ValueError('Saved-state objective differs from numerical recomputation')
            for k,child in value.items():
                if k not in ('saved_numerical_state','parameters'):visit(child)
        elif isinstance(value,list):
            for child in value:visit(child)
    visit(profile)
    free=profile.get('unrestricted',{}).get('objective_chi_square');null=profile.get('null_constrained',{}).get('objective_chi_square')
    if profile.get('statistic') is not None:
        if free is None or null is None:raise ValueError('Reported contrast is missing a saved finite state')
        def actual(search):
            trace=search.get('saved_numerical_state')
            if not isinstance(trace,dict):raise ValueError('Missing selected exact state for numerical contrast')
            return seen[(trace['search_call_index'],trace['trial_index'])][1]
        delta=actual(profile['null_constrained'])-actual(profile['unrestricted'])
        if not _close(delta,profile['raw_profile_delta_chi_square']) or not _close(max(delta,0.),profile['statistic']):raise ValueError('Saved profile contrast changed')
    return {'unique_finite_states_evaluated':count,'exact_objective_comparisons':exact,'maximum_absolute_objective_difference':maxdiff}


def replay_bundle(bundle,*,mode='integrity',wall_seconds=120,max_states=100000):
    if mode not in ('integrity','numerical'):raise ValueError('mode must be integrity or numerical')
    mc._integer(wall_seconds,'replay wall_seconds',1,600);mc._integer(max_states,'max_states',1,100000)
    start=time.monotonic();deadline=start+wall_seconds
    def check_budget():
        if time.monotonic()>deadline:raise TimeoutError('Replay wall budget reached; no completed verification receipt')
    source=BytesIO(bundle) if isinstance(bundle,bytes) else Path(bundle)
    if isinstance(bundle,bytes) and len(bundle)>mc.MAX_EXPORT_BYTES:raise ValueError('Browser replay bundle exceeds128MiB')
    if not isinstance(bundle,bytes) and Path(bundle).stat().st_size>2*1024**3:raise ValueError('CLI replay archive exceeds2GiB file-resource limit')
    with zipfile.ZipFile(source) as archive,tempfile.TemporaryDirectory(prefix='bhsm-mc-read-only-replay-') as directory:
        infos=archive.infolist();names=[i.filename for i in infos]
        if len(names)!=len(set(names)) or not REQUIRED<=set(names) or set(names)-FILES:raise ValueError('Replay archive member roster differs')
        if any(i.is_dir() or (i.external_attr>>16)&0o170000==0o120000 for i in infos):raise ValueError('Only regular allowlisted replay files are admitted')
        if sum(i.file_size for i in infos)>2*mc.MAX_WORKSPACE_BYTES+128*1024**2:raise ValueError('Replay expansion resource limit')
        root=Path(directory);manifest=read_json(archive.read('manifest.json'))
        if manifest.get('schema')!='bhsm.photometry_mc.audit_bundle.v1' or set(manifest.get('files',{}))!=set(names)-{'manifest.json'}:raise ValueError('Manifest member roster mismatch')
        for info in infos:
            if time.monotonic()>deadline:raise TimeoutError('Replay input/integrity wall budget exceeded')
            target=root/info.filename
            with archive.open(info) as incoming,target.open('xb') as output:
                for block in iter(lambda:incoming.read(1024*1024),b''):
                    if time.monotonic()>deadline:raise TimeoutError('Replay extraction wall budget exceeded')
                    output.write(block)
            if info.filename!='manifest.json' and not _same(mc.file_pin(target),manifest['files'][info.filename]):raise ValueError('Replay member bytes/hash mismatch')
        original,data=mc.input_bytes((root/'input.original.utf8.json').read_bytes());request=read_json((root/'request.json').read_bytes());result=read_json((root/'result.json').read_bytes())
        if mc.digest(original)!=request['input_utf8_sha256'] or data.sha256!=request['canonical_input_sha256'] or result['request_sha256']!=mc.digest(mc.canonical(request)):
            raise ValueError('Original input/request identity changed')
        grids={}
        for node in request['nodes']:grids.setdefault(node['parameter'],[]).append(node['value'])
        rebuilt=mc.make_request(original,grids,request['entropy'],**request['resources'])
        saved=deepcopy(request);saved['method_source_pins']=rebuilt['method_source_pins']
        if not _same(saved,rebuilt) or not _same(result['all_node_ids'],[n['node_id'] for n in request['nodes']]) or set(result['nodes'])!=set(result['all_node_ids']):raise ValueError('Fixed method/request/nodes/199seeds changed')
        if not _same(result.get('evidence_scope'),request['evidence_scope']) or not _same(manifest.get('evidence_scope'),request['evidence_scope']):raise ValueError('Evidence/physical-identification scope changed')
        if manifest.get('input_utf8_sha256')!=request['input_utf8_sha256'] or manifest.get('canonical_input_sha256')!=data.sha256 or not _same(manifest.get('method_source_pins'),request['method_source_pins']):raise ValueError('Manifest/input/method identity differs')
        matching=request['method_source_pins']==mc.method_pins()
        if mode=='numerical' and not matching:raise ValueError('Scientific/observer source changed; numerical replay refused (integrity-only remains available)')
        database=result.get('audit_database');audit=None;connection=None;states=0;profiles=0;maxdiff=0.;ranks=0
        if database is not None:
            if database not in ('audit.sqlite','audit.recovered.sqlite') or not (root/database).is_file():raise ValueError('Saved numerical audit data unavailable')
            audit=mc.store.verify(root/database,expected_protocol_sha256=mc.digest(mc.canonical(request)),require_sealed=result['status']=='complete',include_record_metadata=False)
            def compact_verification(value):return {k:v for k,v in value.items() if k not in ('records','record_metadata_collected')}
            if not isinstance(result.get('audit_verification'),dict) or not _same(compact_verification(audit),compact_verification(result['audit_verification'])):
                raise ValueError('Saved audit verification differs from fresh verification')
            connection=sqlite3.connect((root/database).as_uri()+'?mode=ro',uri=True)
        elif mode=='numerical':raise ValueError('No saved numerical audit states are available; use integrity-only for the unknown request')
        elif (root/'audit.sqlite').exists():raise ValueError('Original audit was not admitted as a readable numerical prefix; raw evidence is preserved but integrity replay is unavailable')
        def record(node,slot,stage):
            if connection is None:return None
            check_budget()
            row=connection.execute('SELECT canonical_bytes,canonical_sha256,compressed_sha256,payload FROM records WHERE case_id=? AND parameter=? AND slot=? AND stage=?',(node['node_id'],node['parameter'],slot,stage)).fetchone()
            if row is None:return None
            length,rawsha,compsha,blob=row
            value=mc.store._decode(blob,length,rawsha,compsha,mc.store.MAX_PAYLOAD)
            check_budget();return value
        try:
            for node in request['nodes']:
                if time.monotonic()>deadline:raise TimeoutError('Replay wall budget reached; no completed numerical replay')
                outcome=result['nodes'][node['node_id']]
                if not _same([outcome['parameter'],outcome['value']],[node['parameter'],node['value']]):raise ValueError('Result node identity differs')
                stored_request=record(node,-1,'REQUEST')
                if stored_request is not None and not _same(stored_request,node):raise ValueError('Durable seed request differs')
                final=record(node,-1,'FINAL_ORDINATE')
                if final is not None and not _same(outcome,final):raise ValueError('Exported node differs from committed final ordinate')
                if final is None and (outcome.get('observed_profile') is not None or outcome.get('attempted_slots',0)!=0):
                    raise ValueError('Uncommitted final node cannot replace retained unknown outcome')
                observed=record(node,-1,'OBSERVED_PROFILE')
                if outcome.get('observed_profile') is not None and observed is not None and not _same(outcome['observed_profile'],observed):raise ValueError('Observed state changed after audit commit')
                if mode=='numerical' and observed is not None:
                    checked=numerical_profile(data,observed,deadline=deadline,max_states=max_states-states);states+=checked['unique_finite_states_evaluated'];profiles+=1;maxdiff=max(maxdiff,checked['maximum_absolute_objective_difference'])
                if mode=='numerical' and outcome.get('observed_profile') is not None and observed is None:raise ValueError('Missing saved observed numerical state')
                c=0;unknown=199;observed_stat=None if observed is None else observed.get('statistic')
                slots=outcome['slots']
                if len(slots)!=199:raise ValueError('Full199-slot unknown roster missing')
                for index,row in enumerate(slots):
                    check_budget()
                    if type(row.get('slot')) is not int or row['slot']!=index or not _same(row.get('seed'),node['all199_seed_slots'][index]):raise ValueError('MC seed/slot identity changed')
                    fitted=record(node,index,'FITTED');generated=record(node,index,'GENERATED')
                    if fitted is not None:
                        if generated is None or not _same(generated['seed'],row['seed']):raise ValueError('Fitted state lacks committed original generated observations')
                        child=restore_bootstrap(data,generated)
                        check_budget()
                        if fitted.get('input_sha256')!=child.sha256:raise ValueError('Saved fit/generated input mismatch')
                        if 'input_sha256' in row and row['input_sha256']!=child.sha256:raise ValueError('Rank row/generated input differs')
                        if 'statistic' in row and not _same(row['statistic'],fitted.get('statistic')):raise ValueError('Rank row/stored fit statistic differs')
                        if 'numerical_status' in row and row['numerical_status']!=fitted.get('status'):raise ValueError('Rank row/stored numerical status differs')
                        if mode=='numerical':
                            checked=numerical_profile(child,fitted,deadline=deadline,max_states=max_states-states);states+=checked['unique_finite_states_evaluated'];profiles+=1;maxdiff=max(maxdiff,checked['maximum_absolute_objective_difference'])
                    if row['status'] in ('EXCEEDANCE','NONEXCEEDANCE'):
                        if fitted is None or observed_stat is None or fitted.get('statistic') is None:raise ValueError('Counted rank comparison missing numerical evidence')
                        delta=fitted['statistic']-observed_stat;tol=1e-8*(1+abs(fitted['statistic'])+abs(observed_stat))
                        expected='EXCEEDANCE' if delta>tol else 'NONEXCEEDANCE' if delta< -tol else 'ORDERING_UNRESOLVED_UNKNOWN'
                        if row['status']!=expected:raise ValueError('Saved rank ordering changed')
                        c+=int(expected=='EXCEEDANCE');unknown-=1
                expected=mc.rank_p_bounds(c,unknown)
                if outcome.get('audit_failure') is not None:expected['decision']='UNRESOLVED'
                if not _same(expected,outcome['rank_bounds']):raise ValueError('Fixed-B rank bounds changed')
                ranks+=1
        finally:
            if connection is not None:connection.close()
        if mode=='numerical' and states==0:raise ValueError('No finite saved numerical state exists; integrity-only can preserve unknowns')
        check_budget()
        verification={'passed':True,'mode':'NUMERICAL_SAVED_STATE_REPLAY' if mode=='numerical' else 'INTEGRITY_ONLY','requested_mode':mode,
            'scope':'Exact saved-state forward objectives/contrasts and saved fixed-rank arithmetic; no optimization or coverage validation' if mode=='numerical' else 'Bytes/identities/audit/rank consistency only; not scientific numerical reproduction',
            'method_sources_match':matching,'raw_input_bytes_preserved':True,'nodes_checked':ranks,'profiles_numerically_checked':profiles,
            'exact_vector_states_evaluated':states,'maximum_absolute_objective_difference':maxdiff,'comparison_atol':ATOL,'comparison_rtol':RTOL,
            'recovered_audit_copy_used':database=='audit.recovered.sqlite',
            'optimizer_or_RNG_calls':0,'global_optimum_or_calibration_certified':False,'elapsed_seconds':time.monotonic()-start}
        value={'verification':verification,'summary':summary(request,result),'evidence_scope':deepcopy(mc.EVIDENCE)}
        check_budget();return value
