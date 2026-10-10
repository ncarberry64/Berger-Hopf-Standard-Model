#!/usr/bin/env python
"""Combine frozen physical hadronic applications and evaluate their gradients."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_hadronic_ledger import calibrated_hadronic_ledger


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    packet=calibrated_hadronic_ledger(ROOT,progress=lambda text:print(text,flush=True,file=sys.stderr))
    args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/'physical_hadronic_ledger.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),bytes=target.stat().st_size,
                         sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                         evaluated_subtotal=packet['evaluated_subtotal'],
                         HVP_subtotal=packet['HVP_subtotal'],HLbL_projection=packet['HLbL_projection'],
                         spectral_standard_uncertainty=packet['spectral_standard_uncertainty'],
                         selected_input_gradient=packet['selected_input_gradient'],
                         NNLO_UV_tail=packet['errors']['UV_tail_NNLO']),sort_keys=True))


if __name__=='__main__':
    main()
