"""Consume the continuum VP overlap with the existing normalized soft target."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_calibrated_local_pauli import pauli_tensors,local_spin_pole_application
from bhsm.interface.muon_paired_local_vp_pauli import signed_soft_overlap_enclosure
from evaluate_muon_native_product_factor_graph import serial,deterministic_npz


def materialize(application,output):
    folder=Path(application);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve normalized physical-sector applications')
    path=folder/'result.json';md=json.loads(path.read_bytes())
    if md['classification']!='EVALUATED_NORMALIZED_CONTINUUM_PAIRED_LOCAL_VP_PAULI_OVERLAP':
        raise ValueError('actual continuum Pauli overlap required')
    hashes=dict(md['input_hashes'])
    for name,digest in hashes.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('continuum producer changed: '+name)
    config=json.loads((ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json').read_bytes())
    # The pole matching has already consumed these primitive measurements.
    # It is not a new adjustment of the inherited family operator.
    m=float(config['selected_consumer_values']['m_mu_GeV']['value'])
    arrays={};rows=[]
    for j,u in enumerate(np.eye(3)):
        D,Pu=pauli_tensors(np.r_[0.,m*u],m)
        dd=np.vdot(D,D).real;perp=Pu-D*np.vdot(D,Pu)/dd
        norm=np.vdot(perp,perp).real
        if not norm>0:raise ArithmeticError('soft Pauli target has vanished')
        L=perp/norm;arrays[f'axis_{j}_Dirac']=D;arrays[f'axis_{j}_Pauli']=Pu;arrays[f'axis_{j}_readout']=L
        for t in (-.01,.01,.003):
            _,Pt=pauli_tensors(np.r_[0.,t*m*u],m)
            # Apply the signed tensor derivative to the actual target;
            # the physical scalar at finite t remains enclosed, not guessed.
            unit=np.vdot(L,Pt)/t
            row=signed_soft_overlap_enclosure(md,t,direction_norm_squared=float(u@u))
            row.update(axis=j,Dirac_annihilation_defect=float(abs(np.vdot(L,D))),
                Pauli_unit_pairing_defect=float(abs(np.vdot(L,Pu)-1)),
                signed_tensor_derivative_unit_pairing=dict(real=float(unit.real),imag=float(unit.imag)),
                external_spin_poles=[local_spin_pole_application(m,abs(t)*m/2,spin=s) for s in (-1,1)],
                physical_scope='renormalized local VP graph on calibrated muon mass shell; not an interacting BHSM pole')
            rows.append(row)
    for p in (path,Path(__file__),ROOT/'src/bhsm/interface/muon_calibrated_local_pauli.py',
        ROOT/'src/bhsm/interface/universal_precision_form_factor.py',ROOT/'src/bhsm/interface/universal_lsz.py'):
        hashes[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:raise RuntimeError('matched soft target changed')
    out.mkdir(parents=True);data=deterministic_npz(arrays);(out/'readout.npz').write_bytes(data)
    result=dict(classification='EVALUATED_CONTINUUM_LOCAL_PAIRED_VP_NORMALIZED_SIGNED_SOFT_READOUT',
        input_hashes=hashes,muon_mass_GeV=m,applications=rows,
        paired_zero_transfer_Pauli_interval=md['paired_muon_minus_electron_interval'],
        graph_g_mu_contribution_interval=[2*x for x in md['paired_muon_minus_electron_interval']],
        archive=dict(path='readout.npz',bytes=len(data),sha256=sha256(data).hexdigest()),
        charge_normalization='Thomson charge divided once before Pauli target',
        LSZ_scope='calibrated local on-shell spin-sector residue; Dirac counterterms annihilated analytically by transverse Pauli target',
        frozen_local_overlap_already_counted=True,added_to_frozen_subtotal=False,
        matched_native_boundary_overlap_subtracted=False,complete_a_mu=None,complete_g_mu=None,
        error_scope='certified exact-central continuum graph and spectral soft remainder; tensor/pole residuals are binary64 diagnostics, not interacting native matching or total anomaly uncertainty')
    (out/'result.json').write_text(json.dumps(serial(result),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],paired_zero_transfer_Pauli_interval=result['paired_zero_transfer_Pauli_interval'],
        maximum_Dirac_annihilation_defect=max(r['Dirac_annihilation_defect'] for r in rows),
        maximum_Pauli_unit_pairing_defect=max(r['Pauli_unit_pairing_defect'] for r in rows))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.application,a.output),sort_keys=True))
