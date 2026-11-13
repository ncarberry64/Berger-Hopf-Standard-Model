"""Two-sided external-energy applications on the changing current graph.

The internal Green and its differential domain are held fixed.  An
external-frequency derivative is therefore a derivative of BOTH actual
current moments, not a derivative of an eigenvalue or a selected vacuum.
Continued energy uses the analytic left dual rather than its conjugate.
"""
from __future__ import annotations
import numpy as np

from .muon_changing_magnetic_open_exchange import _base_maps, _trial, _vertex_sources
from .muon_changing_magnetic_current_jets import magnetic_current_angular_images
from .muon_intrinsic_scalar_temporal_image import temporal_image_green_kernel


def external_energy_weights(proper_times, energy, *, variable):
    """Owned plane-wave continuation; the clock origin is arbitrary.

    Real-clock modes are exp(-i E t).  Under t=t0-i tau their
    continuation is exp(-E tau), while the analytic dual is exp(+E tau).
    Continuing these modes does not continue the internal operator.
    """
    t=np.asarray(proper_times);e=np.asarray(energy)
    if (t.dtype.kind not in 'fiu' or e.dtype.kind not in 'fiu' or
            t.ndim!=1 or e.shape!=() or not np.isfinite(t).all() or not np.isfinite(e)):
        raise ValueError('finite real proper clock and explicit external energy required')
    if variable not in ('proper_clock_frequency','continued_Lorentz_energy'):
        raise ValueError('specify real proper frequency or owned continued Lorentz energy')
    z=1j if variable=='proper_clock_frequency' else 1.
    left=np.exp(z*float(e)*t);right=np.exp(-z*float(e)*t)
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ArithmeticError('external energy continuation exceeds this finite numerical chart')
    return dict(left=left,right=right,left_first=z*t*left,right_first=-z*t*right,
        variable=variable,analytic_dual_not_conjugated=True,
        equation='left exp(+z E tau), right exp(-z E tau); z=i before continuation, z=1 after t=t0-i tau')


def proper_clock_at_nodes(coordinate_nodes,lapse,*,order=16):
    """Integrate the reached lapse; report refinement, not an enclosure."""
    u=np.asarray(coordinate_nodes)
    if (u.dtype.kind not in 'fiu' or u.ndim!=1 or not np.isfinite(u).all() or
            np.any(u<0) or type(order)is not int or order<8):
        raise ValueError('finite nonnegative chronological nodes and resolved clock quadrature required')
    def apply(q):
        z,w=np.polynomial.legendre.leggauss(q);out=[]
        for end in u:
            values=np.array([lapse(float(x))for x in (z+1)*end/2])
            if values.dtype.kind not in 'fiu' or not np.isfinite(values).all() or np.any(values<=0):
                raise ValueError('reached future positive lapse application required')
            out.append(float(end/2*(w@values)))
        return np.array(out)
    fine=apply(order);coarse=apply(order//2)
    return dict(proper_times=fine,lower_order_proper_times=coarse,
        quadrature_refinement_difference=fine-coarse,clock_order=order,
        clock_origin='lower face of same chronological numerical cell',clock_enclosure_claimed=False)


def two_current_energy_application(left,right,left_first,right_first,fermion_spectrum,
        field_spectrum,*,cutoff):
    """The Gaussian sign and both numerator derivatives, with fixed Green."""
    L,R,LE,RE=(np.asarray(a)for a in(left,right,left_first,right_first))
    f,b=(np.asarray(a)for a in(fermion_spectrum,field_spectrum))
    if (f.ndim!=1 or b.ndim!=1 or L.ndim!=3 or R.ndim!=3 or
            L.shape[1:]!=(len(f),len(b)) or R.shape[::2]!=(len(f),len(b)) or
            LE.shape!=L.shape or RE.shape!=R.shape or
            any(a.dtype.kind not in 'fciu' or not np.isfinite(a).all()for a in(L,R,LE,RE,f,b))):
        raise ValueError('complete same-domain spectra and both directed current moments required')
    K=temporal_image_green_kernel(f[:,None],b[None,:],cutoff=cutoff)['value']
    apply=lambda a,d:-np.einsum('ifa,fja,fa->ij',a,d,K,optimize=True)
    l,r=apply(LE,R),apply(L,RE)
    return dict(value=apply(L,R),left_energy_contact=l,right_energy_contact=r,
        energy_first=l+r,internal_operator_energy_direction_held_fixed=True)


def current_external_energy_moments(F,B,points,p,dp,measure,external_norm,proper_times,
        *,energy,variable,external=0,map_cache=None):
    """Export actual base/first moments for the inherited constant or n1 leg.

    The external tent is the existing numerical domain.  No physical
    exterior pole, continuum state or altered native boundary is selected.
    Full acted-trial and non-Hermitian left placements remain independent.
    """
    nt=len(points);p,dp,measure,tau=map(np.asarray,(p,dp,measure,proper_times))
    if (external not in (0,1) or p.shape!=(nt,8) or dp.shape!=p.shape or
            measure.shape!=(nt,) or tau.shape!=(nt,) or np.any(measure<=0) or
            not np.isfinite(float(external_norm)) or external_norm<=0):
        raise ValueError('same chronological quadrature and positive external tent Gram required')
    weights=external_energy_weights(tau,energy,variable=variable)
    size=len(F['eigenvalues']);mb=len(B['eigenvalues']);ni=6*(1 if external==0 else 4)
    out=dict(left=np.zeros((ni,size,mb),complex),right=np.zeros((size,ni,mb),complex),
        left_first=np.zeros((ni,size,mb),complex),right_first=np.zeros((size,ni,mb),complex))
    cache={}if map_cache is None else map_cache;images=magnetic_current_angular_images();fi=F['family_indices']
    for j,point in enumerate(points):
        key=(B['name'],j,'base')
        if key not in cache:cache[key]=_base_maps(B,point,images)
        _,fields=cache[key];V,AV=_trial(F,point,p[j],dp[j])
        vertex=point['vertices'][:,fi][:,:,fi]
        R,L=_vertex_sources(fields,vertex,F['real_to_complex'],F['parity'],B['parity'],B['harmonic_indices'],images,external)
        external_tent=2*min(point['response_time']/point['length'],1-point['response_time']/point['length'])
        factor=measure[j]*external_tent/np.sqrt(external_norm)
        l=factor*np.einsum('ida,dI->iIa',L,V,optimize=True)
        r=factor*(AV.conj().T@R.reshape(len(V),-1)).reshape(size,ni,mb)
        out['left']+=weights['left'][j]*l;out['right']+=weights['right'][j]*r
        out['left_first']+=weights['left_first'][j]*l
        out['right_first']+=weights['right_first'][j]*r
    return dict(**out,energy=float(energy),energy_variable=variable,
        two_external_contacts_retained=True,internal_operator_or_domain_continued=False)


def changing_constant_energy_application(fermions,fields,points,p,dp,measure,proper_times,
        *,energy,variable,cutoff,progress=None):
    """Execute the nonmagnetic constant-input kernel and its energy jet.

    All supplied starting field blocks are consumed.  The constant angular
    input fixes the intermediate fermion shell to that field shell, with
    both literal spectator signs and every fixed-Y family retained.
    """
    measure=np.asarray(measure);nt=len(points)
    if not fields or not fermions or nt==0:raise ValueError('actual complete field/current applications required')
    bext=np.array([2*min(a['response_time']/a['length'],1-a['response_time']/a['length'])for a in points])
    norm=float(measure@bext**2);arrays={k:np.zeros((18,18),complex)for k in
        ('value','left_energy_contact','right_energy_contact','energy_first')};records=[]
    for family in sorted(set(f['family']for f in fermions)):
        fs=[f for f in fermions if f['family']==family];fi=fs[0]['family_indices']
        for B in fields:
            cache={};local={k:np.zeros((6,6),complex)for k in arrays};count=0
            for F in fs:
                if F['level']!=B['level'] or abs(-F['level']+2*F['spectator'])!=B['absolute_spectator']:
                    continue
                m=current_external_energy_moments(F,B,points,p,dp,measure,norm,proper_times,
                    energy=energy,variable=variable,map_cache=cache)
                a=two_current_energy_application(m['left'],m['right'],m['left_first'],m['right_first'],
                    F['eigenvalues'],B['eigenvalues'],cutoff=cutoff)
                for k in arrays:local[k]+=a[k]
                count+=1
            if count==0:raise ValueError('complete constant-current fermion return missing for field block '+B['name'])
            for k in arrays:arrays[k][np.ix_(fi,fi)]+=local[k]
            r=dict(family=family,field_block=B['name'],fermion_return_blocks=count,
                value_norm=float(np.linalg.norm(local['value'])),energy_first_norm=float(np.linalg.norm(local['energy_first'])))
            records.append(r)
            if progress is not None:progress(r)
    return dict(**arrays,block_records=records,external_tent_Gram=norm,
        energy=float(energy),energy_variable=variable,proper_times=np.asarray(proper_times),
        complete_supplied_starting_field_blocks_consumed=True,charged_projection_before_full_return=False,
        Gaussian_sign=-1,statistics_or_supertrace_factor_reinserted=False,
        internal_positive_reference_identified_with_continued_Lorentz_operator=False,
        physical_LSZ_residue_or_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None)
