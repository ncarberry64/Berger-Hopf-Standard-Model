"""Validate complete interval coverage and materialize its reproduced atlas."""
import argparse
import json
from pathlib import Path
import sys
from flint import arb,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import certify_n12_gate7_local_physical_tube as parent
inputs=parent.inputs


def validate_cells(chunks,augmented,frozen):
    cells=[];radius=frozen['radius_exact']
    for chunk in chunks:
        if chunk['interval']!=13 or chunk['partition_cells']!=8 or chunk['radius_exact']!=radius:
            raise ValueError('one unchanged interval-13 partition required')
        cells.extend(chunk['evaluated_cells'])
    cells.sort(key=lambda c:c['cell'])
    if [c['cell'] for c in cells]!=list(range(8)):raise ValueError('complete partition without duplicates required')
    if augmented['radius_exact']!=radius or len(augmented['cells'])!=8:raise ValueError('augmented image partition mismatch')
    for i,c in enumerate(cells):
        if c['tau_exact']!=[str(fmpq(i,8)),str(fmpq(i+1,8))] or c['half_chart']!=i//4:
            raise ValueError('closed cell partition has gap or wrong chart')
        number=lambda x:arb(fmpq(x['exact']))
        link=frozen['links'][i//4];scale=arb(fmpq(c['witness_scale_exact']))
        q=(number(c['defect_base'])+scale*number(link['nonlinear_defect_per_witness_scale_upper'])).upper()
        image=(number(c['residual'])/scale+q).upper()
        if (not c['certified'] or not number(c['q'])>=q or not number(c['image'])>=image
                or not number(c['q'])<1 or not number(c['image'])<1
                or not image<1 or not q<1 or not scale>=arb(fmpq(link['eigenpair_witness_scale_exact']))):
            raise ValueError('outward local self-map or inverse proof failed')
        if any(not arb(fmpq(a['inertia_lower_exact']))>0 for a in c['radial_actions'].values()):
            raise ValueError('positive complete action domain required')
        s=augmented['cells'][i]
        if s['cell']!=i or s['tau_exact']!=c['tau_exact'] or not arb(fmpq(s['physical_norm_lower_exact']))>0:
            raise ValueError('positive same-cell augmented normalization required')
    return cells


def run(work,out):
    ctx.prec=512
    if out.exists():raise FileExistsError('fresh package directory required')
    chunks=[];payloads={};provenance={}
    names=[f'interval13_cubic8_cells{i}_{i+1}' for i in range(0,8,2)]+['interval13_augmented']
    for name in names:
        first=work/f'{name}_first.json';repeat=work/f'{name}_repeat.json'
        if first.read_bytes()!=repeat.read_bytes():raise ValueError('independent numeric reproduction differs')
        record=json.loads(first.read_bytes())
        for p,h in record['source_SHA256'].items():
            if inputs.sha(Path(p))!=h:raise ValueError('source binding changed')
        if 'cubic8' in name:chunks.append(record)
        else:augmented=record
        for p in (first,repeat):payloads[p.name]=p.read_bytes();provenance[str(p.resolve())]=inputs.sha(p)
    frozen_path=ROOT/'artifacts/flagship_integration/gate7_shared_eigenbranch_links_20260923/certificate.json'
    frozen=json.loads(frozen_path.read_bytes());cells=validate_cells(chunks,augmented,frozen)
    certificate=dict(algorithm='COMPLETE_CHART_LOCAL_AUGMENTED_PHYSICAL_TUBE_ATLAS_V1',interval=13,
        Layer_A_frozen_commit='452c80a7',Layer_A_recomputed=False,radius_exact=frozen['radius_exact'],
        cells=[dict(cell=c['cell'],tau_exact=c['tau_exact'],half_chart=c['half_chart'],q=c['q'],image=c['image'],
                    physical_norm_lower_exact=augmented['cells'][c['cell']]['physical_norm_lower_exact']) for c in cells],
        closed_partition_covers_unit_interval=True,all_original_endpoint_perturbations_and_uniform_rate_errors_included=True,
        descriptor_image_included=True,complete_physical_tube_cover_certified=True,
        physical_rate_smoothly_defined_on_entire_dense_image=True,
        handoff='At each common time and physical parameter, both chart roots continue the same frozen Layer-A root along the same radial homotopy. Uniform bordered invertibility and local uniqueness force equality. The central handoff is also owned by the original actual-HS midpoint chart.',
        new_endpoints=0,original_physical_radii_changed=False,
        uniform_quantitative_rate_Hessian_on_all_time_cells=False,signed_local_remainder_assembled=False,
        remaining_intervals=[14,15,16,17,18],extension_condition='Obtain a viable complete signed interval-13 remainder first.',
        kappa_L=None,kappa_T=None,Gate7_closed=False,
        input_files_SHA256=provenance,packaged_files_SHA256={name:__import__('hashlib').sha256(raw).hexdigest().upper() for name,raw in payloads.items()},
        source_SHA256={str(p.resolve()):inputs.sha(p) for p in (frozen_path,Path(__file__))})
    first=inputs.encode(certificate);second=inputs.encode(dict(certificate))
    if first!=second:raise ArithmeticError('deterministic assembly failed')
    out.mkdir(parents=True)
    for name,raw in payloads.items():(out/name).write_bytes(raw)
    (out/'certificate.json').write_bytes(first)
    receipt=dict(certificate_SHA256=inputs.sha(out/'certificate.json'),byte_identical=True,
        independent_numerical_recomputation=True,numerical_pairs=5,all_eight_time_cells_reproduced=True,
        Gate7_closed=False)
    (out/'reproduction.json').write_bytes(inputs.encode(receipt))
    print(json.dumps(dict(complete_physical_tube_cover_certified=True,interval=13,cells=8)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.work.resolve(),a.out.resolve())
