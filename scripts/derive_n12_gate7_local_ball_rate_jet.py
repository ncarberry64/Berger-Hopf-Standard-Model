"""A complete, explicitly coordinate-boxed mixed-rate feasibility enclosure."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_augmented_tube_domain as augmented
from bhsm.interface import physical_ball_rate_jet as jet
from bhsm.interface import shared_physical_tube as tube
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface import sparse_arb_mixed_jets as sparse
inputs=augmented.inputs


def pair(x):return [str(x.mid().fmpq()),str(x.rad().fmpq())]
def unpair(x):return arb(fmpq(x[0]))+arb(0,arb(fmpq(x[1])))


class Evaluator:
    def __init__(self,state):
        self.state=state;self.cache={};self.count=0
        self.maps=[inputs.action._dense_mapping(inputs.action._integrand(state,j,0).maps) for j in range(96)]
    def key(self,legs):return tuple(sorted(tuple(tuple(pair(v)) for v in leg) for leg in legs))
    def __call__(self,legs):
        key=('scalar',self.key(legs))
        if key not in self.cache:
            if any(all(v.is_zero() for v in leg) for leg in legs):return arb(0)
            arrays=[np.array(leg,dtype=object) for leg in legs]
            self.cache[key]=arb(inputs.action._contracted_action(self.state,arrays,self.maps))
            self.count+=1;print(json.dumps(dict(action=self.count,kind='scalar',order=len(legs))),flush=True)
        return self.cache[key]
    def gradient(self,legs):
        key=('gradient',self.key(legs))
        if key not in self.cache:
            rows=[]
            for start in range(0,98,14):
                stop=min(98,start+14)
                basis=np.array([[arb(i==j) for j in range(start,stop)] for i in range(98)],dtype=object)
                arrays=[basis]+[np.array(leg,dtype=object)[:,None] for leg in legs]
                rows.extend(inputs.action._contracted_action(self.state,arrays,self.maps))
            self.cache[key]=rows;self.count+=1
            print(json.dumps(dict(action=self.count,kind='gradient',order=len(legs)+1)),flush=True)
        return self.cache[key]


def run(evidence,interval,site,cell_file,augmented_file,out):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512
    charts,rates,step,cert,sources,descriptors=augmented.operands(evidence,interval)
    cover=json.loads(cell_file.read_bytes());domain=json.loads(augmented_file.read_bytes())
    if cover['interval']!=interval or domain['interval']!=interval or cover['radius_exact']!=cert['radius_exact']:
        raise ValueError('same interval and radii required')
    cells=cover['partition_cells'];cell={'left':0,'middle':cells//2-1,'right':cells-1}[site]
    record=next(r for r in cover['evaluated_cells'] if r['cell']==cell)
    if not record['certified']:raise ArithmeticError('local chart not certified')
    for payload in (cover,domain):
        if any(inputs.sha(Path(p))!=h for p,h in payload['source_SHA256'].items()):raise ValueError('input source changed')
    half=2*cell//cells;frozen=cert['links'][half]
    basew=[arb(fmpq(v)) for v in frozen['base_weights_exact']]
    scale=arb(fmpq(record['witness_scale_exact']));w=[v*scale for v in basew]
    q=arb(fmpq(record['q']['exact']));bounds=[arb(cell)/cells,arb(cell+1)/cells]
    ops=tube.tube_operands(charts[0],charts[2],rates,step,(charts[half],charts[half+1],basew,half),bounds,variation=False)
    state=[v.enclosure() for v in ops['state']];s=ops['chart_parameter'].enclosure();a,b=charts[half:half+2]
    psi=[a['y'][i]+s*(b['y'][i]-a['y'][i])+arb(0,w[i]) for i in range(61)]
    R=arb_mat(62,62,[(a['R'][i,j]+s*(b['R'][i,j]-a['R'][i,j]))*(-1 if i==61 else 1)
                     for i in range(62) for j in range(62)])
    def solve(rhs):
        proposal=list((R*arb_mat(62,1,rhs)).entries())
        alpha=max((abs(v).upper()/wi).upper() for v,wi in zip(proposal,w))
        correction=(alpha*q/(1-q)).upper()
        return [v+arb(0,(wi*correction).upper()) for v,wi in zip(proposal,w)]
    with np.load(Path(inputs.action.ENDPOINT).with_suffix('.npz'),allow_pickle=False) as z:
        weights=[arb(float(v)) for v in z['state_weights']]
    support=lambda row:(abs(row[0]).upper()+sum((abs(v).upper()**2 for v in row[1:]),arb(0)).sqrt()).upper()
    directions=[]
    for side in range(2):
        directions.append([arb(0,support(charts[2*side]['scaled'][i])*weights[i]) for i in range(98)]+
                          [arb(0,support(descriptors[side]['scaled']))])
    if site=='middle':
        derivatives=[]
        for n in (interval,interval+1):
            _,p=inputs.import_domain(evidence/f'artifacts/flagship_integration/.coupled_endpoint_uniform_df_work/endpoint_{n:03d}',
                                     'derivative.npz',sources)
            with np.load(p,allow_pickle=False) as z:derivatives.append(inputs.read_array(z,'derivative'))
        d0,d1=[list((arb_mat(99,99,list(A.flat))*arb_mat(99,1,d)).entries()) for A,d in zip(derivatives,directions)]
        direction=[(x+y)/2+step*(f-g)/8 for x,y,f,g in zip(*directions,d0,d1)]
    else:direction=directions[site=='right']
    raw=[direction[i]/weights[i] for i in range(98)]
    normrecord=domain['cells'][cell]
    descriptor=dict(value=unpair(normrecord['descriptor_ball']),u=direction[-1],v=direction[-1],uv=arb(0))
    lower=arb(fmpq(normrecord['physical_norm_lower_exact']))
    qw,rw,_,_=inputs.action.metric_data();qw=[arb(float(v)) for v in qw];rw=[arb(float(v)) for v in rw]
    for p in (cell_file,augmented_file,Path(__file__),Path(jet.__file__),Path(augmented.__file__),
              Path(factored.__file__),Path(sparse.__file__),ROOT/'src/bhsm/interface/shared_complete_rate_jet.py'):
        sources[str(p.resolve())]=inputs.sha(p)
    with sparse.use_optimized_mixed(inputs.action),factored.use_ball_factored_integrand(inputs.action,state):
        evaluate=Evaluator(state)
        result=jet.complete_rate(evaluate,solve,state,psi,raw,raw,descriptor,qw,rw,weights,lower)
    rate=result.pop('rate')
    payload=dict(algorithm='COMPLETE_LOCAL_COORDINATE_BALL_RATE_MIXED_V1',interval=interval,site=site,cell=cell,
        radius_exact=cert['radius_exact'],source_SHA256=sources,
        rate_jets={k:[pair(v) for v in rate[k]] for k in jet.KEYS},
        mixed_norm_upper=inputs.number(sum((abs(v).upper()**2 for v in rate['uv']),arb(0)).sqrt()),
        direction_weighted_augmented=[pair(v) for v in direction],
        descriptor_norm_lower_exact=str(lower.fmpq()),action_evaluations=evaluate.count,
        all_16_moving_descriptor_terms=True,normalization_and_implicit_border_terms_complete=True,
        representation='Coordinate-box outer enclosure, including independent direction components. This may be very pessimistic.',
        nonaffine_midpoint_incidence_composed=False,signed_local_remainder_assembled=False,
        independent_reproduction_required=True,kappa_L=None,kappa_T=None,Gate7_closed=False)
    if any(inputs.sha(Path(p))!=h for p,h in sources.items()):raise RuntimeError('source changed')
    out.write_bytes(inputs.encode(payload));print(json.dumps(dict(site=site,mixed_norm=payload['mixed_norm_upper'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--interval',type=int,choices=range(13,19),required=True)
    p.add_argument('--site',choices=('left','middle','right'),required=True)
    p.add_argument('--cell-file',type=Path,required=True);p.add_argument('--augmented-file',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.interval,a.site,a.cell_file.resolve(),a.augmented_file.resolve(),a.out.resolve())
