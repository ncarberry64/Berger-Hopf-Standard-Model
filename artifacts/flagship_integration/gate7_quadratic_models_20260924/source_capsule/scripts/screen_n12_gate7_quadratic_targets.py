"""Combine/book/transport the selected prototype, never a full-kappa claim."""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from flint import arb,arb_mat,ctx,fmpq

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_expression_graph import restore,pair
from bhsm.interface.sparse_quadratic_enclosure import QuadraticDomain,QuadraticStore,QuadraticModel,accumulate,clean
from bhsm.interface.shared_quadratic_booking import projected_booking
from bhsm.interface.block_quadratic_expansion import expand_batched
from bhsm.interface.quadratic_group_support import grouped_range
from assemble_n12_gate7_shared_remainder import operands,matrix


def number(x):
    return dict(exact=str(x.fmpq()),approximate=float(x))


def describe(d,c,a,q,r):
    interval,blocks=grouped_range(d,c,a,q)
    poly=abs(interval).upper()
    midpoint={k:v.mid() for k,v in q.items()}
    radii={k:v.rad() for k,v in q.items() if not v.rad().is_zero()}
    central,_=grouped_range(d,c.mid(),{k:v.mid() for k,v in a.items()},midpoint)
    uncertainty,_=grouped_range(d,c.rad(),{k:v.rad() for k,v in a.items()},radii)
    return dict(support_upper=number((poly+r).upper()),polynomial_support_upper=number(poly),
                residual_scalar_tail=number(r),retained_monomials=len(q),blocks=blocks,
                canonical_coefficient_l2_upper=number(sum((abs(v).upper()**2 for v in q.values()),arb(0)).sqrt().upper()),
                symmetric_matrix_frobenius_upper=number(sum((abs(v).upper()**2/(1 if i==j else 2)
                                                             for (i,j),v in q.items()),arb(0)).sqrt().upper()),
                midpoint_polynomial_support_upper=number(abs(central).upper()),
                coefficient_uncertainty_support_upper=number(abs(uncertainty).upper()))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--compiled',type=Path,required=True)
    p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();ctx.prec=512
    data=json.loads(args.compiled.read_bytes())
    if data['scope']!='targets' or data['frozen_checkpoint']!='cef38b6b':
        raise ValueError('complete selected-target numerical compilation required')
    d=QuadraticDomain([tuple(g) for g in data['groups']],450,QuadraticStore(data['quadratic_circuit_file']))
    def decode(row):
        return QuadraticModel(d,restore(row['c']),{i:restore(v) for i,v in row['a']},row['q'],
                              arb(fmpq(row['qb'])),{k:arb(fmpq(v)) for k,v in row['tails'].items()})
    models={n:decode(row) for n,row in data['target_circuit_models'].items()}
    atlas,A,h,B,maps,axes,foundation,booking,sources=operands(args.evidence_root)
    if atlas['radius_exact']!=data['radius_exact']:raise ValueError('unchanged radii required')
    rL,rT=[arb(fmpq(v)) for v in data['radius_exact']]
    # A fixed, predeclared projection: frozen affine maximum L destination.
    # This is a selected-source screen, not a new kappa_L or a lower bound.
    G=arb_mat(74,74,[arb(i==j) for i in range(74) for j in range(74)])
    for node in range(15,371):G=matrix(maps[node-1])*G
    axis=arb_mat(74,1,[arb(float(x)) for x in axes[370]])
    projection=axis.transpose()*G
    P=projection*B
    nu=models['normalization/norm']; inv=nu.unary('inverse',1)
    b=models['response/value/61']
    metadata=json.load(gzip.open(ROOT/'artifacts/flagship_integration/gate7_shared_models_20260924/models/middle/metadata.json.gz','rt'))
    t=models['history/value/98']*b.unary('inverse',arb(fmpq(metadata['positive_border_lower_exact'])))
    dominant=sum((models[f'descriptor/J/uv/term{i}'] for i in (13,3,8)),d.model())
    descriptor=dominant*t*inv*(2*h*P[0,98]/3)
    projected={key:sum((models[f'rate/{key}/{i}']*P[0,i] for i in range(99)),d.model())
               for key in ('value','u','v')}
    normal=-(models['normalization/norm_uv']*projected['value']
             +models['normalization/norm_u']*projected['v']
             +models['normalization/norm_v']*projected['u'])*inv*(2*h/3)
    incidence=sum((models[f'nonaffine_midpoint_incidence/{i}']*P[0,i] for i in range(99)),d.model())*(2*h/3)
    selected=descriptor+normal+incidence
    print('expanding combined signed projected quadratic',flush=True)
    q=expand_batched(d.store,[(selected.q,arb(1))],d.groups,progress=lambda s:print(s,flush=True))
    if not selected.c.is_zero() or selected.a or any(not(150<=i<300<=j<450) for i,j in q):
        raise ValueError('mixed physical polynomial must use the frozen u/v namespace exclusively')
    booked=projected_booking(booking,projection,rL,rT)
    difference=q.copy()
    for key,v in booked.items():accumulate(difference,key,-v)
    difference=clean(difference)
    before=describe(d,selected.c,selected.a,q,selected.r)
    after=describe(d,selected.c,selected.a,difference,selected.r)
    booking_description=describe(d,arb(0),{},booked,arb(0))
    mass=arb(0)
    for key in q.keys() & booked.keys():
        mass+=max(arb(0),(abs(q[key]).lower()+abs(booked[key]).lower()-abs(q[key]-booked[key]).upper()).lower())
    source_ledger={}
    for name,model in [('midpoint_descriptor_three_assignments',descriptor),
                       ('complete_second_incidence',incidence),('common_border_normalization',normal)]:
        source_ledger[name]=dict(scalar_tail=number(model.r),
                                tail_classes={k:number(v.upper()) for k,v in sorted(model.tails.items())})
    raw=data['dominant_descriptor_combined']
    rawq={(i,j):restore(v) for i,j,v in raw['quadratic']}
    raw_report=describe(d,restore(raw['c']),{i:restore(v) for i,v in raw['a']},rawq,arb(fmpq(raw['residual_scalar_tail'])))
    frozen_remainder_path=ROOT/'artifacts/flagship_integration/gate7_shared_models_20260924/signed_remainder.json'
    framework=json.loads(frozen_remainder_path.read_bytes())
    sources[str(frozen_remainder_path.resolve())]=hashlib.sha256(frozen_remainder_path.read_bytes()).hexdigest().upper()
    target_L=arb(fmpq(framework['sufficient_framework_targets_lower_exact'][0]))
    normalized_selected=(arb(fmpq(after['support_upper']['exact']))/rL).upper()
    implicit={k:v for k,v in metadata['leaf_provenance'].items() if v.get('role')=='new_implicit_remainder'}
    raw_tails={k:arb(fmpq(v)) for k,v in raw['residual_sources'].items()}
    dominant_tail=max(raw_tails,key=lambda k:raw_tails[k].upper())
    result=dict(frozen_checkpoint='cef38b6b',Gate7_closed=False,physical_budget_debit=False,
                full_interval_compiled=False,full_kappa_recomputed=False,physical_failure_established=False,
                classification='CASE_1 = NUMERICAL_COMPILER_CORRELATION_LOSS',
                frozen_kappa_L_upper=2.98824e10,frozen_kappa_T_upper=5.77960e12,
                projection=dict(causal_destination=370,kind='frozen_longitudinal_axis',
                                scope='selected prototype sources under frozen center causal maps only; not a complete interval remainder',
                                causal_map_error_correction_applied=False),
                raw_dominant_descriptor=dict(OLD_sum_affine_scalar_tails=data['OLD_approximate'],
                                             NEW=raw_report,reduction_factor=float(arb(fmpq(data['OLD_sum_frozen_affine_scalar_tails']))
                                                 /arb(fmpq(raw_report['support_upper']['exact']))),
                                             residual_sources={k:number(v) for k,v in sorted(raw_tails.items())},
                                             dominant_residual_source=dominant_tail),
                projected_selected_before_booking=before,projected_selected_after_booking=after,
                sufficient_framework_comparison=dict(
                    scope='selected-source center-map screen, not kappa_L_interval13',
                    normalized_support_upper=number(normalized_selected),
                    normalized_scalar_tail=number((selected.r/rL).upper()),
                    sufficient_L_target_lower=number(target_L),
                    selected_upper_below_sufficient_L_target=bool(normalized_selected<target_L)),
                booked_LL_LT=booking_description,
                booking_comparison=dict(common_monomials=len(q.keys() & booked.keys()),
                    guaranteed_coefficient_l1_cancellation_lower=number(mass.lower()),
                    change_in_reported_support_upper=float(arb(fmpq(before['support_upper']['exact']))
                                                          -arb(fmpq(after['support_upper']['exact']))),
                    note='Support-upper differences are diagnostic improvements, not physical budget debits.'),
                projected_source_tail_ledger=source_ledger,
                normalization_first_products_retained=True,complete_99_component_second_incidence_retained=True,
                parameter_order=data['parameter_order'],groups=data['groups'],radius_exact=data['radius_exact'],
                input_compilation_SHA256=hashlib.sha256(args.compiled.read_bytes()).hexdigest().upper(),
                source_SHA256=sources,implicit_correction_leaf_provenance=implicit,
                first_missing_representation_object={
                    'object':'shared mixed bordered-resolvent correction jet for eigenline and response',
                    'formula':'delta_z_uv = ((I - E(theta))^(-1) - I) R rhs_uv(theta,u,v), E(theta) = I - R B(theta)',
                    'frozen_leaf_formula':'w_i*q/(1-q)*norm_w(R rhs)',
                    'requirement':'Retain a common parameter-dependent correction operator and its signed mixed action, including the response/eigenline/common-border coupling; a q norm and per-row scalar balls do not specify these coefficients.',
                    'frozen_midpoint_example_leaf_ids':{'eigenline_row_0':17172972,'response_row_0':20485749},
                    'dominant_raw_tail_class':dominant_tail,
                    'status':'q-based correlation loss dominates the raw descriptor ledger; this missing object is not reconstructed here.'
                              if dominant_tail=='q_implicit_correction' else 'Inspect the reported dominant residual class.'})
    args.out.parent.mkdir(parents=True,exist_ok=True)
    polynomial_path=args.out.with_name(args.out.stem+'_polynomial.json.gz')
    polynomial=dict(parameter_order=data['parameter_order'],groups=data['groups'],
                    c=pair(selected.c),a=[[i,pair(v)] for i,v in sorted(selected.a.items())],
                    quadratic_after_booking=[[i,j,pair(v)] for (i,j),v in sorted(difference.items())],
                    booked_quadratic=[[i,j,pair(v)] for (i,j),v in sorted(booked.items())],
                    r=str(selected.r.fmpq()),projection=result['projection'],frozen_checkpoint='cef38b6b')
    with polynomial_path.open('wb') as rawfile,gzip.GzipFile(filename='',mode='wb',fileobj=rawfile,mtime=0) as archive:
        archive.write(json.dumps(polynomial,sort_keys=True,separators=(',',':')).encode()+b'\n')
    result['polynomial_archive_SHA256']=hashlib.sha256(polynomial_path.read_bytes()).hexdigest().upper()
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    d.store.db.commit()
    print(json.dumps(dict(raw_OLD=data['OLD_approximate'],raw_NEW=raw_report['support_upper']['approximate'],
                         projected_NEW=after['support_upper']['approximate'],tail=float(selected.r))),flush=True)


if __name__=='__main__':main()
