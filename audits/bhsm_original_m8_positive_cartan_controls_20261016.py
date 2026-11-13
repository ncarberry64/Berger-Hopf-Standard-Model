"""Independent positive-coframe M8 Cartan/Dirac controls, no native grading.

This tests a geometric identity on the owned original coframe. It is not
a Wick rotation of the physical fields or a selected microscopic carrier.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np


PRIMITIVES=('N','C','A','B','beta','N_t','N_chi','C_t','C_chi',
            'A_t','A_chi','B_t','B_chi','beta_t','beta_chi')
ROOT=Path(__file__).resolve().parents[1]


def maximum(a):return float(np.max(abs(a)))


def levi():
    e=np.zeros((3,3,3))
    for i in range(3):e[i,(i+1)%3,(i+2)%3]=1;e[i,(i+2)%3,(i+1)%3]=-1
    return e


def cartan_positive(p):
    N,C,A,B,z,Nt,Nr,Ct,Cr,At,Ar,Bt,Br,zt,zr=p
    a=Nr/(N*C);k=(Ct-z*Cr-C*zr)/(N*C)
    Hu=(At-z*Ar)/(N*A);Hv=(Bt-z*Br)/(N*B)
    ru=Ar/(C*A);rv=Br/(C*B)
    w=np.zeros((8,8,8));w[0,1,0]=a;w[0,1,1]=-k;e=levi()
    for offset,H,r,scale in((2,Hu,ru,A),(5,Hv,rv,B)):
        for i in range(3):
            w[0,offset+i,offset+i]=-H;w[1,offset+i,offset+i]=-r
            for j in range(3):
                for l in range(3):w[offset+i,offset+j,offset+l]=-e[i,j,l]/scale
    for i in range(8):
        for j in range(i+1,8):w[j,i]=-w[i,j]
    return w,np.array([a,k,Hu,Hv,ru,rv])


def independent_tetrad(p):
    """All eight metric Christoffel/tetrad directions at SU2 chart origins."""
    N,C,A,B,z,Nt,Nr,Ct,Cr,At,Ar,Bt,Br,zt,zr=p
    e=levi();cof=np.diag([N,C,A,A,A,B,B,B]);cof[1,0]=C*z
    dc=np.zeros((8,8,8));dc[0]=np.diag([Nt,Ct,At,At,At,Bt,Bt,Bt]);dc[0,1,0]=Ct*z+C*zt
    dc[1]=np.diag([Nr,Cr,Ar,Ar,Ar,Br,Br,Br]);dc[1,1,0]=Cr*z+C*zr
    for offset,scale in((2,A),(5,B)):
        for i in range(3):
            for j in range(3):
                for k in range(3):dc[offset+j,offset+i,offset+k]=-scale*e[i,j,k]
    g=cof.T@cof;dg=np.array([d.T@cof+cof.T@d for d in dc]);ch=np.zeros((8,8,8))
    for mu in range(8):
        for nu in range(8):ch[:,mu,nu]=np.linalg.solve(g,.5*np.array([dg[mu,s,nu]+dg[nu,s,mu]-dg[s,mu,nu]for s in range(8)]))
    inv=np.linalg.inv(cof);w=np.array([(cof@ch[:,mu,:]-dc[mu])@inv for mu in range(8)])
    lower=w.transpose(1,2,0)
    tetrad=np.array([dc[mu]-cof@ch[:,mu,:]+w[mu]@cof for mu in range(8)])
    return dict(coframe=cof,inverse=inv,lower_coordinate=lower,tetrad=tetrad,metric=g)


def mp_generic(t,r):
    """Literal positive metric on both full quaternion coordinate charts."""
    with mp.workdps(64):
        x0=[mp.mpf(t),mp.mpf(r)]+[mp.mpf(0)]*6;e=levi()
        def vals(t,r):
            return (mp.exp(t/5+11*r/100+3*t*r/100),
                mp.exp(-t/10+7*r/100+t*r/25),
                mp.exp(3*t/50-3*r/25+t*t/50),
                mp.exp(13*t/100+9*r/100-3*r*r/100),
                2*t/25+r/20+t*r/50)
        def cf(*x):
            N,C,A,B,z=vals(x[0],x[1]);c=mp.zeros(8);c[0,0]=N;c[1,1]=C;c[1,0]=C*z
            for offset,scale in((2,A),(5,B)):
                y=x[offset:offset+3];q4=mp.sqrt(1-sum(a*a for a in y))
                for i in range(3):
                    for k in range(3):c[offset+i,offset+k]=scale*(q4*(i==k)+y[i]*y[k]/q4-sum(mp.mpf(float(e[i,j,k]))*y[j]for j in range(3)))
            return c
        co=cf(*x0)
        dc=[mp.matrix([[mp.diff(lambda u:cf(*(x0[:mu]+[u]+x0[mu+1:]))[a,b],x0[mu])for b in range(8)]for a in range(8)])for mu in range(8)]
        g=co.T*co;gi=g**-1;dg=[d.T*co+co.T*d for d in dc];ci=co**-1
        lower=[]
        for mu in range(8):
            ch=mp.matrix([[sum(gi[a,s]*(dg[mu][s,b]+dg[b][s,mu]-dg[s][mu,b])/2 for s in range(8))for b in range(8)]for a in range(8)])
            lower.append((co*ch-dc[mu])*ci)
        p=list(vals(*x0[:2]));p.extend([mp.diff(lambda tt:vals(tt,x0[1])[0],x0[0]),mp.diff(lambda rr:vals(x0[0],rr)[0],x0[1])])
        for a in(1,2,3):p.extend([mp.diff(lambda tt:vals(tt,x0[1])[a],x0[0]),mp.diff(lambda rr:vals(x0[0],rr)[a],x0[1])])
        p.extend([mp.diff(lambda tt:vals(tt,x0[1])[4],x0[0]),mp.diff(lambda rr:vals(x0[0],rr)[4],x0[1])])
        p=np.array([float(a)for a in p]);low=np.array([[[float(lower[mu][a,b])for mu in range(8)]for b in range(8)]for a in range(8)])
        return p,low


def execute(repository,output):
    root,out=Path(repository).resolve(),Path(output)
    if out.exists():raise FileExistsError('Preserve all previous controls')
    sys.path.insert(0,str(root/'src'));sys.path.insert(0,str(root/'audits'))
    from bind_muon_real_changing_gauge_transport_20261016 import archive_bytes
    from bhsm.interface.muon_original_m8_geometric_expression import original_m8_clifford,original_m8_geometric_expression_jets
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    base=root/'artifacts/muon_real_changing_gauge_transport_20261016'
    raw=archive_bytes(base,'stable_time6_run_1/changing_forms.npz')
    expected='9a132366d729c85ea1d83815a5482fbf6352b117507e9f447abb4c3b7534739d'
    if sha256(raw).hexdigest()!=expected:raise ValueError('Exact preserved real snapshots required')
    with np.load(BytesIO(raw),allow_pickle=False)as z:
        saved={side:(z[side+'_radial32_raw'].copy(),z[side+'_radial32_rawtime'].copy())for side in('incoming','outgoing')}
    samples=[]
    for side,(states,rates)in saved.items():
        for ti in(0,6,11):
            state,rate=states[ti],rates[ti]
            if not np.array_equal(rate[:37],state[37:74])or np.any(rate[74:98]!=0):raise ValueError('Actual coherent affine source germ required')
            q,v,m,*_=_geometry_variables(state[:100],differentiate=False)
            for chi in(.13,.37,.69):
                f=_fields(12,q,v,m,type(q[0]).constant(chi,0))
                if any(not np.isfinite(a.value)or complex(a.value).imag!=0 for a in f.values()):raise ValueError('Real coframe values required without projection')
                d={k:float(complex(a.value).real)for k,a in f.items()}
                N,C,A,B,beta=(d[k]for k in('N','C','A','B','beta'))
                p=np.array([N,C,A,B,beta,0,N*d['np'],C*d['lc'],C*d['cp'],A*d['la'],A*d['ap'],B*d['lb'],B*d['bp'],0,d['betap']])
                h0=(d['lc']+3*d['la']+3*d['lb']-beta*(d['cp']+3*d['ap']+3*d['bp'])-d['betap'])/(2*N)
                hr=(d['np']+3*d['ap']+3*d['bp'])/(2*C)
                samples.append((dict(kind='actual_saved_real',side=side,time_index=ti,chi=chi),p,h0,hr,None))
    for t,r in(('-0.15','0.21'),('0.12','0.47'),('0.31','0.66')):
        p,independent=mp_generic(t,r);_,cs=cartan_positive(p);a,k,hu,hv,ru,rv=cs
        samples.append((dict(kind='independent_MP64_literal_metric',t=t,chi=r),p,(k+3*hu+3*hv)/2,(a+3*ru+3*rv)/2,independent))
    G=original_m8_clifford(full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]])
    gamma=np.array([G[0]]+[-1j*g for g in G[1:]])
    left=-1j*gamma[0];pairs=np.einsum('aij,bjk->abik',gamma,gamma)
    arrays=dict(Gamma_L_original=G,gamma_E_positive=gamma,left_unitary=left);records=[]
    for index,(metadata,p,h0,hr,mp_low)in enumerate(samples):
        w,contacts=cartan_positive(p);tetrad=independent_tetrad(p);cof=tetrad['coframe'];inv=tetrad['inverse']
        coordinate=np.einsum('abc,cm->abm',w,cof)
        # Derive the Dirac body from the INDEPENDENT metric Christoffels,
        # not from the closed contracted h0/hchi formula being tested.
        spin_coordinate=.25*np.einsum('abm,abij->mij',tetrad['lower_coordinate'],pairs)
        de_body=1j*sum(np.einsum('A,Aij->ij',inv[mu],gamma)@spin_coordinate[mu]for mu in range(8))
        de_principal=np.array([1j*np.einsum('A,Aij->ij',inv[mu],gamma)for mu in range(8)])
        N,C,A,B,beta=p[:5]
        vals=dict(lapse=N,radial_coframe=C,orbit_A=A,orbit_B=B,coordinate_shift=beta,
                  geometric_time_contact=h0,geometric_radial_contact=hr,volume_density=N*C*A**3*B**3)
        c={name:dict(value=np.array([value]),x=np.zeros(1),y=np.zeros(1),xy=np.zeros(1))for name,value in vals.items()}
        op=original_m8_geometric_expression_jets(c,np.zeros((3,1,1)),np.zeros((3,1,1)),gamma5_base=full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]])
        target=np.array([op['coefficients']['A_time']['value'][0],op['coefficients']['A_radial']['value'][0]]+[-1j*G[0]@G[j]/(A if j<5 else B)for j in range(2,8)])
        original_body=op['coefficients']['A_body']['value'][0]
        body=left@de_body;principal=np.einsum('ij,mjk->mik',left,de_principal)
        arrays[f'point{index}_primitive']=p;arrays[f'point{index}_lower_E_frame']=w
        arrays[f'point{index}_lower_E_coordinate']=coordinate;arrays[f'point{index}_independent_lower_E_coordinate']=tetrad['lower_coordinate']
        arrays[f'point{index}_D_E_body']=de_body;arrays[f'point{index}_A_plus_body']=original_body
        record=dict(**metadata,full8D_Christoffel_Cartan_absolute=maximum(coordinate-tetrad['lower_coordinate']),
            full8D_tetrad_absolute=maximum(tetrad['tetrad']),lower_antisymmetry=maximum(coordinate+coordinate.swapaxes(0,1)),
            unitary_left_multiplier=maximum(left.conj().T@left-np.eye(16)),
            all8_principals_match_original_plus=maximum(principal-target),
            complete_body_match_original_plus=maximum(body-original_body),
            independent_MP64_Christoffel_Cartan_absolute=None if mp_low is None else maximum(coordinate-mp_low),
            coefficient_scope='Fixed actual/generic local value only; physical source jets not assigned')
        records.append(record)
    pins={Path(__file__).resolve().relative_to(root).as_posix():sha256(Path(__file__).read_bytes()).hexdigest()}
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if path and(name.startswith('bhsm')or name.startswith('bind_muon_'))and Path(path).is_relative_to(root):pins[Path(path).relative_to(root).as_posix()]=sha256(Path(path).read_bytes()).hexdigest()
    input_pins={};original=base/'stable_time6_run_1/changing_forms.npz'
    if original.exists():input_pins[original.relative_to(root).as_posix()]=sha256(original.read_bytes()).hexdigest()
    else:
        recipe=base/'exact_archive_reconstruction.json';input_pins[recipe.relative_to(root).as_posix()]=sha256(recipe.read_bytes()).hexdigest()
        for part in json.loads(recipe.read_bytes())['stable_time6_run_1/changing_forms.npz']['chunks']:
            path=base/part['path'];value=path.read_bytes()
            if len(value)!=part['bytes']or sha256(value).hexdigest()!=part['sha256']:raise ValueError('Changed exact raw input chunk')
            input_pins[path.relative_to(root).as_posix()]=part['sha256']
    result=dict(classification='ORIGINAL_M8_POSITIVE_CARTAN_PLUS_DIRAC_IDENTITY_CONTROLS',primitive_order=PRIMITIVES,
        actual_input_archive_sha256=expected,raw_input_pins=dict(sorted(input_pins.items())),records=records,source_pins=dict(sorted(pins.items())),
        positive_metric='N^2dt^2+C^2(dchi+beta dt)^2+A^2theta_u^2+B^2theta_v^2',
        reference_identity='A_plus=(-i gamma_E0)D_E; gamma_E0=Gamma_L0, gamma_Ej=-iGamma_Lj',
        Riemannian_D_E_formal_selfadjoint_on_common_smooth_core=True,
        formal_common_core_geometric_positive_square_equals_D_E_square=True,
        closed_operator_square_identity_requires_matched_selfadjoint_D_E_domain=True,
        outgoing_or_wall_selfadjoint_D_E_domain_selected=False,
        Lorentz_scalar_curvature_identified_with_positive_scalar_curvature=False,
        physical_Wick_rotation_or_contour_selected=False,
        actual_native_statistics_or_stratified_operator_identified=False,
        physical_source_derivative_pass=False,coupled_corrections=0,physical_muon_moment=None)
    out.mkdir(parents=True);_compressed_npz(out/'controls.npz',arrays)
    result['numerical_sha256']=sha256((out/'controls.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=len(records),numerical_sha256=result['numerical_sha256'],max_body=max(r['complete_body_match_original_plus']for r in records))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',default=str(ROOT));p.add_argument('--output',required=True);a=p.parse_args();execute(a.repository,a.output)
