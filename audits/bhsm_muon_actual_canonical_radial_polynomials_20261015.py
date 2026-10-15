"""Recover actual z and full336 polynomials from retained MP shifted outputs.

This is algebraic re-expression, no ODE/source/D5 integration or physical
outgoing completion. The failed shifted-chart comparison remains recorded.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import sys
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from flint import acb,acb_mat,arb,ctx


def run(repository,base,output):
    root,base,out=map(lambda p:Path(p).resolve(),(repository,base,output));out.mkdir(parents=True,exist_ok=False)
    sys.path[:0]=[str(root/'src'),str(root/'audits')]
    from bhsm_exact_action_balls import parse_acb_exact_dyadic
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    ctx.prec=256;pins={};values={};packet={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def mat(a):return acb_mat([[acb(arb(float(v.real)),arb(float(v.imag)))for v in row]for row in a])
    def sub(a,rows,cols):return acb_mat([[a[i,j]for j in cols]for i in rows])
    def stack(a,b):return acb_mat([[a[i,j]for j in range(a.ncols())]for i in range(a.nrows())]+[[b[i,j]for j in range(b.ncols())]for i in range(b.nrows())])
    def horizontal(a,b):return acb_mat([[a[i,j]if j<a.ncols()else b[i,j-a.ncols()]for j in range(a.ncols()+b.ncols())]for i in range(a.nrows())])
    def mid(a):return np.array([[complex(a[i,j].real.mid(),a[i,j].imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
    for order in (128,192):
        stages=[]
        for j in range(2):
            rr=read(base/f'order{order}_reduced_run_1/stage_{j:04d}_original_reduced_operator_and_polynomial_source_maps.npz')
            parse=lambda k:parse_acb_exact_dyadic(rr,k+'_exact')
            Mr,Fr,Rr=[parse(k)for k in ('Mr','Fr','Rr')];inv=Mr.inv()
            gp0,gp1,gf1=[parse(k)for k in ('Gp0','Gp1','Gf1')]
            top1=-inv*gp1;B1=stack(top1,gf1+Fr*top1)
            U,V,ag0,ag1=[parse(k)for k in ('original_Gauss_position_map','original_Gauss_velocity_map','Gauss_wall_value_map','Gauss_wall_rate_map')]
            S,L=mat(rr['interior_field_lift']),mat(rr['named_wall_lift'])
            Sa,Sd=sub(S,range(336),range(48)),sub(S,range(336),range(48,244))
            FS=horizontal(Sd-Sa*U+Sa*V*inv*Rr,-Sa*V*inv)
            FQ=L+Sa*(V*inv*gp0-ag0);FT=Sa*(V*inv*gp1-ag1)
            stages.append(dict(B1=B1,FS=FS,FQ=FQ,FT=FT))
        pieces=[]
        for piece in range(3):
            p=base/f'order{order}_field_run_1/piece_{piece:03d}_certified_canonical_polynomial_and_source.npz'
            a=read(p);w=read(base/f'order{order}_field_run_1/piece_{piece:03d}_certified_wall96_polynomial.npz')
            ckeys=sorted(k.rsplit('_real_mid_mantissa',1)[0]for k in a if k.startswith('canonical_shifted_coefficient_')and k.endswith('_real_mid_mantissa'))
            qkeys=sorted(k.rsplit('_real_mid_mantissa',1)[0]for k in a if k.startswith('actual_source_coefficient_')and k.endswith('_real_mid_mantissa'))
            c=[parse_acb_exact_dyadic(a,k)for k in ckeys];Q=[parse_acb_exact_dyadic(a,k)for k in qkeys]
            r=stages[int(w['stage'])];duration=acb(complex(w['coordinate_bounds'][1]-w['coordinate_bounds'][0]))
            zero=acb_mat(80,3);z=[];f=[]
            for n,cn in enumerate(c):
                q=Q[n]if n<len(Q)else zero;qt=Q[n+1]*(n+1)/duration if n+1<len(Q)else zero
                zn=cn+r['B1']*q;fn=r['FS']*zn+r['FQ']*q+r['FT']*qt
                z.append(zn);f.append(fn)
            pieces.append(dict(z=z,field=f,bounds=w['coordinate_bounds'],sigma=w['sigma_bounds'],stage=int(w['stage'])))
            for name,seq in (('canonical_z',z),('original_field336',f)):
                high=np.array([mid(v)for v in seq]);low=np.array([mid(v-mat(h))for v,h in zip(seq,high)])
                packet[f'order{order}_piece{piece}_{name}_high']=high;packet[f'order{order}_piece{piece}_{name}_low']=low
        values[order]=pieces
    comparisons=[]
    for piece,(a,b)in enumerate(zip(values[128],values[192])):
        if not np.array_equal(a['bounds'],b['bounds'])or not np.array_equal(a['sigma'],b['sigma'])or a['stage']!=b['stage']:raise ValueError('Different piece domains')
        metrics={}
        for name in ('z','field'):
            if len(a[name])!=len(b[name]):raise ValueError('Different polynomial degree; full union required')
            left=np.array([mid(v)for v in a[name]]);right=np.array([mid(v)for v in b[name]])
            delta=np.array([mid(y-x)for x,y in zip(a[name],b[name])])
            metrics[name]=dict(coefficient_stack_relative=float(np.linalg.norm(delta)/max(np.linalg.norm(left),np.linalg.norm(right))),
                coefficient_difference_max=float(np.max(abs(delta))),
                coefficient_triangle_coordinate_norm_estimate=float(sum(np.linalg.norm(d)for d in delta)),
                finer_coefficient_norm=float(np.linalg.norm(right)))
        comparisons.append(dict(piece=piece,stage=a['stage'],metrics=metrics))
    old=read(base/'binding_run_1.json')
    for p,h in pins.items():
        if sha256(Path(p).read_bytes()).hexdigest()!=h:raise ValueError('Input changed during algebraic reconstruction')
    _compressed_npz(out/'actual_canonical_and_original336_polynomials.npz',packet)
    result=dict(classification='ACTUAL_CANONICAL_AND_ORIGINAL336_POLYNOMIAL_RADIAL_QUADRATURE_COMPARISON',comparisons=comparisons,
        max_actual_z_polynomial_coefficient_relative=max(p['metrics']['z']['coefficient_stack_relative']for p in comparisons),
        max_actual_full336_polynomial_coefficient_relative=max(p['metrics']['field']['coefficient_stack_relative']for p in comparisons),
        retained_failed_shifted_w_comparison=old['observed128_to192_all_reported_field_rate_canonical_relative_max'],
        broad_all_reported_criterion_from_prior_binding_pass=old['observed_finite_relative_stabilization_pass'],
        prior_binding_sha256=sha256((base/'binding_run_1.json').read_bytes()).hexdigest(),
        reconstruction='z_n=w_n+B1*Q_n; F_n=FS*z_n+FQ*Q_n+FT*(n+1)*Q_(n+1)/duration; MP256 before midpoint comparison',
        new_integrations_or_matching_corrections_applied=0,
        comparison_is_floating_midpoint_diagnostic_not_outward_continuum_error_bound=True,
        physical_outgoing_derivative_or_radial_Galerkin_convergence_passed=False,
        physical_two_spin_normalization=None,physical_muon_magnetic_moment=None,
        input_hashes=pins,producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        packet_sha256=sha256((out/'actual_canonical_and_original336_polynomials.npz').read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),comparisons=comparisons)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--base',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.base,a.output)
