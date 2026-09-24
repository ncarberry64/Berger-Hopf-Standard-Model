"""Freeze only independently reproduced NEW interval-13 model artifacts.

Large immutable gzip graphs are split into explicitly inventoried 64 MiB
parts for Git storage. The logical byte stream, full size, SHA256, and each
part remain visible. This does not exempt parts from large-artifact review.
"""
import argparse,gzip,hashlib,json,platform,sys
import flint
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.adaptive_expression_reader import read_graph


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest().upper()


def encode(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def verify_site_binding(metadata):
    """Check that reused DF/value/eigenpair authorities describe one family."""
    site=metadata['site'];node=13 if site=='left' else 14
    suffix=(f'/.coupled_endpoint_uniform_df_work/endpoint_{node:03d}/record.json'
        if site!='middle' else '/.coupled_midpoint_uniform_df_work/interval_013/record.json')
    paths=[p for p in metadata['source_SHA256'] if Path(p).as_posix().endswith(suffix)]
    if len(paths)!=1:raise ValueError('one direct first-derivative authority required')
    record=json.loads(Path(paths[0]).read_bytes());binding=record['binding']['files']
    required=([f'.affine_eigenpair_pilot_work/endpoint_{node:03d}/eigenpair.npz',
        f'.affine_physical_value_pilot_work/endpoint_{node:03d}/value.npz'] if site!='middle' else
        ['.coupled_hs_midpoint_domain_work/interval_013/domain.npz',
         '.coupled_midpoint_eigenpair_pilot_work/interval_013/eigenpair.npz',
         '.coupled_midpoint_physical_value_work/interval_013/value.npz'])
    checked=[]
    for tail in required:
        candidates=[(p,h) for p,h in metadata['source_SHA256'].items() if Path(p).as_posix().endswith('/'+tail)]
        if len(candidates)!=1:raise ValueError('matching direct physical-family input required')
        path,h=candidates[0];portable='artifacts/'+Path(path).as_posix().split('/artifacts/',1)[1]
        if binding.get(portable)!=h:raise ValueError('DF authority has different physical-family inputs')
        checked.append({'path':path,'SHA256':h})
    radius_records=[]
    for path in metadata['source_SHA256']:
        if not path.endswith('record.json'):continue
        z=json.loads(Path(path).read_bytes())
        if 'radius_longitudinal_rational' in z:
            if [z['radius_longitudinal_rational'],z['radius_transverse_rational']]!=metadata['radius_exact']:
                raise ValueError('unchanged original radii required in every direct input')
            radius_records.append(path)
    return {'first_derivative_record':paths[0],'same_family_data':checked,'matching_radius_records':radius_records}


def split_verified(first,repeat,out,chunk_size=64*1024*1024):
    digest=sha(first)
    if first.resolve()==repeat.resolve() or first.stat().st_size!=repeat.stat().st_size or sha(repeat)!=digest:
        raise ValueError('distinct independently reproduced byte-identical files required')
    if out.exists():raise FileExistsError('fresh frozen artifact directory required')
    out.mkdir(parents=True)
    rows=[]
    with first.open('rb') as stream:
        for i,block in enumerate(iter(lambda:stream.read(chunk_size),b'')):
            name=f'model.json.gz.part{i:03d}'
            (out/name).write_bytes(block)
            rows.append({'file':name,'bytes':len(block),'SHA256':hashlib.sha256(block).hexdigest().upper()})
    result={'format':'IMMUTABLE_CONCATENATED_GZIP_PARTS_V1','logical_bytes':first.stat().st_size,
        'logical_SHA256':digest,'parts':rows,'byte_identical_pair':True,
        'first_path':str(first.resolve()),'repeat_path':str(repeat.resolve()),
        'reconstruction':'concatenate parts in listed order; verify logical SHA256 before gzip decoding'}
    (out/'archive.json').write_bytes(encode(result))
    return result


def restore_archive(directory,out):
    if out.exists():raise FileExistsError('fresh reconstruction path required')
    record=json.loads((directory/'archive.json').read_bytes())
    if record['format']!='IMMUTABLE_CONCATENATED_GZIP_PARTS_V1':raise ValueError('known archive required')
    out.parent.mkdir(parents=True,exist_ok=True)
    pending=out.with_suffix(out.suffix+'.pending')
    if pending.exists():raise FileExistsError(str(pending))
    total=0;whole=hashlib.sha256()
    with pending.open('wb') as stream:
        for row in record['parts']:
            path=(directory/row['file']).resolve()
            if path.parent!=directory.resolve():raise ValueError('archive part must be a direct child')
            if path.stat().st_size!=row['bytes'] or sha(path)!=row['SHA256']:raise ValueError('frozen part changed')
            with path.open('rb') as source:
                for block in iter(lambda:source.read(8*1024*1024),b''):
                    whole.update(block);stream.write(block);total+=len(block)
    if total!=record['logical_bytes'] or whole.hexdigest().upper()!=record['logical_SHA256']:
        raise ValueError('logical archive identity mismatch')
    pending.replace(out)


def run(args):
    if args.out.exists():raise FileExistsError('fresh frozen package required')
    # Check every independent pair before publishing any frozen package.
    pairs=[(args.work/f'{site}_first.json.gz',args.work/f'{site}_repeat.json.gz') for site in ('left_canonical','right_canonical','middle')]
    pairs += [(args.work/'cells_first'/f'cell_{i:02d}.json',args.work/'cells_repeat'/f'cell_{i:02d}.json') for i in range(8)]
    pairs += [(args.work/'remainder_first.json',args.work/'remainder_repeat.json')]
    for a,b in pairs:
        if a.resolve()==b.resolve() or sha(a)!=sha(b):raise ValueError('new artifact reproduction mismatch: '+str(a))
    args.out.mkdir(parents=True)
    execution=args.out/'execution';execution.mkdir()
    models={};sources={};parents={}
    for site,label in (('left','left_canonical'),('right','right_canonical'),('middle','middle')):
        first,repeat=args.work/f'{label}_first.json.gz',args.work/f'{label}_repeat.json.gz'
        metadata=read_graph(first)
        if metadata['interval']!=13 or metadata['site']!=site or metadata['Gate7_closed'] or metadata['physical_budget_debit']:
            raise ValueError('unchanged interval-13 diagnostic scope required')
        for path,h in metadata['source_SHA256'].items():
            if sha(Path(path))!=h:raise ValueError('model source changed')
        family_binding=verify_site_binding(metadata)
        first_work,repeat_work=args.work/f'{label}_first',args.work/f'{label}_repeat'
        first_inputs=(first_work/'immutable_inputs.json').read_bytes()
        repeat_inputs=(repeat_work/'immutable_inputs.json').read_bytes()
        if first_inputs!=repeat_inputs:raise ValueError('repeat must consume the same immutable input receipt')
        storage=json.loads((repeat_work/'storage.json').read_bytes())
        for row in storage:
            path=Path(row['path'])
            if path.resolve().parent!=repeat_work.resolve() or sha(path)!=row['SHA256']:
                raise ValueError('independent repeat must have its own new action outputs')
        expected=[r['SHA256'] for r in metadata['new_action_receipts'] if 'SHA256' in r]
        if [r['SHA256'] for r in storage]!=expected:
            raise ValueError('every new nonsymmetric action receipt must match the independent output inventory')
        (execution/f'{site}_repeat_inputs.json').write_bytes(repeat_inputs)
        (execution/f'{site}_repeat_actions.json').write_bytes(encode(storage))
        models[site]=split_verified(first,repeat,args.out/'models'/site)
        models[site]['independent_missing_model_reproduction_verified']=True
        models[site]['same_physical_family_binding']=family_binding
        parents[site]=models[site]['logical_SHA256']
        data=gzip.compress(encode(metadata),mtime=0)
        (args.out/'models'/site/'metadata.json.gz').write_bytes(data)
        models[site]['metadata_SHA256']=hashlib.sha256(data).hexdigest().upper()
        models[site]['nodes']=metadata['node_count'];models[site]['named_roots']=len(metadata['roots'])
        sources.update(metadata['source_SHA256'])
    cells=args.out/'cells';cells.mkdir()
    for i in range(8):
        p=args.work/'cells_first'/f'cell_{i:02d}.json';z=json.loads(p.read_bytes())
        if z['cell']!=i or z['interval']!=13 or z['common_parent_graphs_SHA256']!=parents:
            raise ValueError('same parent graphs in all eight cells required')
        (cells/p.name).write_bytes(p.read_bytes());sources.update(z['source_SHA256'])
    diagnostic=args.work/'remainder_first.json'
    (args.out/'signed_remainder.json').write_bytes(diagnostic.read_bytes())
    sources.update(json.loads(diagnostic.read_bytes())['source_SHA256'])
    sources[str(Path(__file__).resolve())]=sha(Path(__file__))
    reader=ROOT/'src/bhsm/interface/adaptive_expression_reader.py';sources[str(reader.resolve())]=sha(reader)
    # Preserve every new source needed to interpret these graphs. Inherited
    # scientific operands remain read-only hash references to their receipts.
    capsule=args.out/'new_source_capsule';capsule.mkdir();source_rows=[]
    for path,h in sorted(sources.items()):
        p=Path(path)
        if sha(p)!=h:raise ValueError('consumed source changed before freeze')
        if p.suffix!='.py':continue
        try:relative=p.resolve().relative_to(ROOT)
        except ValueError:continue
        target=capsule/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
        source_rows.append({'original_path':path,'capsule_path':target.relative_to(args.out).as_posix(),'SHA256':h})
    record={'algorithm':'FREEZE_INDEPENDENTLY_REPRODUCED_NEW_INTERVAL13_SHARED_MODELS_V1',
        'frozen_Layer_B_checkpoint':'baf41b96','correlation_audit':'f5b6b4b6','models':models,
        'numerical_environment':{'python':platform.python_version(),'python_flint':flint.__version__,
            'model_arithmetic_precision_bits':512,'serialized_scalars':'exact rational Arb midpoint/radius pairs'},
        'source_capsule':source_rows,'source_SHA256':sources,
        'independently_reproduced_new_pairs':[{'first':str(a.resolve()),'repeat':str(b.resolve()),'SHA256':sha(a)} for a,b in pairs],
        'all_eight_cells_share_the_same_parent_graphs':True,
        'inherited_producers_rerun':False,'intervals14_to18_evaluated':False,
        'full_correlated_Layer_C_certified':False,'physical_budget_debit':False,'Gate7_closed':False}
    (args.out/'reproduction.json').write_bytes(encode(record))
    files={p.relative_to(args.out).as_posix():{'bytes':p.stat().st_size,'SHA256':sha(p)} for p in sorted(args.out.rglob('*')) if p.is_file()}
    (args.out/'manifest.json').write_bytes(encode({'format':'FROZEN_NEW_SHARED_MODEL_PACKAGE_V1','files':files,'logical_model_bytes':sum(v['logical_bytes'] for v in models.values())}))
    print(json.dumps({'frozen_new_pairs':len(pairs),'models':parents,'logical_model_bytes':sum(v['logical_bytes'] for v in models.values())}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('freeze');a.add_argument('--work',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('restore');a.add_argument('--archive',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.command=='restore':restore_archive(args.archive,args.out)
    else:run(args)
