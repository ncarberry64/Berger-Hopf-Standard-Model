"""Exact reference-only explicit clock of the complete two-arm action.

Actual parent motion belongs to the joint canonical x/v equations. Only
the recorded reference affine germs move in this partial derivative.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_normal_geometry import holomorphic_geometry_rows,holomorphic_cap_and_weights
from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
from .muon_nonlinear_n0_field_action import analytic_intrinsic_n0_jet
from .muon_parent_maxwell_full_weak import M
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_retarded_hypercharge import WALL


def reference_affine_raw_rate(reference_pair):
    ref=np.asarray(reference_pair,complex);rate=np.zeros_like(ref)
    if ref.shape!=(2,268):raise ValueError('same complete reference pair required')
    rate[:,:37]=ref[:,37:74];rate[:,98]=ref[:,99]
    return rate


def joint_reference_explicit_clock(raw_pair,reference_pair,rep,action,*,nu_squared_action):
    """Return partial_t L and grad L at fixed actual raw_pair.

    Parent source J still differentiates the clocked child connection. It
    is completed before the raw536-to-master504 cotangent pullback.
    """
    raw=np.asarray(raw_pair,complex);ref=np.asarray(reference_pair,complex)
    rates=reference_affine_raw_rate(ref);parent=holomorphic_geometry_rows(raw[0,:100],rep['rho'],connection_only=True)
    parentwall=holomorphic_geometry_rows(raw[0,:100],[WALL],connection_only=True)
    keys=('connection_lambda','lambda_tau','lambda_rho')
    def profile_rate(rho):
        parts=[holomorphic_geometry_rows(x[:100],rho,connection_only=True)['rows']for x in ref]
        return sum(sign*np.array([[row[k].gradient@rate[:100]for k in keys]for row in rows])
            for sign,rows,rate in zip((-1,1),parts,rates))
    rt=profile_rate(rep['rho']);wt=profile_rate([WALL])[0]
    field_rate=np.zeros((len(rt),3,5,4),complex);field_rate[:,:,2:]=rt[:,:,None,None]*M[None,None]
    field_rate=field_rate.reshape(len(rt),60)
    fields=action['branch_fields'][1];A,At,Ar=(fields[k]for k in('A','At','Ar'))
    geo=holomorphic_geometry_rows(raw[1,:100],rep['rho']);density_keys=('electric','radial','angular','electric_radial','shift')
    density=np.array([[row[k].value for k in density_keys]for row in geo['rows']]);local=analytic_constant_maxwell_batch(A,At,Ar,density)
    gdc=np.empty((len(rt),60,5),complex)
    for k in range(4):
        unit=np.zeros_like(density);unit[:,k]=1;unit[:,4]=density[:,4]
        gdc[:,:,k]=analytic_constant_maxwell_batch(A,At,Ar,unit)['gradient']
    dp,dm=density.copy(),density.copy();dp[:,4]+=1;dm[:,4]-=1
    gdc[:,:,4]=(analytic_constant_maxwell_batch(A,At,Ar,dp)['gradient']-analytic_constant_maxwell_batch(A,At,Ar,dm)['gradient'])/2
    gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(rt),80,20);gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(rt),80,20)
    raw_clock=np.zeros(536,complex);value_clock=0j
    for j,w in enumerate(rep['radial_quadrature']):
        factor=w*MAXWELL_TO_CAP;rate=field_rate[j];J=np.zeros((60,100),complex)
        for k,key in enumerate(keys):J[k*20+8:(k+1)*20]=M.reshape(12,1)*parent['rows'][j][key].gradient[None,:]
        acted=local['hessian'][j]@rate
        raw_clock[:100]+=factor*J.T@acted
        raw_clock[368:448]+=factor*(gb[j]@acted[:20]+gr[j]@acted[40:])
        raw_clock[448:528]+=factor*gb[j]@acted[20:40]
        df=np.array([geo['rows'][j][k].gradient for k in density_keys])
        raw_clock[268:368]+=factor*df.T@gdc[j].T@rate
        value_clock+=factor*(local['gradient'][j]@rate)
    cap=holomorphic_cap_and_weights(raw[1,:100],points=rep['cap_points']);weights=[cap[k]for k in('wT','wS','wV')]
    wall=fields['wall'];args=dict(lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)
    scalar=analytic_intrinsic_n0_jet(wall,raw[1,260:264],raw[1,264:],np.array([w.value for w in weights]),**args)
    wr=np.zeros(28,complex);wr[12:24]=M.reshape(-1)*wt[0]
    J=np.zeros((28,100),complex);J[12:24]=M.reshape(12,1)*parentwall['rows'][0]['connection_lambda'].gradient[None,:]
    S=np.zeros((28,168),complex);S[:4,160:164]=np.eye(4);S[4:24,:80]=rep['wall_trace_map'].reshape(20,80);S[24:,164:]=np.eye(4)
    acted=scalar['hessian']@wr;raw_clock[:100]+=J.T@acted;raw_clock[368:]+=S.T@acted
    for j,w in enumerate(weights):
        part=analytic_intrinsic_n0_jet(wall,raw[1,260:264],raw[1,264:],np.eye(3)[j],**args)
        raw_clock[268:368]+=w.gradient*(part['gradient']@wr)
    value_clock+=scalar['gradient']@wr
    return dict(value_clock_first=value_clock,raw_gradient_clock_first=raw_clock,
        gradient_clock_first=action['master_lift'].T@raw_clock,reference_raw_coordinate_rate=rates,
        effective_connection_clock_first=rt,effective_wall_connection_clock_first=wt,
        actual_parent_partial_clock_count=0,actual_parent_motion_in_joint_Hvx_v=True,
        cap_and_mechanical_baseline_explicit_reference_clock=0j)
