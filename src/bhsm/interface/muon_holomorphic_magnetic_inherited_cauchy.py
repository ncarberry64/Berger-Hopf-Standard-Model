"""Conditional inherited source-on continuation on the original signed domain.

The algebra is retained from the frozen zero-Cauchy action reduction; only
the supplied initial state and actual-owner source callback change. All
original wall/frame reactions remain, and no physical reset is inferred.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor,lu_solve,solve
from scipy.integrate import solve_ivp
from .muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from .muon_holomorphic_n1_magnetic_action import original_named_wall_lift,complete_gauge_wall_constraints

def inherited_prescribed_magnetic_prefix(forms,coordinate_steps,sources,representation,value_permutation,initial_canonical_state,source_time_germ,*,source_first_time_germ=None,source_knots=(.25,.75),forms_first=None,rtol=2e-10,atol=2e-12):
    """Integrate supplied inherited x/p, after original At/Gauss Schur reduction.

    The caller supplies future-coordinate stage order and positive real
    step orientation. Incoming negative-prefix forms must be REVERSED
    before calling. This solves the finite complex coefficient action,
    without a positive square or an interacting exterior/LSZ assertion.
    """
    h=np.asarray(coordinate_steps,complex);q=len(forms);n=forms[0]['K'].shape[0];nh=n//84
    if q!=2 or h.shape!=(2,)or h[0]!=h[1]or h[0].imag!=0 or h[0].real<=0:
        raise ValueError('future-coordinate same two-stage finite source prefix required')
    lifts=chronological_n0_field_lifts(representation,value_permutation);ids=np.asarray(value_permutation,int)
    labels=representation['gauge_labels'];frame=set(lifts['frame_indices'].tolist())
    kept=[i for i,j in enumerate(ids)if i not in frame and(j>=80 or not labels[j].get('wall_lift',False))]
    S=np.kron(np.eye(84)[:,kept],np.eye(nh));W=np.kron(lifts['W'],np.eye(nh))
    if len(kept)!=61 or np.max(abs(W@S))>2e-13:raise ValueError('all named zero-wall interiors/H and only named frame reduction required')
    na=sum(ids[i]<80 and labels[ids[i]]['field']=='A_tau'for i in kept)*nh
    if na!=12*nh:raise ValueError('all twelve interior At/Gauss rows per harmonic required')
    nd=len(kept)*nh-na;Sa,Sd=S[:,:na],S[:,na:]
    L=np.kron(original_named_wall_lift(representation,value_permutation),np.eye(nh))
    C=complete_gauge_wall_constraints(lifts,nh)['constraint'];ns=sources[0]['Q'].shape[-1];total=np.sum(h)
    k=0 if forms_first is None else len(forms_first[0]['K'])
    reduced=[]
    for j,f in enumerate(forms):
        K,BF,BR,M=(S.T@f[n]@S for n in('K','B_forward','B_reverse','M'))
        if np.max(abs(M[:na]))>1e-13 or np.max(abs(M[:,:na]))>1e-13 or np.max(abs(BR[:na]))>1e-13 or np.max(abs(BF[:,:na]))>1e-13:
            raise ValueError('material At is algebraic; no invented At kinetic rate permitted')
        gauss=lu_factor(K[:na,:na]);U=lu_solve(gauss,K[:na,na:]);V=lu_solve(gauss,BF[:na,na:])
        Kr=K[na:,na:]-K[na:,:na]@U;Fr=BF[na:,na:]-K[na:,:na]@V
        Rr=BR[na:,na:]-BR[na:,:na]@U;Mr=M[na:,na:]-BR[na:,:na]@V
        r=dict(K=Kr,BF=Fr,BR=Rr,M=Mr,gauss_factor=gauss,mass_factor=lu_factor(Mr),
            Kaa=K[:na,:na],Kad=K[:na,na:],BFad=BF[:na,na:],Kda=K[na:,:na],BRda=BR[na:,:na])
        if k:
            derivatives={n:np.array([S.T@a@S for a in forms_first[j][n]])for n in('K','M','B_forward','B_reverse')}
            dK,dM,dBF,dBR=(derivatives[n]for n in('K','M','B_forward','B_reverse'))
            dU=np.array([lu_solve(gauss,dK[c,:na,na:]-dK[c,:na,:na]@U)for c in range(k)])
            dV=np.array([lu_solve(gauss,dBF[c,:na,na:]-dK[c,:na,:na]@V)for c in range(k)])
            r.update(K_first=dK[:,na:,na:]-dK[:,na:,:na]@U-K[na:,:na]@dU,
                BF_first=dBF[:,na:,na:]-dK[:,na:,:na]@V-K[na:,:na]@dV,
                BR_first=dBR[:,na:,na:]-dBR[:,na:,:na]@U-BR[na:,:na]@dU,
                M_first=dM[:,na:,na:]-dBR[:,na:,:na]@V-BR[na:,:na]@dV,
                Kaa_first=dK[:,:na,:na],Kad_first=dK[:,:na,na:],BFad_first=dBF[:,:na,na:],
                Kda_first=dK[:,na:,:na],BRda_first=dBR[:,na:,:na])
        reduced.append(r)
    def known(sigma):
        wall,wallt,walltt=source_time_germ(sigma)
        result=dict(value=tuple(L@v.reshape(20*nh,ns)for v in(wall,wallt,walltt)),wall=(wall,wallt,walltt))
        if k:
            dwall=source_first_time_germ(sigma)
            result.update(first=tuple(np.einsum('ac,kcs->kas',L,v.reshape(k,20*nh,ns))for v in dwall),wall_first=dwall)
        return result
    def source(j,sigma):
        f,r=forms[j],reduced[j];known_germ=known(sigma);a,at,att=known_germ['value'];wall=known_germ['wall']
        gv=S.T@(f['K']@a+f['B_forward']@at);gt=S.T@(f['B_reverse']@a+f['M']@at)
        gvt=S.T@(f['K']@at+f['B_forward']@att);gtt=S.T@(f['B_reverse']@at+f['M']@att)
        ag=lu_solve(r['gauss_factor'],gv[:na]);agt=lu_solve(r['gauss_factor'],gvt[:na])
        result=dict(value=gv[na:]-r['Kda']@ag,rate=gt[na:]-r['BRda']@ag,
            value_time=gvt[na:]-r['Kda']@agt,rate_time=gtt[na:]-r['BRda']@agt,
            gauss=gv[:na],gauss_time=gvt[:na],known=(a,at,att),wall=wall)
        if k:
            df=forms_first[j];da,dat,datt=known_germ['first']
            project=lambda v:np.einsum('ac,kcs->kas',S.T,v)
            dgv=project(df['K']@a+f['K']@da+df['B_forward']@at+f['B_forward']@dat)
            dgt=project(df['B_reverse']@a+f['B_reverse']@da+df['M']@at+f['M']@dat)
            dgvt=project(df['K']@at+f['K']@dat+df['B_forward']@att+f['B_forward']@datt)
            dgtt=project(df['B_reverse']@at+f['B_reverse']@dat+df['M']@att+f['M']@datt)
            dag=np.array([lu_solve(r['gauss_factor'],dgv[c,:na]-r['Kaa_first'][c]@ag)for c in range(k)])
            dagt=np.array([lu_solve(r['gauss_factor'],dgvt[c,:na]-r['Kaa_first'][c]@agt)for c in range(k)])
            result.update(value_first=dgv[:,na:]-r['Kda_first']@ag-r['Kda']@dag,
                rate_first=dgt[:,na:]-r['BRda_first']@ag-r['BRda']@dag,
                value_time_first=dgvt[:,na:]-r['Kda_first']@agt-r['Kda']@dagt,
                rate_time_first=dgtt[:,na:]-r['BRda_first']@agt-r['BRda']@dagt,
                gauss_first=dgv[:,:na],gauss_time_first=dgvt[:,:na],known_first=(da,dat,datt),wall_first=known_germ['wall_first'])
        return result
    states=[];initial=np.asarray(initial_canonical_state,complex).copy();solutions=[];corners=[]
    if initial.shape!=(1+k,2*nd,ns):raise ValueError('all inherited canonical/source columns required')
    inherited_initial=initial.copy()
    for j,r in enumerate(reduced):
        def rhs(sigma,state):
            z=state.reshape(1+k,2*nd,ns);x,p=z[0,:nd],z[0,nd:];s=source(j,sigma)
            v=lu_solve(r['mass_factor'],p-r['BR']@x-s['rate']);force=r['K']@x+r['BF']@v+s['value']
            answer=np.zeros_like(z);answer[0]=np.r_[v,force]
            for c in range(k):
                dx,dp=z[1+c,:nd],z[1+c,nd:]
                dv=lu_solve(r['mass_factor'],dp-r['BR_first'][c]@x-r['BR']@dx-s['rate_first'][c]-r['M_first'][c]@v)
                dforce=r['K_first'][c]@x+r['K']@dx+r['BF_first'][c]@v+r['BF']@dv+s['value_first'][c]
                answer[1+c]=np.r_[dv,dforce]
            return (total*answer).ravel()
        # Split at ramp end and coefficient corners. The state is canonical.
        cuts=sorted({j/2,(j+1)/2,*[float(t)for t in source_knots if j/2<t<(j+1)/2]})
        local=[]
        for left,right in zip(cuts[:-1],cuts[1:]):
            sol=solve_ivp(rhs,(left,right),initial.ravel(),method='DOP853',rtol=rtol,atol=atol,max_step=(right-left)/16,dense_output=True)
            if not sol.success:raise ArithmeticError('literal canonical magnetic source integration failed: '+sol.message)
            initial=sol.y[:,-1].reshape(1+k,2*nd,ns);local.append((left,right,sol))
        solutions.append(local);states.append(initial.copy());corners.append(initial.copy())
    z,w=np.polynomial.legendre.leggauss(5);points=[];maximum=0.
    for j,r in enumerate(reduced):
        cuts=sorted({j/2,(j+1)/2,*[float(t)for t in source_knots if j/2<t<(j+1)/2]})
        for left,right in zip(cuts[:-1],cuts[1:]):
            for vq,wq in zip(z,w):
                sigma=(left+right)/2+(right-left)*vq/2
                sol=next(sol for lo,hi,sol in solutions[j]if lo<=sigma<=hi)
                state=sol.sol(sigma).reshape(1+k,2*nd,ns);x,p=state[0,:nd],state[0,nd:];s=source(j,sigma)
                v=lu_solve(r['mass_factor'],p-r['BR']@x-s['rate']);pd=r['K']@x+r['BF']@v+s['value']
                vd=lu_solve(r['mass_factor'],pd-r['BR']@v-s['rate_time'])
                a=-lu_solve(r['gauss_factor'],r['Kad']@x+r['BFad']@v+s['gauss'])
                ad=-lu_solve(r['gauss_factor'],r['Kad']@v+r['BFad']@vd+s['gauss_time'])
                known_value,known_rate,known_second=s['known'];field=Sa@a+Sd@x+known_value
                rate=Sa@ad+Sd@v+known_rate;acceleration=Sd@vd+known_second # At acceleration is unused.
                f=forms[j];momentum=f['M']@rate+f['B_reverse']@field
                force=f['K']@field+f['B_forward']@rate;momentum_time=f['M']@acceleration+f['B_reverse']@rate
                euler=force-momentum_time
                reaction=solve(C@C.T,C@euler,assume_a='gen');original=euler-C.T@reaction
                projected=S.T@euler;gauss=Sa.T@force
                scale=-1j*total*(right-left)*wq/2
                point=dict(cell=j,sigma=sigma,scale=scale,total_field=field,total_coordinate_rate=rate,
                    canonical_momentum=momentum,canonical_momentum_time=momentum_time,original_action_force=force,
                    original_At_interior_Gauss_rows=gauss,original_unbordered_Euler_rows=euler,
                    wall_and_frame_reactions=reaction,original_reconstructed_rows=original,
                    complete_wall_source=s['wall'][0],complete_wall_source_rate=s['wall'][1],
                    original_full_wall_rows=W@field-s['wall'][0].reshape(20*nh,ns),
                    original_full_wall_rate_rows=W@rate-s['wall'][1].reshape(20*nh,ns),
                    projected_canonical_rows=projected,
                    original_row_uncancelled_scale=abs(force)+abs(momentum_time)+abs(C.T)@abs(reaction),
                    canonical_reduced_source_value=s['value'],canonical_reduced_source_rate=s['rate'])
                if k:
                    fields=[];rates=[];first_rows=[];first_gauss=[];first_reactions=[]
                    for c in range(k):
                        dx,dp=state[1+c,:nd],state[1+c,nd:]
                        dv=lu_solve(r['mass_factor'],dp-r['BR_first'][c]@x-r['BR']@dx-s['rate_first'][c]-r['M_first'][c]@v)
                        dforce=r['K_first'][c]@x+r['K']@dx+r['BF_first'][c]@v+r['BF']@dv+s['value_first'][c]
                        dvd=lu_solve(r['mass_factor'],dforce-r['BR_first'][c]@v-r['BR']@dv-s['rate_time_first'][c]-r['M_first'][c]@vd)
                        da=-lu_solve(r['gauss_factor'],r['Kad_first'][c]@x+r['Kad']@dx+r['BFad_first'][c]@v+r['BFad']@dv
                            +s['gauss_first'][c]+r['Kaa_first'][c]@a)
                        dad=-lu_solve(r['gauss_factor'],r['Kad_first'][c]@v+r['Kad']@dv+r['BFad_first'][c]@vd+r['BFad']@dvd
                            +s['gauss_time_first'][c]+r['Kaa_first'][c]@ad)
                        dav,dat,datt=(v[c]for v in s['known_first']);dfield=Sa@da+Sd@dx+dav
                        drate=Sa@dad+Sd@dv+dat;dacc=Sd@dvd+datt;df=forms_first[j]
                        dg=df['K'][c]@field+f['K']@dfield+df['B_forward'][c]@rate+f['B_forward']@drate
                        dpt=df['M'][c]@acceleration+f['M']@dacc+df['B_reverse'][c]@rate+f['B_reverse']@drate
                        deuler=dg-dpt;dreaction=solve(C@C.T,C@deuler,assume_a='gen')
                        fields.append(dfield);rates.append(drate);first_rows.append(deuler-C.T@dreaction)
                        first_gauss.append(Sa.T@dg);first_reactions.append(dreaction)
                    point.update(total_field_first=np.array(fields),total_coordinate_rate_first=np.array(rates),
                        original_first_reconstructed_rows=np.array(first_rows),original_first_At_Gauss_rows=np.array(first_gauss),
                        wall_and_frame_reactions_first=np.array(first_reactions),complete_wall_source_first=s['wall_first'][0],
                        complete_wall_source_rate_first=s['wall_first'][1])
                points.append(point)
                maximum=max(maximum,float(np.max(abs(original))))
    return dict(point_sources=points,final_reduced_canonical_state=initial[0],final_reduced_canonical_state_first=initial[1:],
        stage_final_reduced_states=np.array(states)[:,0],stage_final_reduced_states_first=np.array(states)[:,1:],
        initial_reduced_canonical_state=inherited_initial[0],initial_reduced_canonical_state_first=inherited_initial[1:],original_interior_field_lift=S,
        original_free_dynamic_count=nd,original_interior_At_Gauss_count=na,
        full_field_per_trace=n,full_At_rows=16*nh,full_named_frames=4*nh,
        original_reconstructed_rows_max=maximum,source_restarted_at_zero=False,
        canonical_initial_x_and_p_inherited=True,physical_adiabatic_exterior_pole_native_or_Pauli_identified=False,
        canonical_momentum_kind='original Lorentz p=M*q_coordinate_rate+B_reverse*q; continued weak momentum is -i*p',
        caller_background_source_first_computed=bool(k),
        numerical_integration_rtol=rtol,numerical_integration_atol=atol)

def actual_owner_piecewise_source_germ(sigma,knots,sources,total_step,*,first=False):
    """C1 Hermite through actual action-owned value/rate germs, no fitted shift."""
    knots=np.asarray(knots,float);q=float(sigma)
    if knots[0]!=0 or knots[-1]!=1 or np.any(np.diff(knots)<=0) or len(sources)!=len(knots):
        raise ValueError('actual ordered source germs on the complete prefix required')
    j=min(max(np.searchsorted(knots,q,side='right')-1,0),len(knots)-2)
    width=knots[j+1]-knots[j];t=(q-knots[j])/width;h=width*total_step
    p=np.array([2*t**3-3*t*t+1,t**3-2*t*t+t,-2*t**3+3*t*t,t**3-t*t])
    dp=np.array([6*t*t-6*t,3*t*t-4*t+1,-6*t*t+6*t,3*t*t-2*t])/h
    ddp=np.array([12*t-6,6*t-4,-12*t+6,6*t-2])/(h*h)
    key='Q_first'if first else'Q';rate='Q_coordinate_time_first'if first else'Q_coordinate_time'
    values=(sources[j][key],h*sources[j][rate],sources[j+1][key],h*sources[j+1][rate])
    return tuple(sum(a*b for a,b in zip(v,values))for v in(p,dp,ddp))


def signed_field_face_source_first(forms,forms_first,interior_lift,wall_lift,wall_first,state_first,base,interior_At_count):
    """Literal source-first Gauss/Legendre solution at fixed field-basis maps.

    At-time derivatives are not needed for the original momentum/Gauss
    derivative and are not invented here. All coefficient/source/target
    columns remain independent analytic high/low directions.
    """
    S,L=np.asarray(interior_lift,complex),np.asarray(wall_lift,complex);na=int(interior_At_count)
    Sa,Sd=S[:,:na],S[:,na:];nd=Sd.shape[1]
    K,BF,BR,M=[np.asarray(forms[n],complex)for n in('K','B_forward','B_reverse','M')]
    D=np.block([[Sd.T@M@Sd,Sd.T@BR@Sa],[Sa.T@BF@Sd,Sa.T@K@Sa]])
    f,ft=base['total_field'],base['total_coordinate_rate'];answer=[];momenta=[];rates=[];rows=[]
    z=np.asarray(state_first,complex)
    for k in range(len(z)):
        dK,dBF,dBR,dM=[forms_first[n][k]for n in('K','B_forward','B_reverse','M')]
        known=L@np.asarray(wall_first[0][k]).reshape(L.shape[1],f.shape[1])
        knownt=L@np.asarray(wall_first[1][k]).reshape(L.shape[1],f.shape[1])
        value=Sd@z[k,:nd]+known
        pp=z[k,nd:]-Sd.T@(dM@ft+dBR@f+M@knownt+BR@value)
        gg=-Sa.T@(dK@f+dBF@ft+K@value+BF@knownt)
        eta=solve(D,np.r_[pp,gg],assume_a='gen');df=value+Sa@eta[nd:];dft=knownt+Sd@eta[:nd]
        dpi=dM@ft+M@dft+dBR@f+BR@df
        gauss=Sa.T@(dK@f+K@df+dBF@ft+BF@dft)
        rows.append(np.r_[Sd.T@dpi-z[k,nd:],gauss]);answer.append(df);rates.append(dft);momenta.append(dpi)
    return dict(total_field_first=np.array(answer),action_coordinate_rate_first=np.array(rates),
        canonical_momentum_first=np.array(momenta),original_source_first_Gauss_and_momentum_rows=np.array(rows),
        algebraic_At_time_rate_first_not_computed=True)

