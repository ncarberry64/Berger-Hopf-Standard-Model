"""Complete anchor adjoint for the interval-14 local midpoint scalar."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def evaluate(root,operands,predictors,direction,out):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,arb_mat,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(ROOT/'src/bhsm/interface'))
    from bhsm.interface import coupled_action_output_adjoint as adjoint
    from bhsm.interface import prescribed_arb_action_jet as prescribed
    from bhsm.interface import sparse_arb_mixed_jets as sparse
    from bhsm.interface import ball_factored_arb_integrand as factored
    import bhsm_immutable_input_hash_cache as hashes
    ctx.prec=512;p=engine.p;cert=p.values.cert;r=p.geometry.residual
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    def matrix(a):return arb_mat(*a.shape,list(a.flat))
    def load(folder,name):
        record=json.loads((folder/'record.json').read_bytes())
        if sha(folder/name)!=record['data_SHA256']:raise ValueError('Matching operand bytes required')
        with np.load(folder/name,allow_pickle=False) as z:
            return record,{k[:-6]:p.hs.restore_balls(z[k],z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
    with hashes.cache_hashes([(p.values,'sha'),(r.center,'_sha'),(r.foundation.coordinate.center,'_sha')]):
        ore,a=load(operands,'operands.npz');pre,s=load(predictors,'predictors.npz')
        if pre['stage']!='midpoint' or pre['interval']!=14:raise ValueError('Midpoint 14 only')
        p.verify_sources(ore['binding'])
        old=json.loads(direction.read_bytes())
        if old['stage']!='midpoint' or any(sha(Path(path))!=digest for path,digest in old['input_source_SHA256'].items()):
            raise ValueError('Complete original midpoint directional enclosure required')
        eigen=root/'artifacts/flagship_integration/.coupled_midpoint_eigenpair_pilot_work/interval_014/eigenpair.npz'
        with np.load(eigen,allow_pickle=False) as z:
            D=matrix(p.hs.restore_balls(z['center_defect_mid_q'],z['center_defect_rad_q']))
        R=matrix(a['paired_rm']);K=R.solve(arb_mat(np.eye(62,dtype=int).tolist())-D)
        lam0=a['paired_eigen_center'][61]
        H=arb_mat(61,61,[K[i,j]+(lam0 if i==j else 0) for i in range(61) for j in range(61)])
        ep=[arb(v).mid() for v in pre['point_checks'][0]['target_midpoints_rational']]
        centers=ep+[v.mid() for i in range(3) for v in s[f'point_solve_{i}'][:,0]]
        _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
        weights,qw,rw=[[arb(float(v)) for v in values] for values in (weights,qw,rw)]
        x=s['center_state'];axis=s['weighted_input_axis'];u=np.array([axis[i]/weights[i] for i in range(98)],dtype=object)
        maps=[cert._dense_mapping(cert._integrand(x,node,0).maps) for node in range(cert.POINTS)]
        basis=np.array([[arb(i==37+j) for j in range(61)] for i in range(98)],dtype=object)
        cache={};calls=[]
        def encoded_leg(leg):
            v=np.asarray(leg,dtype=object)
            return p.geometry.encoded(dict(shape=list(v.shape),values=[[str(a.mid().fmpq()),str(a.rad().fmpq())] for a in v.flat]))
        def contraction(*legs):
            key=tuple(hashlib.sha256(encoded_leg(v)).hexdigest() for v in legs)
            if key not in cache:
                with sparse.use_optimized_mixed(cert),factored.use_ball_factored_integrand(cert,x):
                    cache[key]=prescribed.affine_action_contraction(cert,x,maps,*legs)
                calls.append(dict(order=len(legs),shape=list(cache[key].shape)))
                print(json.dumps(dict(anchor_contraction=len(calls),**calls[-1])),flush=True)
            return cache[key]
        Hu=matrix(contraction(basis,basis,u).reshape(61,61))
        configuration=[qw[i]*x[37+i] for i in range(37)]
        configuration_u=[qw[i]*u[37+i] for i in range(37)]
        constant=lambda v:adjoint.FirstJet(arb(v),arb_mat(1,248))
        def action_jet(*legs):
            values=[np.array([v.c for v in leg],dtype=object) for leg in legs]
            value=contraction(*values).reshape(-1)[0];derivative=arb_mat(1,248)
            for i,leg in enumerate(legs):
                if any(not v.a[0,j].is_zero() for v in leg[:37] for j in range(248)):
                    raise ValueError('State fixed for unknown adjoint')
                variation=arb_mat(61,248,[v for entry in leg[37:] for v in entry.a.entries()])
                if all(v.is_zero() for v in variation.entries()):continue
                other=values[:i]+values[i+1:]
                other.sort(key=lambda arr:hashlib.sha256(encoded_leg(arr)).hexdigest())
                free=contraction(basis,*other).reshape(61)
                derivative += arb_mat(1,61,list(free))*variation
            return adjoint.FirstJet(value,derivative)
        def descriptor(pj,hj,puj,huj):
            pad=lambda v:[constant(0)]*37+v
            scale=lambda v:[rw[i]/weights[37+i]*v[i] for i in range(61)]
            pp,pu=pad(pj),pad(puj);aa,au=pad(scale(pj)),pad(scale(puj))
            dd=[constant(configuration[i]/weights[i]) for i in range(37)]+scale(hj)
            du=[constant(configuration_u[i]/weights[i]) for i in range(37)]+scale(huj)
            uu=[constant(v) for v in u]
            return (action_jet(pp,pp,aa),action_jet(pp,pp,dd),
                action_jet(pp,pp,aa,uu)+2*action_jet(pp,pu,aa)+action_jet(pp,pp,au),
                action_jet(pp,pp,dd,uu)+2*action_jet(pp,pu,dd)+action_jet(pp,pp,du))
        tangent_path=r.center.JACOBIAN.with_suffix('.npz');frozen_path=r.center.PRECONDITIONER.with_suffix('.npz')
        with np.load(tangent_path,allow_pickle=False) as z:tangent=z['endpoint_physical_tangent_action'][15]
        with np.load(frozen_path,allow_pickle=False) as z:frozen=z['reduced_right_Newton_blocks'][14]
        test=r.center.cert._frame(tangent,r.center.cert.TEST_DESCRIPTOR_SCALE).T
        P=arb_mat(frozen.tolist()).solve(arb_mat(test.tolist()))
        h=arb(float(p.values.operands()[-1][14]))
        output=[P[73,i]*(2*h/3) for i in range(99)]
        J,gradient,value=adjoint.linearize(H,Hu,configuration,configuration_u,rw,s['point_descriptor'][0],axis[98],
            output,centers,descriptor)
        beta,defect=adjoint.adjoint_proposal(J,gradient)
        paths=[operands/'record.json',operands/'operands.npz',predictors/'record.json',predictors/'predictors.npz',
               direction,eigen,tangent_path,frozen_path,Path(__file__),Path(cert.__file__),Path(adjoint.__file__),Path(prescribed.__file__),Path(factored.__file__)]
        result=dict(algorithm='INTERVAL14_MIDPOINT_LOCAL_SCALAR_COMPLETE_ANCHOR_ADJOINT_V1',interval=14,stage='midpoint',
            output_coordinate=73,input_coordinate=14,unknowns=248,
            output_formula='(2*h/3) e73^T P DF(midpoint) (u/2-h*DF(endpoint)*u/8)',
            output_covector=[[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in output],
            exact_covectors={name:[str(beta[0,62*k+j].fmpq()) for j in range(62)]
                for k,name in enumerate(('eigenline','response','axis_line','axis_response'))},
            maximum_anchor_adjoint_defect_exact=str(max(abs(v).upper() for v in defect.entries()).fmpq()),
            anchor_output=[str(value.mid().fmpq()),str(value.rad().fmpq())],action_contractions=calls,
            original_action_Hessian_reused=True,full_output_normalization_differentiated=True,
            uniform_remainder_certified=False,interval13_recomputed=False,Gate7_closed=False,
            input_source_SHA256={str(path.resolve()):sha(path) for path in paths})
        with out.open('xb') as stream:stream.write(p.geometry.encoded(result))
        print(json.dumps(dict(completed=True,anchor_adjoint_defect=float(max(abs(v).upper() for v in defect.entries())))),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','operands','predictors','direction','out'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();evaluate(args.evidence_root.resolve(),args.operands.resolve(),args.predictors.resolve(),args.direction.resolve(),args.out.resolve())
