"""Full inherited wall/body and analytic time jets on saved phase cells.

The reconstructed function is exactly the finite midpoint representation:
x is affine inside each cell and v/y are that cell's solved coefficients.
It is not a continuous Euler solution or an identification of its outer
face with E0.  The inherited parent/reference clock motion is composed
once, in addition to the child coefficient derivative.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_birth_finite_normal_trace_graph import affine_connection_profile_two_jet
from .muon_inherited_intrinsic_lepton_operator import inherited_intrinsic_lepton_operator
from .muon_primal_trace_enriched_lepton_operator import (
    primal_trace_enriched_lepton_operator, intrinsic_wall_coordinate_reduction,
)
from .muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL
from .muon_birth_phase_continuation import _compressed_npz


def load_profile_preserving_phase(folder, *, repository=ROOT):
    """Pin a complete incoming or repaired outgoing numerical phase."""
    root=Path(repository);path=Path(folder);path=path if path.is_absolute()else root/path
    raw_receipt=(path/'result.json').read_bytes();receipt=json.loads(raw_receipt)
    if (receipt['completed_steps']!=receipt['steps'] or not receipt['stages']
            or any(s['status']!='REPRESENTED_PHASE_TOLERANCE'for s in receipt['stages'])):
        raise ValueError('all represented chronological cells must have converged')
    refs=dict(receipt['input_hashes'])
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
    archive=(path/'application.npz').read_bytes()
    if sha256(archive).hexdigest()!=receipt['numerical_sha256']:raise ValueError('phase arrays changed')
    with np.load(path/'application.npz',allow_pickle=False)as f:arrays={k:f[k].copy()for k in f.files}
    if receipt['side']=='outgoing':
        if (receipt['classification']!='EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION'
                or receipt['source_image_projected']):
            raise ValueError('outgoing phase must retain the unprojected inherited image')
        source=next(p.rsplit('/',1)[0]for p in refs if p.endswith('/finite_moving_trace_run_1/result.json'))
        stage_key='stage_independent_raw'
    else:
        source=receipt['consumed_base'];stage_key='stage_midpoint_raw'
    base=load_finite_normal_endpoint(source,side=receipt['side'],repository=root)
    if arrays[stage_key].shape[0]!=receipt['steps']:raise ValueError('every chronological cell must be saved')
    relative=path.relative_to(root).as_posix()
    refs[relative+'/result.json']=sha256(raw_receipt).hexdigest()
    refs[relative+'/application.npz']=sha256(archive).hexdigest()
    return dict(receipt=receipt,arrays=arrays,representation=base['representation'],
        coordinates=base['coordinates'],stage_key=stage_key,input_hashes=refs,
        physical_history_or_cutoff_selected=False)


def profile_preserving_raw_sample(phase, coordinate_time):
    """Reconstruct one saved cell without extrapolating its time domain.

    At an internal face the later cell in the represented propagation
    is used; v/y may jump between cells.  Consequently the returned time
    derivative is a one-sided cell derivative at such a face.
    """
    t=float(coordinate_time);r=phase['receipt'];steps=r['steps'];h=r['span']/steps
    u=t/h
    if not np.isfinite(t) or u<0. or u>steps:raise ValueError('sample must lie on the same signed numerical phase')
    k=min(int(np.floor(u)),steps-1);tm=(k+.5)*h
    raw=phase['arrays'][phase['stage_key']][k].copy();P=phase['coordinates']['lift'];n=phase['coordinates']['x_count']
    eta=P.T@raw
    if np.max(abs(P@eta-raw))>1e-12:raise ValueError('saved fields lie outside the preserved phase lift')
    rate=P[:,:n]@eta[n:2*n];raw+=(t-tm)*rate
    return dict(raw_fields=raw,raw_coordinate_time_derivative=rate,stage=k,stage_time=tm,
        coordinate_time=t,cell_signed_step=h,
        time_derivative_scope='inside-cell future coordinate derivative; v/y held at the solved midpoint',
        interpolation_is_continuous_Euler_solution=False)


def _first_germ_rate(raw):
    out=np.zeros_like(raw);out[:37]=raw[37:74];out[98]=raw[99]
    return out


def profile_preserving_lepton_sample(phase, coordinate_time):
    """Apply the full eighteen-dimensional operator and its total time jet.

    The total derivative includes the explicit parent/reference affine
    clock term, which is not contained in a fixed-parent child raw jet.
    No algebraic At coordinate-rate or full physical history is inferred.
    """
    sample=profile_preserving_raw_sample(phase,coordinate_time)
    raw=sample['raw_fields'];rate=sample['raw_coordinate_time_derivative'];rep=phase['representation'];t=sample['coordinate_time']
    explicit={name:np.zeros((18,18),complex)for name in ('W','Omega_tau','H_can')}
    if phase['receipt']['side']=='outgoing':
        pair=phase['arrays']['initial_pair'];reference=phase['arrays']['reference_pair']
        op=inherited_intrinsic_lepton_operator(raw,t,pair,reference,rep)
        parent=affine_geometry_germ(pair[0],t);refs=np.array([affine_geometry_germ(x,t)for x in reference])
        profile=affine_connection_profile_two_jet(np.array([parent,raw]),np.array([WALL]))
        refprofile=affine_connection_profile_two_jet(refs,np.array([WALL]))
        fixed_child_clock=np.r_[_first_germ_rate(pair[0])[:100],np.zeros(100)]
        reference_clock=np.concatenate([_first_germ_rate(x)[:100]for x in reference])
        profile_clock=profile['first'][0,0]@fixed_child_clock-refprofile['first'][0,0]@reference_clock
        wall_clock=np.zeros((5,4));wall_clock[2:]=M*profile_clock
        # An exact twenty-axis wall section is used only for the intrinsic
        # action cotangent. It never projects the bulk radial source image.
        reduced=primal_intrinsic_lepton_operator(op['intrinsic_reduced_raw_fields'],
            intrinsic_wall_coordinate_reduction(rep)['original_representation'])
        direction=np.zeros(228);direction[100:160]=op['trace_realization']@wall_clock.reshape(20)
        for name in explicit:
            explicit[name]=np.einsum('j,juv->uv',direction,reduced[name+'_raw_first_jet'])
    else:
        op=primal_trace_enriched_lepton_operator(raw,rep);profile_clock=0.
    derivative={}
    for name in explicit:
        coefficient=np.einsum('j,juv->uv',rate,op[name+'_raw_first_jet'])
        derivative[name]=dict(coefficient_motion=coefficient,explicit_inherited_clock=explicit[name],
            coordinate_time=coefficient+explicit[name],proper_time=(coefficient+explicit[name])/op['N'])
    measure_rate=float(rate@op['proper_time_Haar_measure_first_jet'])
    return dict(sample=sample,operator=op,time_derivatives=derivative,
        proper_time_density=op['N'],proper_time_Haar_measure_rate=measure_rate,
        explicit_inherited_profile_coordinate_rate=float(profile_clock),
        inherited_connection_count=1,algebraic_At_time_derivative_not_claimed=True,
        physical_history_or_formation_or_Pauli_selected=False,
        derivative_scope='exact derivative of the represented inside-cell interpolation and declared affine parent/reference germs')


def materialize_profile_preserving_samples(phase_directory,output,*,points_per_cell=4,repository=ROOT):
    """Execute interior quadrature samples of the same represented body."""
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier sampled applications')
    if type(points_per_cell)is not int or points_per_cell<2:raise ValueError('resolved explicit cell quadrature required')
    phase=load_profile_preserving_phase(phase_directory,repository=root);r=phase['receipt'];h=r['span']/r['steps']
    u,w=np.polynomial.legendre.leggauss(points_per_cell)
    times=np.concatenate([(k+(u+1)/2)*h for k in range(r['steps'])])
    apps=[profile_preserving_lepton_sample(phase,float(t))for t in times]
    arrays=dict(coordinate_time=times,positive_coordinate_quadrature=np.tile(w*abs(h)/2,r['steps']),
        raw_fields=np.array([a['sample']['raw_fields']for a in apps]),
        raw_coordinate_time_derivative=np.array([a['sample']['raw_coordinate_time_derivative']for a in apps]),
        induced_lapse=np.array([a['operator']['N']for a in apps]),R4=np.array([a['operator']['R4']for a in apps]),
        proper_time_Haar_measure=np.array([a['operator']['proper_time_Haar_measure']for a in apps]),
        proper_time_Haar_measure_coordinate_rate=np.array([a['proper_time_Haar_measure_rate']for a in apps]),
        explicit_inherited_profile_coordinate_rate=np.array([a['explicit_inherited_profile_coordinate_rate']for a in apps]))
    for name in ('W','Omega_tau','H_can'):
        arrays[name]=np.array([a['operator'][name]for a in apps])
        for derivative in ('coefficient_motion','explicit_inherited_clock','coordinate_time','proper_time'):
            arrays[name+'_'+derivative]=np.array([a['time_derivatives'][name][derivative]for a in apps])
    refs=dict(phase['input_hashes'])
    for name in ('muon_profile_preserving_phase_sample','muon_inherited_intrinsic_lepton_operator',
        'muon_inherited_wall_lepton_application','muon_primal_trace_enriched_lepton_operator',
        'muon_primal_intrinsic_lepton_operator'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    if refs!={p:sha256((root/p).read_bytes()).hexdigest()for p in refs}:raise RuntimeError('consumed operator changed during sampling')
    md=dict(classification='EVALUATED_PROFILE_PRESERVING_MULTICELL_BODY_AND_ANALYTIC_TIME_JETS',side=r['side'],
        points_per_cell=points_per_cell,steps=r['steps'],span=r['span'],input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        W_coordinate_rate_norm=float(np.linalg.norm(arrays['W_coordinate_time'])),
        W_explicit_parent_reference_clock_norm=float(np.linalg.norm(arrays['W_explicit_inherited_clock'])),
        sampling_domain='same solved implicit midpoint cells; x affine, v/y midpoint; affine parent/reference first germs explicit',
        quadrature_orientation='positive chronological measure; coordinate derivatives retain future t orientation on both arms',
        proper_time_density_and_contact_included=True,inherited_connection_count=1,
        continuous_Euler_stationarity_or_physical_history_selected=False,
        physical_formation_or_cutoff_or_Pauli_selected=False,
        error_scope='analytic derivatives of the represented interpolation; no temporal representation, producer rounding or physical uncertainty enclosure')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--points-per-cell',type=int,default=4)
    a=p.parse_args();print(json.dumps(materialize_profile_preserving_samples(a.phase_directory,a.output,
        points_per_cell=a.points_per_cell),sort_keys=True))
