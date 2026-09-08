"""Bind all corrected stored quadratic centers to their raw provenance.

The adjoint correction is binary64 center algebra. The enclosures below
cover its stored addition and symmetric representation, not its evaluation
error or the physical Hessian.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import derive_n12_gate7_current_green_scalar_covector_correction as correction
import certify_n12_gate7_symmetric_quadratic_representatives as representatives
from bhsm.interface import scalar_updated_quadratic_representation as updated_representation

RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_SCALAR_COVECTOR_CORRECTION.json'
IDENTITY=ROOT/'artifacts/current_semantics/BHSM_N12_GATE7_SUPPLEMENTAL_MIXED_RATE_UU_VALIDATION.json'
SCOPE='CORRECTED_STORED_QUADRATIC_CENTER_ONLY'
KEYS=[('endpoint',i) for i in range(1,371)]+[('midpoint',i) for i in range(370)]

def _sha(path):
    return correction.recovery._sha(path)

def _manifest():
    digest=hashlib.sha256()
    for kind,index in KEYS:
        digest.update(f'{kind}:{index}:{_sha(correction._path(kind,index))}\n'.encode())
    return digest.hexdigest().upper()

def addition_error(raw,delta,stored):
    """Enclose only fl(raw + stored correction) minus that exact sum."""
    raw,delta,stored=[np.asarray(value,dtype=float) for value in (raw,delta,stored)]
    if raw.shape!=delta.shape or raw.shape!=stored.shape or not all(np.all(np.isfinite(value)) for value in (raw,delta,stored)):
        raise ValueError('Finite identical addition operand shapes required')
    previous=ctx.prec;ctx.prec=512
    try:
        total=arb(0)
        for a,b,c in zip(raw.flat,delta.flat,stored.flat):
            error=abs(arb(float(c))-arb(float(a))-arb(float(b))).upper()
            total+=error*error
        if total.is_zero():return 0.
        value=math.nextafter(float(total.sqrt().upper()),math.inf)
        if not math.isfinite(value):raise RuntimeError('Addition error is not finite')
        return value
    finally:ctx.prec=previous

def build_payload():
    raw=json.loads(representatives.raw_certificate.RESULT.read_text())
    representation=json.loads(representatives.RESULT.read_text())
    representatives.validate_for_consumption(raw,representation)
    identity=json.loads(IDENTITY.read_text())
    if (identity.get('validation_passed') is not True
            or identity.get('scalar_covector_correction_applied') is not True
            or not identity.get('inputs')
            or any(_sha(ROOT/p)!=digest for p,digest in identity['inputs'].items())):
        raise RuntimeError('Current corrected supplemental UU identity required')
    paths=[Path(__file__),Path(correction.__file__),Path(representatives.__file__),
           Path(updated_representation.__file__),
           Path(representatives.representation.__file__),representatives.RESULT,
           representatives.raw_certificate.RESULT,IDENTITY]
    inputs={p.relative_to(ROOT).as_posix():_sha(p) for p in paths}
    fingerprint=correction._fingerprint();rows=[]
    raw_rows={(r['kind'],r['index']):r for r in representation['rows']}
    manifest=_manifest()
    for kind,index in KEYS:
        corrected,basis=correction.corrected_tensor(kind,index)
        with np.load(correction.recovery._path(kind,index)) as source:
            raw_tensor=source['quadratic_tensor'].copy()
        with np.load(correction._path(kind,index)) as source:
            delta=source['scalar_correction'].copy()
        if not np.array_equal(corrected[:-1],raw_tensor[:-1]):
            raise RuntimeError('Correction changed a field output')
        raw_sha=_sha(correction.recovery._path(kind,index))
        raw_row=raw_rows[kind,index]
        if raw_row['raw_shard_SHA256']!=raw_sha:
            raise RuntimeError('Reused field rounding bound has stale raw provenance')
        represented,row=updated_representation.certify_scalar_update(
            raw_tensor,corrected,raw_row['projection_rounding_Frobenius_upper'])
        row['raw_bound_requires_external_verification']=False
        row.update(kind=kind,index=index,
            raw_shard_SHA256=raw_sha,
            correction_shard_SHA256=_sha(correction._path(kind,index)),
            represented_tensor_binary64_SHA256=representatives.array_hash(represented),
            scalar_correction_Frobenius_norm=float(np.linalg.norm(delta)),
            scalar_addition_rounding_Frobenius_upper=addition_error(raw_tensor[-1],delta,corrected[-1]))
        rows.append(row)
    if (_manifest()!=manifest or correction._fingerprint()!=fingerprint
            or representatives.raw_certificate._manifest([correction.recovery._path(kind,i) for kind,i in KEYS])!=raw['shard_manifest_SHA256']
            or any(_sha(ROOT/p)!=digest for p,digest in inputs.items())):
        raise RuntimeError('Correction certificate inputs changed')
    return dict(artifact='BHSM_N12_GATE7_SCALAR_COVECTOR_CORRECTION',scope=SCOPE,
        status='ALL_740_SCALAR_COVECTOR_CORRECTIONS_COMPOSED',
        campaign_fingerprint=fingerprint,raw_campaign_fingerprint=correction.recovery._fingerprint(),
        raw_shard_manifest_SHA256=raw['shard_manifest_SHA256'],correction_manifest_SHA256=manifest,
        coverage=dict(endpoints=370,midpoints=370,complete=True),rows=rows,inputs=inputs,
        maximum_scalar_addition_rounding_Frobenius_upper=max(r['scalar_addition_rounding_Frobenius_upper'] for r in rows),
        maximum_projection_rounding_Frobenius_upper=max(r['projection_rounding_Frobenius_upper'] for r in rows),
        validation_passed=True,claim_boundary=dict(raw_tensors_modified=False,
            corrected_center_derived=True,adjoint_evaluation_rounding_enclosed=False,
            physical_Hessian_error_enclosed=False,causal_rounding_enclosed=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False))

def validate_for_consumption(record):
    if (record.get('validation_passed') is not True or record.get('scope')!=SCOPE
            or record.get('coverage')!=dict(endpoints=370,midpoints=370,complete=True)
            or record.get('campaign_fingerprint')!=correction._fingerprint()
            or record.get('raw_campaign_fingerprint')!=correction.recovery._fingerprint()
            or record.get('correction_manifest_SHA256')!=_manifest()
            or [(r.get('kind'),r.get('index')) for r in record.get('rows',[])]!=KEYS
            or not record.get('inputs')
            or any(_sha(ROOT/p)!=digest for p,digest in record['inputs'].items())):
        raise RuntimeError('Complete current scalar covector correction certificate required')

def main():
    payload=build_payload()
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k not in ('rows','inputs')}))

if __name__=='__main__':main()
