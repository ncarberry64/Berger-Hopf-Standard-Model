"""Signed row contractions for local moving-chart radial tube extensions."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_local_physical_tube as parent
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface import sparse_arb_mixed_jets as sparse
from bhsm.interface import shared_physical_tube as tube
from bhsm.interface import hermite_tube_directions as cubic
inputs=parent.inputs


def rows_for_cell(state,left,eta,directions,progress):
    action=inputs.action
    maps=[action._dense_mapping(action._integrand([arb(0)]*98,j,0).maps) for j in range(96)]
    result=[]
    with sparse.use_optimized_mixed(action),factored.use_ball_factored_integrand(action,state):
        inertia=sum((action._integrand(state,j,0).inertia.d[0] for j in range(96)),arb(0))
        if not inertia>0:raise ArithmeticError('positive radial-domain inertia required')
        for start in range(0,62,4):
            values=action._contracted_action(state,[left[:,start:start+4,None],eta[:,None,None],directions[:,None,:]],maps)
            for row in values:
                support=sum((abs(v).upper() for v in row[:6]),arb(0))
                support+=sum((sum((abs(v).upper()**2 for v in row[a:b]),arb(0)).sqrt() for a,b in [(6,80),(80,154)]),arb(0))
                support+=sum((abs(v).upper() for v in row[154:]),arb(0))
                result.append(arb(0,support.upper()))
            progress(min(start+4,62))
    return result,inertia.lower()


def run(evidence,interval,cells,selected,out):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512
    charts,rates,step,cert,sources=parent.load(evidence,interval)
    for p in (Path(__file__),Path(parent.__file__),Path(factored.__file__),Path(sparse.__file__),Path(cubic.__file__)):
        sources[str(p.resolve())]=inputs.sha(p)
    results=[]
    for cell in selected:
        if not 0<=cell<cells:raise ValueError('cell outside partition')
        half=2*cell//cells;frozen=cert['links'][half]
        w=[arb(fmpq(v)) for v in frozen['base_weights_exact']]
        bounds=[arb(cell)/cells,arb(cell+1)/cells]
        ops=tube.tube_operands(charts[0],charts[2],rates,step,(charts[half],charts[half+1],w,half),bounds,variation=False)
        state=np.array([v.enclosure() for v in ops['state']],dtype=object)
        delta=cubic.displacement_directions(charts[0],charts[2],rates,step,(charts[half],charts[half+1],half),*bounds)
        s=ops['chart_parameter'].enclosure()
        a,b=charts[half:half+2]
        left=np.full((98,62),arb(0),dtype=object)
        for i in range(62):
            for j in range(61):left[37+j,i]=a['R'][i,j]+s*(b['R'][i,j]-a['R'][i,j])
        actions={}
        for kind in ('variation','residual'):
            eta=np.array([arb(0)]*37+[
                arb(0,w[j]) if kind=='variation' else a['y'][j]+s*(b['y'][j]-a['y'][j]) for j in range(61)],dtype=object)
            values,inertia=rows_for_cell(state,left,eta,delta,lambda done:
                print(json.dumps(dict(cell=cell,kind=kind,rows=done,total=62)),flush=True))
            upper=max((abs(v).upper()/wi).upper() for v,wi in zip(values,w,strict=True))
            actions[kind]=dict(upper=inputs.number(upper),signed_row_balls=[
                [str(v.mid().fmpq()),str(v.rad().fmpq())] for v in values],inertia_lower_exact=str(inertia.fmpq()))
        old=lambda k:arb(fmpq(frozen[k]['exact']))
        qbase=(old('complete_centerline_defect_base_upper')+arb(fmpq(actions['variation']['upper']['exact']))).upper()
        Y=(old('residual_upper_in_base_weights')+arb(fmpq(actions['residual']['upper']['exact']))).upper()
        nonlinear=old('nonlinear_defect_per_witness_scale_upper');minimum=arb(fmpq(frozen['eigenpair_witness_scale_exact']))
        candidates=[]
        for power in range(31):
            scale=arb(2)**power
            if scale<minimum:continue
            q=(qbase+scale*nonlinear).upper();candidates.append(((Y/scale+q).upper(),scale,q))
        image,scale,q=min(candidates,key=lambda row:row[0])
        result=dict(cell=cell,tau_exact=[str(v.fmpq()) for v in bounds],half_chart=half,
            radial_actions=actions,defect_base=inputs.number(qbase),residual=inputs.number(Y),
            witness_scale_exact=str(scale.fmpq()),q=inputs.number(q),image=inputs.number(image),
            certified=bool(q<1 and image<1),failure_category=None if q<1 and image<1 else 'INSUFFICIENT_OFF_CENTER_ENCLOSURE')
        results.append(result)
        print(json.dumps(dict(cell=cell,certified=result['certified'],q=float(q),image=float(image))),flush=True)
    payload=dict(algorithm='CUBIC_DIRECTIONAL_LOCAL_HERMITE_TUBE_ROWS_V1',interval=interval,partition_cells=cells,
        evaluated_cells=results,complete_partition_evaluated=sorted(set(selected))==list(range(cells)),
        full_dense_image_eigenchart_cover=sorted(set(selected))==list(range(cells)) and all(v['certified'] for v in results),
        radius_exact=cert['radius_exact'],source_SHA256=sources,Layer_A_recomputed=False,new_endpoints=0,
        original_physical_radii_changed=False,physical_closure_boundary_demonstrated=False,
        complete_physical_rate_authority=False,signed_local_remainder_assembled=False,kappa_L=None,kappa_T=None,Gate7_closed=False)
    if any(inputs.sha(Path(p))!=h for p,h in sources.items()):raise RuntimeError('source changed')
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as stream:stream.write(inputs.encode(payload))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--interval',type=int,choices=range(13,19),required=True)
    p.add_argument('--cells',type=int,choices=(2,4,8,16,32,64),default=8)
    p.add_argument('--selected',type=int,nargs='+')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.interval,a.cells,a.selected or list(range(a.cells)),a.out.resolve())
