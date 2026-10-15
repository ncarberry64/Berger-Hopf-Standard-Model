"""Exact-stored coefficient Schur/source maps for new polynomial propagation.

This only re-expresses the new signed n1 arrays. It does not integrate fields.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def export(repository,coefficients,output):
    import numpy as np
    from flint import acb,acb_mat,arb,ctx
    root,src,out=map(lambda p:Path(p).resolve(),(repository,coefficients,output));out.mkdir(parents=True,exist_ok=False)
    sys.path[:0]=[str(root/'src'),str(Path(__file__).parent)]
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm_exact_action_balls import export_acb_exact_dyadic
    ctx.prec=256;inputs={};archives={}
    def mat(a):return acb_mat([[acb(arb(float(v.real)),arb(float(v.imag)))for v in row]for row in np.asarray(a)])
    def sub(a,i,j):return acb_mat([[a[x,y]for y in j]for x in i])
    for stage in range(2):
        p=src/f'stage_{stage:04d}_exact_raw_signed_n1_forms_and_source.npz';inputs[str(p)]=sha256(p.read_bytes()).hexdigest()
        with np.load(p,allow_pickle=False)as z:a={k:z[k].copy()for k in z.files}
        keep=np.argmax(a['interior_field_lift'],axis=0);na=48;aa=range(na);dd=range(na,244)
        S,L=mat(a['interior_field_lift']),mat(a['named_wall_lift'])
        f={k:mat(a[k][np.ix_(keep,keep)])for k in('K','M','B_forward','B_reverse')}
        K,M,BF,BR=[f[k]for k in('K','M','B_forward','B_reverse')]
        Kaa=sub(K,aa,aa);Kda=sub(K,dd,aa);BRda=sub(BR,dd,aa)
        U=Kaa.solve(sub(K,aa,dd));V=Kaa.solve(sub(BF,aa,dd))
        maps=dict(Mr=sub(M,dd,dd)-BRda*V,Rr=sub(BR,dd,dd)-BRda*U,
            Fr=sub(BF,dd,dd)-Kda*V,Kr=sub(K,dd,dd)-Kda*U,
            Kaa=Kaa,original_Gauss_position_map=U,original_Gauss_velocity_map=V)
        G={k:S.transpose()*mat(a[k])*L for k in f}
        ag0=Kaa.solve(sub(G['K'],aa,range(80)));ag1=Kaa.solve(sub(G['B_forward'],aa,range(80)))
        maps.update(Gf0=sub(G['K'],dd,range(80))-Kda*ag0,Gf1=sub(G['B_forward'],dd,range(80))-Kda*ag1,
                    Gp0=sub(G['B_reverse'],dd,range(80))-BRda*ag0,Gp1=sub(G['M'],dd,range(80))-BRda*ag1,
                    Gauss_wall_value_map=ag0,Gauss_wall_rate_map=ag1)
        packet={}
        for name,value in maps.items():packet.update(export_acb_exact_dyadic(value,name+'_exact'))
        for name in ('Q','Q_coordinate_time','coordinate_time','coordinate_step','raw268','parent_raw268','reference_raw_pair',
                     'interior_field_lift','named_wall_lift','wall_and_frame_rows','original_value_permutation'):
            packet[name]=a[name]
        p=out/f'stage_{stage:04d}_original_reduced_operator_and_polynomial_source_maps.npz';_compressed_npz(p,packet)
        archives[p.name]=sha256(p.read_bytes()).hexdigest()
    result=dict(classification='EXACT_STORED_NEW_N1_OPERATOR_AND_POLYNOMIAL_FORCING_MAPS_NO_INTEGRATION',input_hashes=inputs,archives=archives,
        canonical_equations='v=Mr^-1(p-Rr*x-Gp0*Q-Gp1*Qdot); xdot=v; pdot=Kr*x+Fr*v+Gf0*Q+Gf1*Qdot',
        forcing_transform='z=w+B1*Q; wdot=A*w+(A*B1+B0)*Q; retain z at corner so w_after=w_before+(B1_before-B1_after)*Q',
        geometry_and_self_field_unchanged=True,physical_admission=False,producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(result=str(p),sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--coefficients',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();export(a.repository,a.coefficients,a.output)
