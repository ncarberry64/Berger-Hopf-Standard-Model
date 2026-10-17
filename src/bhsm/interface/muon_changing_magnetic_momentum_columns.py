"""Input-momentum image of the corrected changing magnetic open graph.

External input n1 and output n0/n2 are distinct from the constant input
columns. The unchanged starting field loop is odd20 plus even35; its
source-directed fermion return is odd56 plus even84, including n5/n6.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np

from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_changing_magnetic_current_jets import magnetic_open_current_point,field_current_direction
from .muon_changing_magnetic_open_exchange import (
    _trial,_base_maps,_fermion_sandwich,_field_sandwich,_current_sandwich)


@lru_cache(maxsize=1)
def momentum_current_angular_images():
    """Literal full product maps; exact degree/parity zeros only."""
    s=scalar_s3_discretization(6);labels=s['real_basis_labels'];w=s['haar_weights']
    ids={k:np.array([i for i,l in enumerate(labels)if l[0]in ns])for k,ns in
        dict(even=(0,2,4,6),odd=(1,3,5),field_even=(0,2,4),field_odd=(1,3),out=(0,2),input=(1,)).items()}
    v={k:s['real_basis_values'][:,h]for k,h in ids.items()};maps={}
    def product(target,field,ext):
        q=(v[field][:,:,None]*v[ext][:,None,:]).reshape(len(w),-1)
        G=(v[target].T@(w[:,None]*q)).reshape(len(ids[target]),len(ids[field]),len(ids[ext]))
        n=[np.array([labels[i][0]for i in ids[k]])for k in(target,field,ext)]
        a,b,c=n[0][:,None,None],n[1][None,:,None],n[2][None,None,:]
        G[(a<abs(b-c))|(a>b+c)|((a+b+c)%2!=0)]=0
        return G
    for target in('even','odd'):
        for field in('even','odd'):
            for ext in('out','input'):
                maps[(target,field,ext)]=product(target,field,ext)
    source=maps[('even','odd','input')]
    # Existing base helper consumes these names and full indices.
    return dict(gaunt_even_odd_source=source,external_gaunt=maps,
        derivatives={k:s['real_angular_derivative_matrices'][:,h][:,:,h]for k,h in ids.items()},
        labels={k:[labels[i]for i in h]for k,h in ids.items()},
        basis_values=v,
        external_values={'out':v['out'],'input':v['input']},haar_weights=w,
        full_even_return_count=84,full_odd_return_count=56,
        starting_even_field_count=35,starting_odd_field_count=20,
        source_image_scope='field-even4 × input1 -> fermion5; magnetic1 -> fermion6; output2 × field-even4 returns6. Unchanged field loop; no global angular tail claim.')


def generalized_vertex_sources(fields,vertices,U,gaunt):
    """Both directed placements for arbitrary owned external angular labels."""
    field=np.asarray(fields);v=np.asarray(vertices);u=np.asarray(U);g=np.asarray(gaunt)
    if (field.ndim!=3 or v.ndim!=3 or v.shape[1]!=v.shape[2]or g.ndim!=3
            or u.ndim!=2 or u.shape[1]!=g.shape[0]or field.shape[:2]!=(len(v),g.shape[1])
            or any(not np.isfinite(a).all()for a in(field,v,u,g))):
        raise ValueError('same complete angular/current images required')
    h,n,mb=u.shape[0],v.shape[-1],field.shape[-1];nx=g.shape[-1]
    m=np.einsum('hl,ljx->hjx',u,g,optimize=True)
    right=np.einsum('hjx,cja,cik->ihkxa',m,field,v,optimize=True).reshape(n*h,n*nx,mb)
    left=np.einsum('hjx,cja,cki->kxiha',m.conj(),field,v,optimize=True).reshape(n*nx,n*h,mb)
    return right,left


def _possible(F,B,ext,*,motion=False):
    ns=(0,2)if ext=='out'else(1,);k=-F['level']+2*F['spectator'];bf=(B['level'],)
    bk=(B['absolute_spectator'],-B['absolute_spectator'])
    if motion:
        bf=tuple(n for n in(B['level']-1,B['level']+1)if n>=0)
        bk=tuple(x+y for x in bk for y in(-1,1))
    return any(abs(nB-nx)<=F['level']<=nB+nx and(F['level']+nB+nx)%2==0
        and any(k==b+dx for b in bk for dx in range(-nx,nx+1,2))for nB in bf for nx in ns)


def _point_sources(F,B,fields,vertices,images,ext,*,field_parity=None,field_indices=None):
    par=B['parity']if field_parity is None else field_parity
    hi=B['harmonic_indices']if field_indices is None else field_indices
    G=images['external_gaunt'][(F['parity'],par,ext)][:,hi]
    return generalized_vertex_sources(fields,vertices,F['real_to_complex'],G)


def generalized_current_moments(F,B,points,p,dp,measure,external_norm,images,*,cache,directions=False):
    size=len(F['eigenvalues']);mb=len(B['eigenvalues']);fi=F['family_indices']
    shape=dict(Lout=(60,size,mb),Linput=(24,size,mb),Rout=(size,60,mb),Rinput=(size,24,mb))
    out={key:np.zeros(v,complex)for key,v in shape.items()}
    if directions:out.update({'d'+key:np.zeros((3,*v),complex)for key,v in shape.items()})
    for j,point in enumerate(points):
        key=(B['name'],j,'base')
        if key not in cache:cache[key]=_base_maps(B,point,images)
        base,fields=cache[key];V,AV=_trial(F,point,p[j],dp[j]);vertices=point['vertices'][:,fi][:,:,fi]
        factor=measure[j]*(2*min(point['response_time']/point['length'],1-point['response_time']/point['length']))/np.sqrt(external_norm)
        for ext in('out','input'):
            R,L=_point_sources(F,B,fields,vertices,images,ext)
            out['L'+ext]+=factor*np.einsum('ida,dI->iIa',L,V,optimize=True)
            out['R'+ext]+=factor*(AV.conj().T@R.reshape(len(V),-1)).reshape(size,R.shape[1],mb)
        if directions:
            target='even'if B['parity']=='odd'else'odd'
            G=images['gaunt_even_odd_source']if target=='even'else images['gaunt_even_odd_source'].transpose(1,0,2)
            G=G[:,B['harmonic_indices']]
            for axis in range(3):
                key=(B['name'],j,'direction',axis)
                if key not in cache:
                    D=field_current_direction(base,G,point['source_wall_gauge'][axis,:,:,:4],point['source_H'][axis,:,:4])
                    n=base['harmonic_count'];sl=slice(40*n,56*n)
                    if np.any(D[:,:,:40*n])or np.any(D[:,:,56*n:]):raise ArithmeticError('independent current columns move unexpectedly')
                    cache[key]=np.einsum('chm,ma->cha',D[:,:,sl],B['eigenvectors'][sl],optimize=True)
                D=cache[key];hi=np.arange(D.shape[1])
                for ext in('out','input'):
                    R,L=_point_sources(F,B,D,vertices,images,ext,field_parity=target,field_indices=hi)
                    out['dL'+ext][axis]+=factor*np.einsum('ida,dI->iIa',L,V,optimize=True)
                    out['dR'+ext][axis]+=factor*(AV.conj().T@R.reshape(len(V),-1)).reshape(size,R.shape[1],mb)
    return out


def generalized_action_direction(target,source,points,p,dp,measure,images):
    if target['parity']==source['parity']:raise ValueError('n1 source must connect opposite parity')
    G=images['gaunt_even_odd_source']if target['parity']=='even'else images['gaunt_even_odd_source'].transpose(1,0,2)
    M=np.einsum('hl,ljs,kj->hks',target['real_to_complex'],G,source['real_to_complex'].conj(),optimize=True)
    fi=target['family_indices'];nt=len(target['harmonic_indices']);ns=len(source['harmonic_indices'])
    shape=(3,len(target['eigenvalues']),len(source['eigenvalues']));left=np.zeros(shape,complex);right=left.copy();values=[]
    for j,point in enumerate(points):
        Vt,At=_trial(target,point,p[j],dp[j]);Vs,As=_trial(source,point,p[j],dp[j]);Xi=point['Xi_source_coefficients'][:,:,fi][:,:,:,fi]
        X=np.einsum('hks,Asij->Aihjk',M,Xi,optimize=True).reshape(3,6*nt,6*ns)
        Xrev=np.einsum('khs,Asij->Aikhj',M.conj().transpose(1,0,2),Xi,optimize=True).reshape(3,6*ns,6*nt)
        for axis in range(3):
            left[axis]+=measure[j]*(At.conj().T@X[axis]@Vs)
            right[axis]+=measure[j]*((Xrev[axis]@Vt).conj().T@As)
        values.append((X,Xrev,Vt,At,Vs,As))
    return dict(square_left=left,square_right=right,point_images=values)


def generalized_numerator_direction(target,source,B,points,measure,external_norm,point_images,images,*,cache):
    fi=target['family_indices'];mb=len(B['eigenvalues'])
    out={ext:np.zeros((3,len(target['eigenvalues']),n,mb),complex)for ext,n in(('out',60),('input',24))}
    rev={ext:np.zeros((3,len(source['eigenvalues']),n,mb),complex)for ext,n in(('out',60),('input',24))}
    for j,point in enumerate(points):
        key=(B['name'],j,'base')
        if key not in cache:cache[key]=_base_maps(B,point,images)
        _,fields=cache[key];vertices=point['vertices'][:,fi][:,:,fi]
        factor=measure[j]*(2*min(point['response_time']/point['length'],1-point['response_time']/point['length']))/np.sqrt(external_norm)
        X,Xrev,Vt,At,Vs,As=point_images[j]
        for ext in('out','input'):
            Rs,_=_point_sources(source,B,fields,vertices,images,ext);Rt,_=_point_sources(target,B,fields,vertices,images,ext)
            for axis in range(3):
                out[ext][axis]+=factor*((Xrev[axis]@Vt).conj().T@Rs.reshape(len(Vs),-1)).reshape(len(target['eigenvalues']),Rs.shape[1],mb)
                rev[ext][axis]+=factor*((X[axis]@Vs).conj().T@Rt.reshape(len(Vt),-1)).reshape(len(source['eigenvalues']),Rt.shape[1],mb)
    return out,rev


def changing_magnetic_momentum_columns(phase,first_field_sampler,fermions,fields,field_direction,*,
        times,weights,temporal_values,temporal_rates,cutoff,progress=None):
    """Same-action input n1 -> output n0/n2, plus literal reverse."""
    t=np.asarray(times);w=np.asarray(weights);p=np.asarray(temporal_values);dp=np.asarray(temporal_rates);L=abs(phase['receipt']['span']);c=float(cutoff)
    if (t.ndim!=1 or w.shape!=t.shape or p.shape!=(len(t),8)or dp.shape!=p.shape or np.any(w<=0)
            or np.any(t<0)or np.any(t>L)or not np.isfinite(c)or c<0):raise ValueError('same complete chronological temporal family required')
    images=momentum_current_angular_images();points=[magnetic_open_current_point(phase,float(u),length=L,first_field_sampler=first_field_sampler,include_maps=False)for u in t]
    for point in points:point['length']=L
    measure=w*np.array([a['N']for a in points]);extnorm=float(measure@np.array([2*min(u/L,1-u/L)for u in t])**2)
    names=('fermion_square_left','fermion_square_right','fermion_numerator_contact','field_operator','field_Gram_current','left_current_chart','right_current_chart')
    forward={key:np.zeros((3,180,72),complex)for key in names};reverse={key:np.zeros((3,72,180),complex)for key in names};records=[];max_error=0.
    for family in sorted(set(f['family']for f in fermions)):
        ff=[f for f in fermions if f['family']==family];fi=ff[0]['family_indices'];iout=(fi[:,None]*10+np.arange(10)).ravel();iin=(fi[:,None]*4+np.arange(4)).ravel()
        for B in fields:
            cache={};moments={};count=0
            def moment(F,other=B,directions=False):
                key=(F['name'],other['name'],directions)
                if key not in moments:moments[key]=generalized_current_moments(F,other,points,p,dp,measure,extnorm,images,cache=cache,directions=directions)
                return moments[key]
            lf={key:np.zeros((3,60,24),complex)for key in names};lr={key:np.zeros((3,24,60),complex)for key in names}
            # Every differentiated current is counted once per F/B pair.
            for F in ff:
                if not(_possible(F,B,'input')or _possible(F,B,'out')):continue
                m=moment(F,directions=True)
                if _possible(F,B,'input'):
                    lf['left_current_chart']+=_current_sandwich(m['dLout'],m['Rinput'],F['eigenvalues'],B['eigenvalues'],c)
                    lr['right_current_chart']+=_current_sandwich(m['Linput'],m['dRout'],F['eigenvalues'],B['eigenvalues'],c)
                if _possible(F,B,'out'):
                    lf['right_current_chart']+=_current_sandwich(m['Lout'],m['dRinput'],F['eigenvalues'],B['eigenvalues'],c)
                    lr['left_current_chart']+=_current_sandwich(m['dLinput'],m['Rout'],F['eigenvalues'],B['eigenvalues'],c)
            for Fs in ff:
                if not _possible(Fs,B,'input'):continue
                ms=moment(Fs)
                for Ft in ff:
                    if not _possible(Ft,B,'out')or abs(Ft['level']-Fs['level'])!=1 or abs((-Ft['level']+2*Ft['spectator'])-(-Fs['level']+2*Fs['spectator']))!=1:continue
                    mt=moment(Ft);a=generalized_action_direction(Ft,Fs,points,p,dp,measure,images);count+=1
                    nt,ns=generalized_numerator_direction(Ft,Fs,B,points,measure,extnorm,a['point_images'],images,cache=cache)
                    for key,ds,rs in(('fermion_square_left',a['square_left'],a['square_right'].conj().transpose(0,2,1)),('fermion_square_right',a['square_right'],a['square_left'].conj().transpose(0,2,1))):
                        v,e=_fermion_sandwich(mt['Lout'],ms['Rinput'],ds,Ft['eigenvalues'],Fs['eigenvalues'],B['eigenvalues'],c);lf[key]+=v;max_error=max(max_error,e)
                        v,e=_fermion_sandwich(ms['Linput'],mt['Rout'],rs,Fs['eigenvalues'],Ft['eigenvalues'],B['eigenvalues'],c);lr[key]+=v;max_error=max(max_error,e)
                    lf['fermion_numerator_contact']+=_current_sandwich(mt['Lout'],nt['input'],Ft['eigenvalues'],B['eigenvalues'],c)
                    lr['fermion_numerator_contact']+=_current_sandwich(ms['Linput'],ns['out'],Fs['eigenvalues'],B['eigenvalues'],c)
                for Bt in fields:
                    if Bt['parity']==B['parity']or abs(Bt['level']-B['level'])!=1 or not _possible(Fs,Bt,'out'):continue
                    mt=moment(Fs,other=Bt);dk,dg=field_direction(Bt,B);ut,us=Bt['eigenvectors'],B['eigenvectors']
                    dk=np.array([ut.T@x@us for x in dk]);dg=np.array([ut.T@x@us for x in dg])
                    v,g,e=_field_sandwich(mt['Lout'],ms['Rinput'],dk,dg,Fs['eigenvalues'],Bt['eigenvalues'],B['eigenvalues'],c);lf['field_operator']+=v;lf['field_Gram_current']+=g;max_error=max(max_error,e)
                    v,g,e=_field_sandwich(ms['Linput'],mt['Rout'],dk.transpose(0,2,1),dg.transpose(0,2,1),Fs['eigenvalues'],B['eigenvalues'],Bt['eigenvalues'],c);lr['field_operator']+=v;lr['field_Gram_current']+=g;max_error=max(max_error,e)
            for key in names:
                for axis in range(3):
                    forward[key][axis][np.ix_(iout,iin)]+=lf[key][axis];reverse[key][axis][np.ix_(iin,iout)]+=lr[key][axis]
            record=dict(family=family,field_level=B['level'],absolute_spectator=B['absolute_spectator'],field_dimension=len(B['eigenvalues']),
                forward_contribution_norm=float(np.linalg.norm(sum(lf.values()))),reverse_contribution_norm=float(np.linalg.norm(sum(lr.values()))),
                moment_pair_count=len(moments),fermion_pair_count=count)
            records.append(record)
            if progress is not None:progress(record)
            del cache,moments
    for out in(forward,reverse):out['total']=sum(out.values())
    return dict(forward=forward,reverse=reverse,block_records=records,external_tent_Gram=extnorm,
        maximum_scalar_kernel_approximation_upper=max_error,
        ordering='forward outputspin18*10+realharmonic(n0/n2), inputspin18*4+realharmonic(n1); literal reverse',
        starting_field_domain_enlarged=False,input_momentum_columns_evaluated=True,
        physical_P_strat_Wick_LSZ_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None)
