"""Actual first-order action sewing between independently centered charts.

The intermediate real source-cell boundary is preserved.  Each connector
is evolved from its own action coefficient germ, with the independent
conjugate-reflected branch and both directed magnetic source maps.
This is a canonical trace/dual/source application at c=0.  It is not a
finite-c spectral Schur or a completed relative heat return.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm,expm_frechet
from .muon_continued_action_reality import _geometry,action_reality_coefficient,action_reality_source
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_piecewise_euclidean_action import FAMILY_INDICES
from .muon_changing_magnetic_current_jets import magnetic_current_angular_images


def source_cell_endpoint(phase,curves,cell,endpoint):
    """Execute the actual proper-clock germ at a cell's boundary offset."""
    grid=np.asarray(curves['times'],float);j=int(cell)
    if endpoint not in('left','right')or not 0<=j<len(grid)-1:raise ValueError('actual cell/endpoint required')
    L=abs(float(phase['receipt']['span']));left,right=grid[j:j+2]
    anchor=(left+right)/2-L if phase['receipt']['side']=='incoming'else(left+right)/2
    x=profile_preserving_raw_sample(phase,anchor);raw,rate=x['raw_fields'],x['raw_coordinate_time_derivative']
    gn,gw=np.polynomial.legendre.leggauss(4);half=(right-left)/2
    length=float(half*sum(w*action_reality_coefficient(phase,anchor+half*z)['geometry']['N'].real for z,w in zip(gn,gw)))
    stop=(-1 if endpoint=='left'else 1)*length/2
    def rhs(t,z):return np.array([-1j/_geometry(raw+z[0]*rate)['N']])
    sol=solve_ivp(rhs,(0,stop),[0j],rtol=1e-12,atol=1e-18,max_step=abs(stop)/4)
    if not sol.success:raise ArithmeticError(sol.message)
    offset=sol.y[0,-1]
    real_boundary=float(left if endpoint=='left'else right)-L if phase['receipt']['side']=='incoming'else float(left if endpoint=='left'else right)
    return dict(cell=j,endpoint=endpoint,coordinate_anchor=float(anchor),
        coordinate_endpoint=complex(anchor)+offset,coordinate_offset=offset,
        owned_real_boundary=real_boundary,proper_length=length)


def _block_step(Gt,Gs,X):
    dt,ds=X.shape[-2:];block=np.zeros((dt+ds,dt+ds),complex)
    block[:dt,:dt]=Gt;block[dt:,dt:]=Gs;block[:dt,dt:]=X
    return expm(block)[:dt,dt:]


def canonical_segment_application(coefficient,source,start,stop,*,substeps):
    """Midpoint action evolution and both source placements on a segment.

coefficient(t)->(Hsource,Htarget,N), source(t)->(Xi_ts,Xi_st).
Their independent conjugate-reflected branches are evaluated by calling
the SAME action functions at conj(t).  No external dual is assigned.
    """
    start,stop=complex(start),complex(stop);count=int(substeps)
    if count<1:raise ValueError('positive numerical subdivision required')
    Hs,Ht,N=coefficient((start+stop)/2);Xi,Xrev=source((start+stop)/2)
    ds,dt=len(Hs),len(Ht);axes=len(Xi)
    Us,Ut=np.eye(ds,dtype=complex),np.eye(dt,dtype=complex)
    Rs,Rt=Us.copy(),Ut.copy();Z=np.zeros((axes,dt,ds),complex);Y=np.zeros((axes,ds,dt),complex);Zr=Z.copy()
    step=(stop-start)/count
    for k in range(count):
        t=start+(k+.5)*step;hs,ht,N=coefficient(t);xi,xrev=source(t)
        sr,tr,Nr=coefficient(t.conjugate());xr,_=source(t.conjugate())
        gs,gt=-1j*N*step*hs,-1j*N*step*ht
        grs,grt=-1j*Nr*step.conjugate()*sr,-1j*Nr*step.conjugate()*tr
        us,ut,rs,rt=expm(gs),expm(gt),expm(grs),expm(grt)
        z=np.array([_block_step(gt,gs,-1j*N*step*x)for x in xi])
        y=np.array([_block_step(gs,gt,-1j*N*step*x)for x in xrev])
        zr=np.array([_block_step(grt,grs,-1j*Nr*step.conjugate()*x)for x in xr])
        Z=np.einsum('ij,ajk->aik',ut,Z)+np.einsum('aij,jk->aik',z,Us)
        Y=np.einsum('ij,ajk->aik',us,Y)+np.einsum('aij,jk->aik',y,Ut)
        Zr=np.einsum('ij,ajk->aik',rt,Zr)+np.einsum('aij,jk->aik',zr,Rs)
        Us,Ut,Rs,Rt=us@Us,ut@Ut,rs@Rs,rt@Rt
    left=np.linalg.solve(Us,np.eye(ds));target_left=np.linalg.solve(Ut,np.eye(dt))
    inverse_reverse=-np.einsum('ij,ajk,kl->ail',left,Y,target_left)
    return dict(source_trace=Us,target_trace=Ut,source_left_dual=left,target_left_dual=target_left,
        magnetic_forward_trace=Z,magnetic_reverse_trace=Y,
        independent_reflected_source_trace=Rs,independent_reflected_target_trace=Rt,
        independent_reflected_magnetic_forward=Zr,
        reflected_source_dual_residual_max=float(np.max(abs(Rs.conj().T-left))),
        reflected_target_dual_residual_max=float(np.max(abs(Rt.conj().T-target_left))),
        reflected_source_contact_dual_residual_max=float(np.max(abs(Zr.conj().swapaxes(-1,-2)-inverse_reverse))),
        source_inverse_pairing_residual_max=float(np.max(abs(left@Us-np.eye(ds)))),
        substeps=count,start=start,stop=stop)


def canonical_segment_parameter_variation(coefficient_jet,start,stop,*,start_first=0j,stop_first=0j,substeps):
    """Differentiate trace and analytic dual with coefficient AND clock jets.

coefficient_jet(t,t_first) returns H,N,H_first,N_first from the same
action/chart.  H_first/N_first include both explicit field variation and
their coordinate-time contact t_first.  The moving-segment contribution
is additionally -i N H (stop_first-start_first)/substeps, once.
This consumes an action-derived variation callback; it never chooses a
physical mean or regards fixed-clock source variation as a full mean.
    """
    start,stop=complex(start),complex(stop);a,b=complex(start_first),complex(stop_first)
    n=int(substeps)
    if n<1:raise ValueError('positive numerical subdivision required')
    H,_,_,_=coefficient_jet((start+stop)/2,(a+b)/2);d=len(H)
    U=np.eye(d,dtype=complex);dU=np.zeros((d,d),complex)
    step,dstep=(stop-start)/n,(b-a)/n
    for k in range(n):
        s=(k+.5)/n;t=start+s*(stop-start);dt=a+s*(b-a)
        H,N,Hfirst,Nfirst=coefficient_jet(t,dt)
        G=-1j*N*step*H
        dG=-1j*(step*(Nfirst*H+N*Hfirst)+dstep*N*H)
        P,dP=expm_frechet(G,dG)
        dU=dP@U+P@dU;U=P@U
    left=np.linalg.solve(U,np.eye(d));dleft=-left@dU@left
    return dict(trace=U,trace_first=dU,left_dual=left,left_dual_first=dleft,
        pairing_first_residual_max=float(np.max(abs(dleft@U+left@dU))),
        endpoint_clock_contacts_retained=True,substeps=n)


def _actual_functions(phase,curves,anchor,family):
    fi=FAMILY_INDICES[int(family)];rep=lepton_current_hilbert_representation()
    alpha=rep['alpha'][:,fi][:,:,fi];E=magnetic_current_angular_images()['derivatives']['field_odd']
    angular=-1j*sum(np.kron(a,e)for a,e in zip(alpha,E))
    def coefficient(t):
        a=action_reality_coefficient(phase,float(anchor),complex(t)-float(anchor));H=a['Hcan'][np.ix_(fi,fi)];geo=a['geometry']
        return H,np.kron(H,np.eye(20))+angular/geo['R4'],geo['N']
    def source(t):
        X=action_reality_source(phase,float(anchor),curves,complex(t)-float(anchor))['Xi'][:3][:,:,fi][:,:,:,fi]
        return X.transpose(0,2,1,3).reshape(3,120,6),X.transpose(0,2,3,1).reshape(3,6,120)
    return coefficient,source


def source_corner_application(left_phase,left_curves,left_cell,right_phase,right_curves,right_cell,*,substeps=4,family=1):
    """Execute endpoint→real boundary→endpoint including birth T=I.

The original common canonical frame supplies identity only at the owned
real corner.  It is not assumed between the displaced complex endpoints.
The returned nonunitary connector carries its own independent dual and
source derivative.  Finite-c heat must retain its spectral domain return.
    """
    a=source_cell_endpoint(left_phase,left_curves,left_cell,'right')
    b=source_cell_endpoint(right_phase,right_curves,right_cell,'left')
    if abs(a['owned_real_boundary']-b['owned_real_boundary'])>1e-20:
        raise ValueError('same owned real corner required')
    boundary=a['owned_real_boundary']
    C1,X1=_actual_functions(left_phase,left_curves,a['coordinate_anchor'],family)
    C2,X2=_actual_functions(right_phase,right_curves,b['coordinate_anchor'],family)
    first=canonical_segment_application(C1,X1,a['coordinate_endpoint'],boundary,substeps=substeps)
    second=canonical_segment_application(C2,X2,boundary,b['coordinate_endpoint'],substeps=substeps)
    U=second['source_trace']@first['source_trace'];T=second['target_trace']@first['target_trace']
    Z=np.einsum('ij,ajk->aik',second['target_trace'],first['magnetic_forward_trace'])
    Z+=np.einsum('aij,jk->aik',second['magnetic_forward_trace'],first['source_trace'])
    Y=np.einsum('ij,ajk->aik',second['source_trace'],first['magnetic_reverse_trace'])
    Y+=np.einsum('aij,jk->aik',second['magnetic_reverse_trace'],first['target_trace'])
    return dict(source_trace=U,target_trace=T,magnetic_forward_trace=Z,magnetic_reverse_trace=Y,
        source_left_dual=np.linalg.solve(U,np.eye(6)),target_left_dual=np.linalg.solve(T,np.eye(120)),
        left_endpoint=a,right_endpoint=b,corner_displacement=b['coordinate_endpoint']-a['coordinate_endpoint'],
        first_segment=first,second_segment=second,
        source_trace_identity_difference_norm=float(np.linalg.norm(U-np.eye(6))),
        source_trace_unitarity_defect_norm=float(np.linalg.norm(U.conj().T@U-np.eye(6))),
        magnetic_forward_trace_norm=float(np.linalg.norm(Z)),
        first_order_c0_action_application_only=True,
        finite_c_heat_or_maximal_exterior_domain_completed=False)
