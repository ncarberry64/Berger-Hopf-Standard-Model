"""Shared-area family of the represented signed normal boundary form.

This application tests an actual complete integrated action form.  It
does not replace an endpoint DtN by the local restoring density in c=I/R.
The frozen primal's nonzero area Euler load is retained at positive gamma;
any crossing is only a conditional candidate for a coupled base solve.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_finite_normal_boundary_action import load_completed_finite_normal_cell,eliminate_attachment_traces
from .muon_birth_chronological_normal_inertia import true_legendre_normal_trial
from .muon_birth_chronological_normal_boundary_response import mixed_canonical_far_response
from .muon_exact_material_response import exact_moving_cap_action_jet
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_phase_continuation import _compressed_npz


def fixed_primal_area_operator_family(base, gamma):
    """Differentiate the literal area action in the same full-field chart."""
    if not np.isfinite(gamma) or gamma<0:raise ValueError('nonnegative formal area-family coefficient required')
    rep=base['representation'];raw=base['raw'];c=generic_coordinate_lift(rep['gauge_labels']);P=c['lift'];n=c['x_count']
    area=exact_moving_cap_action_jet(12,raw[:37],raw[37:74],raw[74:98],points=rep['cap_points'],
        source_value=raw[98],source_rate=raw[99])['surface_per_gamma']
    a=base['arrays'];H=a['stage_action_hessian'][0].copy();g=a['stage_action_gradient'][0].copy()
    area_g=P[:100].T@area.gradient;area_H=P[:100].T@area.hessian@P[:100]
    H+=gamma*area_H;g+=gamma*area_g
    kinetic=true_legendre_normal_trial(H,raw,rep)
    response=mixed_canonical_far_response(H,abs(base['receipt']['span']),int(base['receipt']['side']=='incoming'),kinetic,rep)
    reduced=eliminate_attachment_traces(response['response'])
    inertia=eliminate_attachment_traces(kinetic['response'])
    return dict(response=response,kinetic=kinetic,reduced=reduced,inertia=inertia,
        area_gradient=area_g,area_hessian=area_H,
        fixed_primal_algebraic_residual=g[2*n:],normal_form=reduced['normal_response'],
        gamma=float(gamma),fixed_primal_area_load_norm=float(np.linalg.norm(gamma*area_g)),
        raw_area_Hessian_identified_with_Jacobi=False,
        physical_stationarity_at_positive_gamma_claimed=False)


def materialize_finite_normal_formation_family(incoming_phase,outgoing_phase,output,*,
        gamma_values=(0.,1e-6,1e-4,.01,.1,1.,10.,100.),repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier family applications')
    bases=[load_completed_finite_normal_cell(p,repository=root)for p in (incoming_phase,outgoing_phase)]
    if [b['receipt']['side']for b in bases]!=['incoming','outgoing']:raise ValueError('signed incoming/child phase order required')
    rows=[];arrays={};refs={};archives=[]
    for base in bases:refs.update(base['input_hashes'])
    for k,gamma in enumerate(gamma_values):
        apps=[fixed_primal_area_operator_family(b,float(gamma))for b in bases]
        scalar=apps[1]['normal_form']+apps[0]['normal_form']
        rows.append(dict(gamma=float(gamma),incoming_signed_form=apps[0]['normal_form'],
            drive_negative_incoming=-apps[0]['normal_form'],child_form=apps[1]['normal_form'],
            integrated_formation_form=float(scalar),
            frozen_primal_algebraic_norms=[float(np.linalg.norm(a['fixed_primal_algebraic_residual']))for a in apps],
            area_load_norms=[a['fixed_primal_area_load_norm']for a in apps],
            same_kinetic_forms=[a['inertia']['normal_response']for a in apps],
            all_original_response_defects=[float(np.max(abs(a['response']['solve_residual'])))for a in apps]))
        for side,a in zip(('incoming','outgoing'),apps):
            prefix=f'gamma_{k:03d}_{side}_'
            arrays.update({prefix+key:value for key,value in a['response'].items()if isinstance(value,np.ndarray)})
            arrays[prefix+'normal_trace_lift']=a['reduced']['trace_lift']
            arrays[prefix+'area_gradient']=a['area_gradient'];arrays[prefix+'area_hessian']=a['area_hessian']
    out.mkdir(parents=True)
    # Split by parameter value, retaining every original array bit for bit.
    for k in range(len(gamma_values)):
        path=out/f'gamma_{k:03d}.npz'
        _compressed_npz(path,{key:value for key,value in arrays.items()if key.startswith(f'gamma_{k:03d}_')})
        if path.stat().st_size>10*1024**2:raise ValueError('individual full parameter application exceeds publication limit')
        archives.append(dict(path=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()))
    for name in ('muon_birth_finite_normal_formation_family','muon_birth_finite_normal_boundary_action',
        'muon_birth_chronological_normal_inertia','muon_birth_chronological_normal_boundary_response','muon_exact_material_response'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    md=dict(classification='EVALUATED_SIGNED_FULL_FIELD_INTEGRATED_NORMAL_AREA_FAMILY',rows=rows,input_hashes=refs,
        numerical_archives=archives,
        signed_formation_rule='K_child(boundary)-H_drive; H_drive=-K_incoming(boundary)',
        boundary_policy='fixed recorded outer canonical covectors, coordinates free; outer faces are numerical, not E0/finalchild',
        normal_domain='left-SU2 invariant constant proper normal, full internal trace/y equations and both attachment responses retained',
        area_rule='literal common M8 area action twojet added before all internal solves; its first traction and path contacts are retained, not discarded to rename its raw Hessian J',
        gamma_law='gamma=alpha_FSC*c^(-7/2) on the retained M8 worldvolume action; no alphaEM substitution',
        reference_zero_is_physical_gamma_zero=False,
        fixed_primal_positive_gamma_is_stationary=False,
        local_restoring_R_or_physical_cutoff_selected=False,
        physical_Pauli_completed=False,
        error_scope='Binary64 full action block applications on fixed primal; no physical event, continuum/action rounding or coupled gamma-base certificate')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--incoming-phase',type=Path,required=True);p.add_argument('--outgoing-phase',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_finite_normal_formation_family(a.incoming_phase,a.outgoing_phase,a.output),sort_keys=True))
