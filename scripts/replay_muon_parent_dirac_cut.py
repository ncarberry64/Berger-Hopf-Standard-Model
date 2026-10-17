"""New canonical bulk body action; reuse the completed source/contact run."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np


def run(root, cached_contact, output):
    if output.exists():raise FileExistsError('Fresh output directory required')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_parent_source_contact import cut_metric_dirac_actions,retained_source_cut_rate
    source=root/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz'
    geometry=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'
    rate=retained_source_cut_rate(root)
    with np.load(source) as s,np.load(geometry) as g,np.load(cached_contact) as c:
        arrays,checks=cut_metric_dirac_actions(s,g,c,cut_rate=rate)
    output.mkdir(parents=True)
    np.savez_compressed(output/'parent_metric_dirac_actions.npz',**arrays)
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def save(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
    save(output/'result.json',dict(
        classification='canonical metric/common-A bulk Dirac summand on compact cut probes/source image',
        calculation_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        source_cut_rate=rate,
        equations=dict(coframe='theta0=nu dtau; theta4=C(drho+zeta dtau); thetaa=r thetaR_a',
            h0='[(partial_tau-zeta partial_rho)log(C r^3)-partial_rho zeta]/(2nu)',
            h4='partial_rho log(nu r^3)/(2C)',
            C_spin='i gamma0 h0+i gamma4 h4-3i gamma1 gamma2 gamma3/(2r)',
            D5='i gamma0/nu (partial_tau-zeta partial_rho)+i gamma4/C partial_rho+i gammaa/r E_a+C_spin+i gammaa ((lambda-1)/r) jmath_a',
            E_a='coefficient action +2iJ_a on active m, saved RIGHT coframe',
            source_image_time_jet='D5(Xi_A chi b)=D5_image_b*b+D5_image_b_tau*partial_tau b; T_b_prime=-H T_b/2'),
        checks=checks,
        input_interpolation='piecewise affine rho; right derivative on first inherited forward time cell',
        scope='one sheet, one family, canonical metric/common-A summand. Owned additional zero-order/interface/quotient/temporal-domain terms unevaluated, never assigned zero.',
        source_scope='all n1+n3 and 64 output components retained for four spin probes on one charged weak-doublet coordinate; no physical-state choice',
        error_scope='binary64 body/actions and four-point cut quadrature; no certified rational-Dirac quadrature, interpolation/history or complement error',
        execution=dict(old_producers=0,source_contact_recomputed=False,native_heat_actions=0,causal_returns=0,physical_transfer_directions=0),
        physical_a_mu=None,physical_g_mu=None))
    inputs=[source,geometry,cached_contact,root/'src/bhsm/interface/muon_parent_source_contact.py',Path(__file__)]
    save(output/'input_hashes.json',[dict(path=str(p),sha256=sha(p)) for p in inputs])
    save(output/'receipt.json',dict(files=[dict(path=p.name,sha256=sha(p)) for p in sorted(output.iterdir())]))
    print(json.dumps(dict(output=str(output),checks=checks)))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--contact',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.contact.resolve(),a.output.resolve())
