"""One anchored HS history continuation prototype, using frozen point data.

Only third-action contractions on genuinely new connecting domains are run.
Each contraction is hash-addressed and atomically checkpointed. Subdivision
changes the history/integration cell, never the original physical radii.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, fmpq, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_mixed_eigenline_certificate as base
import bhsm.interface.shared_action_gradient as action_gradient
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.history_eigenbranch_variation import hermite_history, row_certificate


def atomic(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    pending=path.with_suffix('.pending');pending.write_bytes(base.encode(value));os.replace(pending,path)


def endpoint(evidence,index,receipt):
    result={}
    for kind,filename in (('.affine_eigenpair_pilot_work','eigenpair.npz'),
                          ('.coupled_normalized_physical_value_work','value.npz')):
        folder=evidence/f'artifacts/flagship_integration/{kind}/endpoint_{index:03d}'
        record=json.loads((folder/'record.json').read_bytes())
        repeat=json.loads((folder/'reproduction.json').read_bytes())
        expected={str((folder/'record.json').resolve()):repeat['record_SHA256'],
                  str((folder/filename).resolve()):record['data_SHA256']}
        if not repeat['byte_identical'] or not repeat['independent_recomputation'] or not record['report']['validation_passed']:
            raise ValueError('independently reproduced frozen endpoint required')
        for path,digest in expected.items():
            if path in receipt:
                if receipt[path]!=digest:raise ValueError('imported binding changed')
            elif base.sha(Path(path))!=digest:raise ValueError('frozen boundary hash mismatch')
            receipt[path]=digest
        for name in ('record.json','reproduction.json'):
            path=folder/name;receipt[str(path.resolve())]=base.sha(path)
        with np.load(folder/filename,allow_pickle=False) as z:
            if filename=='eigenpair.npz':
                trial=next(i for i,t in enumerate(record['report']['trials']) if t['validation_passed'])
                for k in ('center_state','affine_directions','eigenpair_center','preconditioner','center_defect','residual_bounds'):
                    result[k]=base.read_array(z,k)
                result['w']=base.read_array(z,f'trial_{trial}_radii')
                result['V']=base.read_array(z,f'trial_{trial}_variation_bounds')
                result['radii']=[record['radius_longitudinal_rational'],record['radius_transverse_rational']]
                result['selected_index']=record['report']['selected_zero_based_index_verified']
            else:
                result['rate']=base.read_array(z,'rate_candidate')[:98]
    return result


def operands(evidence,work):
    imported=work/'import_receipt.json'
    hashes=json.loads(imported.read_bytes()) if imported.exists() else {}
    left=endpoint(evidence,18,hashes);right=endpoint(evidence,19,hashes)
    if left['radii']!=right['radii'] or left['selected_index']!=24 or right['selected_index']!=24:
        raise ValueError('same physical radii and selected eigenline required')
    midpoint=evidence/'artifacts/flagship_integration/.coupled_hs_midpoint_domain_work/interval_018'
    mr=json.loads((midpoint/'record.json').read_bytes());mp=json.loads((midpoint/'reproduction.json').read_bytes())
    if not mr['actual_HS_midpoint_image_enclosed'] or not mr['uniform_endpoint_fields_independently_paired'] or not mp['byte_identical'] or not mp['independent_recomputation']:
        raise ValueError('owned reproduced actual HS midpoint domain required')
    for name,digest in (('record.json',mp['record_SHA256']),('domain.npz',mr['data_SHA256'])):
        path=midpoint/name;key=str(path.resolve())
        if key not in hashes and base.sha(path)!=digest:raise ValueError('midpoint boundary hash mismatch')
        if key in hashes and hashes[key]!=digest:raise ValueError('midpoint binding changed')
        hashes[key]=digest
    hashes[str((midpoint/'reproduction.json').resolve())]=base.sha(midpoint/'reproduction.json')
    for path,digest in list(hashes.items()):
        if '/endpoint_' in path.replace('\\','/') and path.endswith(('value.npz','eigenpair.npz')):
            relative=Path(path).relative_to(evidence).as_posix()
            if mr['binding']['files'].get(relative)!=digest:raise ValueError('HS domain and endpoint operands differ')
    statepath=base.action.ENDPOINT.with_suffix('.npz')
    with np.load(statepath,allow_pickle=False) as z:
        weights=[arb(float(v)) for v in z['state_weights']]
        reference=[arb(float(v)) for v in z['branch_reference']]
        step=arb(float(z['collocation_arc_parameters'][19]-z['collocation_arc_parameters'][18]))
    seedpath=ROOT/'artifacts/flagship_integration/gate7_uniform_action_20260923/scalar.json'
    seed=json.loads(seedpath.read_bytes())
    if {v for k,v in seed['source_SHA256'].items() if Path(k).name==Path(base.action.__file__).name}!={base.sha(Path(base.action.__file__))}:
        raise ValueError('retained action source changed')
    paths=(statepath,seedpath,Path(__file__),ROOT/'src/bhsm/interface/history_eigenbranch_variation.py',
           Path(action_gradient.__file__),ROOT/'src/bhsm/interface/factored_arb_integrand.py',
           ROOT/'src/bhsm/interface/shared_action_taylor.py',Path(base.__file__),
           ROOT/'src/bhsm/interface/affine_eigenpair_contraction.py',Path(base.action.__file__))
    hashes.update({str(p.resolve()):base.sha(p) for p in paths})
    if not imported.exists():atomic(imported,hashes)
    elif json.loads(imported.read_bytes())!=hashes:raise ValueError('prototype input hashes changed')
    groups=[(0,1,'interval'),(1,2,'interval'),(2,3,'interval'),(3,77,'euclidean'),
            (77,78,'interval'),(78,152,'euclidean'),(152,348,'box'),(348,409,'box')]
    d=TaylorDomain(groups,409)
    def variable(offset,constant,coefficient):
        a=[arb(0)]*409;a[offset]=coefficient;return d.affine(constant,a)
    rL,rT=[arb(fmpq(x)) for x in left['radii']]
    states=[];rates=[]
    for n,ep in enumerate((left,right)):
        values=[];fs=[]
        for i in range(98):
            co=[arb(0)]*409
            co[2+75*n:77+75*n]=[ep['affine_directions'][i,j]*(rL if j==0 else rT) for j in range(75)]
            values.append(d.affine(ep['center_state'][i],co))
            fs.append(variable(152+98*n+i,ep['rate'][i].mid()/weights[i],ep['rate'][i].rad()/weights[i]))
        states.append(values);rates.append(fs)
    eta=[d.affine(0)]*37+[variable(348+i,0,left['w'][i]) for i in range(61)]
    psi=[d.affine(0)]*37+[d.affine(v) for v in left['eigenpair_center'][:61]]
    return dict(left=left,right=right,domain=d,states=states,rates=rates,eta=eta,psi=psi,
                step=step,reference=reference,hashes=hashes,variable=variable)


def action_block(s,work,tau_cell,sigma_cell,kind):
    d=s['domain'];variable=s['variable']
    tau=variable(0,(tau_cell[0]+tau_cell[1])/2,(tau_cell[1]-tau_cell[0])/2)
    sigma=variable(1,(sigma_cell[0]+sigma_cell[1])/2,(sigma_cell[1]-sigma_cell[0])/2)
    curve=hermite_history(*s['states'],*s['rates'],s['step'],tau)
    dx=[v-c for v,c in zip(curve,s['left']['center_state'],strict=True)]
    state=[d.affine(c)+sigma*v for c,v in zip(s['left']['center_state'],dx,strict=True)]
    leg=s['psi'] if kind=='RESIDUAL' else s['eta']
    inputs=dict(tau=[str(x.fmpq()) for x in tau_cell],sigma=[str(x.fmpq()) for x in sigma_cell],
                kind=kind,source_SHA256=s['hashes'])
    key=base.digest(inputs);path=work/'blocks'/f'{key}.json'
    if path.exists():
        record=json.loads(path.read_bytes());receipt=json.loads(path.with_suffix('.receipt.json').read_bytes())
        if base.sha(path)!=receipt['payload_SHA256'] or record['inputs']!=inputs:raise ValueError('block receipt mismatch')
        print(json.dumps(dict(phase='REUSE_COMPLETED_SEGMENT_BLOCK',key=key)),flush=True)
    else:
        print(json.dumps(dict(phase='NEW_SEGMENT_THIRD_ACTION',key=key,**{k:inputs[k] for k in ('tau','sigma','kind')})),flush=True)
        inertia=[];original=action_gradient.factored_local_algebra
        def capture(*args):
            b,I=original(*args);j=len(inertia)
            inertia.append(float(base.action._BASIS[1][j])*I.value.d[0]);return b,I
        try:
            action_gradient.factored_local_algebra=capture
            values=action_gradient.gradient(base.action,state,[leg,dx],
                lambda done,total:print(json.dumps(dict(phase='SEGMENT_QUADRATURE',key=key[:10],completed=done,total=total)),flush=True))
            positive=sum(inertia,d.affine(0)).enclosure().lower()
            record=dict(inputs=inputs,models=[base.model(v) for v in values],
                        inertia_lower=base.number(positive),success=True)
        except ArithmeticError as error:
            record=dict(inputs=inputs,success=False,error=str(error),models=None,
                inertia_lower=base.number(sum(inertia,d.affine(0)).enclosure().lower()) if len(inertia)==96 else None)
        finally:action_gradient.factored_local_algebra=original
        atomic(path,record);atomic(path.with_suffix('.receipt.json'),dict(completed=True,payload_SHA256=base.sha(path),inputs_SHA256=key))
    if not record['success']:return None,dict(key=key,SHA256=base.sha(path),success=False,error=record['error'])
    # Both fresh and resumed contractions use the same outward saved-ball decoding.
    values=[base.unmodel(d,x) for x in record['models']]
    R=s['left']['preconditioner'];rows=[]
    for i in range(62):
        value=sum((R[i,j]*values[37+j] for j in range(61)),d.affine(0))
        co=value.a.entries();co[1]=arb(0)  # Exact integral of centered sigma parameter.
        rows.append(d.affine(value.c,co,value.r)*(sigma_cell[1]-sigma_cell[0]))
    return rows,dict(key=key,SHA256=base.sha(path),success=True,inertia_lower=record['inertia_lower'])


def serializable(value):
    if isinstance(value,arb):return dict(exact=str(value.fmpq()),approximate=float(value))
    if isinstance(value,dict):return {k:serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serializable(v) for v in value]
    return value


def run(evidence,work,out,subdivisions):
    ctx.prec=512;work.mkdir(parents=True,exist_ok=True);s=operands(evidence,work);ep=s['left'];segments=[]
    # Uniform tau and integration subdivision; no physical-domain reduction.
    for cell in range(subdivisions):
        tau=[arb(cell)/subdivisions,arb(cell+1)/subdivisions];totals={};receipts=[]
        for kind in ('RESIDUAL','HESSIAN'):
            total=[s['domain'].affine(0)]*62
            for j in range(subdivisions):
                sigma=[arb(j)/subdivisions,arb(j+1)/subdivisions]
                values,receipt=action_block(s,work,tau,sigma,kind);receipts.append(receipt)
                if values is None:break
                total=[a+b for a,b in zip(total,values,strict=True)]
            if values is None:break
            totals[kind]=[v.support() for v in total]
        if values is None:
            report=dict(validation_passed=False,status='ACTION_ENCLOSURE_FAILED',q_segment=None)
        else:
            report=row_certificate(ep['residual_bounds'],ep['center_defect'],ep['preconditioner'],ep['w'],
                totals['RESIDUAL'],totals['HESSIAN'],s['reference'],ep['eigenpair_center'])
            report['status']='PASS' if report['validation_passed'] else 'FAIL_TO_CERTIFY'
        segment=dict(anchor=18,history_interval=18,tau=[str(x.fmpq()) for x in tau],
            q0_upper=max((v/w).upper() for v,w in zip(ep['V'],ep['w'],strict=True)),
            action_blocks=receipts,**report)
        atomic(work/f'segment_n{subdivisions}_{cell}.json',serializable(segment));segments.append(segment)
    valid=all(v['validation_passed'] for v in segments)
    result=dict(algorithm='BHSM_N12_GATE7_PRECONDITIONED_HESSIAN_HISTORY_VARIATION',
        anchor_index=18,history_range=[18,19],history_subdivisions=subdivisions,integration_subdivisions=subdivisions,
        domain_definition='Cubic Hermite history of both frozen original affine endpoint tubes and frozen uniform physical endpoint rates; exact actual HS midpoint at tau=1/2. MVT integration state x18+sigma*(history(tau)-x18).',
        owned_HS_midpoint_domain_reused=True,owned_HS_domain_interval=18,
        state_parameters=150,auxiliary_rate_error_parameters=196,history_and_integration_parameters=2,operator_test_parameters=61,
        independent_spherical_domain_substituted=False,original_physical_radii=ep['radii'],physical_domain_shrunk=False,
        frozen_rate_enclosure_limitation='Inherited uniform rate balls are auxiliary component errors; unknown additional endpoint-rate correlations are not asserted.',
        third_action_structure='Affine local maps have zero higher derivatives. Quadratic gravity prefactors have zero third derivative before their exponential product; polynomial ADM and xeta powers retain sparse product derivatives. Bulk exponentials, global inertia reciprocal and boundary square root use analytic jets and positive interval denominators.',
        bordered_variation='Saved point defect + integrated R0 DeltaH box action + exact existing quadratic eigenpair/normalization border; not q0 plus a duplicate local-domain defect.',
        point_residual_bound='Inherited residual_bounds safely bounds the point residual; its old local state allowance is retained conservatively.',
        selected_eigenline_index=24,selected_eigenline_continuation_certified=valid,
        identity_argument='Uniform Banach self-inclusion in a witness containing the frozen anchor, nonsingular bordered derivative, positive original-reference overlap and connected domain.' if valid else None,
        segments=segments,validation_passed=valid,covered_history_intervals=[18] if valid else [],
        total_certified_connecting_intervals=1 if valid else 0,total_history_intervals=370,
        new_anchor_evaluations=0,point_hessians_recomputed=False,endpoint19_prototype_recomputed=False,
        source_SHA256=s['hashes'],Gate7_closed=False,kappa_L=None,kappa_T=None,new_physical_budget_debit=False)
    atomic(out,serializable(result))
    print(json.dumps(dict(validation_passed=valid,segments=[dict(tau=x['tau'],status=x['status'],
        contraction_upper=float(x['contraction_upper']) if 'contraction_upper' in x else None) for x in segments])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--subdivisions',type=int,default=1,choices=(1,2,4))
    a=p.parse_args();run(a.evidence_root.resolve(),a.work.resolve(),a.out.resolve(),a.subdivisions)
