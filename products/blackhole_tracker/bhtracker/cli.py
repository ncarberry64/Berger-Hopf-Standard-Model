import argparse
import json
from pathlib import Path
from .data import load_dataset
from .examples import make_example,TITLES
from .inference import fit,profile
from .report import export_result,replay_analysis

def main(argv=None):
    parser=argparse.ArgumentParser(prog='blackhole-tracker',description='Resolved compact-lens mass/motion and conditional R1 research inference')
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
        elif args.command=='validate':print(json.dumps({'valid':True,'summary':load_dataset(args.dataset).summary()},indent=2))
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
        elif args.command=='serve':
            from .server import serve
            serve(args.port,args.open)
    except (ValueError,OSError,KeyError) as error:
        parser.exit(2,f'Input/model error: {error}\n')

if __name__=='__main__':main()
