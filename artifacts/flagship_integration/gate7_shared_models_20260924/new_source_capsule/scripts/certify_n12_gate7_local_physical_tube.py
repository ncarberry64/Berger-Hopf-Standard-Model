"""Extend frozen Layer-A moving charts over the actual dense history image.

Only new radial off-center D3 contractions are evaluated. Identity and D4
center-line work are imported. Cells partition time, never physical radii.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_shared_connecting_hessian as inputs
from bhsm.interface import shared_physical_tube as tube


def load(evidence, interval):
    base = evidence/'artifacts/flagship_integration'
    package = ROOT/'artifacts/flagship_integration'
    frozen = (package/'gate7_shared_eigenbranch_links_20260923' if interval == 13 else
              package/'gate7_child_atlas_20260924'/f'interval_{interval:03d}')
    source = {str((frozen/'certificate.json').resolve()): inputs.sha(frozen/'certificate.json')}
    cert = json.loads((frozen/'certificate.json').read_bytes())
    receipt = json.loads((frozen/'reproduction.json').read_bytes())
    if source[str((frozen/'certificate.json').resolve())] != receipt['certificate_SHA256']:
        raise ValueError('frozen Layer A binding differs')
    if not receipt['byte_identical'] or not cert['connected_eigenbranch_evaluation_cover_certified']:
        raise ValueError('frozen Layer A authority required')
    rows = []
    names = [f'.affine_eigenpair_pilot_work/endpoint_{interval:03d}',
             f'.coupled_midpoint_eigenpair_pilot_work/interval_{interval:03d}',
             f'.affine_eigenpair_pilot_work/endpoint_{interval+1:03d}']
    for name in names:
        record, path = inputs.import_domain(base/name, 'eigenpair.npz', source)
        if cert['source_SHA256'][str(path.resolve())] != inputs.sha(path):
            raise ValueError('chart data differs from frozen Layer A')
        with np.load(path, allow_pickle=False) as z:
            x,y,R = [inputs.read_array(z,k) for k in ('center_state','eigenpair_center','preconditioner')]
            row = dict(x=x,y=y,R=arb_mat(62,62,list(R.flat)))
            if name.startswith('.affine'):
                D=inputs.read_array(z,'affine_directions')
                radii=[arb(fmpq(v)) for v in cert['radius_exact']]
                row['scaled']=[[D[i,j]*radii[j != 0] for j in range(75)] for i in range(98)]
            rows.append(row)
    p=Path(inputs.action.ENDPOINT).with_suffix('.npz')
    source[str(p.resolve())]=inputs.sha(p)
    with np.load(p,allow_pickle=False) as z:
        weights=[arb(float(v)) for v in z['state_weights']]
        step=arb(float(z['collocation_arc_parameters'][interval+1]-z['collocation_arc_parameters'][interval]))
    rates=[]
    for n in (interval,interval+1):
        record,path=inputs.import_domain(base/f'.coupled_normalized_physical_value_work/endpoint_{n:03d}', 'value.npz',source)
        if (not record['report']['validation_passed'] or not record['report']['uniform_physical_value_enclosed']
                or not record['report']['positive_physical_G_norm']
                or [record['radius_longitudinal_rational'],record['radius_transverse_rational']] != cert['radius_exact']):
            raise ValueError('complete original-domain endpoint field required')
        with np.load(path,allow_pickle=False) as z:
            rate=inputs.read_array(z,'rate_candidate')
            if rate.shape != (99,):raise ValueError('complete descriptor rate required')
            rates.append([rate[i]/weights[i] for i in range(98)])
    mr,mp=inputs.import_domain(base/f'.coupled_hs_midpoint_domain_work/interval_{interval:03d}','domain.npz',source)
    if cert['source_SHA256'][str(mp.resolve())]!=inputs.sha(mp):
        raise ValueError('actual HS midpoint changed')
    for path,digest in source.items():
        portable=Path(path).relative_to(evidence).as_posix() if Path(path).is_relative_to(evidence) else None
        if portable and path.endswith(('value.npz','eigenpair.npz')) and '/endpoint_' in portable:
            if mr['binding']['files'].get(portable)!=digest:
                raise ValueError('dense history and HS midpoint use different endpoint inputs')
    for path in (Path(__file__),Path(tube.__file__),Path(inputs.__file__),Path(inputs.producer.__file__),
                 Path(inputs.action.__file__),ROOT/'src/bhsm/interface/history_eigenbranch_variation.py',
                 ROOT/'src/bhsm/interface/shared_action_taylor.py',ROOT/'src/bhsm/interface/factored_arb_integrand.py',
                 ROOT/'src/bhsm/interface/shared_parameter_residual.py',
                 Path(sys.modules[inputs.action.metric_data.__module__].__file__),
                 Path(sys.modules[inputs.action.standard_model_casimir_coefficient.__module__].__file__)):
        source[str(path.resolve())]=inputs.sha(path)
    return rows,rates,step,cert,source


def run(evidence,interval,cells,out):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512
    rows,rates,step,cert,sources=load(evidence,interval)
    reports=[]
    for cell in range(cells):
        half=int(2*cell//cells)
        bounds=[arb(cell)/cells,arb(cell+1)/cells]
        frozen=cert['links'][half]
        w=[arb(fmpq(v)) for v in frozen['base_weights_exact']]
        actions={}
        for kind in ('variation','residual'):
            ops=tube.tube_operands(rows[0],rows[2],rates,step,(rows[half],rows[half+1],w,half),bounds,
                                   variation=kind=='variation')
            result,inertia=inputs.producer.contract(inputs.action,ops['state'],ops['legs'],
                lambda done,total: print(json.dumps(dict(cell=cell,kind=kind,completed=done,total=total)),flush=True))
            actions[kind]=dict(upper=inputs.number(result.support()),model=inputs.model(result),
                inertia_lower_exact=str(inertia.lower().fmpq()))
        number=lambda field:arb(fmpq(frozen[field]['exact']))
        Y=(number('residual_upper_in_base_weights')+arb(fmpq(actions['residual']['upper']['exact']))).upper()
        qbase=(number('complete_centerline_defect_base_upper')+arb(fmpq(actions['variation']['upper']['exact']))).upper()
        nonlinear=number('nonlinear_defect_per_witness_scale_upper')
        original_scale=arb(fmpq(frozen['eigenpair_witness_scale_exact']))
        candidates=[]
        for power in range(31):
            scale=arb(2)**power
            if scale<original_scale:continue
            q=(qbase+scale*nonlinear).upper()
            candidates.append(((Y/scale+q).upper(),scale,q))
        image,scale,q=min(candidates,key=lambda row:row[0])
        passed=bool(image<1 and q<1)
        report=dict(cell=cell,tau_exact=[str(v.fmpq()) for v in bounds],half_chart=half,
            new_radial_contractions=actions,complete_residual_upper=inputs.number(Y),
            complete_defect_base_upper=inputs.number(qbase),witness_scale_exact=str(scale.fmpq()),
            contraction_upper=inputs.number(q),image_upper=inputs.number(image),
            frozen_centerline_witness_contained=bool(scale>=original_scale),
            physical_tube_chart_certified=passed,
            failure_category=None if passed else 'INSUFFICIENT_OFF_CENTER_ENCLOSURE',
            physical_closure_boundary_demonstrated=False)
        reports.append(report)
        print(json.dumps(dict(cell=cell,passed=passed,q=float(q),image=float(image))),flush=True)
    result=dict(algorithm='LOCAL_MOVING_CHART_HERMITE_PHYSICAL_TUBE_ARB512_V1',interval=interval,
        cells=reports,radius_exact=cert['radius_exact'],
        full_dense_image_eigenchart_cover=all(r['physical_tube_chart_certified'] for r in reports),
        domain='Cubic Hermite image of both original endpoint affine domains and paired uniform endpoint rate enclosures; state and rate errors shared across each cell.',
        overlap_rule='Within each half, shared-time witnesses have the same center and proportional weights, hence nested boxes. At tau=1/2 both contain the frozen complete actual-HS midpoint eigenbox.',
        Layer_A_frozen_commit='452c80a7',Layer_A_recomputed=False,new_endpoints=0,
        original_physical_radii_changed=False,complete_physical_rate_authority=False,
        signed_local_remainder_assembled=False,kappa_L=None,kappa_T=None,Gate7_closed=False,
        source_SHA256=sources)
    if any(inputs.sha(Path(p))!=h for p,h in sources.items()):raise RuntimeError('source changed during evaluation')
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as stream:stream.write(inputs.encode(result))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--interval',type=int,choices=range(13,19),required=True)
    p.add_argument('--cells',type=int,choices=(2,4,8,16,32),default=2)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.interval,a.cells,a.out.resolve())
