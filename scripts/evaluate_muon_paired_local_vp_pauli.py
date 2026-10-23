"""Apply the actual normalized continuum local VP overlap and soft bound."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_paired_local_vp_pauli import paired_local_vp_pauli,signed_soft_overlap_enclosure


def materialize(output,*,precision_bits=192):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve executed continuum applications')
    names=['artifacts/muon_calibrated_pauli_20261009/inputs.json',
        'src/bhsm/interface/muon_paired_local_vp_pauli.py',
        'src/bhsm/interface/muon_calibrated_local_pauli.py',
        Path(__file__).relative_to(ROOT).as_posix()]
    hashes={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
    config=json.loads((ROOT/names[0]).read_bytes())
    result=paired_local_vp_pauli(
        alpha_inverse_decimal=config['primary_measurements']['alpha_inverse_0']['value_decimal'],
        mass_ratio_decimal=config['primary_measurements']['muon_electron_mass_ratio']['value_decimal'],
        precision_bits=precision_bits)
    result['signed_soft_applications']=[signed_soft_overlap_enclosure(result,t) for t in (-.01,.01,.003)]
    result['input_hashes']=hashes
    result['primary_source']='https://arxiv.org/abs/2210.11071; Thomson VP and same-mass coefficient Eq46'
    result['physical_native_subtraction_consumer']='subtract this overlap only AFTER common photon/current/domain and external muon-shell matching; it is already contained in frozen local QED'
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in names}:
        raise RuntimeError('consumed inputs changed during continuum contraction')
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--precision-bits',type=int,default=192)
    a=p.parse_args();print(json.dumps(materialize(a.output,precision_bits=a.precision_bits),sort_keys=True))
