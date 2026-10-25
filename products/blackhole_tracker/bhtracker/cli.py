import argparse
import json
import sys
from pathlib import Path
from .data import load_dataset
from .examples import make_example,TITLES
from .inference import fit,profile
from .report import export_result,replay_analysis

def main(argv=None):
    arguments=list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0]=='known-system':
        # Lazy, lossless delegation keeps the research engine and optional
        # dependencies separate from every existing command and optical route.
        try:
            from .known_system_v3 import main as known_main
            return known_main(arguments[1:])
        except ImportError as error:
            print('Known-system research needs the optional joint-research dependencies: '+str(error),file=sys.stderr)
            raise SystemExit(2) from error
        except (ValueError,OSError,KeyError,RuntimeError,FloatingPointError) as error:
            print('Known-system input/model error: '+str(error),file=sys.stderr)
            raise SystemExit(2) from error
    parser=argparse.ArgumentParser(prog='blackhole-tracker',description='BHSM compact-lens research: resolved images, native photometry and optional joint astrometry; mass requires identifying observations')
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('known-system',help='versioned Gaussian/spectral research engine; use known-system --help (scientific acceptance pending)')
    ex=commands.add_parser('example',help='write a reproducible synthetic measurement set')
    ex.add_argument('name',choices=list(TITLES),nargs='?',default='nearby_motion');ex.add_argument('--output',type=Path,required=True)
    val=commands.add_parser('validate');val.add_argument('dataset',type=Path)
    imp=commands.add_parser('import-csv',help='combine measurements, metadata and a required full covariance')
    imp.add_argument('measurements',type=Path);imp.add_argument('--metadata',type=Path,required=True)
    imp.add_argument('--covariance',type=Path,required=True);imp.add_argument('--output',type=Path,required=True)
    run=commands.add_parser('fit');run.add_argument('dataset',type=Path);run.add_argument('--family',choices=['gr','r1'],default='gr')
    run.add_argument('--nuisance',choices=['none','shear','full'],default='shear');run.add_argument('--starts',type=int,default=2)
    run.add_argument('--output',type=Path,required=True)
    native=commands.add_parser('import-ogle3',help='preserve native optimized OGLE-III magnitudes, errors, times and source row identities')
    native.add_argument('measurements',type=Path);native.add_argument('--metadata',type=Path)
    native.add_argument('--output',type=Path,required=True)
    benchmark=commands.add_parser('import-benchmark',help='import the versioned 2022 Zenodo OGLE/MOA photometry with separate instruments')
    benchmark.add_argument('--ogle',type=Path,required=True);benchmark.add_argument('--moa',type=Path,required=True)
    benchmark.add_argument('--output',type=Path,required=True)
    astrometry=commands.add_parser('import-hst',help='preserve native HST rows and report missing precision-inference metadata')
    astrometry.add_argument('--f606w',type=Path,required=True);astrometry.add_argument('--f814w',type=Path,required=True)
    astrometry.add_argument('--metadata',type=Path);astrometry.add_argument('--output',type=Path,required=True)
    phot=commands.add_parser('fit-photometry',help='fit all unresolved native magnitude rows; lens mass remains unavailable')
    phot.add_argument('dataset',type=Path);phot.add_argument('--starts',type=int,default=12)
    phot.add_argument('--max-nfev',type=int,default=1500);phot.add_argument('--noise-scale',type=float,default=1.)
    phot.add_argument('--equal-instrument-weight',action='store_true')
    phot.add_argument('--allow-negative-blend',action='store_true',help='phenomenological calibration-offset sensitivity, not negative stellar luminosity')
    phot.add_argument('--output',type=Path,required=True)
    photprof=commands.add_parser('profile-photometry',help='reoptimize admissible nuisance states at fixed photometric timescales')
    photprof.add_argument('dataset',type=Path);photprof.add_argument('result',type=Path)
    photprof.add_argument('--timescales',nargs='+',type=float,required=True);photprof.add_argument('--output',type=Path,required=True)
    joint=commands.add_parser('joint',help='joint calibrated photometry/astrometry research workflow (use joint --help for commands)')
    joint.add_argument('--scientific-version',choices=['v1','v2'],default='v2')
    joint.add_argument('workflow_arguments',nargs=argparse.REMAINDER,help='import, fit, profile or replay and their arguments')
    jexport=commands.add_parser('export-joint',help='verify and export a saved joint result as a portable replay bundle directory')
    jexport.add_argument('result',type=Path);jexport.add_argument('--output',type=Path,required=True)
    replay=commands.add_parser('replay',help='verify and reproduce an exported analysis ZIP or directory')
    replay.add_argument('analysis',type=Path);replay.add_argument('--output',type=Path,required=True)
    prof=commands.add_parser('profile');prof.add_argument('dataset',type=Path);prof.add_argument('result',type=Path)
    prof.add_argument('--parameter',choices=['mass_msun','motion_x','motion_y'],default='mass_msun');prof.add_argument('--output',type=Path,required=True)
    serve=commands.add_parser('serve');serve.add_argument('--port',type=int,default=8765);serve.add_argument('--open',action='store_true')
    serve.add_argument('--page',choices=['resolved','photometry','photometry-mc','joint','atlas','spectrum','skytrack'],default='resolved')
    mc=commands.add_parser('mc-photometry',help='pending approximate fixed-node MC inference, durable audit/export and saved-state replay; no BH mass')
    mc_commands=mc.add_subparsers(dest='mc_command',required=True)
    mc_run=mc_commands.add_parser('run');mc_run.add_argument('dataset',type=Path)
    mc_run.add_argument('--timescales',nargs='+',type=float);mc_run.add_argument('--impacts',nargs='+',type=float)
    mc_run.add_argument('--entropy',nargs='+',type=int,required=True);mc_run.add_argument('--output',type=Path,required=True)
    mc_run.add_argument('--wall-seconds',type=int,default=600);mc_run.add_argument('--max-saved-bytes',type=int,default=268435456)
    mc_status=mc_commands.add_parser('status');mc_status.add_argument('workspace',type=Path)
    mc_export=mc_commands.add_parser('export');mc_export.add_argument('workspace',type=Path);mc_export.add_argument('--output',type=Path,required=True)
    mc_export.add_argument('--max-archive-bytes',type=int,default=536870912)
    mc_replay=mc_commands.add_parser('replay');mc_replay.add_argument('bundle',type=Path)
    mc_replay.add_argument('--mode',choices=['integrity','numerical'],default='integrity');mc_replay.add_argument('--wall-seconds',type=int,default=120)
    mc_replay.add_argument('--max-states',type=int,default=100000);mc_replay.add_argument('--output',type=Path)
    spectrum=commands.add_parser('spectrum',help='inspect/export/verify the frozen read-only evidence spectrum; no fitting or classification')
    spectrum_commands=spectrum.add_subparsers(dest='spectrum_command',required=True)
    spectrum_commands.add_parser('summary')
    spectrum_export=spectrum_commands.add_parser('export');spectrum_export.add_argument('--output',type=Path,required=True)
    spectrum_verify=spectrum_commands.add_parser('verify');spectrum_verify.add_argument('directory',type=Path)
    skytrack=commands.add_parser('skytrack',help='measured lens angular track with supplied covariance; no mass or black-hole identity inference')
    sky_commands=skytrack.add_subparsers(dest='skytrack_command',required=True)
    sky_example=sky_commands.add_parser('example');sky_example.add_argument('--output',type=Path,required=True)
    sky_validate=sky_commands.add_parser('validate');sky_validate.add_argument('input',type=Path)
    sky_fit=sky_commands.add_parser('fit');sky_fit.add_argument('input',type=Path);sky_fit.add_argument('--output',type=Path,required=True)
    sky_fit.add_argument('--reference-native-time',type=float);sky_fit.add_argument('--alpha',type=float)
    sky_replay=sky_commands.add_parser('replay');sky_replay.add_argument('result',type=Path);sky_replay.add_argument('--output',type=Path)
    sky_export=sky_commands.add_parser('export');sky_export.add_argument('result',type=Path);sky_export.add_argument('--output',type=Path,required=True)
    atlas=commands.add_parser('atlas',help='catalog directions, evidence-qualified targets and lossless candidate-inventory replay; no physical fitting')
    atlas_commands=atlas.add_subparsers(dest='atlas_command',required=True)
    for name in ('list','export'):
        sub=atlas_commands.add_parser(name)
        sub.add_argument('--inventory',type=Path,help='versioned external inventory; default is the bundled reviewed catalog')
        for field in ('query','tier','cohort','flag'):
            sub.add_argument('--'+field,default='')
        sub.add_argument('--sort',choices=['event_id','ra_deg','tier'],default='event_id')
        sub.add_argument('--output',type=Path,required=name=='export')
    atlas_validate=atlas_commands.add_parser('validate');atlas_validate.add_argument('inventory',type=Path)
    atlas_replay=atlas_commands.add_parser('replay');atlas_replay.add_argument('bundle',type=Path)
    atlas_replay.add_argument('--output',type=Path,help='fresh directory for exact inventory bytes and selected records')
    args=parser.parse_args(argv)
    try:
        if args.command=='mc-photometry':
            from .photometry_mc import MCWorkspace,workspace_status,canonical
            from .photometry_mc_replay import export_workspace,replay_bundle,summary
            if args.mc_command=='run':
                grids={}
                if args.timescales is not None:grids['tE_days']=args.timescales
                if args.impacts is not None:grids['u0']=args.impacts
                workspace=MCWorkspace(args.dataset,grids,args.entropy,args.output,wall_seconds=args.wall_seconds,max_saved_bytes=args.max_saved_bytes)
                print('Local pending MC audit: '+str(workspace.directory),flush=True)
                result=workspace.run();value=summary(workspace.request,result)
            elif args.mc_command=='status':value=workspace_status(args.workspace)
            elif args.mc_command=='export':value=export_workspace(args.workspace,args.output,max_archive_bytes=args.max_archive_bytes)
            else:value=replay_bundle(args.bundle,mode=args.mode,wall_seconds=args.wall_seconds,max_states=args.max_states)
            if args.mc_command=='replay' and args.output:
                with args.output.open('xb') as stream:stream.write(canonical(value))
                print(str(args.output.resolve()))
            else:print(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False))
        elif args.command=='skytrack':
            from . import skytrack
            if args.skytrack_command=='example':value=skytrack.synthetic_example()
            elif args.skytrack_command=='validate':value=skytrack.validate_skytrack(args.input.read_bytes().decode('utf8'))
            elif args.skytrack_command=='fit':value=skytrack.fit_skytrack(args.input.read_bytes().decode('utf8'),reference_native_time=args.reference_native_time,significance_alpha=args.alpha)
            else:
                saved=skytrack._document(args.result.read_bytes().decode('utf8'),max_bytes=96_000_000)[0]
                value=skytrack.replay_skytrack(saved) if args.skytrack_command=='replay' else skytrack.export_skytrack(saved,args.output)
            if args.skytrack_command in ('example','fit') or (args.skytrack_command=='replay' and args.output):
                args.output.parent.mkdir(parents=True,exist_ok=True)
                with args.output.open('xb') as stream:stream.write((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8'))
                print(str(args.output.resolve()))
            else:print(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False))
        elif args.command=='spectrum':
            from . import spectrum
            if args.spectrum_command=='summary':value=spectrum.summary()
            elif args.spectrum_command=='export':value=spectrum.export_snapshot(args.output)
            else:value=spectrum.verify_snapshot(args.directory)
            print(json.dumps(value,indent=2,allow_nan=False))
        elif args.command=='atlas':
            from . import candidate_atlas as cat
            if args.atlas_command=='replay':
                checked=cat.validate_replay(cat.read_json(args.bundle.read_bytes().decode('utf-8')))
                if args.output:
                    args.output.mkdir(parents=True,exist_ok=False)
                    (args.output/'inventory.json').write_bytes(checked['inventory_json'].encode('utf-8'))
                    (args.output/'selected_events.json').write_text(json.dumps({'metadata':checked['inventory']['metadata'],
                        'filters':checked['filters'],'events':checked['filtered_events']},indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
                print(json.dumps({'verified':True,'scope':'Inventory consistency only; no fit, classification inference or uncertainty calibration',
                    'inventory_utf8_sha256':checked['inventory_utf8_sha256'],**cat.summary(checked['inventory'],checked['filters'])},indent=2))
            else:
                inventory,text=cat.load_inventory(args.inventory)
                if args.atlas_command=='validate':
                    print(json.dumps({'valid':True,'inventory_utf8_sha256':cat.text_sha256(text),**cat.summary(inventory)},indent=2))
                else:
                    filters={k:getattr(args,k) for k in cat.default_filters()}
                    value=cat.create_replay(text,filters,origin='blackhole-tracker atlas export') if args.atlas_command=='export' else {
                        **cat.summary(inventory,filters),'filters':filters,'events':cat.filter_events(inventory,filters)}
                    rendered=json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
                    if args.output:
                        args.output.parent.mkdir(parents=True,exist_ok=True)
                        with args.output.open('x',encoding='utf-8',newline='\n') as stream:stream.write(rendered)
                        print(str(args.output.resolve()))
                    else:print(rendered)
        elif args.command=='example':
            data,truth=make_example(args.name);args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8');print(str(args.output.resolve()))
        elif args.command=='validate':
            from .data import read_json
            raw=read_json(args.dataset.read_bytes())
            if raw.get('schema')=='bhsm_unresolved_observations/1':
                from .observations import UnresolvedPhotometry
                data=UnresolvedPhotometry.from_dict(raw)
                summary={'route':raw['schema'],'native_magnitude_rows':len(data.rows),'instruments':list(data.instruments),
                         'input_sha256':data.sha256,'mass_status':'MASS_UNRESOLVED','timing_and_calibration':raw['instruments']}
            elif raw.get('schema')=='bhtracker.native_joint_mass.v1':
                from .server import joint_dataset,joint_summary
                summary=joint_summary(joint_dataset(raw))
            else:summary=load_dataset(raw).summary()
            print(json.dumps({'valid':True,'summary':summary},indent=2,allow_nan=False))
        elif args.command in ('import-ogle3','import-benchmark','import-hst'):
            from .data import read_json
            metadata=read_json(args.metadata.read_bytes()) if getattr(args,'metadata',None) else None
            if args.command=='import-ogle3':
                from .observations import load_ogle_photometry
                raw=load_ogle_photometry(args.measurements,metadata=metadata).to_dict()
            elif args.command=='import-benchmark':
                from .observations import load_benchmark_photometry
                raw=load_benchmark_photometry({'OGLE':args.ogle,'MOA':args.moa}).to_dict()
            else:
                from .astrometry import load_hst_astrometry
                raw=load_hst_astrometry({'F606W':args.f606w,'F814W':args.f814w},metadata=metadata)
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(raw,indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(json.dumps({'output':str(args.output.resolve()),'schema':raw['schema'],'native_rows':len(raw['rows']),
                              'precision_inference':raw.get('precision_inference')},indent=2,allow_nan=False))
        elif args.command=='fit-photometry':
            from .data import read_json
            from .photometry import fit_photometry
            result=fit_photometry(read_json(args.dataset.read_bytes()),starts=args.starts,max_nfev=args.max_nfev,
                noise_scale=args.noise_scale,equal_instrument_weight=args.equal_instrument_weight,
                allow_negative_blend=args.allow_negative_blend)
            export_result(result,args.output)
            print(json.dumps({'status':result['status'],'mass_status':result['mass_status'],
                              'parameters':result['parameters'],'bhsm_interpretation':result['bhsm_interpretation'],'output':str(args.output.resolve())},indent=2,allow_nan=False))
        elif args.command=='profile-photometry':
            from .data import read_json
            from .photometry import profile_timescale
            value=profile_timescale(read_json(args.dataset.read_bytes()),read_json(args.result.read_bytes()),args.timescales)
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(str(args.output.resolve()))
        elif args.command=='import-csv':
            from .importers import import_measurement_csv
            raw=import_measurement_csv(args.measurements,args.metadata,args.covariance)
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(raw,indent=2,allow_nan=False)+'\n',encoding='utf8')
            print(json.dumps({'valid':True,'output':str(args.output.resolve()),'summary':load_dataset(raw).summary()},indent=2))
        elif args.command=='fit':
            result=fit(args.dataset,family=args.family,nuisance=args.nuisance,starts=args.starts)
            export_result(result,args.output)
            print(json.dumps({'status':result['status'],'estimates':result['estimates'],
                  'bhsm_interpretation':result['bhsm_interpretation'],'output':str(args.output.resolve())},indent=2))
        elif args.command=='profile':
            r=profile(args.dataset,json.loads(args.result.read_text()),parameter=args.parameter)
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(r,indent=2)+'\n');print(str(args.output.resolve()))
        elif args.command=='replay':print(json.dumps(replay_analysis(args.analysis,args.output),indent=2))
        elif args.command=='joint':
            if args.scientific_version=='v2':
                from .joint_workflow_v2 import main as joint_main
            else:
                from .joint_workflow import main as joint_main
            return joint_main(args.workflow_arguments)
        elif args.command=='export-joint':
            from .data import read_json
            from .joint_report import export_result as export_joint
            print(export_joint(read_json(args.result.read_bytes()),args.output))
        elif args.command=='serve':
            from .server import serve
            serve(args.port,args.open,args.page)
    except ImportError:
        parser.exit(2,'The joint route requires the matching wheel with its [astrometry] extra, including Astropy.\n')
    except (ValueError,OSError,KeyError) as error:
        parser.exit(2,f'Input/model error: {error}\n')

if __name__=='__main__':
    import sys
    sys.exit(main())
