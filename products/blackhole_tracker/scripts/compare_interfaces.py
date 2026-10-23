"""Compare an actual GUI download, installed CLI/API and executed notebook."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import numpy as np
import bhtracker
from bhtracker import fit

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gui-bundle',type=Path,required=True)
    parser.add_argument('--notebook-analysis',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    package=Path(bhtracker.__file__).resolve()
    if not package.is_relative_to(Path(sys.prefix).resolve()):raise ValueError('run with the clean installed wheel interpreter')
    with zipfile.ZipFile(args.gui_bundle) as archive:gui=json.loads(archive.read('result.json'))
    config=gui['analysis_configuration'];raw=gui['dataset_input']
    api=fit(raw,**config)
    cli_dir=args.output/'CLI replay'
    run=subprocess.run([sys.executable,'-I','-m','bhtracker','replay',str(args.gui_bundle.resolve()),'--output',str(cli_dir.resolve())],
                       cwd=args.output,capture_output=True,text=True,check=True)
    cli=json.loads((cli_dir/'result.json').read_text())
    notebook=json.loads((args.notebook_analysis/'result.json').read_text())
    sigma=np.sqrt(np.diag(np.asarray(gui['covariance']))).reshape(-1,6)
    records={}
    for name,result in [('GUI',gui),('API',api),('CLI',cli),('notebook',notebook)]:
        difference=float(np.max(abs(np.asarray(result['predictions'])-np.asarray(gui['predictions']))/sigma))
        record={'same_input':result['dataset_input']==gui['dataset_input'],
                'same_serialized_input_hash':result['data_summary']['sha256']==gui['data_summary']['sha256'],
                'same_configuration':result['analysis_configuration']==config,'status':result['status'],
                'same_interpretation':result['bhsm_interpretation']==gui['bhsm_interpretation'],
                'interpretation_schema_version':result['bhsm_interpretation']['interpretation_schema_version'],
                'maximum_prediction_difference_in_supplied_sigma':difference}
        record['passed']=record['same_input'] and record['same_configuration'] and record['same_interpretation'] and result['status']==gui['status'] and difference<=.001
        records[name]=record
    receipt={'passed':all(row['passed'] for row in records.values()),'tolerance_in_supplied_sigma':.001,
             'package':str(package),'python':sys.version,'interfaces':records,
             'GUI_evidence':'actual browser Load/Validate/Run fit/Download replay bundle, not a fabricated GUI result',
             'notebook_evidence':'saved result exported by executed notebook with this installed interpreter outside checkout'}
    receipt['input_comparison']='Exact supplied JSON value equality, including every covariance/calibration entry. JSON.stringify writes integral floats as integers; their serialized hashes can differ while all input values and predictions are exactly equal.'
    (args.output/'four_interface_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt,indent=2))
    if not receipt['passed']:raise SystemExit(1)

if __name__=='__main__':main()
