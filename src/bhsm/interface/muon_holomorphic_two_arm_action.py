"""Literal full536 two-arm action on the complexified material trace graph.

The child's total connection depends on the actual parent mechanical
profile and the fixed reference difference. All parent profile first and
second contacts are applied before taking temporal cotangents. Analytic
realified coefficient duals use transpose, with no Hilbert conjugation.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_child_action import holomorphic_inherited_child_action
from .muon_holomorphic_normal_geometry import holomorphic_geometry_rows,holomorphic_cap_and_weights
from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
from .muon_nonlinear_n0_field_action import analytic_intrinsic_n0_jet
from .muon_parent_maxwell_full_weak import M
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_retarded_hypercharge import WALL
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_complex_endpoint_area_action import original_endpoint_area_coefficient


def _profile(raw,rho):
    return holomorphic_geometry_rows(raw[:100],rho,connection_only=True)


def _values(application):
    return np.array([[r[k].value for k in ('connection_lambda','lambda_tau','lambda_rho')]for r in application['rows']])


def holomorphic_two_arm_action(raw_pair,reference_pair,representation,*,
        nu_squared_action=4,surface_gamma=None):
    """Execute the anchored finite graph, including its nonlinear source maps.

    Inputs are simultaneous supplied snapshots. A prescribed affine parent
    is not declared a solved canonical parent merely because it is passed
    here. The reference clock is a separate explicit source application.
    """
    raw=np.asarray(raw_pair,complex);reference=np.asarray(reference_pair,complex);rep=representation
    if raw.shape!=(2,268)or reference.shape!=raw.shape:raise ValueError('complete same-vector two-arm fields/reference required')
    nr=268;hs=260;N=80;dim=536
    params=dict(nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)
    # Both base applications retain the exact cap, child subtraction,
    # density/scalar weights and independent field derivatives. Only their
    # fixed-profile source chart is completed below.
    pairP=np.stack((raw[0],raw[0]));parent_fixed=holomorphic_inherited_child_action(raw[0],0,pairP,pairP,rep,**params)
    child_fixed=holomorphic_inherited_child_action(raw[1],0,raw,reference,rep,**params)
    g=np.r_[parent_fixed['raw_gradient'],child_fixed['raw_gradient']]
    H=np.zeros((dim,dim),complex);H[:nr,:nr]=parent_fixed['raw_hessian'];H[nr:,nr:]=child_fixed['raw_hessian']
    value=parent_fixed['value']+child_fixed['value'];parent_g=parent_fixed['raw_gradient'].copy();parent_H=parent_fixed['raw_hessian'].copy()
    source_profile=_profile(raw[0],rep['rho']);source_wall=_profile(raw[0],[WALL]);pp=_values(source_profile)
    rp,rc=(_values(_profile(x,rep['rho']))for x in reference)
    wp=_values(source_wall)[0];wrp,wrc=(_values(_profile(x,[WALL]))[0]for x in reference)
    gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(pp),80,20)
    gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(pp),80,20)
    fieldmap=np.zeros((len(pp),60,160),complex);fieldmap[:,:20,:80]=gb.transpose(0,2,1)
    fieldmap[:,20:40,80:]=gb.transpose(0,2,1);fieldmap[:,40:,:80]=gr.transpose(0,2,1)
    source_gradient=np.zeros(dim,complex);source_Hessian=np.zeros((dim,dim),complex)
    branch_fields=[];branch_local=[];branch_scalar=[];reference_work=0j
    # Source profile maps only into the first geometry100 block: the
    # child's own lambda cancels in its TOTAL connection, while its
    # subtracted mechanical action/geometry remains in child_fixed.
    for arm in range(2):
        offset=arm*nr;eff=pp if arm==0 else pp-rp+rc;wv=wp if arm==0 else wp-wrp+wrc
        A=np.einsum('rjc,j->rc',gb,raw[arm,100:180]).reshape(-1,5,4)
        At=np.einsum('rjc,j->rc',gb,raw[arm,180:260]).reshape(-1,5,4)
        Ar=np.einsum('rjc,j->rc',gr,raw[arm,100:180]).reshape(-1,5,4)
        A[:,2:]+=M[None]*(eff[:,0]-1)[:,None,None]
        At[:,2:]+=M[None]*eff[:,1,None,None];Ar[:,2:]+=M[None]*eff[:,2,None,None]
        geometry=holomorphic_geometry_rows(raw[arm,:100],rep['rho'])
        density_names=('electric','radial','angular','electric_radial','shift')
        density=np.array([[r[k].value for k in density_names]for r in geometry['rows']])
        local=analytic_constant_maxwell_batch(A,At,Ar,density)
        gdc=np.empty((len(pp),60,5),complex)
        for k in range(4):
            c=np.zeros_like(density);c[:,k]=1;c[:,4]=density[:,4]
            gdc[:,:,k]=analytic_constant_maxwell_batch(A,At,Ar,c)['gradient']
        cplus=density.copy();cminus=density.copy();cplus[:,4]+=1;cminus[:,4]-=1
        gdc[:,:,4]=(analytic_constant_maxwell_batch(A,At,Ar,cplus)['gradient']-
            analytic_constant_maxwell_batch(A,At,Ar,cminus)['gradient'])/2
        for j,(row,weight)in enumerate(zip(source_profile['rows'],rep['radial_quadrature'])):
            J=np.zeros((60,100),complex);J2=np.zeros((60,100,100),complex)
            for k,key in enumerate(('connection_lambda','lambda_tau','lambda_rho')):
                J[k*20+8:(k+1)*20]=M.reshape(12,1)*row[key].gradient[None,:]
                J2[k*20+8:(k+1)*20]=M.reshape(12,1,1)*row[key].hessian[None,:,:]
            factor=weight*MAXWELL_TO_CAP;lg=local['gradient'][j];lk=local['hessian'][j]
            sg=factor*J.T@lg;sh=factor*(J.T@lk@J+np.einsum('a,aij->ij',lg,J2,optimize=True))
            source_gradient[:100]+=sg;source_Hessian[:100,:100]+=sh
            fieldcross=factor*J.T@lk@fieldmap[j]
            source_Hessian[:100,offset+100:offset+260]+=fieldcross
            source_Hessian[offset+100:offset+260,:100]+=fieldcross.T
            density_first=np.array([geometry['rows'][j][k].gradient for k in density_names])
            cross=factor*J.T@gdc[j]@density_first
            source_Hessian[:100,offset:offset+100]+=cross
            source_Hessian[offset:offset+100,:100]+=cross.T
            if arm==0:
                parent_g[:100]+=sg;parent_H[:100,:100]+=sh+cross+cross.T
                parent_H[:100,100:260]+=fieldcross;parent_H[100:260,:100]+=fieldcross.T
            else:
                # F_t=-M delta_lambda_ref,t. Positive work is the negative
                # explicit connection-clock action variation, as in the
                # retained anchored-reference energy equation.
                template=np.zeros(60,complex);template[28:40]=M.reshape(-1)*(rp[j,1]-rc[j,1])
                reference_work+=factor*(lg@template)
        cap=holomorphic_cap_and_weights(raw[arm,:100],points=rep['cap_points'])
        weights=[cap[k]for k in ('wT','wS','wV')];weights_values=np.array([x.value for x in weights])
        wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[arm,100:180]);wall[2:]+=M*(wv[0]-1)
        scalar=analytic_intrinsic_n0_jet(wall,raw[arm,260:264],raw[arm,264:],weights_values,
            lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)
        J=np.zeros((28,100),complex);J[12:24]=M.reshape(12,1)*source_wall['rows'][0]['connection_lambda'].gradient[None,:]
        J2=np.zeros((28,100,100),complex);J2[12:24]=M.reshape(12,1,1)*source_wall['rows'][0]['connection_lambda'].hessian[None,:,:]
        S=np.zeros((28,168),complex);S[:4,160:164]=np.eye(4);S[4:24,:80]=rep['wall_trace_map'].reshape(20,80);S[24:,164:]=np.eye(4)
        sg=J.T@scalar['gradient'];sh=J.T@scalar['hessian']@J+np.einsum('a,aij->ij',scalar['gradient'],J2,optimize=True)
        fieldcross=J.T@scalar['hessian']@S
        source_gradient[:100]+=sg;source_Hessian[:100,:100]+=sh
        source_Hessian[:100,offset+100:offset+268]+=fieldcross
        source_Hessian[offset+100:offset+268,:100]+=fieldcross.T
        cross=np.zeros((100,100),complex)
        for k,weight in enumerate(weights):
            part=analytic_intrinsic_n0_jet(wall,raw[arm,260:264],raw[arm,264:],np.eye(3)[k],
                lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)
            cross+=np.outer(J.T@part['gradient'],weight.gradient)
        source_Hessian[:100,offset:offset+100]+=cross
        source_Hessian[offset:offset+100,:100]+=cross.T
        if arm==0:
            parent_g[:100]+=sg;parent_H[:100,:100]+=sh+cross+cross.T
            parent_H[:100,100:]+=fieldcross;parent_H[100:,:100]+=fieldcross.T
        branch_fields.append(dict(A=A,At=At,Ar=Ar,wall=wall));branch_local.append(local);branch_scalar.append(scalar)
    g+=source_gradient;H+=source_Hessian
    c=generic_coordinate_lift(rep['gauge_labels']);P=c['lift'];R=np.zeros((536,504),complex);R[:268,:252]=P;R[268:,252:]=P
    n=106;vi=np.r_[np.arange(n,2*n),252+np.arange(n,2*n)];yi=np.r_[np.arange(2*n,252),252+np.arange(2*n,252)]
    G=R.T@g;HH=R.T@H@R;pg=P.T@parent_g;ph=P.T@parent_H@P
    theta=-G[vi].copy();theta[:n]+=2*pg[n:2*n]
    theta_first=-HH[vi].copy();theta_first[:n,:252]+=2*ph[n:2*n]
    area=[original_endpoint_area_coefficient(x,P)for x in raw]
    ag=np.r_[area[0]['gradient'],area[1]['gradient']];ah=np.zeros((504,504),complex)
    ah[:252,:252]=area[0]['hessian'];ah[252:,252:]=area[1]['hessian']
    area_theta=-ag[vi].copy();area_theta[:n]+=2*area[0]['gradient'][n:2*n]
    return dict(value=value,raw_gradient=g,raw_hessian=H,gradient=G,hessian=HH,
        parent=dict(value=parent_fixed['value'],raw_gradient=parent_g,raw_hessian=parent_H,gradient=pg,hessian=ph),
        constant_profile_child=child_fixed,source_gradient_contact=source_gradient,source_Hessian_contact=source_Hessian,
        temporal_cotangent=theta,temporal_cotangent_first=theta_first,
        area_gradient_per_gamma=ag,area_Hessian_per_gamma=ah,area_temporal_cotangent_per_gamma=area_theta,
        area_value_per_gamma=area[0]['value']+area[1]['value'],reference_clock_work=reference_work,
        master_lift=R,one_lift=P,velocity_indices=vi,algebraic_indices=yi,
        branch_fields=branch_fields,profile_parent_values=pp,profile_reference_difference=rp-rc,
        original_material_advection_count=1,raw_action_dual_conjugated=False,
        simultaneous_pair_or_parent_stationarity_claimed=False,physical_reset_first_hit_selected=False)
