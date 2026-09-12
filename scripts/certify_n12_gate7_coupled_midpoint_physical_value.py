"""Enclose the actual HS midpoint field using its paired grouped eigenpair."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_coupled_midpoint_eigenpair_pilot as eq
from bhsm.interface import affine_hs_midpoint_domain as grouped
from bhsm.interface import coupled_physical_normalization as normalization
from bhsm.interface import weighted_response_enclosure as response_bounds
from bhsm.interface import affine_response_residual as response_legs

p=eq.p
WORK=ROOT/'artifacts/flagship_integration/.coupled_midpoint_physical_value_work'
THEORY=ROOT/'theory/n12_gate7_coupled_midpoint_physical_value.md'
ALGORITHM='SIGNED_ACTUAL_HS_MIDPOINT_PHYSICAL_VALUE_ARB512_V1'


def load_inputs(index):
    ctx.prec=512
    source=eq.load_inputs(index)
    directory=eq.WORK/f'interval_{index:03d}'
    record_path=directory/'record.json';data_path=directory/'eigenpair.npz';receipt_path=directory/'reproduction.json'
    record=json.loads(record_path.read_bytes());receipt=json.loads(receipt_path.read_bytes())
    if (record.get('binding')!=source['binding'] or record.get('interval')!=index
            or record.get('algorithm')!=eq.ALGORITHM
            or record.get('report',{}).get('validation_passed') is not True
            or record['report'].get('selected_zero_based_index_verified')!=24
            or record['report'].get('uniform_action_eigenpair_enclosed') is not True
            or record['report'].get('uniform_actual_HS_midpoint_eigenpair_enclosed') is not True
            or record_path.read_bytes()!=p.geometry.encoded(record)
            or record.get('data_SHA256')!=p.values.sha(data_path)
            or receipt.get('record_SHA256')!=p.values.sha(record_path)
            or receipt.get('byte_identical') is not True
            or receipt.get('independent_recomputation') is not True):
        raise RuntimeError('paired unchanged affine index-24 eigenpair evidence required')
    with np.load(data_path,allow_pickle=False) as a:
        def read(name):return p.hs.restore_balls(a[name+'_mid_q'],a[name+'_rad_q'])
        eigenbox=read('eigenpair_box');center=read('center_state');rm=read('preconditioner')
        eigen_center=read('eigenpair_center');directions=read('affine_directions')
        trial=len(record['report']['trials'])-1
        radii=read(f'trial_{trial}_radii');variation=read(f'trial_{trial}_variation_bounds')
        full=read('raw_segment_hull')
    domain_path=eq.midpoint.WORK/f'interval_{index:03d}'/'domain.npz'
    with np.load(domain_path,allow_pickle=False) as a:
        source['raw_center']=p.hs.restore_balls(a['raw_center_mid_q'],a['raw_center_rad_q'])
        source['raw_domain']=p.hs.restore_balls(a['raw_segment_hull_mid_q'],a['raw_segment_hull_rad_q'])
    if (source['raw_center'].shape!=(99,) or source['raw_domain'].shape!=(99,)
            or not all(v.is_finite() for key in ('raw_center','raw_domain') for v in source[key])
            or not all(v.rad().is_zero() for v in source['raw_center'])):
        raise ArithmeticError('complete exact actual midpoint center and finite hull required')
    if any(not a.contains(b) or not b.contains(a) for a,b in zip(center,source['raw_center'][:98],strict=True)):
        raise ArithmeticError('paired eigenpair anchor and actual midpoint center differ')
    source['paired']=dict(eigenbox=eigenbox,center=center,rm=rm,eigen_center=eigen_center,
        directions=directions,radii=radii,variation=variation,full=full)
    shapes=dict(eigenbox=(62,),center=(98,),rm=(62,62),eigen_center=(62,),
                directions=(98,249),radii=(62,),variation=(62,),full=(98,))
    if any(a.shape!=shapes[key] or not all(v.is_finite() for v in a.flat)
           for key,a in source['paired'].items()):
        raise ArithmeticError('complete finite paired eigenpair arrays required')
    if not all(v.rad().is_zero() for a in (center,rm,eigen_center) for v in a.flat):
        raise ArithmeticError('fixed exact eigenpair centers and preconditioner required')
    for path in (record_path,data_path,receipt_path,Path(__file__),THEORY,
                 Path(response_bounds.__file__),Path(response_legs.__file__),
                 Path(grouped.__file__),Path(normalization.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(path):p.values.sha(path)})
    source['binding']['algorithm']=ALGORITHM
    p.verify_sources(source['binding'])
    return source


def signed_response_derivatives(cert,full,legs,directions,maps,progress=None):
    count=directions.shape[1]
    derivative=np.empty((62,count),dtype=object)
    for start in range(0,62,4):
        stop=min(start+4,62)
        g=legs['gradient_left'][:,start:stop,None]
        a=legs['configuration_left'][:,start:stop,None]
        c=legs['hessian_left'][:,start:stop,None]
        v=directions[:,None,:]
        tile=cert._contracted_action(full,[g,v],maps)
        tile-=cert._contracted_action(full,[a,legs['configuration'][:,None,None],v],maps)
        tile-=cert._contracted_action(full,[a,legs['configuration_derivative'][:,None,:]],maps)
        tile-=cert._contracted_action(full,[c,legs['hard'][:,None,None],v],maps)
        tile=np.asarray(tile,dtype=object)
        if tile.shape!=(stop-start,count) or not all(isinstance(t,arb) and t.is_finite() for t in tile.flat):
            raise ArithmeticError('complete finite signed physical response derivatives required')
        derivative[start:stop]=tile
        if progress:progress(stop)
    return derivative


def evaluate(source):
    ctx.prec=512
    cert=p.values.cert;index=source['index']
    eigenbox,center,rm,eigen_center,directions,radii,variation,full=[source['paired'][key] for key in
        ('eigenbox','center','rm','eigen_center','directions','radii','variation','full')]
    R=arb_mat(62,62,list(rm.flat))
    states,weights,descriptors,reference,_=p.values.operands()
    original_solve=cert._verified_solve;original_eigenline=cert._eigenline
    arrays={};report={};point_response=[];point_operands=[]


    def point_solve(matrix,rhs):
        point_operands.append((cert._arb_action_jets(center),rhs))
        result=original_solve(matrix,rhs)
        point_response.append(np.array([v.mid() for v in result.entries()],dtype=object))
        return result


    def uniform_solve(matrix,rhs):
        if (matrix.nrows()!=62 or matrix.ncols()!=62 or rhs.nrows()!=62 or rhs.ncols()!=1
                or len(point_response)!=1 or len(point_operands)!=1 or 'response_box' in arrays):
            raise ArithmeticError('one retained bordered physical response solve required')
        x0=point_response[0]
        # K=J*diag(I,-1), so z0=diag(I,-1)*x0 and the existing RJ bound applies.
        jets,center_rhs=point_operands[0]
        H0=arb_mat(61,61,list(jets.hessian_arb[37:,37:].flat))
        K0=arb_mat(62,62)
        for i in range(61):
            for j in range(61):K0[i,j]=H0[i,j]-(eigen_center[-1] if i==j else 0)
            K0[i,61]=eigen_center[i];K0[61,i]=eigen_center[i]
        center_residual=R*(center_rhs-K0*arb_mat(62,1,list(x0)))
        qw,rw,_,_=cert.metric_data()
        legs=response_legs.response_legs(full,rm,x0[:61],qw,rw,weights,directions)
        derivative=signed_response_derivatives(cert,full,legs,directions,jets.dense_maps,
            lambda rows:print(json.dumps(dict(phase='SIGNED_RESPONSE_RESIDUAL',rows=rows,total=62)),flush=True))
        state_bound=grouped.group_row_bounds(derivative,source['groups'])
        eigen_bound=response_legs.eigenpair_variation(rm,x0[:61],x0[-1],radii)
        absolute=np.array([(abs(center_residual[i,0]).upper()+state_bound[i]+eigen_bound[i]).upper() for i in range(62)],dtype=object)
        residual=arb_mat(62,1,[arb(0,v) for v in absolute])
        arrays.update(signed_response_derivatives=derivative,response_state_bounds=state_bound,
            response_eigenpair_bounds=eigen_bound,response_absolute_residual=absolute,
            response_center_residual=np.array(center_residual.entries(),dtype=object))
        z0=x0.copy();z0[-1]=-z0[-1]
        z,proof=response_bounds.enclose_response(z0,residual.entries(),radii,variation)
        z[-1]=-z[-1]
        arrays.update(response_center=x0,preconditioned_response_residual=np.array(residual.entries(),dtype=object),response_box=z)
        report['response_bound']=proof
        return arb_mat(62,1,list(z))


    try:
        cert._verified_solve=point_solve
        checks=[]
        with p.df.sparse.use_optimized_mixed(cert),eq.engine.affine.factored.use_ball_factored_integrand(cert,center):
            with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
                point=cert._rate_enclosure(center,source['raw_center'][98],weights,reference,None)
        if len(checks)!=1 or not p.proof_valid(checks[0]) or len(point_response)!=1:
            raise ArithmeticError('verified point response and eigenpair required')
        arrays['point_rate']=point.value
        cert._verified_solve=uniform_solve
        # Zero is only a conservative unused gap diagnostic, not a claimed gap proof.
        cert._eigenline=lambda *args:(eigenbox[:61],eigenbox[-1],arb(0),arb(0))
        raw_domain=source['raw_domain']
        with p.df.sparse.use_optimized_mixed(cert),eq.engine.affine.factored.use_ball_factored_integrand(cert,full):
            result=cert._rate_enclosure(full,raw_domain[98],weights,reference,None)
        arrays['rate_candidate']=result.value
        report['finite_rate_candidate']=all(isinstance(v,arb) and v.is_finite() for v in result.value)
        report['center_overlap']=all(a.overlaps(b) for a,b in zip(result.value,point.value,strict=True))
    except Exception as error:
        report['error']=repr(error)
    finally:
        cert._verified_solve=original_solve;cert._eigenline=original_eigenline
    p.verify_sources(source['binding'])
    if 'response_box' in arrays:
        qw,rw,_,_=cert.metric_data()
        configuration=[arb(float(qw[i]))*full[37+i] for i in range(37)]
        hard=arrays['response_box'][:61];border=arrays['response_box'][-1]
        descriptor=source['raw_domain'][98]
        G=np.array([descriptor*v for v in configuration]+[
            arb(float(rw[i]))*(border*eigenbox[i]+descriptor*hard[i]) for i in range(61)],dtype=object)
        squared=sum((v*v for v in G),arb(0))
        norm=squared.sqrt()
        arrays['physical_G']=G
        if norm.is_finite():
            arrays['physical_G_norm']=np.array([norm],dtype=object)
            report['physical_G_norm_lower_rational']=str(norm.lower().fmpq())
        report['positive_physical_G_norm']=bool(norm.is_finite() and norm>0)
    if report.get('positive_physical_G_norm') and 'error' not in report:
        try:
            rw=np.array([arb(float(v)) for v in rw],dtype=object)
            w=np.array([arb(float(v)) for v in weights],dtype=object)
            configuration=np.array(configuration,dtype=object)
            psi=eigenbox[:61]
            pfull=np.concatenate((np.full(37,arb(0)),psi))
            psi_action=np.concatenate((np.full(37,arb(0)),rw*psi))
            hard_action=np.concatenate((configuration,rw*hard))
            da_dh=np.stack((psi_action/w,hard_action/w),axis=1)[:,None,:]
            with p.df.sparse.use_optimized_mixed(cert),eq.engine.affine.factored.use_ball_factored_integrand(cert,full):
                jets=cert._arb_action_jets(full)
                cr=np.asarray(cert._contracted_action(full,[pfull[:,None,None],pfull[:,None,None],da_dh],jets.dense_maps),dtype=object).reshape(2)
            value,proof=normalization.normalized_value(configuration,rw,psi,hard,border,descriptor,*cr,
                normalized_eigenpair=True,bordered_orthogonality=True)
            if not all(a.overlaps(b) for a,b in zip(value,arrays['rate_candidate'],strict=True)):
                raise ArithmeticError('coupled and original midpoint fields disagree')
            arrays['original_rate_candidate']=arrays['rate_candidate']
            arrays['rate_candidate']=value
            arrays['complete_descriptor_contractions']=cr
            report['coupled_normalization']=proof
            report['normalized_mode_and_response_orthogonality_from_paired_systems']=True
        except Exception as error:
            report['error']=repr(error)
    report['validation_passed']=bool(arrays.get('rate_candidate',np.empty(0)).shape==(99,)
        and report.get('finite_rate_candidate') and report.get('center_overlap')
        and report.get('positive_physical_G_norm')
        and report.get('normalized_mode_and_response_orthogonality_from_paired_systems')
        and 'error' not in report)
    report.update(uniform_physical_value_enclosed=report['validation_passed'],
        scope='ACTUAL_HS_MIDPOINT_OUTER_DOMAIN',actual_HS_midpoint_domain_enclosed=True,
        uniform_actual_HS_midpoint_field_enclosed=report['validation_passed'],
        uniform_physical_derivatives_enclosed=False,physical_quotient_identified=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    arrays['raw_domain']=source['raw_domain']
    p.verify_sources(source['binding'])
    return arrays,report


def main():
    import argparse
    import time
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval',type=int,default=13)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--recompute',action='store_true')
    args=parser.parse_args();source=load_inputs(args.interval)
    if args.preflight:
        print(json.dumps(dict(inputs_verified=True,numerical_evaluation=False)));return
    directory=WORK/f'interval_{args.interval:03d}';directory.mkdir(parents=True,exist_ok=True)
    data=directory/'value.npz';record_path=directory/'record.json';receipt=directory/'reproduction.json'
    previous=json.loads(record_path.read_bytes()) if record_path.exists() else None
    if args.recompute!=(previous is not None):
        raise RuntimeError('first run requires no record; repeat requires existing record')
    if previous is not None and (previous['data_SHA256']!=p.values.sha(data)
            or record_path.read_bytes()!=p.geometry.encoded(previous)):
        raise RuntimeError('prior physical value evidence changed')
    if receipt.exists():receipt.replace(directory/f'reproduction.before_attempt_{time.time_ns()}.json')
    candidate=directory/f'value.candidate_{time.time_ns()}.npz'
    attempted=dict(binding=source['binding'],interval=args.interval,FULL_BHSM_COMPLETE=False)
    candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted))
    try:
        arrays,report=evaluate(source)
    except Exception as error:
        attempted['error']=repr(error)
        candidate.with_suffix('.json').write_bytes(p.geometry.encoded(attempted));raise
    encoded={}
    for name,array in arrays.items():
        if all(isinstance(v,arb) and v.is_finite() for v in array.flat):
            encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(array)
        else:report[name+'_contains_nonfinite']=True
    np.savez_compressed(candidate,**encoded)
    record=dict(algorithm=ALGORITHM,binding=source['binding'],interval=args.interval,
        data_SHA256=p.values.sha(candidate),report=report,
        groups=[dict(start=g['start'],stop=g['stop'],norm=g['norm'],radius_rational=str(g['radius'].fmpq())) for g in source['groups']],FULL_BHSM_COMPLETE=False)
    candidate_record=candidate.with_suffix('.json');candidate_record.write_bytes(p.geometry.encoded(record))
    if not report['validation_passed']:
        raise ArithmeticError('uniform affine physical value failed; candidate preserved')
    if previous is not None:
        if record_path.read_bytes()!=candidate_record.read_bytes():
            raise ArithmeticError('independent affine physical value differs; candidates preserved')
        candidate.unlink();candidate_record.unlink()
        receipt.write_bytes(p.geometry.encoded(dict(independent_recomputation=True,byte_identical=True,
            record_SHA256=p.values.sha(record_path),actual_HS_midpoint_domain_enclosed=True,FULL_BHSM_COMPLETE=False)))
    else:
        candidate.replace(data);candidate_record.replace(record_path)
    print(json.dumps(dict(interval=args.interval,reproduced=args.recompute,validation_passed=True,FULL_BHSM_COMPLETE=False)),flush=True)


if __name__=='__main__':main()
