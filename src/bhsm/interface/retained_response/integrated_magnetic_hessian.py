"""Full radial Maxwell Hessian magnetic derivative, odd n1 versus even n0.

Includes electric, radial, spatial and shift curvature terms at each exported
history sample. Fixed background/metric except the explicitly applied magnetic
trace and its inherited coordinate-time motion. No quantum or complete
physical source/domain derivative is claimed.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np,json
from .integrated_source import (FieldJet,curvature_second,curvature_first,
    flatten_curvature,real_exact,zero_field,_basis_jet,point_linear_maps,
    probe_coefficients,save_npz,verify_input)

def weight_map40(a,d):
    e,r,da,k,sh=np.moveaxis(d,-1,0)
    X,T,Z,B=a[:,:4],a[:,4:16],a[:,16:28],a[:,28:40]
    y=T-sh[:,None,None]*Z
    return np.concatenate([k[:,None,None]*X,e[:,None,None]*y,
        -e[:,None,None]*sh[:,None,None]*y-r[:,None,None]*Z,-da[:,None,None]*B],axis=1)

def weight_map160(a,d):
    # Reshape harmonics into the last (column) axis for W to act on curvatures.
    r,_,n=a.shape
    x=a.reshape(r,40,4,n)
    return weight_map40(x.reshape(r,40,4*n),d).reshape(r,160,n)

def second_tensor():
    I=np.eye(20).reshape(20,5,4);z=np.zeros_like(I)
    u=FieldJet(I[:,None],z[:,None],z[:,None],np.zeros((20,1,3,5,4)))
    v=FieldJet(I[None],z[None],z[None],np.zeros((1,20,3,5,4)))
    return real_exact(flatten_curvature(curvature_second(u,v))).transpose(2,0,1)

def point_blocks(sample):
    L,Lr,Lt=point_linear_maps(sample['connection_value'])
    # FRAME's antisymmetric matrices have zero diagonal: remove the harmonic
    # factor to recover the independent n0 linear maps (checked separately).
    nr=len(L);N0=L.reshape(nr,40,4,20,4)[:,:,0,:,0]
    Nr=Lr.reshape(nr,40,4,20,4)[:,:,0,:,0]
    Nt=Lt.reshape(nr,40,4,20,4)[:,:,0,:,0]
    p=probe_coefficients(sample);b=sample['radial_basis'][:,3];br=sample['radial_derivative_basis'][:,3]
    w=p['W'].reshape(4,80,3)[3];wd=p['Wdot'].reshape(4,80,3)[3]
    P=b[:,None,None]*w;Pr=br[:,None,None]*w;Pt=b[:,None,None]*wd
    F=np.einsum('rij,rjk->rik',L,P)+np.einsum('rij,rjk->rik',Lr,Pr)+np.einsum('rij,rjk->rik',Lt,Pt)
    Fdot=np.einsum('rij,rjk->rik',Lt,P)
    C=second_tensor();d=sample['metric_densities']
    output=[]
    for k in range(3):
        # Q represents F''(probe, even value), resolved on every n1 harmonic.
        Q=np.einsum('iab,rah->rihb',C,P[:,:,k].reshape(nr,20,4),optimize=True)
        Q160=Q.reshape(nr,160,20)
        Q40=Q.transpose(0,1,3,2).reshape(nr,40,80)
        def t1(E): return np.matmul(Q40.swapaxes(1,2),weight_map40(E,d))
        def t2(O): return np.matmul(O.swapaxes(1,2),weight_map160(Q160,d))
        def t3(FF):
            wf=weight_map160(FF[:,:,None],d)[:,:,0].reshape(nr,40,4)
            return np.einsum('rih,iaj->rahj',wf,C,optimize=True).reshape(nr,80,20)
        output.append({'vv':t1(N0)+t2(L)+t3(F[:,:,k]),
            'vr':t1(Nr),'rv':t2(Lr),'vt':t1(Nt),'tv':t2(Lt),
            'bdot_vv':t3(Fdot[:,:,k])})
    return output

def integrate(sample,normalization):
    b,br=sample['radial_basis'],sample['radial_derivative_basis'];w=normalization*sample['radial_quadrature']
    def I(a,c,x):return np.einsum('r,rj,rk,rab->jakb',w,a,c,x,optimize=True).reshape(320,80)
    out={'b_vv':[],'b_vt':[],'b_tv':[],'bdot_vv':[]}
    for k in point_blocks(sample):
        out['b_vv'].append(I(b,b,k['vv'])+I(b,br,k['vr'])+I(br,b,k['rv']))
        out['b_vt'].append(I(b,b,k['vt']));out['b_tv'].append(I(b,b,k['tv']))
        out['bdot_vv'].append(I(b,b,k['bdot_vv']))
    return {k:np.array(v) for k,v in out.items()}

def run(inputs,output):
    root,out=Path(inputs),Path(output);out.mkdir(parents=True,exist_ok=False)
    md,val=verify_input(root);rows=[]
    for side in ('incoming','outgoing'):
        for label in ('lo','q000','q001','q002','q003','hi'):
            s=dict(np.load(root/side/(label+'.npz')));a=integrate(s,md['MAXWELL_TO_CAP'])
            save_npz(out/(side+'_'+label+'.npz'),a)
            row={'side':side,'label':label,'max_by_block':{k:float(np.max(abs(v))) for k,v in a.items()}}
            rows.append(row);print(row,flush=True)
    (out/'result.json').write_text(json.dumps({'classification':'RADIAL_MAXWELL_MAGNETIC_THIRD_VARIATION_N1_N0',
        'records':rows,'physical_total_derivative_admitted':False,'physical_response_executed':False},indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.inputs,a.output)
