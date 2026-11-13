"""Materialize and independently check the actual known wall/current rows."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from bhsm.interface.retained_response.field_spin_connection import verify_application_result
from bhsm.interface.retained_response.finite_time_response import write_npz
from bhsm.interface.retained_response.operator_current_system import (
    assemble_known_open_system,hermitian_coordinates,
)

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_retained_response_20261018/run_A'
MATTER=ROOT/'artifacts/muon_causal_operator_wall_current_20261018/run_A'


def load(path):
    with np.load(path,allow_pickle=False) as source:
        return {k:source[k].copy() for k in source.files}


def main(out):
    verify_application_result(BASE)
    out.mkdir(parents=True,exist_ok=False)
    sources=json.loads((MATTER/'result.json').read_text())
    records={}
    for side in ('incoming','outgoing'):
        path=MATTER/f'{side}_causal_operator_current.npz'
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sources['sides'][side]['artifact']['sha256']:
            raise ValueError('current input changed: '+side)
        classical=load(BASE/f'{side}_joint_open_response.npz');current=load(path)
        arrays=assemble_known_open_system(classical,current)
        # A signed Hermitian algebra probe checks trace-dual signs and composition.
        # It is not a positive physical occupation or a selected reference.
        raw=np.sin(np.arange(900).reshape(30,30)+.23)+1j*np.cos(np.arange(900).reshape(30,30)+.17)
        probe=.001*(raw+raw.conj().T)
        eta=.02*np.sin(np.arange(574)+.31);n=hermitian_coordinates(probe)
        independently=classical['classical_wall_map']@eta+np.einsum('ij,cji->c',probe,current['actual_direct_plus_causal_wall134_hat'])
        difference=arrays['known_wall_map']@np.r_[eta,n]-independently
        target=out/f'{side}_known_current_open_system.npz';write_npz(target,arrays)
        records[side]=dict(path=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            input_current_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            trace_composition_maximum_entry_absolute=float(np.max(abs(difference))),
            known_wall_shape=list(arrays['known_wall_map'].shape),known_final_shape=list(arrays['known_final_map'].shape))
        if np.max(abs(difference))>2e-14:
            raise ArithmeticError('independent trace/current composition failed')
    result=dict(classification='EVALUATED_KNOWN_CLASSICAL_AND_CAUSAL_OPERATOR_CURRENT_OPEN_ROWS',
        coordinates='eta574 and explicit Hermitian occupation coordinates900',records=records,
        physical_state_selected=False,physical_wall_closed=False,complete_physical_derivative_admitted=False,
        physical_a_mu=None,physical_g_mu=None,physical_uncertainty=None,
        NEXT_OPERAND='Add the actual collision/interface/source/domain/normal/native/exterior/reference equations; these known rows are not a homogeneous wall law.')
    (out/'CHECKPOINT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(records,sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    main(p.parse_args().output)
