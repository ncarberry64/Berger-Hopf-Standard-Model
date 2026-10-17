"""Magnetic first variation of the actual joint one-form/DG action.

Both angular parity images are differentiated before the paired Green
application. The curvature contact and the background dependence of the
gauge-orbit images are retained. Lorenz fixing is differentiated only
after integration of its weak maps and ghost Gram.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import cho_solve,cholesky
from .muon_magnetic_mixed_green import _finite
from .muon_coupled_higgs_magnetic_source import _multiplication
from .muon_coupled_field_angular_images import one_form_angular_point
from .muon_parent_positive_brst_ghost import _linear_curvature
from .muon_parent_positive_gauge_form import _weighted_curvature_maps,positive_curvature_contact_matrix
from .muon_parent_maxwell_corrected_retarded import _ad
from .muon_matched_mechanical_source import epsilon


def _curvature_direction(A,a,at,ar,Es):
    ea=np.einsum('fcs,ijs->ifcj',a,Es)
    c=_linear_curvature(A,a,at,ar,ea)
    return dict(Ftr=c[0],Ft=c[1],Fr=c[2],B=c[3])


def _point_direction(base,target_count,G,a,deltaF,radial,temporal,densities):
    """d value and d curvature, including d_A D_A eta=[F,eta]."""
    no=base['point_harmonic_count'];ne=target_count;mo=56*no
    ad=lambda x:_multiplication(np.moveaxis(np.array([_ad(v)for v in x.T]),0,-1),G)
    ma=np.array([ad(x)for x in a]);value=base['value_map'].reshape(5,4*no,mo)
    dv=np.zeros((5,4*ne,mo));dc=np.zeros((40*ne,mo))
    # Independent one-forms: only the background connection varies.
    v=value[:,:,:40*no]
    X=ma[0]@v[1]-ma[1]@v[0]
    Ft=np.array([ma[0]@v[2+i]-ma[2+i]@v[0]for i in range(3)])
    Fr=np.array([ma[1]@v[2+i]-ma[2+i]@v[1]for i in range(3)])
    B=np.zeros_like(Ft)
    for i,j,k in np.argwhere(epsilon()):B[i]+=epsilon()[i,j,k]*(ma[2+j]@v[2+k])
    dc[:,:40*no]=_weighted_curvature_maps((X,Ft,Fr,B),densities)
    # The complete DG columns, with unchanged eta coefficient charts.
    curves=(ad(deltaF['Ftr']),np.array([ad(x)for x in deltaF['Ft']]),
        np.array([ad(x)for x in deltaF['Fr']]),np.array([ad(x)for x in deltaF['B']]))
    for p in range(2):
        g=temporal[2+2*p]
        for k,r in enumerate(radial):
            sl=slice(40*no+(2*p+k)*4*no,40*no+(2*p+k+1)*4*no)
            dv[:,:,sl]=g*r[0]*ma
            dc[:,sl]=g*r[0]*_weighted_curvature_maps(curves,densities)
    return dict(value=dv.reshape(20*ne,mo),curvature=dc)


def one_form_magnetic_source_point(*,connection,connection_time,connection_radial,
        odd_derivatives,even_derivatives,source_derivatives,gaunt,radial,metric,
        densities,temporal,source_gauge,source_gauge_time,source_gauge_radial):
    """Complete deltaK/deltaGram even<-odd on all five field components.

    The source already carries the physical magnetic charge normalization.
    The metric is held fixed in this first odd angular field direction.
    DG curvature is varied through deltaF, so source time/radial/angular
    derivatives enter the action rather than being discarded at the wall.
    No scalar or Lorenz term is assigned zero by this sector application.
    """
    names=('actual A','actual A time','actual A radial','complete odd E','complete even E',
        'complete source E','complete product image','same radial functions','actual positive metric',
        'same two-form densities','same temporal functions','total source','total source time','total source radial')
    A,At,Ar,Eo,Ee,Es,G,r,metric,d,t,a,at,ar=[_finite(v,n,real=True)for v,n in zip(
        (connection,connection_time,connection_radial,odd_derivatives,even_derivatives,source_derivatives,
         gaunt,radial,metric,densities,temporal,source_gauge,source_gauge_time,source_gauge_radial),names)]
    if (G.ndim!=3 or a.ndim!=4 or a.shape[1:3]!=(5,4)or a.shape[0]!=3 or a.shape[3]!=G.shape[2]
        or at.shape!=a.shape or ar.shape!=a.shape or Es.shape!=(3,G.shape[2],G.shape[2])
        or Eo.shape!=(3,G.shape[1],G.shape[1])or Ee.shape!=(3,G.shape[0],G.shape[0])):
        raise ValueError('complete same-angular source value/rate/radial image required')
    bo=one_form_angular_point(A,At,Ar,Eo,r,metric,d,t)
    be=one_form_angular_point(A,At,Ar,Ee,r,metric,d,t)
    no,ne=G.shape[1],G.shape[0];Co=positive_curvature_contact_matrix(bo['curvature'],d,no)
    Ce=positive_curvature_contact_matrix(be['curvature'],d,ne)
    _,gt,gr,gs,beta,_=metric
    small=np.diag([gt,gr+beta*beta*gt,gs,gs,gs]);small[0,1]=small[1,0]=-beta*gt
    Go,Ge=np.kron(small,np.eye(4*no)),np.kron(small,np.eye(4*ne))
    K=[];M=[];contacts=[];motions=[];fc=[]
    for j in range(3):
        f=_curvature_direction(A,a[j],at[j],ar[j],Es)
        do=_point_direction(bo,ne,G,a[j],f,r,t,d)
        de=_point_direction(be,no,G.transpose(1,0,2),a[j],f,r,t,d)
        Csource=np.stack([positive_curvature_contact_matrix({k:v[...,s]for k,v in f.items()},d,1)
            for s in range(G.shape[2])],axis=-1)
        dC=_multiplication(Csource,G)
        Vo,Ve=bo['value_map'],be['value_map'];Fo,Fe=bo['curvature_map'],be['curvature_map']
        contact=Ve.T@dC@Vo+de['value'].T@Co@Vo+Ve.T@Ce@do['value']
        K.append(Fe.T@do['curvature']+de['curvature'].T@Fo+contact)
        M.append(Ve.T@Ge@do['value']+de['value'].T@Go@Vo)
        contacts.append(contact);motions.append([np.linalg.norm(do['value']),np.linalg.norm(do['curvature'])])
        fc.append(np.concatenate([f['Ftr'].ravel(),f['Ft'].ravel(),f['Fr'].ravel(),f['B'].ravel()]))
    return dict(one_form_delta_Hessian_even_odd=np.array(K),one_form_delta_Gram_even_odd=np.array(M),
        curvature_contact_delta_Hessian_even_odd=np.array(contacts),
        dependent_DG_value_and_curvature_motion_norms=np.array(motions),source_curvature_coefficients=np.array(fc),
        ghost_Gram_source_variation_exact_zero=True,
        ghost_Gram_zero_reason='fixed geometry eta scalar Gram has no A dependence; DG one-form images do vary',
        Lorenz_source_derivative_requires_integrated_weak_maps=True,
        scalar_coupling_not_filled_zero=True,physical_P_strat_or_Pauli_completed=False)


def integrated_lorenz_magnetic_source(*,even_one_form_Gram,odd_one_form_Gram,
        even_ghost_Gram,odd_ghost_Gram,delta_one_form_Gram_even_odd):
    """Differentiate B^T Gram_ghost^-1 B on the integrated parity charts.

    B=<D_A eta,a> includes the moving DG field images; the fixed-metric
    eta Gram is action-independent of A. Both product placements are
    retained. This is the weak Lorenz component before MAXWELL_TO_CAP.
    """
    Ge,Go,He,Ho,dG=[_finite(v,n,real=True)for v,n in zip(
        (even_one_form_Gram,odd_one_form_Gram,even_ghost_Gram,odd_ghost_Gram,delta_one_form_Gram_even_odd),
        ('integrated even one-form Gram','integrated odd one-form Gram','integrated even eta Gram',
         'integrated odd eta Gram','integrated magnetic Gram derivative'))]
    ne,no=len(Ge)//56,len(Go)//56
    if (Ge.shape!=(56*ne,56*ne)or Go.shape!=(56*no,56*no)or min(ne,no)<1
        or He.shape!=(16*ne,16*ne)or Ho.shape!=(16*no,16*no)or dG.ndim!=3 or dG.shape[1:]!=(56*ne,56*no)):
        raise ValueError('complete integrated one-form/DG parity Grams required')
    Be,Bo=Ge[40*ne:],Go[40*no:]
    Fe=cho_solve((cholesky(He,lower=True),True),Be)
    Fo=cho_solve((cholesky(Ho,lower=True),True),Bo)
    delta=np.array([Fe.T@d[40*ne:]+d[:,40*no:]@Fo for d in dG])
    return dict(Lorenz_delta_Hessian_even_odd=delta,even_weak_Lorenz_map=Fe,odd_weak_Lorenz_map=Fo,
        integrated_before_gauge_fixing=True,all_two_product_placements_retained=True,
        no_new_Rxi_mass_or_gauge_parameter_selected=True)
