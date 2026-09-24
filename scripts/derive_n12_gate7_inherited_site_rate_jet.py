"""Promote the three HS evaluation sites using frozen primal/first jets.

Imports the original endpoint/actual-HS domains, not the broader radial
coordinate hull. Only new mixed derivatives carry new action authority.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_local_ball_rate_jet as parent
inputs=parent.inputs


def run(evidence,site,direction_file,out):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512;base=evidence/'artifacts/flagship_integration';sources={}
    source=json.loads(direction_file.read_bytes())
    if source['site']!=site or source['interval']!=13:raise ValueError('matching interval-13 incidence required')
    for p,h in source['source_SHA256'].items():
        if inputs.sha(Path(p))!=h:raise ValueError('incidence operand changed')
    charts,rates,step,atlas,binding,descriptors=parent.augmented.operands(evidence,13)
    sources.update(binding)
    weights_path=Path(inputs.action.ENDPOINT).with_suffix('.npz')
    with np.load(weights_path,allow_pickle=False) as z:weights=[arb(float(v)) for v in z['state_weights']]
    endpoint_maps=[arb_mat(99,75,[charts[2*side]['scaled'][i][j]*weights[i] if i<98 else descriptors[side]['scaled'][j]
                               for i in range(99) for j in range(75)]) for side in range(2)]
    if site=='middle':
        composed=[]
        for side in range(2):
            _,p=inputs.import_domain(base/f'.coupled_endpoint_uniform_df_work/endpoint_{13+side:03d}','derivative.npz',sources)
            with np.load(p,allow_pickle=False) as z:A=inputs.read_array(z,'derivative')
            operator=arb_mat(99,99,[arb(i==j)/2+(-1 if side else 1)*step*A[i,j]/8 for i in range(99) for j in range(99)])
            composed.append(operator*endpoint_maps[side])
        direction_map=arb_mat(99,150,[composed[j//75][i,j%75] for i in range(99) for j in range(150)])
    else:direction_map=endpoint_maps[site=='right']
    def direction_support(row):
        return sum((abs(row[start]).upper()+sum((abs(x).upper()**2 for x in row[start+1:start+75]),arb(0)).sqrt()
                    for start in range(0,len(row),75)),arb(0)).upper()
    direction=[arb(0,direction_support([direction_map[i,j] for j in range(direction_map.ncols())])) for i in range(99)]
    middle=site=='middle';n=13 if site!='right' else 14;name=f'interval_{n:03d}' if middle else f'endpoint_{n:03d}'
    eigkind='.coupled_midpoint_eigenpair_pilot_work' if middle else '.affine_eigenpair_pilot_work'
    valuekind='.coupled_midpoint_physical_value_work' if middle else '.affine_physical_value_pilot_work'
    dfkind='.coupled_midpoint_uniform_df_work' if middle else '.coupled_endpoint_uniform_df_work'
    eh,ep=inputs.import_domain(base/eigkind/name,'eigenpair.npz',sources)
    vh,vp=inputs.import_domain(base/valuekind/name,'value.npz',sources)
    dh,dp=inputs.import_domain(base/dfkind/name,'derivative.npz',sources)
    if not all(h['report']['validation_passed'] for h in (eh,vh,dh)):raise ValueError('certified primal and first jets required')
    trial=next(i for i,t in enumerate(eh['report']['trials']) if t['validation_passed'])
    with np.load(ep,allow_pickle=False) as z:
        psi=inputs.read_array(z,'eigenpair_box')[:61]
        w=inputs.read_array(z,f'trial_{trial}_radii');V=inputs.read_array(z,f'trial_{trial}_variation_bounds')
        oldR=inputs.read_array(z,'preconditioner')
    q=max((a/b).upper() for a,b in zip(V,w))
    if not q<1:raise ArithmeticError('original inverse authority unavailable')
    R=arb_mat(62,62,[oldR[i,j]*(-1 if i==61 else 1) for i in range(62) for j in range(62)])
    with np.load(vp,allow_pickle=False) as z:
        full=inputs.read_array(z,'raw_domain');response=list(inputs.read_array(z,'response_box'))
    with np.load(dp,allow_pickle=False) as z:pre=inputs.read_array(z,'preconditioned_variation_rhs')
    first=[]
    for block,size in ((0,61),(1,62)):
        alpha=[]
        for batch in dh['report']['coupled_inverse_bounds']:
            alpha.extend(arb(fmpq(a['weighted_error_upper_rational'])) for a in batch['solve_bounds'][block])
        if len(alpha)!=99:raise ValueError('complete first-variation input coverage required')
        coefficients=arb_mat(size,99,[(pre[block,i,j]+arb(0,(V[i]*alpha[j]).upper()))*(-1 if i==61 else 1)
                                      for i in range(size) for j in range(99)])
        composed=coefficients*direction_map
        first.append([arb(0,direction_support([composed[i,j] for j in range(composed.ncols())])) for i in range(size)])
    raw=[direction[i]/weights[i] for i in range(98)];state=list(full[:98])
    descriptor=dict(value=full[98],u=direction[98],v=direction[98],uv=arb(0))
    lower=arb(fmpq(vh['report']['physical_G_norm_lower_rational']))
    qw,rw,_,_=inputs.action.metric_data();qw=[arb(float(x)) for x in qw];rw=[arb(float(x)) for x in rw]
    calls=[]
    def solve(rhs):
        index=len(calls);calls.append(index)
        if index in (0,1):
            # Historical projected first solve has no lambda derivative.
            # rhs=-H_u psi, so its new scalar contraction is -lambda_u.
            return first[0]+[sum((p*r for p,r in zip(psi,rhs[:61])),arb(0))]
        if index==3:return response
        if index in (4,5):return first[1]
        if index not in (2,6):raise ValueError('unexpected physical graph solve')
        proposal=list((R*arb_mat(62,1,rhs)).entries())
        error=(max((abs(x).upper()/wi).upper() for x,wi in zip(proposal,w))*q/(1-q)).upper()
        return [x+arb(0,(wi*error).upper()) for x,wi in zip(proposal,w)]
    for p in (direction_file,weights_path,Path(__file__),Path(parent.__file__),Path(parent.jet.__file__),
              Path(parent.factored.__file__),Path(parent.sparse.__file__)):
        sources[str(p.resolve())]=inputs.sha(p)
    with parent.sparse.use_optimized_mixed(inputs.action),parent.factored.use_ball_factored_integrand(inputs.action,state):
        evaluate=parent.Evaluator(state)
        result=parent.jet.complete_rate(evaluate,solve,state,psi,raw,raw,descriptor,qw,rw,weights,lower)
    if len(calls)!=7:raise ArithmeticError('incomplete mixed graph')
    rate=result['rate']
    payload=dict(algorithm='INHERITED_PRIMAL_FIRST_SITE_COMPLETE_MIXED_RATE_V1',interval=13,site=site,
        radius_exact=source['radius_exact'],source_SHA256=sources,
        rate_jets={k:[parent.pair(x) for x in rate[k]] for k in parent.jet.KEYS},
        mixed_norm_upper=inputs.number(sum((abs(v).upper()**2 for v in rate['uv']),arb(0)).sqrt()),
        direction_weighted_augmented=[parent.pair(x) for x in direction],
        incidence_and_frozen_first_jets_contracted_before_direction_support=True,
        independent_direction_groups=direction_map.ncols()//75,
        frozen_primal_response_and_first_jets_reused=True,original_site_domain_used=True,
        all_16_moving_descriptor_terms=True,normalization_and_implicit_border_terms_complete=True,
        descriptor_norm_lower_exact=str(lower.fmpq()),action_evaluations=evaluate.count,
        nonaffine_midpoint_incidence_composed=False,signed_local_remainder_assembled=False,
        representation='Complete coordinate-ball enclosure with inherited primal and first jets; shared affine coefficients are still lost.',
        kappa_L=None,kappa_T=None,Gate7_closed=False)
    if any(inputs.sha(Path(p))!=h for p,h in sources.items()):raise RuntimeError('source changed')
    out.write_bytes(inputs.encode(payload));print(json.dumps(dict(site=site,mixed_norm=payload['mixed_norm_upper'])))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--site',choices=('left','middle','right'),required=True)
    p.add_argument('--direction-file',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.site,a.direction_file.resolve(),a.out.resolve())
