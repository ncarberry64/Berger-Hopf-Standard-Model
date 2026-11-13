"""Same-quadrature magnetic variation of the changing joint field form.

The full retarded first fields supply the source. The positive reference
form is differentiated on its unchanged radial/time/angular coefficient
domain. Exact Wigner spectators only split matrix arithmetic; every
even/odd pair is retained, including small stored Gaunt entries.
"""
from __future__ import annotations
import numpy as np
from scipy.interpolate import CubicSpline,CubicHermiteSpline
from .muon_coupled_gauge_magnetic_source import one_form_magnetic_source_point,integrated_lorenz_magnetic_source
from .muon_coupled_higgs_magnetic_source import intrinsic_coupled_magnetic_source_point
from .muon_intrinsic_higgs_positive_source import higgs_magnetic_source_image_space
from .muon_even_coupled_temporal_field import complete_even_angular_blocks
from .muon_parent_positive_brst_ghost import ghost_radial_values,smooth_ghost_temporal_values
from .muon_parent_positive_coupled_field import corrected_positive_parent_reference
from .muon_corrected_profile_magnetic_response import corrected_wall_reference
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .muon_parent_retarded_hypercharge import regular_radial_basis,WALL
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_magnetic_mixed_green import _finite


def corrected_magnetic_first_field_interpolation(primal,phase,velocity,contacts):
    """Retain saved value/rate fields in one explicitly numerical sampler.

    Dynamic positions use their saved future rates in one Hermite curve.
    The algebraic At uses a cubic value curve and its SAME derivative.
    Wall source value/rate use one Hermite curve. This does not infer an
    exact continuous BVP or delete its interpolation error.
    """
    times=_finite(phase['times'],'same future times',real=True)
    v=_finite(velocity['velocity'],'saved future rates',real=True)
    c=_finite(phase['state'],'saved full phase',real=True)
    av=_finite(contacts['A_tau'],'actual algebraic At',real=True)
    qv=_finite(contacts['source_trace'],'actual wall source',real=True)
    qrate=_finite(contacts['source_trace_rate'],'actual wall source rate',real=True)
    if (times.ndim!=1 or not np.array_equal(times,contacts['times'])or not np.array_equal(times,velocity['times'])
        or c.shape!=(len(times),800,8)or v.shape!=(len(times),400,8)
        or av.shape!=(len(times),80,8)or qv.shape!=(len(times),400,8)or qrate.shape!=qv.shape):
        raise ValueError('complete SAME future-clock phase/rate/contact fields required')
    pos=CubicHermiteSpline(times,c[:,:400],v)
    at=CubicSpline(times,av)
    trace=CubicHermiteSpline(times,qv,qrate)
    marker=np.array([l[0]==3 for l in primal['harmonic_labels']])if 'harmonic_labels'in primal else np.r_[np.zeros(4,bool),np.ones(16,bool)]
    for x in (c[:,:400].reshape(len(times),5,4,20,8),v.reshape(len(times),5,4,20,8),
              av.reshape(len(times),4,20,8),qv.reshape(len(times),5,4,20,8),qrate.reshape(len(times),5,4,20,8)):
        if np.any(x[...,marker,:]):raise ValueError('nonzero n3 first-field/rate requires even n6 before this application')
    def sample(u,rho):
        p,pt=pos(u),pos.derivative()(u);a,atime=at(u),at.derivative()(u)
        q,qt=trace(u),trace.derivative()(u)
        interior=np.concatenate((a,p[:320]),axis=0).T.reshape(8,5,4,20)
        interior_t=np.concatenate((atime,pt[:320]),axis=0).T.reshape(8,5,4,20)
        q=q.T.reshape(8,5,4,20);qt=qt.T.reshape(8,5,4,20)
        f,fr=regular_radial_basis(np.asarray(rho),1)
        return dict(gauge=f[:,0,None,None,None,None]*interior[None]+f[:,1,None,None,None,None]*q[None],
            gauge_time=f[:,0,None,None,None,None]*interior_t[None]+f[:,1,None,None,None,None]*qt[None],
            gauge_radial=fr[:,0,None,None,None,None]*interior[None]+fr[:,1,None,None,None,None]*q[None],
            wall_gauge=q,H=p[320:400].T.reshape(8,4,20),Hdot=pt[320:400].T.reshape(8,4,20))
    return sample


def changing_coupled_magnetic_variation(phase,angular,first_field_sampler,*,times,weights,
        even_one_form_Gram,odd_one_form_Gram,even_ghost_Gram,odd_ghost_Gram,progress=None):
    """Execute all3 fixed-background deltaK/Gram on the unchanged full domain.

    Same12 temporal points and all retained radial points precede the
    differentiated global Lorenz term. Intrinsic-H and bulk-YM sectors
    share one source and one geometric coefficient chart. No independent
    inverse, new Rxi mass, statistical factor or cutoff is selected.
    """
    u=np.asarray(times);tw=np.asarray(weights);L=abs(float(phase['receipt']['span']))
    if u.ndim!=1 or tw.shape!=u.shape or not np.isfinite(u).all()or not np.isfinite(tw).all()or min(tw)<=0 or min(u)<=0 or max(u)>=L:
        raise ValueError('actual split time quadrature of the SAME finite field domain required')
    Eo=np.asarray(angular['derivative_matrices']);labels=angular['harmonic_labels']
    even=complete_even_angular_blocks();odd=[]
    for n,k in ((1,1),(3,1),(3,3)):
        ids=np.array([j for j,l in enumerate(labels)if l[0]==n and abs(l[2])==k])
        odd.append(dict(harmonic_indices=ids,derivatives=Eo[:,ids][:,:,ids]))
    mask=np.ones((20,20),bool)
    for b in odd:mask[np.ix_(b['harmonic_indices'],b['harmonic_indices'])]=False
    if np.any(Eo[:,mask]):raise ValueError('declared exact odd Wigner spectators are not invariant')
    rep=phase['representation'];lam=rep['scalar_matching']['lambda_H'];nu=phase['receipt']['action_parameters']['nu_squared_action']
    radial=ghost_radial_values(rep['rho']);wrad=ghost_radial_values(np.array([WALL]))[0]
    ghosts=smooth_ghost_temporal_values(u,L);K=np.zeros((3,2100,1200));M=K.copy();C=K.copy();HS=K.copy();dGaugeGram=np.zeros((3,1960,1120))
    records=[]
    for j,(uu,ww,ghost)in enumerate(zip(u,tw,ghosts)):
        t=float(uu-L if phase['receipt']['side']=='incoming'else uu)
        raw=profile_preserving_raw_sample(phase,t)['raw_fields'];kwargs={}
        if phase['receipt']['side']=='outgoing':kwargs=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
        ref=corrected_positive_parent_reference(raw,rep,coordinate_time=t,**kwargs)
        wall=corrected_wall_reference(raw,rep,coordinate_time=t,**kwargs)['background_values'][0]
        geo=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        sw=np.array([geo[k].value for k in ('wT','wS','wV')])
        b=2*min(uu/L,1-uu/L);bp=2/L if uu<L/2 else-2/L
        tf=np.array([b,bp,ghost[0,0],ghost[0,1],ghost[1,0],ghost[1,1]])
        first=first_field_sampler(float(uu),rep['rho'])
        support=np.where((first['H']!=0)|(first['Hdot']!=0),1.,0.)
        image=higgs_magnetic_source_image_space(angular,first['wall_gauge'],support)
        if image['source_maximum_level']!=1:raise ValueError('this full even2100 domain requires bit-exact source n3 absence')
        G=image['gaunt_even_odd_source'];Es=image['source_derivative_matrices']
        for eb in even['blocks']:
            ei=eb['harmonic_indices'];ne=len(ei);ie=(np.arange(60)[:,None]*35+ei).ravel();ige=(np.arange(56)[:,None]*35+ei).ravel()
            for ob in odd:
                oi=ob['harmonic_indices'];no=len(oi);io=(np.arange(60)[:,None]*20+oi).ravel();igo=(np.arange(56)[:,None]*20+oi).ravel()
                gaunt=G[ei][:,oi];Eeb,Eob=eb['derivatives'],ob['derivatives']
                kk=np.zeros((3,56*ne,56*no));mm=kk.copy();cc=kk.copy()
                for r,(A,At,Ar,metric,density,rw)in enumerate(zip(ref['background_values'],ref['background_time_derivatives'],ref['background_radial_derivatives'],ref['positive_metric_coefficients'],ref['positive_two_form_densities'],ref['radial_weights'])):
                    p=one_form_magnetic_source_point(connection=A,connection_time=At,connection_radial=Ar,
                        odd_derivatives=Eob,even_derivatives=Eeb,source_derivatives=Es,gaunt=gaunt,radial=radial[r],metric=metric,densities=density,
                        temporal=tf,source_gauge=first['gauge'][r,:3,:,:,:4],source_gauge_time=first['gauge_time'][r,:3,:,:,:4],
                        source_gauge_radial=first['gauge_radial'][r,:3,:,:,:4])
                    kk+=rw*p['one_form_delta_Hessian_even_odd'];mm+=rw*p['one_form_delta_Gram_even_odd'];cc+=rw*p['curvature_contact_delta_Hessian_even_odd']
                h=intrinsic_coupled_magnetic_source_point(weights=sw,H=raw[-8:-4],Hdot=raw[-4:],connection=wall,
                    odd_derivatives=Eob,even_derivatives=Eeb,source_derivatives=Es,gaunt=gaunt,temporal=tf,wall_radial=wrad,
                    source_gauge=first['wall_gauge'][:3,:,:,:4],source_H=first['H'][:3,:,:4],source_Hdot=first['Hdot'][:3,:,:4],
                    lambda_H=lam,nu_squared_action=nu)
                for axis in range(3):
                    K[axis][np.ix_(ige,igo)]+=ww*MAXWELL_TO_CAP*kk[axis]
                    M[axis][np.ix_(ige,igo)]+=ww*MAXWELL_TO_CAP*mm[axis]
                    C[axis][np.ix_(ige,igo)]+=ww*MAXWELL_TO_CAP*cc[axis]
                    dGaugeGram[axis][np.ix_(ige,igo)]+=ww*mm[axis]
                    K[axis][np.ix_(ie,io)]+=ww*h['intrinsic_coupled_delta_Hessian_even_odd'][axis]
                    HS[axis][np.ix_(ie,io)]+=ww*h['intrinsic_coupled_delta_Hessian_even_odd'][axis]
                    M[axis][np.ix_(ie,io)]+=ww*h['intrinsic_coupled_delta_Gram_even_odd'][axis]
        record=dict(sample=j,response_time=float(uu),coordinate_time=t,source_H_norm=float(np.linalg.norm(first['H'][:3])),
            source_Hdot_norm=float(np.linalg.norm(first['Hdot'][:3])),source_wall_norm=float(np.linalg.norm(first['wall_gauge'][:3])),
            accumulated_delta_Hessian_norm=float(np.linalg.norm(K)),source_n3_value_and_rate_exactzero=True)
        records.append(record)
        if progress is not None:progress(record)
    fix=integrated_lorenz_magnetic_source(even_one_form_Gram=even_one_form_Gram,odd_one_form_Gram=odd_one_form_Gram,
        even_ghost_Gram=even_ghost_Gram,odd_ghost_Gram=odd_ghost_Gram,delta_one_form_Gram_even_odd=dGaugeGram)
    LF=np.zeros_like(K);LF[:,:1960,:1120]=MAXWELL_TO_CAP*fix['Lorenz_delta_Hessian_even_odd'];K+=LF
    return dict(coupled_delta_Hessian_even_odd=K,coupled_delta_Gram_even_odd=M,
        YM_curvature_contact_delta_Hessian_even_odd=C,intrinsic_complete_delta_Hessian_even_odd=HS,
        integrated_Lorenz_delta_Hessian_even_odd=LF,integrated_one_form_delta_Gram_per_kappa=dGaugeGram,
        sample_records=records,all_even_and_odd_field_coordinates_retained=True,
        source_space='3 physical local magnetic axes; complete even0/2/4 and odd1/3 field/DG/H images',
        first_field_interpolation='saved future dynamic value/rate Hermite, algebraic At cubic derivative, wall trace Hermite; interpolation error outside',
        no_Rxi_mass_or_statistics_or_cutoff_selected=True,physical_P_strat_LSZ_or_Pauli_completed=False)
