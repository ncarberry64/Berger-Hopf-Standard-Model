"""Reached local-Fermi template test of the on-shell current tensor.

This compares the actual muon-source/electron-readout kernel with the
local charged-current operator in exactly the same transported Cauchy
frame.  It does not substitute a W mass or infer a physical c_F from a fit.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from flint import arb,ctx

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_parent_mean_causal_action import VOLUME
from .muon_primal_charged_current_response import charged_current_matrices


def transported_fermi_template(midpoint_lift,*,N,R4,step):
    """Local Fermi operator in canonical chi and HS current coordinates.

    chi_hat=R4^(3/2)psi/V, angular carrier=1/sqrt(V), V=2pi².
    Raw intrinsic S4 is divided by V² in the common cap action.
    The cross-family action is -4sqrt2*c_F*h*N*V/R4³ times
    j1,e eta j1,mu+j2,e eta j2,mu.  Each local current is pulled by
    the actual midpoint map V_c=(I+U)/2 to the initial Cauchy frame.
    This is the declared unit canonical-fermion action convention.
    """
    if midpoint_lift is None or any(x is None or not np.isrealobj(x) for x in (N,R4,step)):
        raise ValueError('explicit midpoint lift and real metric/step required')
    V=np.asarray(midpoint_lift,complex)
    if V.shape!=(18,18) or not np.isfinite(V).all() or not np.isfinite([N,R4,step]).all() or N<=0 or R4<=0 or step==0:
        raise ValueError('actual complete midpoint lift, positive metric, and oriented nonzero step required')
    maps={}
    for family,name in ((1,'muon'),(2,'electron')):
        X=charged_current_matrices(family)
        moved=np.einsum('ij,ajk,kl->ail',V.conj().T,X,V)
        L=np.einsum('bij,aji->ab',X,moved)
        if np.max(abs(L.imag))>1e-12*max(1.,np.max(abs(L))):raise ValueError('Hermitian transported current map must be real')
        maps[name]=L.real
    eta=np.diag([1.,-1.,-1.,-1.]);metric=np.kron(np.eye(2),eta)
    density=-4*np.sqrt(2)*step*N*VOLUME/R4**3
    tensor=density*maps['electron'].T@metric@maps['muon']
    return dict(template_tensor=tensor,muon_current_map=maps['muon'],electron_current_map=maps['electron'],
        canonical_local_action_density_factor=density,metric_tensor_in_HS_currents=metric,
        normalization='common S4/V²; chi_hat=R4^(3/2)psi/V; angular carrier1/sqrt(V), V=2pi²; HS spin sigma/sqrt2',
        action_equation='S_F,cross=-4sqrt2*c_F*h*N*(2pi²)/R4³*(j1,e eta j1,mu+j2,e eta j2,mu)',
        raw_intrinsic_S4_to_cap_factor=1/VOLUME**2,
        canonical_spinor_definition='chi_hat=R4^(3/2)psi/(2pi²)',
        coordinate_time_step_held_fixed=True,physical_action_unit_or_low_energy_LSZ_match_evaluated=False)


def exact_stored_fermi_template_fit(template,paired_lower,paired_upper,*,precision_bits=192):
    """Outward one-template quotient/remainder for the stored finite tensor.

    The paired-current entries are intervals from the actual source/adjoint
    solve.  The template is treated as its exact stored binary64 array.
    Source, Cayley and metric formation errors remain separate.
    """
    T=np.asarray(template);lo=np.asarray(paired_lower);hi=np.asarray(paired_upper)
    if any(not np.isrealobj(x) or x.shape!=(8,8) or not np.isfinite(x).all() for x in (T,lo,hi)) or np.any(lo>hi):
        raise ValueError('complete finite real template and ordered paired-current intervals required')
    if type(precision_bits) is not int or precision_bits<128:raise ValueError('Arb precision>=128 required')
    previous=ctx.prec
    try:
        ctx.prec=precision_bits
        t=[arb(float(v)) for v in T.ravel()]
        # Exact endpoint hull. No rounded midpoint substitutes for the
        # interval or halves its export uncertainty.
        g=[]
        for l,u in zip(lo.ravel(),hi.ravel()):
            a,b=arb(float(l)),arb(float(u));g.append((a+b)/2+arb(0,(b-a)/2))
        denom=sum(x*x for x in t)
        if not denom>0:raise ValueError('nonzero local Fermi template required')
        coefficient=sum(x*y for x,y in zip(t,g))/denom
        remainder=[y-coefficient*x for x,y in zip(t,g)]
        square=lambda x:abs(x)**2
        norm=sum(square(x) for x in remainder).sqrt()
        kernelnorm=sum(square(x) for x in g).sqrt()
        lower=lambda x:float(np.nextafter(float(x.lower()),-np.inf)) if not x.is_zero() else 0.
        upper=lambda x:float(np.nextafter(float(x.upper()),np.inf)) if not x.is_zero() else 0.
        ratio=norm/kernelnorm if kernelnorm>0 else None
        return dict(finite_cell_template_fit_coefficient_lower=lower(coefficient),
            finite_cell_template_fit_coefficient_upper=upper(coefficient),
            remainder_Frobenius_norm_lower=max(0.,lower(norm)),remainder_Frobenius_norm_upper=upper(norm),
            relative_remainder_lower=None if ratio is None else max(0.,lower(ratio)),
            relative_remainder_upper=None if ratio is None else upper(ratio),
            exact_stored_template_and_pairing_one_coefficient_representation_excluded=bool(norm>0),
            physical_c_F=None,precision_bits=precision_bits,
            physical_low_energy_Wilson_coefficient_or_LSZ_error_enclosed=False,
            source_Cayley_metric_template_formation_error_enclosed=False)
    finally:ctx.prec=previous


def retained_fermi_reduction(repository=ROOT,*,application='artifacts/muon_charged_current_cell_amputation_20261010/run_1'):
    """Consume the actual completed muon/electron on-shell paired tensor."""
    root=Path(repository);folder=root/application;raw=(folder/'result.json').read_bytes();receipt=json.loads(raw)
    blob=(folder/'application.npz').read_bytes()
    if sha256(blob).hexdigest()!=receipt['array_sha256']:raise ValueError('on-shell current values changed')
    for source in receipt['source_records']:
        if sha256((root/source['path']).read_bytes()).hexdigest()!=source['sha256']:raise ValueError('on-shell current source changed: '+source['path'])
    with np.load(folder/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
    def values(ref):return arrays[ref['array_key']]
    arms=[]
    for row in receipt['arms']:
        source=row['muon_source'];V=values(source['amputation']['midpoint_lift']);op=source['lepton_application']
        template=transported_fermi_template(V,N=op['N'],R4=op['R4'],step=row['oriented_step'])
        frames=[]
        for mixed,original in zip(row['electron_readout_muon_source'],row['applications']):
            c=mixed['exact_stored_certificate']
            fitted=exact_stored_fermi_template_fit(template['template_tensor'],values(c['paired_current_lower']),values(c['paired_current_upper']))
            frames.append(dict(frame=original['frame'],fit=fitted,
                auxiliary_Gauss_reaction_norm=original['auxiliary_Gauss_reaction_norm'],
                source_adjoint_intervals_overlap=c['source_adjoint_intervals_overlap']))
        arms.append(dict(side=row['side'],oriented_step=row['oriented_step'],action_parameters=row['action_parameters'],
            template=template,frames=frames,temporal_scope=row['temporal_scope'],
            actual_fixed_Y_H_source_norm=source['reached_fixed_Y_H_source_norm']))
    return dict(classification='EVALUATED_TRANSPORTED_LOCAL_FERMI_TEMPLATE_REMAINDER_ON_ACTUAL_FINITE_CELLS',
        input_records=[dict(path=(folder/name).relative_to(root).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest())
            for name,data in (('result.json',raw),('application.npz',blob))],arms=arms,
        local_g2_over_MW_squared_substituted=False,physical_c_F=None,E_kappa_GeV=None,
        physical_low_energy_projection_or_LSZ_completed=False,
        conclusion_scope='exact stored finite-cell paired tensor cannot be replaced by the evaluated one-coefficient transported Fermi template; no verdict about its future low-energy limit',
        error_scope='Arb stored paired intervals and stored template; upstream source/Cayley/geometry/field/continuum errors not enclosed')


if __name__=='__main__':
    import argparse
    from .muon_birth_phase_continuation import _compressed_npz
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    output=args.output if args.output.is_absolute() else ROOT/args.output
    if output.exists():raise FileExistsError('preserve earlier Fermi reductions')
    packet=retained_fermi_reduction();arrays={}
    def extract(value,key):
        if isinstance(value,np.ndarray):arrays[key]=value;return dict(array_key=key)
        if isinstance(value,dict):return {k:extract(v,key+'_'+k) for k,v in value.items()}
        if isinstance(value,list):return [extract(v,key+'_'+str(i)) for i,v in enumerate(value)]
        return value
    result=extract(packet,'fermi');source=Path(__file__);data=source.read_bytes()
    result['producer_source']=dict(path=source.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest())
    output.mkdir(parents=True);_compressed_npz(output/'application.npz',arrays)
    result['array_sha256']=sha256((output/'application.npz').read_bytes()).hexdigest()
    (output/'result.json').write_bytes((json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps(dict(receipt_sha256=sha256((output/'result.json').read_bytes()).hexdigest(),array_sha256=result['array_sha256'],
        arms=[dict(side=r['side'],frames=r['frames']) for r in packet['arms']]),sort_keys=True))
