"""Keep every witness input column signed until the complete D3 sum."""
import argparse
import math
import hashlib
import inspect
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_local_physical_tube as parent
from bhsm.interface.affine_eigenpair_contraction import nonlinear_eigenpair_variation
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface import sparse_arb_mixed_jets as sparse
from bhsm.interface import shared_physical_tube as tube
inputs=parent.inputs


def rows_for_cell(state,left,eta,delta,progress):
    action=inputs.action
    maps=[action._dense_mapping(action._integrand([arb(0)]*98,j,0).maps) for j in range(96)]
    variation=all(v.mid().is_zero() for v in eta) and any(not v.rad().is_zero() for v in eta)
    result=[];matrix=[]
    with sparse.use_optimized_mixed(action),factored.use_ball_factored_integrand(action,state):
        inertia=sum((action._integrand(state,j,0).inertia.d[0] for j in range(96)),arb(0))
        if not inertia>0:raise ArithmeticError('positive radial-domain inertia required')
        if variation:
            basis=np.full((98,61),arb(0),dtype=object)
            for j in range(61):basis[37+j,j]=eta[37+j].rad()
        for start in range(0,62,4):
            if variation:
                legs=[left[:,start:start+4,None],basis[:,None,:],delta[:,None,None]]
                values=action._contracted_action(state,legs,maps)
                matrix.extend([list(row) for row in values])
                result.extend([arb(0,sum((abs(v).upper() for v in row),arb(0)).upper()) for row in values])
            else:
                values=action._contracted_action(state,[left[:,start:start+4],eta[:,None],delta[:,None]],maps)
                result.extend(list(values))
            progress(min(start+4,62))
    return result,inertia.lower(),matrix


def run(evidence,interval,cells,selected,out,terms=None):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512
    charts,rates,step,cert,sources=parent.load(evidence,interval)
    for p in (Path(__file__),Path(parent.__file__),Path(factored.__file__),Path(sparse.__file__)):
        sources[str(p.resolve())]=inputs.sha(p)
    results=[]
    for cell in selected:
        if not 0<=cell<cells:raise ValueError('cell outside partition')
        half=2*cell//cells;frozen=cert['links'][half]
        w=[arb(fmpq(v)) for v in frozen['base_weights_exact']]
        bounds=[arb(cell)/cells,arb(cell+1)/cells]
        ops=tube.tube_operands(charts[0],charts[2],rates,step,(charts[half],charts[half+1],w,half),bounds,variation=False)
        state=np.array([v.enclosure() for v in ops['state']],dtype=object)
        delta=np.array([v.enclosure() for v in ops['displacement']],dtype=object)
        s=ops['chart_parameter'].enclosure()
        a,b=charts[half:half+2]
        left=np.full((98,62),arb(0),dtype=object)
        for i in range(62):
            for j in range(61):left[37+j,i]=a['R'][i,j]+s*(b['R'][i,j]-a['R'][i,j])
        actions={}
        for kind in ('variation','residual'):
            eta=np.array([arb(0)]*37+[
                arb(0,w[j]) if kind=='variation' else a['y'][j]+s*(b['y'][j]-a['y'][j]) for j in range(61)],dtype=object)
            cache=terms or out.with_suffix('.terms')
            cache.mkdir(parents=True,exist_ok=True)
            key_data=dict(interval=interval,cells=cells,cell=cell,kind=kind,
                sources={p:h for p,h in sources.items() if p!=str(Path(__file__).resolve())},
                numerical_kernel_SHA256=hashlib.sha256(inspect.getsource(rows_for_cell).encode()).hexdigest().upper())
            key=hashlib.sha256(inputs.encode(key_data)).hexdigest().upper()
            path=cache/(key+'.json')
            if not path.exists():
                values,inertia,matrix=rows_for_cell(state,left,eta,delta,lambda done:
                    print(json.dumps(dict(cell=cell,kind=kind,rows=done,total=62)),flush=True))
                ball=lambda v:[str(v.mid().fmpq()),str(v.rad().fmpq())]
                raw=dict(inputs=key_data,values=[ball(v) for v in values],inertia=ball(inertia),
                         matrix=[[ball(v) for v in row] for row in matrix])
                path.write_bytes(inputs.encode(raw))
                path.with_suffix('.sha256').write_text(inputs.sha(path))
            raw=json.loads(path.read_bytes())
            if raw['inputs']!=key_data or path.with_suffix('.sha256').read_text()!=inputs.sha(path):
                raise ValueError('completed contraction binding changed')
            restore=lambda p:arb(fmpq(p[0]))+arb(0,arb(fmpq(p[1])))
            values=[restore(v) for v in raw['values']];inertia=restore(raw['inertia']).lower()
            matrix=[[restore(v) for v in row] for row in raw['matrix']]
            if kind=='variation':variation_matrix=matrix
            else:residual_rows=values
            upper=max((abs(v).upper()/wi).upper() for v,wi in zip(values,w,strict=True))
            actions[kind]=dict(upper=inputs.number(upper),signed_row_balls=[
                [str(v.mid().fmpq()),str(v.rad().fmpq())] for v in values],inertia_lower_exact=str(inertia.fmpq()))
        old=lambda k:arb(fmpq(frozen[k]['exact']))
        qbase=(old('complete_centerline_defect_base_upper')+arb(fmpq(actions['variation']['upper']['exact']))).upper()
        Y=(old('residual_upper_in_base_weights')+arb(fmpq(actions['residual']['upper']['exact']))).upper()
        # Rebalance only the eigenpair witness. Keep the already certified
        # Layer-A center-line box inside every proposal.
        minimum=arb(fmpq(frozen['eigenpair_witness_scale_exact']))
        M=np.zeros((62,62))
        exact_M=[]
        # Variation is first; preserve its matrix before residual evaluation.
        for i,row in enumerate(variation_matrix):
            exact_M.append([(abs(x).upper()/w[i]).upper() for x in row]+[arb(0)])
            for j,x in enumerate(exact_M[-1]):M[i,j]=float(x)
        Yrows=[(abs(v).upper()/wi+old('residual_upper_in_base_weights')).upper()
               for v,wi in zip(residual_rows,w,strict=True)]
        q0=old('complete_centerline_defect_base_upper')
        Rfull=np.array([[a['R'][i,j]+s*(b['R'][i,j]-a['R'][i,j]) for j in range(62)] for i in range(62)],dtype=object)
        minimum_r=np.array([(wi*minimum).upper() for wi in w],dtype=object)
        radii=minimum_r.copy();attempts=[];passed=False
        Yphysical=[(wi*y).upper() for wi,y in zip(w,Yrows)]
        for attempt in range(100):
            t=[(ri/wi).upper() for ri,wi in zip(radii,w)]
            nl=nonlinear_eigenpair_variation(Rfull,radii)
            variation=[(w[i]*(q0*max(t)+sum((exact_M[i][j]*t[j] for j in range(62)),arb(0)))+nl[i]).upper() for i in range(62)]
            q=max((v/ri).upper() for v,ri in zip(variation,radii))
            image=max(((v+y)/ri).upper() for v,y,ri in zip(variation,Yphysical,radii))
            passed=bool(q<1 and image<1)
            if passed or attempt==99:
                attempts.append(dict(attempt=attempt,q=inputs.number(q),image=inputs.number(image)))
                break
            proposal=np.array([max(rmin,(arb('1.02')*(v+y)).upper())
                for rmin,v,y in zip(minimum_r,variation,Yphysical)],dtype=object)
            if max(float(ri/wi) for ri,wi in zip(proposal,w))>2**50:
                attempts.append(dict(attempt=attempt,q=inputs.number(q),image=inputs.number(image),proposal_limit_reached=True))
                break
            radii=proposal
        result=dict(cell=cell,tau_exact=[str(v.fmpq()) for v in bounds],half_chart=half,
            radial_actions=actions,scaled_absolute_variation_matrix=[[str(v.fmpq()) for v in row] for row in exact_M],
            complete_scaled_residual_rows=[str(v.fmpq()) for v in Yrows],
            witness_scale_upper_exact=[str(v.fmpq()) for v in t],
            witness_radii_exact=[str(v.fmpq()) for v in radii],
            q=inputs.number(q),image=inputs.number(image),attempts=attempts,
            minimum_inclusion_margin_exact=str(min((ri-v-y).lower() for ri,v,y in zip(radii,variation,Yphysical)).fmpq()),
            original_centerline_witness_contained=all(ri>=rmin for ri,rmin in zip(radii,minimum_r)),
            certified=passed,failure_category=None if passed else 'INSUFFICIENT_OFF_CENTER_ENCLOSURE')
        results.append(result)
        print(json.dumps(dict(cell=cell,certified=result['certified'],q=float(q),image=float(image))),flush=True)
    payload=dict(algorithm='REBALANCED_LOCAL_HERMITE_TUBE_OPERATOR_V1',interval=interval,partition_cells=cells,
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
    p.add_argument('--reuse-terms',type=Path)
    a=p.parse_args();run(a.evidence_root.resolve(),a.interval,a.cells,a.selected or list(range(a.cells)),a.out.resolve(),a.reuse_terms)
