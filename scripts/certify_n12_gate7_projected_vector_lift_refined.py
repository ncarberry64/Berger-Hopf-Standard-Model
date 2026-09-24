"""Lift the saved physical scalar to every output row by exact descriptor elimination.

All rows retain one common Taylor domain. No new action evaluation is needed.
This proves a fixed-direction midpoint vector enclosure, not endpoint transport.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
from bhsm.interface.shared_parameter_residual import linear_support
import bhsm.interface.shared_action_taylor as implementation
import evaluate_n12_gate7_coupled_residual_saved as saved


def restore(pair):
    mid, radius = pair
    r = Fraction(radius)
    if r.denominator & (r.denominator-1):
        raise ValueError('exact dyadic radius required')
    exponent = 1-r.denominator.bit_length()
    value = arb(arb(mid), (r.numerator, exponent))
    if str(value.rad().fmpq()) != radius:
        value = arb(arb(mid), (2*r.numerator-1, exponent-1))
    if str(value.mid().fmpq()) != mid or str(value.rad().fmpq()) != radius:
        raise ArithmeticError('exact saved ball restoration failed')
    return value


def encode_model(model):
    return [[str(v.mid().fmpq()), str(v.rad().fmpq())]
            for v in [model.c, *model.a.entries(), model.r]]


def upper(value):
    value = value.upper()
    return dict(exact=str(value.fmpq()), approximate=float(value))


def norm(values):
    return sum((abs(v).upper()**2 for v in values), arb(0)).sqrt().upper()


def dot(a, b):
    return sum((x*y for x,y in zip(a,b,strict=True)), arb(0))


def evaluate(root, scalar_path, coefficients_path):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    verified = saved.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p, cert = base.p, base.p.values.cert
    scalar = json.loads(scalar_path.read_bytes())
    exported = json.loads(coefficients_path.read_bytes())
    if (scalar.get('family') != 'midpoint' or scalar.get('parameters') != 497
            or exported.get('certificate_SHA256') != saved.sha(scalar_path)
            or any(scalar['source_hashes'].get(k) != v
                   for k,v in verified['paired_source_hashes'].items())):
        raise ValueError('original shared midpoint scalar and physical sources required')
    if scalar['source_hashes']['shared_action_taylor'] != saved.sha(Path(implementation.__file__)):
        raise ValueError('original Taylor arithmetic required')
    data = root/'tmp/bhsm_midpoint_center_mean_value_right_pair_20260913/value/first/column.npz'
    eigenfile = root/'artifacts/flagship_integration/.coupled_midpoint_eigenpair_pilot_work/interval_013/eigenpair.npz'
    with np.load(data,allow_pickle=False) as z, np.load(eigenfile,allow_pickle=False) as e:
        centers = [saved.read_matrix(z, f'point_center_{i}',center=True) for i in range(7)]
        ep = saved.read_matrix(e,'eigenpair_center',center=True)
        center = saved.read_matrix(e,'center_state',center=True)
        directions = saved.read_matrix(z,'weighted_tube_directions')
        axis = saved.read_matrix(z,'weighted_input_axis',center=True)
        raw_domain = saved.read_matrix(z,'raw_domain')
        point = saved.read_matrix(z,'point_derivative')
    ninput, nparam = 249,497
    groups = verified['families']['midpoint']['groups']+[(249,497,'box')]
    domain = TaylorDomain(groups,nparam)
    if list(map(list,domain.groups)) != scalar['groups'] or scalar['groups'] != exported['groups']:
        raise ValueError('same original shared domain required')
    values = [restore(v) for v in exported['models']['physical_scalar']]
    if hashlib.sha256(saved.encoded(exported['models']['physical_scalar'])).hexdigest().upper() != scalar['physical_scalar']['coefficients_SHA256']:
        raise ValueError('physical scalar coefficient fingerprint mismatch')
    W = Taylor(domain,values[0],arb_mat(1,nparam,values[1:-1]),values[-1])
    original_radii = [arb(v) for v in scalar['correction_radii_exact']]
    radii = original_radii.copy()
    # Integrate the saved same-family derivative minus the affine predictor
    # derivative. These correction radii tighten the solution enclosure,
    # never the physical input domain. Point-solve uncertainty is retained.
    with np.load(data,allow_pickle=False) as z:
        for block,derivative_index in ((0,4),(1,5),(2,6)):
            point_solve=saved.read_matrix(z,f'point_solve_{block}')
            derivative=saved.read_matrix(z,f'uniform_solve_{derivative_index}')
            for i in range(62):
                candidate=(abs(point_solve[i,0]-centers[block][i,0]).upper()
                    +linear_support([derivative[i,j]-centers[derivative_index][i,j]
                                     for j in range(ninput)],groups[:-1])).upper()
                index=62*(block+1)+i
                radii[index]=min(radii[index],candidate)
    coefficients=W.a.entries()
    for i,(new,old) in enumerate(zip(radii,original_radii,strict=True)):
        if old.is_zero():
            if not new.is_zero():raise ArithmeticError('zero original correction radius')
        else:coefficients[ninput+i]*=new/old
    W=Taylor(domain,W.c,arb_mat(1,nparam,coefficients),W.r)
    def model(c, derivatives, rows, offset):
        result=[]
        for i in range(rows):
            a=[derivatives[i,j] for j in range(ninput)]+[arb(0)]*248
            a[ninput+offset+i]=radii[offset+i]
            result.append(domain.affine(c[i,0],a))
        return result
    psi=model(ep,centers[3],61,0)
    hard=model(centers[0],centers[4],62,62)
    psi_u=model(centers[1],centers[5],62,124)
    hard_u=model(centers[2],centers[6],62,186)
    _,weights,_,_,_=p.values.operands()
    qw,rw,_,_=cert.metric_data()
    weights,qw,rw=[[arb(float(v)) for v in vv] for vv in (weights,qw,rw)]
    state=[domain.affine(center[i,0],[directions[i,j]/weights[i] for j in range(ninput)]+[arb(0)]*248)
           for i in range(98)]
    if any(not raw_domain[i,0].contains(v.enclosure()) for i,v in enumerate(state)):
        raise ArithmeticError('original physical state domain must contain shared model')
    raw_axis=[axis[i,0]/weights[i] for i in range(98)]
    s=domain.affine(raw_domain[98,0].mid(),[directions[98,j] for j in range(ninput)]+[arb(0)]*248)
    su=axis[98,0]
    configuration=[qw[i]*state[37+i] for i in range(37)]
    configuration_u=[qw[i]*raw_axis[37+i] for i in range(37)]
    N=[s*x for x in configuration]+[rw[i]*(hard[61]*psi[i]+s*hard[i]) for i in range(61)]
    Nu=[su*x+s*y for x,y in zip(configuration,configuration_u)]
    Nu += [rw[i]*(hard_u[61]*psi[i]+hard[61]*psi_u[i]+su*hard[i]+s*hard_u[i]) for i in range(61)]
    length=(dot(N,N).log()/2).exp()
    inner=dot(N,Nu)
    numerator=[Nu[i]/length-N[i]*inner/(length**3) for i in range(98)]
    residual=p.geometry.residual
    with base.cache.cache_hashes([(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]):
        local=base.reader.load_inputs(13)
    P=base.matrix(local['frozen_right']).solve(base.matrix(local['test']))
    axesfile=root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axesfile,allow_pickle=False) as z:
        axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None]
    axes[0]=0
    if hashlib.sha256(np.asarray(axes,dtype='<f8').tobytes()).hexdigest().upper()!=local['binding']['axes_SHA256']:
        raise ValueError('frozen projection mismatch')
    a=[arb(float(x)) for x in axes[14]]
    Q=arb_mat(74,74,[arb(i==j)-a[i]*a[j] for i in range(74) for j in range(74)])
    L=Q*P*(2*arb(float(local['step']))/3)
    if L[73,98].contains(0):
        raise ArithmeticError('descriptor pivot must be nonzero')
    anchor=L*point
    models=[]
    rows=[]
    for i in range(74):
        ratio=arb(1) if i==73 else L[i,98]/L[73,98]
        # The descriptor coordinate vanishes by the exact ratio identity.
        # The pivot row itself is identically the certified scalar.
        complement=domain.affine(0) if i==73 else dot([L[i,j]-ratio*L[73,j] for j in range(98)],numerator)
        value=ratio*W+complement
        difference=value-anchor[i,0]
        models.append(difference)
        rows.append(dict(component=f'projected_row_{i:02d}',center=[str(anchor[i,0].mid().fmpq()),str(anchor[i,0].rad().fmpq())],
            linear=upper(difference.linear_bound()),nonlinear_remainder=upper(difference.r),
            anchor_difference=upper(abs(difference.c)),total_radius=upper(difference.support()),
            descriptor_projection_multiplier=[str(ratio.mid().fmpq()),str(ratio.rad().fmpq())],
            complement_linear=upper(complement.linear_bound()),complement_remainder=upper(complement.r),
            dominant_uncertainty_source='nonlinear remainder' if difference.r>difference.linear_bound() else 'linear correction/input support',
            scope='midpoint fixed direction; endpoint transport still required'))
    # Bounds are taken only after the complete shared output model is formed.
    linear_row_norm=norm([v.linear_bound() for v in models])
    nonlinear_norm=norm([v.r for v in models])
    constant_norm=norm([v.c for v in models])
    total=min(norm([v.support() for v in models]),(constant_norm+linear_row_norm+nonlinear_norm).upper())
    p.verify_sources(json.loads((data.parent/'record.json').read_bytes())['binding'])
    return dict(algorithm='MEAN_VALUE_CORRECTION_REFINED_SHARED_VECTOR_LIFT_ARB512_V2',
        source_commit='b33d94e4eaa94b6be9d7ca423d45205a23f5e797',
        physical_target='(2*dt/3)*Q*P*DF(Z_M(theta))*w0; all 74 rows, one fixed input direction',
        domain_fingerprint=scalar['binding'],parameters=nparam,groups=domain.groups,
        physical_projection_fingerprint=local['binding']['axes_SHA256'],
        projection_matrix_SHA256=hashlib.sha256(saved.encoded([[str(v.mid().fmpq()),str(v.rad().fmpq())] for v in L.entries()])).hexdigest().upper(),
        correction_radii_exact=[str(v.fmpq()) for v in radii],
        original_correction_radii_exact=scalar['correction_radii_exact'],
        correction_refinement='same-family integral of uniform solve derivative minus saved predictor slope',
        scalar_nonlinear_remainder_unchanged=True,components=rows,vector_norm=dict(anchor_deviation=upper(total),linear=upper(linear_row_norm),nonlinear=upper(nonlinear_norm),constant=upper(constant_norm)),
        shared_models=[encode_model(v) for v in models],
        shared_model_encoding='per row: constant, 497 common linear coefficients, nonlinear remainder; rational midpoint/radius pairs',
        exact_descriptor_elimination=True,all_output_rows_retained=True,original_domain_unchanged=True,
        inherited_same_family_solution_boxes=True,full_vector_enclosure_rigorous=True,
        endpoint_transport_certified=False,complete_local_column_certified=False,
        physical_global_margin=None,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_hashes={**verified['paired_source_hashes'],'scalar':saved.sha(scalar_path),'coefficients':saved.sha(coefficients_path),
                       'evaluator':saved.sha(Path(__file__)),'shared_action_taylor':saved.sha(Path(implementation.__file__))})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--scalar',type=Path,required=True)
    parser.add_argument('--coefficients',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    ctx.prec=512
    if args.out.exists():raise FileExistsError('use a fresh output path')
    result=evaluate(args.evidence_root.resolve(),args.scalar.resolve(),args.coefficients.resolve())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('xb') as f:f.write(saved.encoded(result))
    print(json.dumps(dict(vector_norm=result['vector_norm'],worst_row=max(range(74),key=lambda i:result['components'][i]['total_radius']['approximate']))),flush=True)


if __name__=='__main__':main()
