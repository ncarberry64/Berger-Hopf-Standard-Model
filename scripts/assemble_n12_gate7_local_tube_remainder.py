"""Complete interval-13 HS remainder and its isolated causal kappa screen.

All 99 output rows, non-affine midpoint incidence, signed LL/LT booking,
and the frozen causal-map perturbation are included. Coordinate boxing
may make this rigorous upper enclosure useless; it cannot prove growth.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx,fmpq
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_local_ball_rate_jet as rate
from bhsm.interface.shared_hs_physical_pullback import signed_hs_second,composed_rate_second
inputs=rate.inputs


def norm(v):return sum((abs(x).upper()**2 for x in v),arb(0)).sqrt().upper()
def matrix(a):return arb_mat(a.shape[0],a.shape[1],[arb(float(x)) for x in a.flat])


def run(evidence,work,out):
    if out.exists():raise FileExistsError('fresh output required')
    ctx.prec=512;sources={};jets={};base=evidence/'artifacts/flagship_integration'
    for site in ('left','middle','right'):
        p=work/f'interval13_ballrate_{site}_first.json';r=work/f'interval13_ballrate_{site}_repeat.json'
        if p.read_bytes()!=r.read_bytes():raise ValueError('independent mixed-rate reproduction required')
        z=json.loads(p.read_bytes())
        if z['site']!=site or z['interval']!=13 or not z['all_16_moving_descriptor_terms']:
            raise ValueError('same complete interval-13 jets required')
        for path,digest in z['source_SHA256'].items():
            if inputs.sha(Path(path))!=digest:raise ValueError('rate operand changed')
        jets[site]=[rate.unpair(v) for v in z['rate_jets']['uv']]
        for path in (p,r):sources[str(path.resolve())]=inputs.sha(path)
    radii=[arb(fmpq(x)) for x in z['radius_exact']]
    header,p=inputs.import_domain(base/'.coupled_midpoint_uniform_df_work/interval_013','derivative.npz',sources)
    if not header['report']['uniform_physical_first_derivatives_enclosed']:raise ValueError('actual HS midpoint DF required')
    with np.load(p,allow_pickle=False) as a:A=inputs.read_array(a,'derivative')
    endpoint=base/'BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
    jacobian=base/'BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz'
    inverse=base/'BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz'
    causal=base/'BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz'
    foundation=base/'BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE.json'
    foundation_record=json.loads(foundation.read_bytes())
    if not foundation_record['validation_passed'] or foundation_record['coverage']!=dict(intervals=370,nodes=371,complete=True):
        raise ValueError('complete frozen map arithmetic lemma required')
    for path in (endpoint,jacobian,inverse,causal):
        if inputs.sha(path)!=foundation_record['inputs'][path.relative_to(evidence).as_posix()]:
            raise ValueError('frozen map operand changed')
    with np.load(endpoint,allow_pickle=False) as a:h=arb(float(a['collocation_arc_parameters'][14]-a['collocation_arc_parameters'][13]))
    with np.load(jacobian,allow_pickle=False) as a:tangent=a['endpoint_physical_tangent_action'][14].copy()
    with np.load(inverse,allow_pickle=False) as a:right=matrix(a['reduced_right_Newton_blocks'][13])
    test=matrix(inputs.action._frame(tangent,inputs.action.TEST_DESCRIPTOR_SCALE).T)
    B=right.solve(test)
    with np.load(causal,allow_pickle=False) as a:maps=a['causal_maps_center'].copy()
    axes_path=evidence/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axes_path,allow_pickle=False) as a:axes=a['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None];axes[0]=0
    ah=lambda a:hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest().upper()
    if ah(maps)!=foundation_record['causal_maps_SHA256'] or ah(axes)!=foundation_record['axes_SHA256']:
        raise ValueError('frozen causal-map/axis identity changed')
    msecond=[h*(x-y)/8 for x,y in zip(jets['left'],jets['right'])]
    incidence=list((arb_mat(99,99,list(A.flat))*arb_mat(99,1,msecond)).entries())
    residual=signed_hs_second(h,jets['left'],composed_rate_second(jets['middle'],incidence),jets['right'])
    unbooked=-(B*arb_mat(99,1,residual))
    folder=base/'.direct_physical_quadratic_source_work/interval_013'
    manifest=json.loads((folder/'manifest.json').read_bytes());receipt=json.loads((folder/'reproduction.json').read_bytes())
    if receipt['manifest_SHA256']!=inputs.sha(folder/'manifest.json') or not receipt['byte_identical'] or not receipt['independent_recomputation']:
        raise ValueError('booked point-source lemma reproduction required')
    booked=[arb(0)]*74
    for family in ('LL','LT'):
        for pair in ('00','01','10','11'):
            p=folder/f'{family}_{pair}.npz';rp=p.with_suffix('.json');record=json.loads(rp.read_bytes())
            if (record['data_SHA256']!=inputs.sha(p) or record['interval']!=13 or record['family']!=family
                    or record['endpoint_pair']!=pair or not record['taylor_half_included']
                    or record['axes_SHA256']!=foundation_record['axes_SHA256']
                    or record['causal_maps_SHA256']!=foundation_record['causal_maps_SHA256']):
                raise ValueError('matching booked half-Hessian required')
            for path in (p,rp):
                digest=manifest['files'][path.relative_to(evidence).as_posix()]
                if digest not in (inputs.sha(path),hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest().upper()):
                    raise ValueError('booked source not in manifest')
                sources[str(path.resolve())]=inputs.sha(path)
            with np.load(p,allow_pickle=False) as a:Q=inputs.read_array(a,'Q')
            for i in range(74):
                # Enclose the signed booked FUNCTION on the same u/v domain.
                # LL differentiates to 2Q; LT has two distinct input orders.
                upper=(2*radii[0]**2*abs(Q[i,0]).upper() if family=='LL' else 4*radii[0]*radii[1]*norm(Q[i]))
                booked[i]+=arb(0,upper.upper())
    source=unbooked-arb_mat(74,1,booked)
    G=arb_mat(74,74,[arb(i==j) for i in range(74) for j in range(74)])
    maximum=[arb(0),arb(0)];node_bounds=[]
    for node in range(14,371):
        if node>14:G=matrix(maps[node-1])*G
        value=G*source;e=arb_mat(74,1,[arb(float(v)) for v in axes[node]])
        longitudinal=(e.transpose()*value)[0,0]
        transverse=list((value-e*longitudinal).entries())
        bounds=[abs(longitudinal).upper(),norm(transverse)]
        maximum=[max(a,b) for a,b in zip(maximum,bounds)]
        node_bounds.append(dict(node=node,projected_bounds=[inputs.number(v) for v in bounds]))
    al,at=[arb(float(v)) for v in foundation_record['fixed_axis_projection_norms_upper']]
    gain=arb(float(foundation_record['frozen_map_perturbation_gain_upper']))
    error=(gain*(al*maximum[0]+maximum[1])/(1-gain)).upper()
    kappa=[((maximum[0]+al*error)/radii[0]).upper(),((maximum[1]+at*error)/radii[1]).upper()]
    ledger_path=ROOT/'artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json'
    ledger=json.loads(ledger_path.read_bytes())
    targets=[min(2*arb(fmpq(row['remaining_normalized_self_map_allowance']['exact'])),
                 arb(fmpq(row['remaining_derivative_row_allowance']['exact']))).lower() for row in ledger['rows']]
    for p in (endpoint,jacobian,inverse,causal,foundation,axes_path,folder/'manifest.json',folder/'reproduction.json',
              ledger_path,Path(__file__),Path(rate.__file__),Path(signed_hs_second.__globals__['__file__'])):
        sources[str(p.resolve())]=inputs.sha(p)
    result=dict(algorithm='INTERVAL13_COMPLETE_BOXED_SIGNED_REMAINDER_CAUSAL_SCREEN_V1',interval=13,
        radius_exact=z['radius_exact'],source_SHA256=sources,full_99_HS_source=[rate.pair(v) for v in residual],
        midpoint_second_incidence=[rate.pair(v) for v in msecond],
        signed_local_remainder=[rate.pair(v) for v in source.entries()],
        full_midpoint_Am_muv_term=True,booked_LL_LT_function_subtracted=True,booked_Hessian_factor_two=True,
        interval14_mask_applicable=False,all_357_causal_destination_nodes_included=True,
        node_bounds=node_bounds,frozen_map_error_upper=inputs.number(error),
        isolated_interval_kappa_upper=[inputs.number(v) for v in kappa],
        sufficient_framework_targets_lower_exact=[str(v.fmpq()) for v in targets],
        enclosure_viable=all(k<t for k,t in zip(kappa,targets)),
        classification='COMPLETE_ISOLATED_UPPER_ENCLOSURE_NOT_A_GLOBAL_KAPPA',
        limitation='Coordinate boxing loses shared signed cancellations before causal support. Failure of this upper screen proves neither physical growth nor impossibility of contraction.',
        global_kappa_L=None,global_kappa_T=None,Gate7_closed=False)
    if any(inputs.sha(Path(p))!=h for p,h in sources.items()):raise RuntimeError('source changed')
    out.write_bytes(inputs.encode(result));print(json.dumps(dict(kappa_upper=[float(v) for v in kappa],viable=result['enclosure_viable'])))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.work.resolve(),a.out.resolve())
