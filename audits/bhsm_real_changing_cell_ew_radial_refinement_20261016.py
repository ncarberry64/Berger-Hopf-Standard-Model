"""Exact cached/sparse radial refinement of the same changing REAL forms.

Twelve saved actual time snapshots are reused without a history replay.
Owned value-only geometric/profile maps replace redundant100-Hessians;
their full q32 coefficient/matrix application is compared to the original
producer before any64/128 readout is interpreted. Sparse products discard
only exact zeros, retaining the complete1200/320 coefficient spaces.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy import sparse
from scipy.linalg import cho_factor, cho_solve

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'audits'))
import bhsm_real_changing_cell_ew_higgs_fp_stable_weight_20261016 as prior
import bhsm_real_ew_higgs_fp_common_forms_20261016 as frozen
from bhsm.interface.muon_holomorphic_normal_geometry import (
    _geometry_variables,_fields,_sqrt,holomorphic_geometry_rows)
from bhsm.interface.muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from bhsm.interface.muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_positive_brst_ghost import (
    ghost_radial_values,_linear_curvature,smooth_ghost_temporal_values)
from bhsm.interface.muon_parent_positive_gauge_form import (
    _weighted_curvature_maps,positive_curvature_contact_matrix)
from bhsm.interface.muon_parent_positive_coupled_temporal import paired_scalar_orbit_maps,one_form_point_row
from bhsm.interface.muon_parent_positive_coupled_field import coupled_wall_maps
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad,constant_angular_curvatures
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

INPUT_JSON_SHA='182928faef437728923fa279d44be51bdc4739f5a0ddb10eff83c01f1c95d95a'
INPUT_NPZ_SHA='9a132366d729c85ea1d83815a5482fbf6352b117507e9f447abb4c3b7534739d'
PRIOR_SHA='2a536410954923a6a4cd7865264fbae1b14ad61d8db1a7d58b1c1cfc84eb3874'


def real(a,name):return frozen.real(a,name)


def load_sparse(a,name):
    return sparse.csr_matrix((a[name+'_data'],a[name+'_indices'],a[name+'_indptr']),shape=tuple(a[name+'_shape']))


def compare(a,b):
    a,b=np.asarray(a),np.asarray(b);delta=abs(a-b);scale=np.maximum(1,np.maximum(abs(a),abs(b)))
    index=np.unravel_index(np.argmax(delta/scale),a.shape)
    return dict(max_absolute=float(delta.max()),max_entry_scaled=float((delta/scale)[index]),
        index=list(map(int,index)),old_value=float(a[index]),new_value=float(b[index]),
        relative_global_max_entry=float(delta.max()/max(abs(a).max(),abs(b).max(),np.finfo(float).tiny)),
        relative_Frobenius=float(np.linalg.norm(a-b)/max(np.linalg.norm(b),np.finfo(float).tiny)))


def connection_profile(raw,rho):
    g=holomorphic_geometry_rows(np.asarray(raw)[:100],rho,differentiate=False,connection_only=True)
    return real(np.array([[r[k].value for k in ('connection_lambda','lambda_tau','lambda_rho')]for r in g['rows']]),'owned real profile')


def fixed_basis(rep,rho):
    """Literal trace_enriched_radial_basis formula, value-only same owners."""
    B,D=regular_radial_basis(rho,2);states=rep['affine_profile_reference_states']
    profile=[connection_profile(np.r_[x,0.,0.],rho)for x in states]
    d,dr=profile[0][:,0]-profile[1][:,0],profile[0][:,2]-profile[1][:,2]
    projection=rep['affine_interior_projection'];wall=rep['affine_wall_coefficient'];norm=rep['affine_complement_norm']
    return np.c_[B[:,:2],(d-B[:,:2]@projection-wall*B[:,-1])/norm,B[:,-1]],np.c_[D[:,:2],(dr-D[:,:2]@projection-wall*D[:,-1])/norm,D[:,-1]]


def fields(raw,rate,t,rho,basis,basisr,side,pairs):
    """Same constitutive coefficients on the proven coherent cell tangent."""
    if not np.array_equal(rate[:37],raw[37:74])or rate[98]!=raw[99]:
        raise ValueError('Actual qdot=v and sdot=raw99 required for source lambda_tau identity')
    geo=holomorphic_geometry_rows(raw[:100],rho,differentiate=False)
    own=real(np.array([[r[k].value for k in ('connection_lambda','lambda_tau','lambda_rho')]for r in geo['rows']]),'real own profile')
    if side=='outgoing':
        initial,reference=pairs
        parent=affine_geometry_germ(initial[0],t);refs=[affine_geometry_germ(x,t)for x in reference]
        profile=connection_profile(parent,rho)-connection_profile(refs[0],rho)+connection_profile(refs[1],rho)
    else:profile=own
    A=np.einsum('ri,ifc->rfc',basis,raw[100:180].reshape(4,5,4))
    At=np.einsum('ri,ifc->rfc',basis,rate[100:180].reshape(4,5,4))
    Ar=np.einsum('ri,ifc->rfc',basisr,raw[100:180].reshape(4,5,4))
    A[:,2:]+=M*(profile[:,0,None,None]-1);At[:,2:]+=M*profile[:,1,None,None];Ar[:,2:]+=M*profile[:,2,None,None]
    q,v,m,delta,dr,wall,_=_geometry_variables(raw[:100],differentiate=False)
    R=[];N=[];C=[]
    for rr in rho:
        f=_fields(12,q,v,m,(float(rr)/WALL)*wall)
        R.append((f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)).value)
        N.append(f['N'].value);C.append((f['C']*wall/WALL).value)
    R,N,C=[real(a,'real coframe')for a in(R,N,C)]
    density=real(np.array([[r[k].value for k in('electric','radial','angular','electric_radial','shift')]for r in geo['rows']]),'stable densities')
    e,r,d,k,z=density.T;metric=np.column_stack((d*R**4,e*R**2,r*R**2,d*R**2,z,R))
    f=_fields(12,q,v,m,wall);U=f['C']*(dr+f['beta'])/f['N'];ell=real(np.array((f['N']*_sqrt(1-U*U)).value),'induced clock').item()
    if min(ell,metric[:,:4].min(),density[:,:4].min())<=0:raise ValueError('Positive regular actual coefficient branch required')
    weights=np.array([R[-1]**3/ell,ell*R[-1],ell*R[-1]**3])
    return dict(A=A,A_time=At,A_radial=Ar,positive_metric=metric,positive_two_form_densities=density,
        H=raw[260:264],H_time=rate[260:264],intrinsic_weights=weights,profile=profile)


def cache_radial(E,radial):
    I=np.eye(400).reshape(5,80,400);Ef=np.array([np.kron(np.eye(4),e)for e in E])
    V=np.concatenate([p[0]*I for p in radial],axis=2);Vr=np.concatenate([p[1]*I for p in radial],axis=2)
    Va=np.einsum('phk,fkA->pfhA',Ef,V);zero=np.zeros_like(V)
    C1=_linear_curvature(np.zeros((5,4)),zero.reshape(5,4,-1),V.reshape(5,4,-1),zero.reshape(5,4,-1),np.zeros_like(Va).reshape(3,5,4,-1))
    return dict(V=V,Vr=Vr,Va=Va,zero=zero,C1=C1,Ef=Ef)


def sparse_point(A,At,Ar,E,radial,metric,density,t,cache):
    """Identical complete point maps; exact sparse products, no threshold."""
    V,Vr,Va,zero=(cache[k]for k in('V','Vr','Va','zero'))
    convert=lambda a:a.reshape(a.shape[:-1]+(20,800))
    C0=_linear_curvature(A,V.reshape(5,4,-1),zero.reshape(5,4,-1),Vr.reshape(5,4,-1),Va.reshape(3,5,4,-1))
    C0,C1=(_weighted_curvature_maps(tuple(convert(a)for a in cc),density)for cc in(C0,cache['C1']))
    F=constant_angular_curvatures(A,At,Ar);D=np.array([np.kron(_ad(a),np.eye(20))for a in A]);D[2:]+=cache['Ef']
    G=[];R=[];CG=[];eta=[]
    for p in radial:
        g=p[0]*D;g[1]+=p[1]*np.eye(80);r=np.zeros_like(g);r[0]=p[0]*np.eye(80)
        G.append(g.reshape(400,80));R.append(r.reshape(400,80));eta.append(p[0]*np.eye(80))
        fc=tuple(p[0]*np.kron(_ad(a),np.eye(20))for a in(F['Ftr'],*F['Ft'],*F['Fr'],*F['B']))
        CG.append(_weighted_curvature_maps((fc[0],np.array(fc[1:4]),np.array(fc[4:7]),np.array(fc[7:10])),density))
    G,R,CG,eta=(np.concatenate(a,axis=1)for a in(G,R,CG,eta))
    value=np.zeros((400,1120));curv=np.zeros((800,1120));etas=np.zeros((80,320))
    value[:,:800]=t[0]*V.reshape(400,800);curv[:,:800]=t[0]*C0+t[1]*C1
    for i in range(2):
        p=2+2*i;s=slice(800+160*i,960+160*i)
        value[:,s]=t[p]*G+t[p+1]*R;curv[:,s]=t[p]*CG;etas[:,160*i:160*(i+1)]=t[p]*eta
    value,curv,etas=map(sparse.csr_matrix,(value,curv,etas))
    contact=value.T@sparse.csr_matrix(positive_curvature_contact_matrix(F,density,20))@value
    mu,gt,gr,gs,beta,radius=metric;g=np.diag([gt,gr+beta*beta*gt,gs,gs,gs]);g[0,1]=g[1,0]=-beta*gt
    Gram=value.T@sparse.kron(sparse.csr_matrix(g),sparse.eye(80),format='csr')@value
    return curv.T@curv+contact,Gram,contact,mu*(etas.T@etas)


def finalize(K,G,contact,ghostG,scalar):
    K,G,contact,ghostG=[a.toarray()if sparse.issparse(a)else a for a in(K,G,contact,ghostG)]
    Kkin,K4,K2,scalarG=scalar;ghostK=G[800:,800:].copy();B=np.zeros((320,1200));B[:,:1120]=G[800:]
    F=cho_solve(cho_factor(ghostG,lower=True),B);Pi=np.eye(1200);Pi[800:1120]-=cho_solve(cho_factor(ghostK,lower=True),B)
    common=Kkin.copy();common[:1120,:1120]+=MAXWELL_TO_CAP*K;commonG=scalarG.copy();commonG[:1120,:1120]+=MAXWELL_TO_CAP*G
    return dict(zip(prior.MATRIX_NAMES,(K,G,contact,ghostK,ghostG,F,B,Pi,Kkin,K4,K2,scalarG,common,commonG,MAXWELL_TO_CAP*B.T@F)))


def execute(application,output,orders):
    application,out=Path(application),Path(output)
    if out.exists():raise FileExistsError('Preserve every previous rule')
    rb=(application/'result.json').read_bytes();ab=(application/'changing_forms.npz').read_bytes()
    if sha256(rb).hexdigest()!=INPUT_JSON_SHA or sha256(ab).hexdigest()!=INPUT_NPZ_SHA:raise ValueError('Original corrected TIME6 pair required')
    if sha256((ROOT/'audits/bhsm_real_changing_cell_ew_higgs_fp_stable_weight_20261016.py').read_bytes()).hexdigest()!=PRIOR_SHA:raise ValueError('Preserve original coefficient producer')
    report=json.loads(rb)
    with np.load(application/'changing_forms.npz',allow_pickle=False)as z:old={k:z[k].copy()for k in z.files}
    pins=dict(report['input_and_source_sha256'])
    base=ROOT/frozen.BASE
    with np.load(base/'application.npz',allow_pickle=False)as z:rep={k:z[k].copy()for k in('affine_profile_reference_states','affine_interior_projection')}
    br=json.loads((base/'result.json').read_text());rep.update(affine_wall_coefficient=br['affine_profile_enrichment']['wall_coefficient'],affine_complement_norm=br['affine_profile_enrichment']['boundary_anchored_complement_norm'])
    with np.load(ROOT/prior.PHASES['outgoing']/'application.npz',allow_pickle=False)as z:pairs=(z['initial_pair'].copy(),z['reference_pair'].copy())
    E=old['EW4_real_angular_derivatives'];records=[];out.mkdir(parents=True)
    for side in('incoming','outgoing'):
        source=side+'_radial32_';raws,rates=old[source+'raw'],old[source+'rawtime'];times=old[source+'temporal_coordinate_time'];u=old[source+'temporal_u'];tw=old[source+'temporal_coordinate_weights'];temporal=old[source+'ghost_temporal_value_rate_second'];length=1e-5
        previous={name:load_sparse(old,source+name).toarray()for name in prior.MATRIX_NAMES};previous_order=32
        for order in orders:
            x,w=np.polynomial.legendre.leggauss(order);rho=np.r_[(x+1)*WALL/2,WALL];rw=w*WALL/2
            B,Br=fixed_basis(rep,rho);radial=ghost_radial_values(rho);caches=[cache_radial(E,r)for r in radial[:order]]
            K,G,C=[sparse.csr_matrix((1120,1120))for _ in range(3)];GG=sparse.csr_matrix((320,320));scalar=[np.zeros((1200,1200))for _ in range(4)]
            values={};point_controls=[];coefficient_controls=[]
            for i,(raw,rate,t,uu,ww,tg)in enumerate(zip(raws,rates,times,u,tw,temporal)):
                f=fields(raw,rate,float(t),rho,B,Br,side,pairs)
                b=2*min(uu/length,1-uu/length);bp=(2 if uu<length/2 else -2)/length;tf=np.r_[b,bp,tg[0,:2],tg[1,:2]]
                for j in range(order):
                    rr=sparse_point(f['A'][j],f['A_time'][j],f['A_radial'][j],E,radial[j],f['positive_metric'][j],f['positive_two_form_densities'][j],tf,caches[j]);scale=ww*rw[j]
                    K+=scale*rr[0];G+=scale*rr[1];C+=scale*rr[2];GG+=scale*rr[3]
                    if i in(0,len(times)//2,len(times)-1)and j in(0,order//2,order-1):
                        literal=one_form_point_row(f['A'][j],f['A_time'][j],f['A_radial'][j],E,radial[j],f['positive_metric'][j],f['positive_two_form_densities'][j],tf)
                        point_controls.append(dict(time_index=i,radial_index=j,Hessian=compare(literal['Hessian'],rr[0].toarray()),Gram=compare(literal['Gram'],rr[1].toarray()),curvature_contact=compare(literal['curvature_contact'],rr[2].toarray()),ghost_Gram=compare(literal['ghost_Gram'],rr[3].toarray())))
                W=np.zeros((400,1200));W[:,:1120]=np.einsum('t,tij->ij',tf,coupled_wall_maps(f['A'][-1],E,length=length)['wall_time_profile_value_maps'])
                hs=paired_scalar_orbit_maps(f['H'],f['H_time'],tf,radial[-1]);sc=frozen.scalar_point(f['intrinsic_weights'],f['H'],f['H_time'],f['A'][-1],E,W,hs)
                for n in range(4):scalar[n]+=ww*sc[n]
                for name,a in f.items():values.setdefault(name,[]).append(a)
                if order==32:
                    coefficient_controls.append(dict(time_index=i,fields={name:compare(old[source+name][i],f[name])for name in('A','A_time','A_radial','positive_metric','positive_two_form_densities','H','H_time','intrinsic_weights')}))
                print(json.dumps(dict(side=side,radial_order=order,time_index=i+1,time_count=len(times))),flush=True)
            matrices=finalize(K,G,C,GG,scalar);difference={name:compare(previous[name],a)for name,a in matrices.items()}
            max_scaled=max(v['max_entry_scaled']for v in difference.values());folder=out/f'{side}_radial{order}';folder.mkdir();arrays=dict(radial_points=rho,radial_coordinate_weights=rw,temporal_u=u,temporal_coordinate_time=times,temporal_coordinate_weights=tw,ghost_radial_value_rate_second=radial,ghost_temporal_value_rate_second=temporal,raw=raws,rawtime=rates,fixed_basis=B,fixed_basis_radial=Br)
            arrays.update({name:np.array(a)for name,a in values.items()})
            for name,a in matrices.items():frozen.save_sparse(arrays,name,a)
            _compressed_npz(folder/'forms.npz',arrays)
            record=dict(side=side,radial_order=order,compared_to_order=previous_order,time_rule_per_half=6,matrix_comparisons=difference,maximum_all_blocks_entry_scaled=max_scaled,coefficient_controls_against_original_q32=coefficient_controls,independent_dense_point_controls=point_controls,archive_bytes=(folder/'forms.npz').stat().st_size,numerical_sha256=sha256((folder/'forms.npz').read_bytes()).hexdigest(),physical_derivative_or_state_convergence=False,coupled_corrections=0)
            (folder/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');records.append(record);previous,previous_order=matrices,order
            if order==32 and max(row['fields'][name]['max_entry_scaled']for row in coefficient_controls for name in row['fields'])>2e-10:
                raise ArithmeticError('Fast owned coefficient correspondence did not pass; preserve q32 evidence')
            if order>=64 and max_scaled<=2e-10:break
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name.startswith('bhsm.')or name in('bhsm_real_changing_cell_ew_higgs_fp_stable_weight_20261016','bhsm_real_ew_higgs_fp_common_forms_20261016'))and Path(p).is_relative_to(ROOT):pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for p,h in pins.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise RuntimeError('Owner changed: '+p)
    result=dict(classification='EXACT_CACHED_SPARSE_REAL_CHANGING_EW_RADIAL_REFINEMENT',records=records,original_time6_json_sha256=INPUT_JSON_SHA,original_time6_archive_sha256=INPUT_NPZ_SHA,source_time_snapshots_replayed=False,coefficient_and_trial_bases_renormalized=False,exact_zero_only_sparse_storage=True,potential_matching_values_assigned=False,physical_native_outgoing_or_state_convergence=False,physical_muon_moment=None,coupled_corrections=0,input_and_source_sha256=dict(sorted(pins.items())))
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--application',required=True);p.add_argument('--output',required=True);p.add_argument('--orders',nargs='+',type=int,default=[32,64,128]);a=p.parse_args()
    if a.orders[0]!=32:raise ValueError('Validate original q32 first')
    execute(a.application,a.output,a.orders)
