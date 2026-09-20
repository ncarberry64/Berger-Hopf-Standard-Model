"""Assemble the single shared interval-14 entry and its frozen transport cost.

No ledger debit is made here. Independent reproduction is a separate gate.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def evaluate(root,endpoint_path,midpoint_path,budget_path,jet_path,out,midpoint_scalar_path=None):
    sys.path[:0]=[str(root/'scripts'),str(root/'src')]
    import numpy as np
    from flint import arb,arb_mat,ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm_immutable_input_hash_cache as cache
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(ROOT/'src/bhsm/interface'))
    from bhsm.interface.shared_action_taylor import Taylor,TaylorDomain
    ctx.prec=512;p=engine.p;residual=p.geometry.residual
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    sources={str(path.resolve()):sha(path) for path in
             (endpoint_path,midpoint_path,budget_path,jet_path,Path(__file__))}
    # Bind the actual loaded arithmetic implementation, never an inferred path.
    sources[str(Path(sys.modules[Taylor.__module__].__file__).resolve())]=sha(Path(sys.modules[Taylor.__module__].__file__))
    def read(path):
        sources[str(path.resolve())]=sha(path)
        return json.loads(path.read_bytes())
    end=read(endpoint_path);mid=read(midpoint_path);budget=read(budget_path);jet=read(jet_path)
    for record,stage in ((end,'endpoint'),(mid,'midpoint')):
        if (record['algorithm']!='INTERVAL14_ORIGINAL_DOMAIN_SHARED_DIRECTION_TAYLOR_V1'
                or record['stage']!=stage or record['interval']!=14 or not record['original_domain_unchanged']):
            raise ValueError('Complete original-domain directional enclosure required')
        if any(sha(Path(path))!=digest for path,digest in record['input_source_SHA256'].items()):
            raise ValueError('Directional proof source changed')
    if not mid['variable_endpoint_chain_included'] or mid['input_source_SHA256'].get(str(endpoint_path.resolve()))!=sha(endpoint_path):
        raise ValueError('Same endpoint model must occur inside and outside the midpoint chain')
    shared_tail=mid.get('endpoint_nonlinear_error_parameters_shared',False)
    n=348 if shared_tail else 249
    domain=TaylorDomain(mid['parameter_groups'],n)
    def decode(data,dimension,component=None):
        values=[arb(m)+arb(0,arb(r)) for m,r in data]
        if len(values)!=dimension+2:raise ValueError('Complete Taylor coefficients required')
        if dimension==75:
            c=[arb(0)]*n;c[1]=values[1];c[76:150]=values[2:76]
            if shared_tail:
                if component is None:raise ValueError('Shared endpoint remainder component required')
                c[249+component]=values[-1]
        else:c=values[1:-1]
        return Taylor(domain,values[0],arb_mat(1,n,c),arb(0) if dimension==75 and shared_tail else values[-1])
    A=[decode(v,75,i) for i,v in enumerate(end['physical_derivative_models'])]
    B=[decode(v,n) for v in mid['physical_derivative_models']]
    axis=[arb(m)+arb(0,arb(r)) for m,r in end['input_axis_ball']]
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with cache.cache_hashes(targets,excluded_roots=[out.parent]):
        tangent_path=residual.center.JACOBIAN.with_suffix('.npz')
        frozen_path=residual.center.PRECONDITIONER.with_suffix('.npz')
        for path in (tangent_path,frozen_path):sources[str(path.resolve())]=sha(path)
        with np.load(tangent_path,allow_pickle=False) as z:tangent=z['endpoint_physical_tangent_action'][15]
        with np.load(frozen_path,allow_pickle=False) as z:R=z['reduced_right_Newton_blocks'][14]
        cert=residual.center.cert
        test=cert._frame(tangent,cert.TEST_DESCRIPTOR_SCALE).T
        P=arb_mat(R.tolist()).solve(arb_mat(test.tolist()))
        h=arb(float(p.values.operands()[-1][14]))
    # Identity entry is zero because output 73 differs from input 14.
    if midpoint_scalar_path is None:
        value=sum((P[73,i]*(-axis[i]+h*A[i]/6+2*h*B[i]/3) for i in range(99)),domain.affine(0))
    else:
        scalar=read(midpoint_scalar_path)
        if (scalar['algorithm']!='INTERVAL14_MIDPOINT_LOCAL_SCALAR_TAYLOR_V1'
                or scalar['base_midpoint_record_SHA256']!=sha(midpoint_path)
                or not scalar['original_domain_unchanged']):raise ValueError('Matching midpoint scalar proof required')
        if any(sha(Path(path))!=digest for path,digest in scalar['input_source_SHA256'].items()):
            raise ValueError('Midpoint scalar proof source changed')
        covector=[arb(m)+arb(0,arb(r)) for m,r in scalar['output_covector']]
        if len(covector)!=99 or any(not v.overlaps(P[73,i]*(2*h/3)) for i,v in enumerate(covector)):
            raise ValueError('Same frozen midpoint output operator required')
        value=sum((P[73,i]*(-axis[i]+h*A[i]/6) for i in range(99)),domain.affine(0))+decode(scalar['scalar_model'],n)
    artifacts=root/'artifacts/flagship_integration'
    direct=artifacts/'.full_direct_physical_local_defect_work'
    manifest=read(direct/'manifest.json');receipt=read(direct/'reproduction.json')
    if (receipt['manifest_SHA256']!=sha(direct/'manifest.json') or not receipt['byte_identical']
            or not receipt['independent_recomputation']):raise ValueError('Frozen point lemma reproduction required')
    def frozen_npz(folder,name,manifest):
        path=folder/(name+'.json');data=folder/(name+'.npz');record=read(path)
        if sha(data)!=record['data_SHA256']:raise ValueError('Frozen point operand changed')
        for file in (path,data):
            raw=file.read_bytes()
            # Historic manifests may bind canonical LF JSON rather than the
            # checkout's CRLF bytes; accept exactly either declared digest.
            declared=manifest['files'][file.relative_to(root).as_posix()]
            if declared not in (sha(file),hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest().upper()):
                raise ValueError('Frozen point operand is outside its manifest')
            sources[str(file.resolve())]=sha(file)
        with np.load(data,allow_pickle=False) as z:
            return record,{k:z[k].copy() for k in z.files}
    point,arrays=frozen_npz(direct,'interval_014',manifest)
    if point['interval']!=14:raise ValueError('Matching point anchor required')
    a0=arb(str(arrays['DR_mid_q'][73,14]))+arb(0,arb(str(arrays['DR_rad_q'][73,14])))
    quadratic=artifacts/'.direct_physical_quadratic_source_work/interval_014'
    qm=read(quadratic/'manifest.json');qr=read(quadratic/'reproduction.json')
    if qr['manifest_SHA256']!=sha(quadratic/'manifest.json') or not qr['byte_identical'] or not qr['independent_recomputation']:
        raise ValueError('Frozen half-Hessian lemma reproduction required')
    def row(family,pair):
        record,arrays=frozen_npz(quadratic,family+'_'+pair,qm)
        if (record['interval']!=14 or record['family']!=family or record['endpoint_pair']!=pair
                or not record['taylor_half_included']):raise ValueError('Matching half-Hessian required')
        return [arb(str(m))+arb(0,arb(str(r))) for m,r in zip(arrays['Q_mid_q'][73],arrays['Q_rad_q'][73],strict=True)]
    rL,rT=map(arb,json.loads((artifacts/'BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json').read_bytes())[
        'stored_polynomial_adjudication']['witness']['radius'])
    radius_path=artifacts/'BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json'
    sources[str(radius_path.resolve())]=sha(radius_path)
    linear=[arb(0)]*n
    linear[0]=2*row('LT','01')[14]*rL;linear[1]=2*row('LT','11')[14]*rL
    q01,q10,q11=[row('TT',pair) for pair in ('01','10','11')]
    for j in range(74):
        linear[2+j]=(q01[j*74+14]+q10[14*74+j])*rT
        linear[76+j]=(q11[j*74+14]+q11[14*74+j])*rT
    error=value-domain.affine(a0,linear)
    bound=error.support();threshold=arb('0.000394150')
    cost=arb(budget['transverse_value_cost_per_unit_unaccounted_derivative_entry_upper']['exact'])
    tt=arb(jet['TT_linear_state_support_upper']['exact'])
    allowance=arb(budget['available_total_transverse_remainder_budget_lower']['exact'])/10
    transported=(cost*(bound+tt)).upper()
    rho=arb(budget['input_coordinate_support_upper']['exact'])
    longitudinal=(rho*arb(budget['frozen_map_projection_gains_upper'][0])*(bound+tt)).upper()
    def report(x):return dict(exact=str(x.upper().fmpq()),approximate=float(x.upper()))
    result=dict(algorithm='INTERVAL14_SHARED_ENTRY_TAYLOR_ASSEMBLY_V1',interval=14,
        input_coordinate=14,output_coordinate=73,original_domain_unchanged=True,
        endpoint_midpoint_shared_chain_retained=True,
        endpoint_nonlinear_error_parameters_shared=shared_tail,
        midpoint_residual_cancelled_scalar_used=midpoint_scalar_path is not None,
        anchor_translation_error_upper=report(abs(error.c)),
        first_jet_translation_and_midpoint_domain_slack_upper=report(error.linear_bound()),
        nonlinear_Taylor_remainder_upper=report(error.r),uniform_entry_error_upper=report(bound),
        required_strict_threshold=report(threshold),strict_entry_target_pass=bool(bound<threshold),
        rigorous_entry_margin_lower_exact=str((threshold-bound).lower().fmpq()),
        frozen_transverse_transport_including_TT_linear_upper=report(transported),
        frozen_longitudinal_transport_including_TT_linear_upper=report(longitudinal),
        weighted_derivative_row_contributions_upper=[report(longitudinal/rL),report(transported/rT)],
        one_tenth_transverse_allocation=report(allowance),
        strict_transport_allocation_pass=bool(transported<allowance),
        independent_reproduction_completed=False,transverse_ledger_debited=False,
        interval13_recomputed=False,Gate7_closed=False,input_source_SHA256=sources)
    if any(sha(Path(path))!=digest for path,digest in sources.items()):raise ValueError('Proof operand changed')
    with out.open('xb') as stream:stream.write(p.geometry.encoded(result))
    print(json.dumps({k:v for k,v in result.items() if k!='input_source_SHA256'}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','endpoint','midpoint','budget','jet','out'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--midpoint-scalar',type=Path)
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.endpoint.resolve(),args.midpoint.resolve(),
             args.budget.resolve(),args.jet.resolve(),args.out.resolve(),None if args.midpoint_scalar is None else args.midpoint_scalar.resolve())
