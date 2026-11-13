"""MP ordinary one-form Gram moments on the same changing real cell.

The remaining one-form Gram blocks are the already evaluated covariant
gradient pairing B and its transpose. This calculation does not recompute B,
select a new field history, or certify scalar/native/outgoing operators.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'audits')]
import bhsm_changing_lorenz_mp_coefficient_values_20261016 as owner
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

OWNER_SHA = '1b0a9713749feb062fecdb664598a7a5b3528bd72ec5aa18176ae88eb5b88eff'


def ordinary_point(metric, radial, tent):
    """Literal positive covector pairing, BEFORE the full I80 lift."""
    mu, gt, gr, gs, beta, radius = metric
    g = owner.tensor.zeros((5, 5))
    g[0, 0] = gt
    g[0, 1] = g[1, 0] = -beta*gt
    g[1, 1] = gr+beta**2*gt
    for k in range(2, 5):
        g[k, k] = gs
    out = owner.tensor.zeros((10, 10))
    for i in range(2):
        for j in range(2):
            out[5*i:5*i+5, 5*j:5*j+5] = tent**2*radial[i, 0]*radial[j, 0]*g
    return out


def execute(refinement, application, output, orders, dps, time_order):
    out = Path(output).resolve()
    if out.exists():
        raise FileExistsError('Preserve every previous numerical readout')
    if sha256(Path(owner.__file__).read_bytes()).hexdigest() != OWNER_SHA:
        raise ValueError('The peer-reviewed value owner must remain frozen')
    phases, reference, frozen, E, pins = owner.load_inputs(refinement, application)
    out.mkdir(parents=True)
    arrays, records = {}, []
    with mp.workdps(dps):
        c = owner.constants()
        for side in ('incoming', 'outgoing'):
            phase = phases[side]
            length = abs(owner.m(phase['span']))
            origin = min(owner.m(phase['span']), mp.mpf(0))
            times, weights = owner.time_nodes(phase, frozen[side, 32], 'mp', time_order, dps)
            snapshots = []
            for u, w in zip(times, weights):
                t = u+origin
                raw = owner.raw_at(phase, t)
                g = owner.geometry(raw, c['WALL']/2, c)
                chart = owner.response_chart(g['delta'], c, 96, 'mp', dps)
                snapshots.append(dict(t=t, raw=raw, weight=w, chart=chart,
                                      tent=2*min(u/length, 1-u/length)))
            previous = None
            for order in orders:
                nodes, rw = owner.radial_nodes(frozen[side, order], 'mp', order, dps, c)
                total = owner.tensor.zeros((10, 10))
                independent = []
                for ri, (r, wr) in enumerate(zip(nodes, rw)):
                    basis = owner.radial_basis(r, reference, c)
                    for ti, s in enumerate(snapshots):
                        val = owner.coefficient(s['raw'], s['t'], r, side, phase.get('parent_reference'),
                                                reference, c, s['chart'], basis_data=basis)
                        point = ordinary_point(val['metric'], val['radial'], s['tent'])
                        total += wr*s['weight']*point
                        if ri in (0, order//2, order-1) and ti in (0, len(times)-1):
                            # Independent literal covector-component contraction.
                            mu, gt, gr, gs, beta, radius = val['metric']
                            worst = mp.mpf(0)
                            for i in range(10):
                                pi, ci = divmod(i, 5)
                                left = [mp.mpf(0)]*5
                                left[ci] = s['tent']*val['radial'][pi, 0]
                                for j in range(10):
                                    pj, cj = divmod(j, 5)
                                    right = [mp.mpf(0)]*5
                                    right[cj] = s['tent']*val['radial'][pj, 0]
                                    literal = (gt*(left[0]-beta*left[1])*(right[0]-beta*right[1])
                                        +gr*left[1]*right[1]+gs*mp.fsum(left[k]*right[k] for k in range(2, 5)))
                                    worst = max(worst, abs(literal-point[i, j]))
                            independent.append(dict(radial_index=ri, time_index=ti,
                                                    literal_max_absolute=mp.nstr(worst, 65)))
                tag=f'{side}_radial{order}'
                arrays[tag+'_ordinary_Gram10']=owner.tensor.as_float(total)
                records.append(dict(side=side, radial_order=order,
                    temporal_order_per_half=time_order, anchored_response_order=96,
                    full_unrounded_MP_adjacent_rule=(owner.mp_compare(previous,total) if previous is not None else None),
                    all100_unrounded_MP_entries=[[mp.nstr(x,65) for x in row] for row in total],
                    literal_covector_controls=independent,
                    positive_component_pairing='gt*(a0-beta*a1)*(b0-beta*b1)+gr*a1*b1+gs*sum_a a_a*b_a',
                    full_ordinary_dimension=800, exact_identity_factor_dimension=80,
                    identity_internal_dimension=4, identity_harmonic_dimension=20,
                    fields_and_reference_coordinates_held=True))
                previous=total
                print(json.dumps(dict(completed=tag, time_order=time_order, dps=dps)),flush=True)
    _compressed_npz(out/'ordinary_Gram.npz',arrays)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and (name.startswith('bhsm.') or name.startswith('bhsm_')) and Path(p).is_relative_to(ROOT):
            pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for rel,h in pins.items():
        if sha256((ROOT/rel).read_bytes()).hexdigest()!=h:
            raise ValueError('Consumed source changed: '+rel)
    result=dict(classification='MP_ORDINARY_COVECTOR_GRAM_ON_SAME_AFFINE_REAL_CELL',
        records=records,arithmetic_dps=dps,
        source_and_owner_sha256=dict(sorted(pins.items())),
        original_TIME6_archive_sha256=owner.tensor.TIME6_SHA,
        numerical_sha256=sha256((out/'ordinary_Gram.npz').read_bytes()).hexdigest(),
        complete_1120_Gram='[[Goo,B[:,:800]^T],[B[:,:800],B[:,800:1120]]]',
        existing_B_recomputed=False, scalar80_added_to_one_form_Gram=False,
        physical_source_or_domain_derivatives_evaluated=False,
        complete15_form_or_native_convergence=False,
        physical_outgoing_derivative_at_2e_minus10=False,
        coupled_matching_corrections_applied=0,physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',
                                  encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--refinement',required=True);p.add_argument('--application',required=True)
    p.add_argument('--output',required=True);p.add_argument('--orders',nargs='+',type=int,default=[64,128])
    p.add_argument('--dps',type=int,default=80);p.add_argument('--time-order',type=int,default=6)
    a=p.parse_args()
    if a.dps<65 or a.time_order<6 or any(q not in (32,64,128) for q in a.orders):
        raise ValueError('Declared retained rules and meaningful precision required')
    execute(a.refinement,a.application,a.output,a.orders,a.dps,a.time_order)
