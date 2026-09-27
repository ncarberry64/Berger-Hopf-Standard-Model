"""Native retained-action sector jets at the stored parent/event center.

No moving-seam embedding or environment law is chosen. These are local raw
action jets, not the on-shell seven-row environment response. All sector
momenta use the SAME complete-action canonical lift and its derivative.
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx
import derive_n12_gate7_slaved_interface as r
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded,bound
from diagnose_n12_gate7_eight_reaction_center import block,identity

A=r.A
SOURCE=r.center.BASE/'BHSM_N12_FULL_RESET_ACTION_JACOBIAN.npz'
NAMES=('spatial_gravity','intrinsic_curvature','cosmological',
       'eta_quadratic','eta_quartic','adm_kinetic','hopf_inertia',
       'boundary_scalar_vacuum','boundary_vector_vacuum','boundary_Weyl_vacuum')


def local_sectors(base,node):
    """Algebraic split of the unchanged _integrand, with its exact float constants."""
    x=float(A._BASIS[0][node]);z=A._local_variables(base.values,2,None)
    log_c,log_a,log_b,cp,ap,bp,lc,la,lb,log_n,np_,beta,betap=z
    C=A.RADIUS0*log_c.exp();aa=(A.RADIUS0*math.cos(x))*log_a.exp()
    bb=(A.RADIUS0*math.sin(x))*log_b.exp();N=log_n.exp()
    hc=(lc-beta*cp-betap)/N;ha=(la-beta*ap)/N;hb=(lb-beta*bp)/N
    adm=hc**2+3*ha**2+3*hb**2-(hc+3*ha+3*hb)**2
    X=1/C**2+3*math.cos(x)**2/aa**2+3*math.sin(x)**2/bb**2-(-beta/N)**2
    sig=-0.5+2*x/math.pi-math.sin(4*x)/(2*math.pi)
    loc=1-4*sig**2;kappa=15*5**(1/3)/4
    vol=C*aa**3*bb**3;NV=N*vol;w=float(A._BASIS[1][node])
    terms=(3*aa**3*bb**3/C*N*(np_*(ap+bp)+ap**2+bp**2+3*ap*bp),
           NV*(3/aa**2+3/bb**2),NV*(-0.5*kappa),
           -NV*loc*(0.5*X),-NV*loc*(0.125*X**4),NV*(0.5*adm))
    return [w*t for t in terms], w*vol*loc*(1+X**3)/N


def accumulate(term,maps):
    n=len(maps);D=arb_mat(n,98)
    for k,items in enumerate(maps):
        for i,v in items:D[k,i]=v
    g=r.mat(np.asarray(term.d[1],dtype=object).reshape(n,1))
    h=r.mat(np.asarray(term.d[3],dtype=object).reshape(n,n))
    return term.d[0],D.transpose()*g,D.transpose()*h*D


def calculate(out):
    ctx.prec=512
    meta=json.loads(SOURCE.with_suffix('.json').read_bytes())
    if digest(SOURCE)!=meta['data']['SHA256']:raise ValueError('parent/reset packet changed')
    with np.load(SOURCE) as f:
        state=np.array([arb(float(v)) for v in f['center_state'][:98]],dtype=object)
        weights=np.array([arb(float(v)) for v in f['state_weights']],dtype=object)
        stored=f['analytic_full_reset_jacobian']
        normq=f['normalization_coordinates']
    values={name:arb(0) for name in NAMES}
    grads={name:arb_mat(98,1) for name in NAMES}
    hess={name:arb_mat(98,98) for name in NAMES}
    iv=arb(0);ig=arb_mat(98,1);ih=arb_mat(98,98)
    U=arb_mat(98,98)
    for i in range(98):U[i,i]=1/weights[i]
    with r.center.sparse.use_optimized_mixed(A):
        for node in range(A.POINTS):
            base=A._integrand(state,node,0)
            terms,inertia=local_sectors(base,node)
            for name,term in zip(NAMES[:6],terms):
                v,g,h=accumulate(term,base.maps)
                values[name]+=v;grads[name]+=g;hess[name]+=h
            v,g,h=accumulate(inertia,base.maps);iv+=v;ig+=g;ih+=h
        coefficient=arb(0.25/(2*A.HOPF_ORBIT_VOLUME**2))
        values['hopf_inertia']=-coefficient/iv
        grads['hopf_inertia']=coefficient*ig/iv**2
        hess['hopf_inertia']=coefficient*(ih/iv**2-2*ig*ig.transpose()/iv**3)
        maps,boundary=A._boundary(state,2);v,g,h=accumulate(boundary,maps)
        # Exact shares of the ALREADY ROUNDED total 59/30 coefficient.
        # They reproduce the frozen action rather than silently rationalizing it.
        shares=(arb(1)/118,arb(33)/59,arb(51)/118)
        for name,share in zip(NAMES[7:],shares):
            values[name]=v*share;grads[name]=share*g;hess[name]=share*h
        print('parent sector values and Hessians assembled',flush=True)
        with r.center.factored.use_ball_factored_integrand(A,state):
            owned=A._arb_action_jets(state)
            H=r.mat(owned.hessian_arb);g=r.mat(owned.gradient_arb[:,None])
            B,signs,t,sech=r.attachment(state[:37])
            dB=r.attachment_variation(r.arr(U),signs,t,sech)
            K,L,target=r.kkt(H,B,37)
            eye=np.full((98,98),arb(0),dtype=object)
            for i in range(98):eye[i,i]=arb(1)
            lv,lm=r.components(L,37);legs=np.concatenate((lv+lm,lv),axis=1)
            T=np.asarray(A._contracted_action(state,[eye[:,:,None,None],legs[:,None,:,None],r.arr(U)[:,None,None,:]],owned.dense_maps),dtype=object)
            KL=r.zeros((63,2,98))
            for k in range(98):
                KL[:37,:,k]=T[37:74,:2,k];KL[39:,:,k]=T[74:,2:,k]
                db=r.mat(dB[:,:,k])
                KL[:37,:,k]+=r.arr(db.transpose()*block(L,[37,38],range(2)))
                KL[37:39,:,k]=r.arr(db*block(L,range(37),range(2)))
            DL=-K.solve(r.mat(KL.reshape(63,196)))
            momenta={};momentum_jets={}
            for name in NAMES:
                gv=arb_mat(block(grads[name],range(37,74),[0]).tolist()+[[arb(0)]]*26)
                eta=K.solve(gv)
                gu=arb_mat(block(hess[name]*U,range(37,74),range(98)).tolist()+[[arb(0)]*98]*26)
                momenta[name]=L.transpose()*gv
                deriv=L.transpose()*gu
                for k in range(98):
                    corr=eta.transpose()*r.mat(KL[:,:,k])
                    for j in range(2):deriv[j,k]-=corr[0,j]
                momentum_jets[name]=deriv
            total_mom=sum(momenta.values(),arb_mat(2,1))
            total_dp=sum(momentum_jets.values(),arb_mat(2,98))
            gv=arb_mat(block(g,range(37,74),[0]).tolist()+[[arb(0)]]*26)
            gu=arb_mat(block(H*U,range(37,74),range(98)).tolist()+[[arb(0)]*98]*26)
            direct=L.transpose()*gu
            for k in range(98):
                dl=arb_mat([[DL[i,j*98+k] for j in range(2)] for i in range(63)])
                contribution=dl.transpose()*gv
                for j in range(2):direct[j,k]+=contribution[j,0]
    gsum=sum(grads.values(),arb_mat(98,1));hsum=sum(hess.values(),arb_mat(98,98))
    # Raw point value independently recomputed through the unchanged action.
    fullvalue=r.center.action_value(state)
    trace=arb_mat(3,98)
    for i in range(3):trace[i,0]=1
    for j in range(12):
        for i in range(3):trace[i,1+j]=(-1)**(j+1)
        trace[0,13+j]=(-1)**j;trace[1,25+j]=(-1)**j;trace[2,25+j]=-(-1)**j
    native5=arb_mat((trace*U).tolist()+total_dp.tolist())
    data=dict(parent_center=state,weights=weights,native_trace_momentum_jet=native5,
        common_canonical_lift=L,common_lift_derivative=DL,canonical_K=K,
        gradient_sum=gsum,hessian_sum=hsum,gradient_owner=g,hessian_owner=H)
    ledger={}
    for name in NAMES:
        data[name+'_value']=np.array([values[name]],dtype=object)
        data[name+'_gradient']=grads[name];data[name+'_hessian']=hess[name]
        data[name+'_momentum']=momenta[name];data[name+'_momentum_jet']=momentum_jets[name]
        ledger[name]=dict(value_mid=str(values[name].mid().fmpq()),value_approx=float(values[name].mid()),
            gradient_norm=bound(grads[name]),hessian_norm=bound(hess[name]),
            canonical_momentum_jet_norm=bound(momentum_jets[name]))
    r.save_arrays(out/'arrays.npz',data)
    replays=dict(gradient=bound(gsum-g),hessian=bound(hsum-H),
        value=bound(arb_mat([[sum(values.values(),arb(0))-fullvalue]])),
        momentum_value=bound(total_mom-L.transpose()*gv),momentum_derivative=bound(total_dp-direct),
        canonical_inverse=bound(identity(63)-K*K.inv()))
    if not all(x.contains(0) for x in (gsum-g).entries()+(hsum-H).entries()+(total_dp-direct).entries()):
        raise ArithmeticError('sector sum fails interval replay')
    sources=(Path(__file__),Path(r.__file__),Path(A.__file__),SOURCE,SOURCE.with_suffix('.json'),
        Path(r.center.sparse.__file__),Path(r.center.factored.__file__),
        r.ROOT/'src/bhsm/interface/aether_full_reset_action_jacobian.py',
        r.ROOT/'src/bhsm/interface/aether_m4_standard_model_zeta_backreaction_v15_51.py')
    report=dict(status='N12_PARENT_NATIVE_SECTOR_JETS_AND_FIVE_ROW_RESPONSE_DERIVED',
        point_source=str(SOURCE),point_key='center_state[:98]',
        coordinate_domain='Exact stored binary64 parent/event point; 98 raw state coordinates; derivative columns W^-1. Not a uniform parent history or interval-13 seam image.',
        sector_ledger=ledger,sector_names=list(NAMES),sector_split_is_algebraic_not_independent_energy_decomposition=True,
        boundary_shares=dict(scalar='1/118',vector='33/59',Weyl='51/118'),
        frozen_total_Casimir=str(arb(A.standard_model_casimir_coefficient()).fmpq()),
        same_total_canonical_lift_for_all_sectors=True,independent_sector_inverse_used=False,
        native_response_shape=[5,98],native_response_rows=['trace_1','trace_2','trace_3','canonical_momentum_1','canonical_momentum_2'],
        environment_physical_inputs=0,
        missing_for_7x73=['owned fixed-environment seam embedding/normal/measure jet with 73 p/q columns',
            'two dynamic-flux material jets on that same environmental realization; radial flux alone is not their replacement'],
        on_shell_environment_Hessian_derived=False,environment_response_7x73_derived=False,
        replay=replays,source_SHA256={str(p):digest(p) for p in sources},arrays_SHA256=digest(out/'arrays.npz'),
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({'status':report['status'],'replay':{k:v['approximate_upper'] for k,v in replays.items()}},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);calculate(a.out)
