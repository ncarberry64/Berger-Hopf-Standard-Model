"""Magnetic derivative of the changing, source-directed Gaussian graph.

The Gaussian minus sign, literal non-Hermitian left vertex and current
Gram contacts are kept. This is an application of the declared positive
reference component, not an identification with the graded P_strat or an
interacting LSZ/Pauli projection.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh

from .muon_intrinsic_scalar_temporal_image import temporal_image_green_kernel
from .muon_common_cutoff_green_kernel import common_total_cutoff_green_kernel
from .muon_changing_magnetic_current_jets import (
    magnetic_current_angular_images, magnetic_open_current_point,
    field_current_direction)
from .muon_coupled_higgs_magnetic_source import coupled_intrinsic_wall_images
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def magnetic_three_green_kernel(a,b,d,*,cutoff):
    """Stable L3 of exact supplied spectra, with a close-pair allowance.

    Distinct entries use the literal divided difference of exp(-cx)/x.
    Near triplets use the retained positive series. A nearly repeated
    closest pair uses its Hermite midpoint, with the Laplace d² bound.
    Binary evaluation and eigen/assembly error are separate.
    """
    x=np.broadcast_arrays(np.asarray(a,float),np.asarray(b,float),np.asarray(d,float))
    c=float(cutoff)
    if not np.isfinite(c)or c<0 or any(not np.isfinite(z).all()or np.any(z<=0)for z in x):
        raise ValueError('positive finite same-spectrum Green arguments required')
    if c==0:return dict(value=1/(x[0]*x[1]*x[2]),absolute_approximation_upper=0.)
    shape=x[0].shape;xx=np.stack([z.ravel()for z in x]);hi=xx.max(axis=0)
    near=np.max((hi-xx)/hi,axis=0)<=.125
    out=np.empty(hi.shape);err=0.
    if near.any():
        r=common_total_cutoff_green_kernel(*[z[near]for z in xx],cutoff=c,terms=10)
        out[near]=r['value'];err=float(r['positive_series_truncation_upper'])
    wide=~near
    if wide.any():
        z=xx[:,wide];pairs=((0,1),(0,2),(1,2))
        gaps=np.array([abs(z[i]-z[j])/np.minimum(z[i],z[j])for i,j in pairs])
        chosen=gaps.argmin(axis=0);vals=np.empty(chosen.shape)
        for k,(i,j)in enumerate(pairs):
            use=chosen==k
            if not use.any():continue
            u,v=z[i,use],z[j,use];q=z[3-i-j,use];mid=(u+v)/2
            repeated=abs(u-v)<=1e-6*np.minimum(u,v);local=np.empty(u.shape)
            if repeated.any():
                aa=mid[repeated];qq=q[repeated];delta=qq-aa
                ga=np.exp(-c*aa)/aa;gq=np.exp(-c*qq)/qq
                gp=-np.exp(-c*aa)*(c/aa+1/aa**2)
                local[repeated]=(gq-ga-gp*delta)/delta**2
                allowance=((u[repeated]-v[repeated])/2)**2/(np.minimum(u[repeated],v[repeated])**4*qq)
                err=max(err,float(np.max(allowance)))
            separate=~repeated
            if separate.any():
                uu,vv,qq=u[separate],v[separate],q[separate]
                local[separate]=(np.exp(-c*uu)/uu/((uu-vv)*(uu-qq))+
                    np.exp(-c*vv)/vv/((vv-uu)*(vv-qq))+
                    np.exp(-c*qq)/qq/((qq-uu)*(qq-vv)))
            vals[use]=local
        out[wide]=vals
    if not np.isfinite(out).all()or np.any(out<=0):
        raise ArithmeticError('positive common L3 evaluation unresolved; no zero filling')
    return dict(value=out.reshape(shape),absolute_approximation_upper=float(np.nextafter(err,np.inf))if err else 0.)


def gaussian_spectral_direction(Pf,Pb,L,R,dPf,dPb,dL,dR,*,cutoff=0.,dGb=None):
    """Exact finite spectral Fréchet placements, supplied CONTROL_ONLY scope.

    Inputs are already in their base Gram-normalized eigenframes. dPb
    denotes the literal dK, while dGb supplies its Gram variation. Thus
    dP=dK-(lambda_i+lambda_j)dG/2 and both current frame contacts survive.
    """
    f,b=np.asarray(Pf,float),np.asarray(Pb,float);L,R,dPf,dPb,dL,dR=map(np.asarray,(L,R,dPf,dPb,dL,dR))
    if (f.ndim!=1 or b.ndim!=1 or L.ndim!=3 or R.ndim!=3 or L.shape[1:]!=(len(f),len(b))
            or R.shape[::2]!=(len(f),len(b))or dPf.shape!=(len(f),len(f))or dPb.shape!=(len(b),len(b))
            or dL.shape!=L.shape or dR.shape!=R.shape
            or any(not np.isfinite(a).all()for a in(f,b,L,R,dPf,dPb,dL,dR))):
        raise ValueError('complete finite spectral operator and literal current placements required')
    g=np.zeros_like(dPb)if dGb is None else np.asarray(dGb)
    if g.shape!=dPb.shape or not np.isfinite(g).all():raise ValueError('same field Gram contact required')
    k=temporal_image_green_kernel(f[:,None],b[None,:],cutoff=cutoff)['value']
    out={name:np.zeros((L.shape[0],R.shape[1]),complex)for name in
        ('fermion_operator','field_operator','left_current','right_current','field_Gram_current')}
    out['left_current']=-np.einsum('ifa,fja,fa->ij',dL,R,k)
    out['right_current']=-np.einsum('ifa,fja,fa->ij',L,dR,k)
    for a,z in enumerate(b):
        k3=magnetic_three_green_kernel(f[:,None],f[None,:],z,cutoff=cutoff)['value']
        out['fermion_operator']+=L[:,:,a]@(k3*dPf)@R[:,:,a]
    dp=dPb-.5*(b[:,None]+b[None,:])*g
    for i,z in enumerate(f):
        k3=magnetic_three_green_kernel(b[:,None],b[None,:],z,cutoff=cutoff)['value']
        out['field_operator']+=L[:,i,:]@(k3*dp)@R[i].T
        contacts=.5*(k[i,:,None]+k[i,None,:])*g
        out['field_Gram_current']+=L[:,i,:]@contacts@R[i].T
    out['total']=sum(out.values())
    return out


def _gaunt_for(Fpar,Bpar,images):
    if Fpar==Bpar:return None
    G=images['gaunt_even_odd_source']
    return G if Fpar=='even'else G.transpose(1,0,2)


def _vertex_sources(fields,vertices,U,Fpar,Bpar,bhi,images,external):
    """Literal directed angular placements in normalized S3 coefficients."""
    nh=U.shape[0];mb=fields.shape[-1];n=vertices.shape[-1]
    if external==0:
        if Fpar!=Bpar:return np.zeros((n*nh,n,mb),complex),np.zeros((n,n*nh,mb),complex)
        right=np.einsum('hj,cja,cik->ihka',U[:,bhi],fields,vertices,optimize=True).reshape(n*nh,n,mb)
        left=np.einsum('hj,cja,cki->kiha',U[:,bhi].conj(),fields,vertices,optimize=True).reshape(n,n*nh,mb)
    else:
        G=_gaunt_for(Fpar,Bpar,images)
        if G is None:return np.zeros((n*nh,n*4,mb),complex),np.zeros((n*4,n*nh,mb),complex)
        M=np.einsum('hl,ljx->hjx',U,G[:,bhi])
        right=np.einsum('hjx,cja,cik->ihkxa',M,fields,vertices,optimize=True).reshape(n*nh,n*4,mb)
        left=np.einsum('hjx,cja,cki->kxiha',M.conj(),fields,vertices,optimize=True).reshape(n*4,n*nh,mb)
    return right,left


def _trial(F,point,p,dp):
    fi=F['family_indices'];hi=F['harmonic_indices'];alpha=lepton_current_hilbert_representation()['alpha']
    n=len(hi);d=6*n;E=F['derivatives']
    A=np.kron((point['W']+point['Omega_tau'])[np.ix_(fi,fi)],np.eye(n))-1j*sum(
        np.kron(a[np.ix_(fi,fi)],e)for a,e in zip(alpha,E))/point['R4']
    V=np.concatenate([x*np.eye(d)for x in p],axis=1)@F['eigenvectors']
    AV=np.concatenate([y*np.eye(d)/point['N']+x*A for x,y in zip(p,dp)],axis=1)@F['eigenvectors']
    return V,AV


def _base_maps(B,point,images):
    h=B['harmonic_indices'];E=images['derivatives']['even'if B['parity']=='even'else'field_odd'][:,h][:,:,h]
    base=coupled_intrinsic_wall_images(point['wall_connection'],point['raw_fields'][-8:-4],point['raw_fields'][-4:],E,point['temporal_image'],point['wall_radial_image'])
    m=base['count'];n=base['harmonic_count']
    fields=np.concatenate((base['gauge'].reshape(20*n,m),base['scalar'])).reshape(24,n,m)
    return base,np.einsum('chm,ma->cha',fields,B['eigenvectors'],optimize=True)


def current_moments(F,B,points,p,dp,measure,external_norm,*,directions=False,map_cache=None):
    """Actual base and chart-motion moments for both external angular legs."""
    images=magnetic_current_angular_images();s=len(F['eigenvalues']);a=len(B['eigenvalues']);U=F['real_to_complex'];fi=F['family_indices']
    out={key:np.zeros(shape,complex)for key,shape in dict(L0=(6,s,a),L1=(24,s,a),R0=(s,6,a),R1=(s,24,a)).items()}
    if directions:
        for key in ('L0','L1','R0','R1'):out['d'+key]=np.zeros((3,*out[key].shape),complex)
    cache={}if map_cache is None else map_cache
    for j,point in enumerate(points):
        key=(B['name'],j,'base')
        if key not in cache:cache[key]=_base_maps(B,point,images)
        V,AV=_trial(F,point,p[j],dp[j]);base,fields=cache[key]
        vertex=point['vertices'][:,fi][:,:,fi];scale=measure[j]*(2*min(point['response_time']/point['length'],1-point['response_time']/point['length']))/np.sqrt(external_norm)
        for ext in (0,1):
            R,L=_vertex_sources(fields,vertex,U,F['parity'],B['parity'],B['harmonic_indices'],images,ext)
            out['L'+str(ext)]+=scale*np.einsum('ida,dI->iIa',L,V)
            out['R'+str(ext)]+=scale*(AV.conj().T@R.reshape(len(V),-1)).reshape(s,R.shape[1],a)
        if directions:
            # Motion lands in the opposite parity; all return harmonics retained.
            target='even'if B['parity']=='odd'else'odd'
            G=images['gaunt_even_odd_source']if target=='even'else images['gaunt_even_odd_source'].transpose(1,0,2)
            G=G[:,B['harmonic_indices']]
            for axis in range(3):
                key=(B['name'],j,'direction',axis)
                if key not in cache:
                    D=field_current_direction(base,G,point['source_wall_gauge'][axis,:,:,:4],point['source_H'][axis,:,:4])
                    # Only DG columns move; the independent columns are
                    # literal zero chart variations, retained in the base.
                    n=base['harmonic_count'];sl=slice(40*n,56*n)
                    if np.any(D[:,:,:40*n])or np.any(D[:,:,56*n:]):raise ArithmeticError('independent current-chart motion is not zero')
                    cache[key]=np.einsum('chm,ma->cha',D[:,:,sl],B['eigenvectors'][sl],optimize=True)
                D=cache[key]
                ids=np.arange(D.shape[1])
                for ext in (0,1):
                    R,L=_vertex_sources(D,vertex,U,F['parity'],target,ids,images,ext)
                    out['dL'+str(ext)][axis]+=scale*np.einsum('ida,dI->iIa',L,V)
                    out['dR'+str(ext)][axis]+=scale*(AV.conj().T@R.reshape(len(V),-1)).reshape(s,R.shape[1],a)
    return out


def fermion_action_direction(target,source,points,p,dp,measure):
    """Both placements of the literal changing A†A first variation."""
    images=magnetic_current_angular_images();G=_gaunt_for(target['parity'],source['parity'],images)
    if G is None:raise ValueError('magnetic n1 connects opposite fermion parity')
    M=np.einsum('hl,ljs,kj->hks',target['real_to_complex'],G,source['real_to_complex'].conj())
    fi=target['family_indices'];nt=len(target['harmonic_indices']);ns=len(source['harmonic_indices'])
    shape=(3,len(target['eigenvalues']),len(source['eigenvalues']))
    left=np.zeros(shape,complex);right=left.copy();values=[]
    for j,point in enumerate(points):
        Vt,At=_trial(target,point,p[j],dp[j]);Vs,As=_trial(source,point,p[j],dp[j])
        Xi=point['Xi_source_coefficients'][:,:,fi][:,:,:,fi]
        X=np.einsum('hks,Asij->Aihjk',M,Xi).reshape(3,6*nt,6*ns)
        # Reverse source uses SAME Xi, then its literal adjoint placement.
        Xrev=np.einsum('khs,Asij->Aikhj',M.conj().transpose(1,0,2),Xi).reshape(3,6*ns,6*nt)
        for axis in range(3):
            left[axis]+=measure[j]*(At.conj().T@X[axis]@Vs)
            right[axis]+=measure[j]*((Xrev[axis]@Vt).conj().T@As)
        values.append((X,Xrev,Vt,At,Vs,As))
    return dict(square_left=left,square_right=right,point_images=values)


def numerator_direction(target,source,B,points,measure,external_norm,point_images,*,map_cache=None):
    """The changed acted-trial numerator before the fermion inverse."""
    images=magnetic_current_angular_images();fi=target['family_indices'];a=len(B['eigenvalues'])
    out={key:np.zeros((3,len(target['eigenvalues']),n,a),complex)for key,n in(('R0',6),('R1',24))}
    reverse={key:np.zeros((3,len(source['eigenvalues']),n,a),complex)for key,n in(('R0',6),('R1',24))}
    cache={}if map_cache is None else map_cache
    for j,point in enumerate(points):
        key=(B['name'],j,'base')
        if key not in cache:cache[key]=_base_maps(B,point,images)
        _,fields=cache[key];vertex=point['vertices'][:,fi][:,:,fi]
        scale=measure[j]*(2*min(point['response_time']/point['length'],1-point['response_time']/point['length']))/np.sqrt(external_norm)
        X,Xrev,Vt,At,Vs,As=point_images[j]
        for ext in (0,1):
            Rs,_=_vertex_sources(fields,vertex,source['real_to_complex'],source['parity'],B['parity'],B['harmonic_indices'],images,ext)
            Rt,_=_vertex_sources(fields,vertex,target['real_to_complex'],target['parity'],B['parity'],B['harmonic_indices'],images,ext)
            for axis in range(3):
                out['R'+str(ext)][axis]+=scale*((Xrev[axis]@Vt).conj().T@Rs.reshape(len(Vs),-1)).reshape(len(target['eigenvalues']),Rs.shape[1],a)
                reverse['R'+str(ext)][axis]+=scale*((X[axis]@Vs).conj().T@Rt.reshape(len(Vt),-1)).reshape(len(source['eigenvalues']),Rt.shape[1],a)
    return out,reverse


def _fermion_sandwich(L,R,D,ft,fs,b,cutoff,*,field_batch=12):
    out=np.zeros((3,L.shape[0],R.shape[1]),complex);allowance=0.
    for start in range(0,len(b),field_batch):
        end=min(start+field_batch,len(b));r=magnetic_three_green_kernel(ft[:,None,None],fs[None,:,None],b[None,None,start:end],cutoff=cutoff)
        allowance=max(allowance,r['absolute_approximation_upper'])
        for axis in range(3):
            mid=np.einsum('tsa,sja->tja',r['value']*D[axis,:,:,None],R[:,:,start:end],optimize=True)
            out[axis]+=np.einsum('ita,tja->ij',L[:,:,start:end],mid,optimize=True)
    return out,allowance


def _field_sandwich(L,R,dK,dG,f,bt,bs,cutoff):
    out=np.zeros((3,L.shape[0],R.shape[1]),complex);gram=out.copy();allowance=0.
    dp=dK-.5*(bt[None,:,None]+bs[None,None,:])*dG
    kt=temporal_image_green_kernel(f[:,None],bt[None,:],cutoff=cutoff)['value']
    ks=temporal_image_green_kernel(f[:,None],bs[None,:],cutoff=cutoff)['value']
    for i,lam in enumerate(f):
        r=magnetic_three_green_kernel(bt[:,None],bs[None,:],lam,cutoff=cutoff)
        allowance=max(allowance,r['absolute_approximation_upper'])
        for axis in range(3):
            out[axis]+=L[:,i,:]@(r['value']*dp[axis])@R[i].T
            gram[axis]+=L[:,i,:]@(.5*(kt[i,:,None]+ks[i,None,:])*dG[axis])@R[i].T
    return out,gram,allowance


def _current_sandwich(L,R,f,b,c):
    k=temporal_image_green_kernel(f[:,None],b[None,:],cutoff=c)['value']
    return -np.einsum('Aifa,fja,fa->Aij',L,R,k,optimize=True)if L.ndim==4 else -np.einsum('ifa,Afja,fa->Aij',L,R,k,optimize=True)


def changing_magnetic_constant_columns(phase,first_field_sampler,fermions,fields,field_direction,*,
        times,weights,temporal_values,temporal_rates,cutoff,progress=None):
    """Apply complete represented field loops to the actual n1<-n0 jet.

    fermions/fields are the retained full invariant blocks, reorganizing
    every supplied coordinate. field_direction(target,source) returns
    the literal dK,dG in coordinate bases, before both eigen congruences.
    This ordinary application never removes a numerical small direction.
    """
    times=np.asarray(times);weights=np.asarray(weights);p=np.asarray(temporal_values);dp=np.asarray(temporal_rates)
    L=abs(phase['receipt']['span']);c=float(cutoff)
    if (times.ndim!=1 or weights.shape!=times.shape or p.shape!=(len(times),8)or dp.shape!=p.shape
            or np.any(weights<=0)or np.any(times<0)or np.any(times>L)or not np.isfinite(c)or c<0):
        raise ValueError('same complete chronological quadrature/trial required')
    points=[magnetic_open_current_point(phase,float(u),length=L,first_field_sampler=first_field_sampler,include_maps=False)for u in times]
    for point in points:point['length']=L
    measure=weights*np.array([a['N']for a in points]);b=np.array([2*min(u/L,1-u/L)for u in times]);extnorm=float(measure@b**2)
    names=('fermion_square_left','fermion_square_right','fermion_numerator_contact','field_operator',
        'field_Gram_current','left_current_chart','right_current_chart')
    forward={name:np.zeros((3,72,18),complex)for name in names}
    reverse={name:np.zeros((3,18,72),complex)for name in names};records=[];max_error=0.
    families=sorted(set(f['family']for f in fermions))
    for family in families:
        fs=[f for f in fermions if f['family']==family];fi=fs[0]['family_indices']
        output=(fi[:,None]*4+np.arange(4)).ravel()
        for B in fields:
            moments={};action={};map_cache={}
            def moment(F,directions=False,other=None):
                key=(F['name'],(B if other is None else other)['name'],directions)
                if key not in moments:moments[key]=current_moments(F,B if other is None else other,points,p,dp,measure,extnorm,directions=directions,map_cache=map_cache)
                return moments[key]
            same=[f for f in fs if f['level']==B['level']and abs(-f['level']+2*f['spectator'])==B['absolute_spectator']]
            opposite=[f for f in fs if abs(f['level']-B['level'])==1]
            local_f={name:np.zeros((3,24,6),complex)for name in names};local_r={name:np.zeros((3,6,24),complex)for name in names}
            chart_targets=set()
            for Fs in same:
                ms=moment(Fs,True)
                local_f['left_current_chart']+=_current_sandwich(ms['dL1'],ms['R0'],Fs['eigenvalues'],B['eigenvalues'],c)
                local_r['right_current_chart']+=_current_sandwich(ms['L0'],ms['dR1'],Fs['eigenvalues'],B['eigenvalues'],c)
                for Ft in opposite:
                    if abs((-Ft['level']+2*Ft['spectator'])-(-Fs['level']+2*Fs['spectator']))!=1:continue
                    mt=moment(Ft,True);key=(Ft['name'],Fs['name'])
                    a=fermion_action_direction(Ft,Fs,points,p,dp,measure);action[key]=a
                    numt,nums=numerator_direction(Ft,Fs,B,points,measure,extnorm,a['point_images'],map_cache=map_cache)
                    for name,square,rsquare in (('fermion_square_left',a['square_left'],a['square_right'].conj().transpose(0,2,1)),
                            ('fermion_square_right',a['square_right'],a['square_left'].conj().transpose(0,2,1))):
                        v,e=_fermion_sandwich(mt['L1'],ms['R0'],square,Ft['eigenvalues'],Fs['eigenvalues'],B['eigenvalues'],c);local_f[name]+=v;max_error=max(max_error,e)
                        v,e=_fermion_sandwich(ms['L0'],mt['R1'],rsquare,Fs['eigenvalues'],Ft['eigenvalues'],B['eigenvalues'],c);local_r[name]+=v;max_error=max(max_error,e)
                    local_f['fermion_numerator_contact']+=_current_sandwich(mt['L1'],numt['R0'],Ft['eigenvalues'],B['eigenvalues'],c)
                    local_r['fermion_numerator_contact']+=_current_sandwich(ms['L0'],nums['R1'],Fs['eigenvalues'],B['eigenvalues'],c)
                    if Ft['name']not in chart_targets:
                        local_f['right_current_chart']+=_current_sandwich(mt['L1'],mt['dR0'],Ft['eigenvalues'],B['eigenvalues'],c)
                        local_r['left_current_chart']+=_current_sandwich(mt['dL0'],mt['R1'],Ft['eigenvalues'],B['eigenvalues'],c)
                        chart_targets.add(Ft['name'])
                for Bt in fields:
                    if Bt['parity']==B['parity']or abs(Bt['level']-B['level'])!=1:continue
                    k=-Fs['level']+2*Fs['spectator']
                    if all(abs(k+d)!=Bt['absolute_spectator']for d in(-1,1)):continue
                    mt=moment(Fs,other=Bt);dK,dG=field_direction(Bt,B)
                    ut,us=Bt['eigenvectors'],B['eigenvectors']
                    dk=np.array([ut.T@v@us for v in dK]);dg=np.array([ut.T@v@us for v in dG])
                    v,g,e=_field_sandwich(mt['L1'],ms['R0'],dk,dg,Fs['eigenvalues'],Bt['eigenvalues'],B['eigenvalues'],c)
                    local_f['field_operator']+=v;local_f['field_Gram_current']+=g;max_error=max(max_error,e)
                    v,g,e=_field_sandwich(ms['L0'],mt['R1'],dk.transpose(0,2,1),dg.transpose(0,2,1),Fs['eigenvalues'],B['eigenvalues'],Bt['eigenvalues'],c)
                    local_r['field_operator']+=v;local_r['field_Gram_current']+=g;max_error=max(max_error,e)
            for name in names:
                for axis in range(3):
                    forward[name][axis][np.ix_(output,fi)]+=local_f[name][axis]
                    reverse[name][axis][np.ix_(fi,output)]+=local_r[name][axis]
            record=dict(family=family,field_level=B['level'],absolute_spectator=B['absolute_spectator'],field_dimension=len(B['eigenvalues']),
                forward_contribution_norm=float(np.linalg.norm(sum(local_f.values()))),reverse_contribution_norm=float(np.linalg.norm(sum(local_r.values()))),
                moment_pair_count=len(moments),fermion_pair_count=len(action))
            records.append(record)
            if progress is not None:progress(record)
            del moments,action,map_cache
    for out in(forward,reverse):out['total']=sum(out.values())
    return dict(forward=forward,reverse=reverse,block_records=records,external_tent_Gram=extnorm,
        maximum_scalar_kernel_approximation_upper=max_error,chronological_times=times,chronological_weights=weights,
        external_columns='complete n1<-n0 72x18 and literal reverse18x72; input-momentum n1 columns not substituted',
        one_joint_field_Green_per_exact_angular_block=True,fermion_Gram_source_direction_zero_fixed_geometry_only=True,
        both_fermion_squares_and_numerator_contact=True,field_Gram_and_both_current_motion_contacts=True,
        starting_field_angular_complement_or_continuum_bound=False,physical_P_strat_LSZ_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None)
