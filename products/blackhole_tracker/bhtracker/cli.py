import argparse
import json
from pathlib import Path
from .data import load_dataset
from .examples import make_example,TITLES
from .inference import fit,profile
from .report import export_result,replay_analysis

def main(argv=None):
    parser=argparse.ArgumentParser(prog='blackhole-tracker',description='BHSM compact-lens research: resolved images, native photometry and optional joint astrometry; mass requires identifying observations')
    commands=parser.add_subparsers(dest='command',required=True)
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
    args=parser.parse_args(argv)
    try:
        if args.command=='example':
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
                              'parameters':result['parameters'],'output':str(args.output.resolve())},indent=2,allow_nan=False))
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
            serve(args.port,args.open)
    except ImportError:
        parser.exit(2,'The joint route requires the matching wheel with its [astrometry] extra, including Astropy.\n')
    except (ValueError,OSError,KeyError) as error:
        parser.exit(2,f'Input/model error: {error}\n')

if __name__=='__main__':
    import sys
    sys.exit(main())
