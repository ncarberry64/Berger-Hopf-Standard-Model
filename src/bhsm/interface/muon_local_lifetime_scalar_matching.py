"""Joint local lifetime/pole equations on the original coupled field chart.

Changing lambda_H at held coefficients is a parameter application of the
same action.  It is not a new stationary phase, an exterior resonance
selection, or a calibration of the fixed lepton Yukawas.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import numpy as np
from scipy.linalg import eig
from .muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_lepton_sample
from .muon_birth_finite_normal_trace_graph import pointwise_finite_normal_action
from .muon_birth_inherited_finite_normal_phase import inherited_child_finite_normal_action
from .muon_coupled_lorentz_field_symbol import coupled_field_symbol
from .muon_coupled_lorentz_radial_green import coupled_radial_trace_application
from .muon_static_coupled_charged_current import static_coupled_charged_current
from .muon_coupled_tensor_decay_rate import tensor_tree_decay_rate,temporal_charged_current_series


def retained_lambda_field_family(side,*,repository):
    """Rebuild the full owned action and its affine lambda_H field pencil."""
    if side not in('incoming','outgoing'):raise ValueError('retained chronological arm required')
    folder=('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'
            else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    phase=load_profile_preserving_phase(folder,repository=Path(repository))
    sample=profile_preserving_lepton_sample(phase,0.);raw=sample['sample']['raw_fields'];rep=deepcopy(phase['representation'])
    lam=float(rep['scalar_matching']['lambda_H']);delta=lam/4
    opts=phase['receipt']['action_parameters'];applications=[];symbols=[]
    for value in(lam,lam+delta,lam+2*delta):
        varied=deepcopy(rep);varied['scalar_matching']['lambda_H']=value
        if side=='incoming':action=pointwise_finite_normal_action(raw,varied,**opts)
        else:action=inherited_child_finite_normal_action(raw,0.,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],varied,**opts)
        applications.append(action)
        symbols.append(coupled_field_symbol(action,varied,lapse=sample['operator']['N'],H=raw[-8:-4]))
    C0,C1,C2=[s['proper_frequency_coefficients']for s in symbols]
    derivative=(C1-C0)/delta;residual=C2-C0-2*delta*derivative
    mask=np.ones(C0.shape,bool);mask[0,64:68,64:68]=False
    # Only the full real H4 potential block enters fixed-geometry field
    # frequency variation.  Full action gradients do change with lambda.
    if np.max(abs(derivative[mask]))>1e-13:
        raise ArithmeticError('owned lambda variation changed an unanticipated field/gauge kinetic block')
    h=raw[-8:-4];H=h[:2]+1j*h[2:]
    return dict(side=side,lambda_H_base=lam,proper_frequency_coefficients=C0,
        lambda_H_frequency_derivative=derivative,lambda_H_affinity_residual=residual,
        full_action_gradient_lambda_derivative=(applications[1]['gradient']-applications[0]['gradient'])/delta,
        full_action_hessian_lambda_derivative=(applications[1]['hessian']-applications[0]['hessian'])/delta,
        field_quotient_lift=symbols[0]['field_quotient_lift'],joint_trace_map=symbols[0]['joint_trace_map'],
        scalar_radial_source=symbols[0]['scalar_radial_source'],central_radial_frame_rows=symbols[0]['central_radial_frame_rows'],
        raw_fields=raw,H=H,radius=sample['operator']['R4'],lapse=sample['operator']['N'],
        lambda_probe_values=np.array([lam,lam+delta,lam+2*delta]),input_hashes=phase['input_hashes'],
        original_phase_resolved_at_varied_lambda=False,physical_unit_or_pole_selected=False)


def scalar_lambda_candidates(family,*,frequency):
    """Solve full gauge-returned H4 pole equation for lambda at fixed omega.

    All four scalar directions and all76 gauge/algebraic quotient rows
    are retained.  A radial projection labels algebraic local candidates;
    it does not identify a measured scalar resonance or a physical mode.
    """
    w=float(frequency)
    if not np.isfinite(w)or w<=0:raise ValueError('positive local target frequency required')
    Q=family['field_quotient_lift'];C=family['proper_frequency_coefficients'];D=family['lambda_H_frequency_derivative']
    P=Q.T@sum(C[k]*w**k for k in range(3))@Q
    dP=Q.T@sum(D[k]*w**k for k in range(3))@Q
    hi=np.flatnonzero(np.any(Q[64:68]!=0,axis=0));gi=np.setdiff1d(np.arange(80),hi)
    gh=P[np.ix_(gi,hi)];returned=P[np.ix_(hi,hi)]-P[np.ix_(hi,gi)]@np.linalg.solve(P[np.ix_(gi,gi)],gh)
    delta=dP[np.ix_(hi,hi)]
    values,vectors=eig(-returned,delta)
    lambdas=family['lambda_H_base']+values
    tangent=Q.T@family['scalar_radial_source'];r=tangent[hi]
    overlap=abs(r.conj()@vectors)**2/(np.sum(abs(vectors)**2,axis=0)*np.vdot(r,r).real)
    residual=np.array([np.linalg.norm((returned+z*delta)@v)/((np.linalg.norm(returned)+abs(z)*np.linalg.norm(delta))*np.linalg.norm(v))for z,v in zip(values,vectors.T)])
    return dict(local_lambda_candidates=lambdas,radial_projection_fractions=overlap,
        scalar_returned_pole_vectors=vectors,returned_scalar_operator=returned,
        returned_lambda_derivative=delta,local_pole_equation_relative_residual=residual,
        target_frequency=w,physical_radial_resonance_selected=False)


def local_initial_scalar_lifetime_probe(family,*,muon_mass_GeV,electron_mass_GeV,
        scalar_mass_GeV,lifetime_seconds,hbar_GeV_seconds,iterations=7):
    """Execute the same local lifetime and radial candidate equations.

    The algebraic candidate of largest radial projection is reported with
    every other candidate, as a computational continuation diagnostic.
    No unstable modes, continuum normalization, or phase equations are
    replaced by this two-equation parameter application.
    """
    M,m,Mh,tau,hbar=map(float,(muon_mass_GeV,electron_mass_GeV,scalar_mass_GeV,lifetime_seconds,hbar_GeV_seconds))
    if not np.isfinite([M,m,Mh,tau,hbar]).all()or not 0<m<M or min(Mh,tau,hbar)<=0:
        raise ValueError('same independent measured positive masses/lifetime/SI clock required')
    if not isinstance(iterations,int)or iterations<2:raise ValueError('explicit convergent local iteration required')
    Q=family['field_quotient_lift'];T=family['joint_trace_map'];r=family['scalar_radial_source'];F=family['central_radial_frame_rows']
    C0=family['proper_frequency_coefficients'];D=family['lambda_H_frequency_derivative'];base=family['lambda_H_base']
    E=40. if family['side']=='outgoing'else 50.;records=[]
    last=None
    for _ in range(iterations):
        candidates=scalar_lambda_candidates(family,frequency=Mh/E)
        positive=np.flatnonzero((abs(candidates['local_lambda_candidates'].imag)<1e-9)&(candidates['local_lambda_candidates'].real>0))
        if len(positive)==0:
            return dict(status='NO_POSITIVE_REAL_LOCAL_LAMBDA_AT_REACHED_FREQUENCY',iterations=np.array(records),candidates=candidates,physical_matching_completed=False)
        j=positive[np.argmax(candidates['radial_projection_fractions'][positive])];lam=float(candidates['local_lambda_candidates'][j].real)
        C=C0+(lam-base)*D;green=coupled_radial_trace_application(C,Q,T,r,F,frequency=0)
        current=static_coupled_charged_current(green['joint_wall_Green'],family['H'],radius=family['radius'],lapse=family['lapse'],family=1,out_family=2)
        series=temporal_charged_current_series(C,Q,T,current['charged_current_right_vertices'],current['charged_current_left_vertices'],maximum_frequency=1.02*M/E)
        rate=tensor_tree_decay_rate(current['full_charged_current_tensor'],muon_mass_GeV=M,electron_mass_GeV=m,radial_order=24,
            temporal_coefficients=series['temporal_current_coefficients'],action_energy_unit=E)
        value=rate['tree_rate_coefficient_GeV5'];next_E=(value*tau/hbar)**.25
        records.append([E,lam,value,next_E,candidates['radial_projection_fractions'][j]])
        E=next_E;last=(candidates,current,series,rate,C,lam,j)
    candidates,current,series,rate,C,lam,j=last
    # The final pole equation and lifetime equation use the same E.  This
    # residual tests convergence instead of assigning the target by fiat.
    final=scalar_lambda_candidates(family,frequency=Mh/E)
    pole_parameter_residual=abs(final['local_lambda_candidates'][np.argmax(final['radial_projection_fractions'])]-lam)
    return dict(status='EVALUATED_LOCAL_JOINT_PARAMETER_APPLICATION',iterations=np.array(records),
        conditional_E_kappa_GeV=E,conditional_lambda_H=lam,
        target_pole_frequency=Mh/E,final_lambda_candidates=final['local_lambda_candidates'],
        final_radial_projection_fractions=final['radial_projection_fractions'],
        local_pole_parameter_iteration_residual=pole_parameter_residual,
        lifetime_rate_GeV=rate['tree_rate_coefficient_GeV5']/E**4,measured_rate_GeV=hbar/tau,
        varied_proper_frequency_coefficients=C,full_charged_current_tensor=current['full_charged_current_tensor'],
        original_phase_resolved_at_varied_lambda=False,continuum_scalar_residue_matched=False,
        non_VA_radiative_correction_completed=False,spatial_momentum_completion=False,
        physical_matching_completed=False,physical_unit_or_pole_selected=False)


def local_joint_matching_scan(family,*,muon_mass_GeV,electron_mass_GeV,
        scalar_mass_GeV,lifetime_seconds,hbar_GeV_seconds,
        frequencies=(.02,.04,.08,.12,.2,.3,.4,.5,.6,.7,.8,.9,1.,1.1,1.2,1.4)):
    """Evaluate both matching equations along every reached radial candidate.

    E=M_h/omega is substituted in the lifetime equation.  All four
    lambda candidates are exported at every frequency; positive real
    candidates with a nonzero radial projection are evaluated with the
    complete tensor.  An actual sign-changing bracket is solved, rather
    than a negative candidate at one seed being called a no-go theorem.
    No conclusion outside the sampled/bracketed finite chart is inferred.
    """
    from scipy.optimize import brentq
    M,m,Mh,tau,hbar=map(float,(muon_mass_GeV,electron_mass_GeV,scalar_mass_GeV,lifetime_seconds,hbar_GeV_seconds))
    f=np.asarray(frequencies)
    if (not np.isrealobj(f)or f.ndim!=1 or len(f)<2 or not np.isfinite(f).all()
        or np.any(f<=0)or np.any(np.diff(f)<=0)or not np.isfinite([M,m,Mh,tau,hbar]).all()
        or not 0<m<M or min(Mh,tau,hbar)<=0):raise ValueError('ordered positive local frequencies and independent measured inputs required')
    C0=family['proper_frequency_coefficients'];D=family['lambda_H_frequency_derivative'];base=family['lambda_H_base']
    Q=family['field_quotient_lift'];T=family['joint_trace_map'];r=family['scalar_radial_source'];F=family['central_radial_frame_rows']
    rows=[];lambda_rows=[];projection_rows=[];roots=[]
    def evaluate(w):
        a=scalar_lambda_candidates(family,frequency=w)
        j=int(np.argmax(a['radial_projection_fractions']));z=a['local_lambda_candidates'][j]
        if abs(z.imag)>1e-8 or z.real<=0:return None,a
        lam=float(z.real);E=Mh/w;C=C0+(lam-base)*D
        green=coupled_radial_trace_application(C,Q,T,r,F,frequency=0)
        current=static_coupled_charged_current(green['joint_wall_Green'],family['H'],radius=family['radius'],lapse=family['lapse'],family=1,out_family=2)
        series=temporal_charged_current_series(C,Q,T,current['charged_current_right_vertices'],current['charged_current_left_vertices'],maximum_frequency=M/E)
        rate=tensor_tree_decay_rate(current['full_charged_current_tensor'],muon_mass_GeV=M,electron_mass_GeV=m,radial_order=16,
            temporal_coefficients=series['temporal_current_coefficients'],action_energy_unit=E)['tree_rate_coefficient_GeV5']
        ratio=rate/E**4/(hbar/tau)
        return np.array([w,lam,E,rate,ratio,a['radial_projection_fractions'][j],series['grouped_square_norm_estimate'],series['uniform_tensor_series_tail_estimate']]),a
    previous=None
    for w in f:
        row,a=evaluate(float(w));lambda_rows.append(a['local_lambda_candidates']);projection_rows.append(a['radial_projection_fractions'])
        if row is None:continue
        rows.append(row)
        if previous is not None and (row[4]-1)*(previous[4]-1)<0:
            root=brentq(lambda z:evaluate(z)[0][4]-1,previous[0],row[0],xtol=1e-11,rtol=1e-11)
            roots.append(evaluate(root)[0])
        previous=row
    return dict(sampled_frequencies=f.astype(float),all_local_lambda_candidates=np.array(lambda_rows),
        all_radial_projection_fractions=np.array(projection_rows),
        positive_radial_candidate_equation_rows=np.array(rows).reshape(-1,8),
        joint_local_equation_roots=np.array(roots).reshape(-1,8),
        row_order='omega,lambda_H,E_kappa,C_rate,rate_over_measured,radial_fraction,series_rho2,tensor_tail_estimate',
        matching_equations=['E_kappa*omega=M_h_measured','C_rate(lambda_H,E_kappa)/E_kappa^4=hbar/tau_mu_plus'],
        no_sampled_sign_change=len(roots)==0,global_no_solution_theorem=False,
        original_phase_resolved_at_varied_lambda=False,physical_unit_or_pole_selected=False)
