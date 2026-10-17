"""Replay only the saved source-time repair and canonical trial conormal.

Point --packet-root at the extracted BHSM_muon_source_rate_and_conormal packet.
This loader imports the one exact operator module without the unrelated BHSM
package initializers. It does not construct a new physical operator or state.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
import types


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    root=a.packet_root.resolve();out=a.output.resolve()
    if out.exists():raise FileExistsError('Use a fresh output directory')
    manifest=json.loads((root/'bundle_hashes.json').read_text())
    for entry in manifest:
        path=root/entry['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('Changed packet input: '+entry['path'])
    out.mkdir(parents=True)
    for name,folder in [('bhsm',root/'src/bhsm'),('bhsm.interface',root/'src/bhsm/interface')]:
        module=types.ModuleType(name);module.__path__=[str(folder)]
        sys.modules[name]=module
    def run_script(name,args):
        script=root/'scripts'/name
        saved=sys.argv
        try:
            sys.argv=[str(script),'--repository',str(root)]+args
            runpy.run_path(str(script),run_name='__main__')
        finally:sys.argv=saved
    run_script('replay_muon_parent_source_rate.py',['--output',str(out/'repair')])
    run_script('replay_muon_corrected_spinor_conormal.py',[
        '--corrected',str(out/'repair/parent_source_rate_corrected.npz'),
        '--output',str(out/'conormal')])
    print(json.dumps(dict(output=str(out),scope='additive finite-array repair and canonical trial conormal',
        stationary_exterior_response_applications=0,native_heat_evaluations=0,physical_transfer_directions=0)))


if __name__=='__main__':main()
