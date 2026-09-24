"""Bind the 99th dense-history coordinate and a positive physical norm.

This is rate-domain authority, not a numerical rate-derivative enclosure.
The action/eigenpair cover is supplied separately by reproduced local cells.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, ctx, fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_local_physical_tube as parent
from bhsm.interface.history_eigenbranch_variation import hermite_history
from bhsm.interface import shared_physical_tube as tube
inputs=parent.inputs


def operands(evidence,interval):
    charts,rates,step,cert,sources=parent.load(evidence,interval)
    base=evidence/'artifacts/flagship_integration'
    _,path=inputs.import_domain(base/f'.coupled_hs_midpoint_domain_work/interval_{interval:03d}','domain.npz',sources)
    with np.load(path,allow_pickle=False) as z:D=inputs.read_array(z,'raw_directions')
    with np.load(Path(inputs.action.ENDPOINT).with_suffix('.npz'),allow_pickle=False) as z:
        centers=[arb(float(v)) for v in z['independent_signed_descriptors'][interval:interval+2]]
    radii=[arb(fmpq(v)) for v in cert['radius_exact']]
    descriptors=[]
    for side in range(2):
        # The actual-HS domain stores half of each complete endpoint map.
        columns=[side]+list(range(2+74*side,76+74*side))
        scaled=[2*D[98,j]*radii[k!=0] for k,j in enumerate(columns)]
        _,p=inputs.import_domain(base/f'.coupled_normalized_physical_value_work/endpoint_{interval+side:03d}','value.npz',sources)
        with np.load(p,allow_pickle=False) as z:rate=inputs.read_array(z,'rate_candidate')[98]
        descriptors.append(dict(center=centers[side],scaled=scaled,rate=rate))
    return charts,rates,step,cert,sources,descriptors


def run(evidence,interval,cells,out):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512
    charts,rates,step,cert,sources,descriptors=operands(evidence,interval)
    qw=[arb(float(v)) for v in inputs.action.metric_data()[0]]
    rows=[]
    for cell in range(cells):
        half=2*cell//cells
        w=[arb(fmpq(v)) for v in cert['links'][half]['base_weights_exact']]
        bounds=[arb(cell)/cells,arb(cell+1)/cells]
        ops=tube.tube_operands(charts[0],charts[2],rates,step,(charts[half],charts[half+1],w,half),bounds,variation=False)
        d=ops['domain'];state=[];field=[]
        for side,item in enumerate(descriptors):
            co=[arb(0)]*d.dimension;co[2+75*side:77+75*side]=item['scaled']
            state.append(d.affine(item['center'],co))
            # The descriptor error is an interval coefficient. Enlarging its
            # correlation with the raw rate errors is safe for this scalar bound.
            field.append(d.affine(item['rate']))
        descriptor=hermite_history([state[0]],[state[1]],[field[0]],[field[1]],step,ops['tau'])[0].enclosure()
        lower=abs(descriptor).lower()
        c_lower=[abs(qw[i]*ops['curve'][37+i].enclosure()).lower() for i in range(37)]
        chosen=max(range(37),key=lambda i:c_lower[i])
        norm_lower=(lower*c_lower[chosen]).lower()
        rows.append(dict(cell=cell,tau_exact=[str(v.fmpq()) for v in bounds],
            descriptor_ball=[str(descriptor.mid().fmpq()),str(descriptor.rad().fmpq())],
            descriptor_absolute_lower_exact=str(lower.fmpq()),configuration_component=chosen,
            configuration_absolute_lower_exact=str(c_lower[chosen].fmpq()),
            physical_norm_lower_exact=str(norm_lower.fmpq()),positive=bool(norm_lower>0)))
    for p in (Path(__file__),Path(hermite_history.__globals__['__file__'])):sources[str(p.resolve())]=inputs.sha(p)
    result=dict(algorithm='AUGMENTED_HERMITE_TUBE_DESCRIPTOR_AND_NORM_V1',interval=interval,
        partition_cells=cells,cells=rows,radius_exact=cert['radius_exact'],
        proof='The first 37 numerator entries are s*c. Hence nu>=abs(s*c_j). The descriptor is excluded from the 98-component norm.',
        positive_norm_on_complete_dense_image=all(row['positive'] for row in rows),
        requires_separate_reproduced_eigenchart_cover=True,complete_physical_rate_authority=False,
        physical_rate_Hessian_enclosed=False,kappa_L=None,kappa_T=None,Gate7_closed=False,source_SHA256=sources)
    if any(inputs.sha(Path(p))!=h for p,h in sources.items()):raise RuntimeError('source changed')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(inputs.encode(result))
    print(json.dumps(dict(interval=interval,positive=result['positive_norm_on_complete_dense_image'],
                         minimum_norm_lower=float(min(arb(fmpq(r['physical_norm_lower_exact'])) for r in rows)))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--interval',type=int,choices=range(13,19),required=True)
    p.add_argument('--cells',type=int,choices=(2,4,8,16,32,64),default=8)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.interval,a.cells,a.out.resolve())
