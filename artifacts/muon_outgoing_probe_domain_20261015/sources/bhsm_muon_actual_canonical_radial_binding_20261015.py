"""Separate actual-response convergence observations from shifted-chart drift."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from flint import acb,acb_mat,arb,ctx


def run(base,output):
    base,out=Path(base).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    pins={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    old=read(base/'binding_run_1.json')
    a,b=base/'actual_canonical_polynomials_run_1',base/'actual_canonical_polynomials_run_2'
    pair={}
    for name in ('result.json','actual_canonical_and_original336_polynomials.npz'):
        if (a/name).read_bytes()!=(b/name).read_bytes():raise ValueError('Independent actual-polynomial reconstruction differs')
        pair[name]=sha256((a/name).read_bytes()).hexdigest()
    md=read(a/'result.json');packet=read(a/'actual_canonical_and_original336_polynomials.npz')
    ctx.prec=256
    def mat(a):return acb_mat([[acb(arb(float(v.real)),arb(float(v.imag)))for v in row]for row in a])
    def mid(a):return np.array([[complex(a[i,j].real.mid(),a[i,j].imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
    def poly(high,low,u):
        value=acb_mat(high.shape[1],high.shape[2])
        for h,l in zip(high[::-1],low[::-1]):value=value*acb(u)+mat(h)+mat(l)
        return value
    validations=[]
    for order in (128,192):
        folder=base/f'order{order}_field_run_1'
        for path in sorted(folder.glob('cell_*_one_sided_node.npz'))+sorted(folder.glob('cell_*_same_stage_retarded_n1_midpoint.npz')):
            z=read(path);stage=int(z['stage']);sigma=float(z['node'])/4 if 'node'in z else float(z['sigma'])
            piece=2 if stage==1 else(0 if sigma<=.25 else 1)
            lo,hi=((0.,.25),(.25,.5),(.5,1.))[piece];u=(sigma-lo)/(hi-lo)
            observed={}
            for name,key in (('canonical_z','canonical'),('original_field336','field')):
                p=f'order{order}_piece{piece}_{name}'
                value=poly(packet[p+'_high'],packet[p+'_low'],u)
                if name=='canonical_z':
                    reference=mat(np.concatenate([z[k+'_high']for k in ('free_position196','free_momentum196')],axis=0))+mat(np.concatenate([z[k+'_low']for k in ('free_position196','free_momentum196')],axis=0))
                else:reference=mat(z['actual_total_field336_high'])+mat(z['actual_total_field336_low'])
                delta=mid(value-reference);norm=max(np.linalg.norm(mid(value)),np.linalg.norm(mid(reference)))
                observed[key]=dict(absolute_max=float(np.max(abs(delta))),
                    relative=float(np.linalg.norm(delta)/norm)if norm else 0.)
            validations.append(dict(order=order,file=path.name,piece=piece,metrics=observed))
    actual=max(md['max_actual_z_polynomial_coefficient_relative'],md['max_actual_full336_polynomial_coefficient_relative'],
        old['comparisons'][-1]['max_full336_field_relative'],old['comparisons'][-1]['max_full336_rate_relative'],
        old['comparisons'][-1]['max_canonical_endpoint_relative'])
    errors=max(v['metrics'][k]['relative']for v in validations for k in ('canonical','field'))
    result=dict(classification='ACTUAL_FINITE_RESPONSE_RADIAL_QUADRATURE_STABILIZATION_WITH_SHIFTED_CHART_CAVEAT',
        actual_response_128_to192_relative_max=actual,actual_response_stabilization_target=2e-10,
        actual_response_observed_stabilization_pass=bool(actual<=2e-10),
        shifted_w_polynomial_relative=md['retained_failed_shifted_w_comparison'],
        broad_all_reported_including_shifted_w_criterion_pass=md['broad_all_reported_criterion_from_prior_binding_pass'],
        actual_polynomial_reconstruction=md,actual_polynomial_sample_reconstruction_checks=validations,
        maximum_polynomial_to_original_MP_sample_relative=errors,
        reconstruction_validation_arithmetic='MP256 Horner of published high/low coefficients, subtract saved high/low samples in MP before reporting midpoint norms; avoids cancellation of the large first-piece At coefficients in ordinary floating Horner.',
        reconstruction_sample_checks_meet_2e_minus_10=bool(errors<=2e-10),
        independent_actual_polynomial_reconstruction_pair=dict(left=str(a),right=str(b),files=pair),
        repeat_pairs=old['repeat_pairs']+[dict(kind='actual_canonical_algebraic_reconstruction',order='128_and_192',left=str(a),right=str(b),files=pair)],
        prior_ten_independent_repeat_pairs=old['repeat_pairs'],prior_binding_sha256=sha256((base/'binding_run_1.json').read_bytes()).hexdigest(),
        claim_scope='Observed stabilization of the same original frozen finite radial basis and piecewise-stage retarded response under radial quadrature refinement. Shifted w=z-B1Q is quadrature-dependent and its reported 3.94e-8 comparison fails; actual z and full336 polynomials are reconstructed separately. Neither criterion supplies an outward continuum/Galerkin/exterior error bound.',
        physical_outgoing_energy_field_response_evaluated=False,physical_radial_convergence_established=False,
        physical_full_derivative_passed=False,physical_two_spin_normalization=None,muon_magnetic_moment=None,
        coupled_matching_corrections_applied=0,new_integrations_in_this_postprocessing=0,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_hashes=pins)
    for p,h in pins.items():
        if sha256(Path(p).read_bytes()).hexdigest()!=h:raise ValueError('Input changed during reconstruction binding')
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(out.read_bytes()).hexdigest(),actual_response_relative=actual,
        sample_reconstruction_relative=errors,actual_response_pass=actual<=2e-10,shifted_w_pass=False)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.base,a.output)
