"""Prescribed finite-pair moment bound and covariant regular-pole source domain.

No physical columns, occupations, entering port flux or native source is filled.
The quadrature values below concern only v66's already-owned velocity load.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
import argparse,json,math
import numpy as np
from prepare_evidence import save,npz
HERE=Path(__file__).resolve().parent
def maxabs(x):return float(np.max(abs(x)))

def exact_identities():
    # D_r P=-F, Re<P,A_r P>=0. Set I=integral r^-6|P|^2,
    # J=integral r^-4|F|^2, C=integral r^-5 Re<P,F>,
    # B=[r^-5|P|^2]_0^R. The action pole power is six.
    # Integration by parts: C=-(5 I+B)/2.
    # integral r^-4|F+(5/2)P/r|^2=J+25/4 I+5 C.
    square_I=F(25,4)-F(25,2);square_B=-F(5,2)
    checks={
      'Hardy_square_I_coefficient':square_I+F(25,4),
      'Hardy_square_boundary_coefficient':square_B+F(5,2),
      'Hardy_return_norm_constant':F(4,25)*F(25,4)-1,
      'radial_jump_sign':F(-1)+F(1),
      'finite_source_weight_exponent_relation':2*F(4)-4-4,
      'weighted_flux_Cauchy_Schwarz_primitive':F(1,5)*5-1,
    }
    # Addition kernels for normalized Haar: (n+1) U_n(1)=(n+1)^2.
    U={0:F(1),1:F(2)}
    for n in (2,3):U[n]=2*U[n-1]-U[n-2]
    dimensions={n:(n+1)*U[n] for n in (1,3)}
    checks['n1_reproducing_diagonal']=dimensions[1]-4
    checks['n3_reproducing_diagonal']=dimensions[3]-16
    checks['twenty_mode_reproducing_diagonal']=sum(dimensions.values())-20
    assert all(v==0 for v in checks.values()),checks
    return {k:str(v) for k,v in checks.items()}

def calculate():
    p=HERE/'evidence';prov=json.loads((p/'provenance.json').read_text())
    assert sha256((p/'inputs.npz').read_bytes()).hexdigest()==prov['input_sha256']
    assert sha256((p/'adopted_pair.npz').read_bytes()).hexdigest()==prov['git_pair_sha256']
    b=dict(np.load(p/'inputs.npz',allow_pickle=False));pair=dict(np.load(p/'adopted_pair.npz',allow_pickle=False))
    rho=pair['pair_Fock_density16'];N=pair['one_body_occupation4']
    sign=np.diag([1.,1.,-1.,-1.]);S=N@sign
    eig=np.linalg.eigvalsh(S);trace_norm=float(np.sum(abs(eig)))
    # Only the inherited exact-pair coefficients needed for the new norm are used.
    checks={
      'adopted_pair_trace':float(abs(np.trace(rho)-1)),
      'adopted_signed_current_weights':maxabs(S-np.diag([.5,.5,-.5,-.5])),
      'signed_operator_selfadjoint':maxabs(S-S.conj().T),
      'signed_current_trace_norm':abs(trace_norm-2),
      'signed_identity_trace':float(abs(np.trace(S))),
    }
    # Known v66 forcing regularity, with no new nodes or physical source values.
    r=b['radial_nodes49'][:-1];w=b['radial_weights'];K=b['known_canonical_Gauss_load49x4x20x4x8'][:-1]
    weighted=np.einsum('n,nchpA,nchpA->pA',w/r**4,K,K)
    # This is a fixed-rule diagnostic of J, not a certified continuum integral.
    hardy_quadrature=(4/25)*weighted
    component=np.einsum('n,nchpA,nchpA->chpA',w/r**4,K,K)
    checks['known_forcing_norm_component_sum']=maxabs(np.sum(component,axis=(0,1))-weighted)
    alpha=float(b['alpha']);forcing_power=4+alpha;flux_power=5+alpha
    exponent=2*forcing_power-4
    assert forcing_power>1.5 and exponent>-1 and flux_power>2.5
    old=json.loads((p/'v67_result.json').read_text())
    assert old['charged_rank18']==12 and old['neutral_rank18']==6
    bounds=np.array([trace_norm*math.sqrt(d) for d in (4,16,20)])
    result=dict(schema='bhsm.muon-pair-flux-domain.v68',
      classification='CONDITIONAL_FINITE_PAIR_CHARGE_ENCLOSURE_AND_COVARIANT_POLE_FLUX_DOMAIN',
      numeric_checks=checks,maximum_numeric_defect=max(checks.values()),exact_identity_checks=exact_identities(),
      adopted_pair_sha256=prov['git_pair_sha256'],adopted_pair_recovered_from_commit=prov['git_commit'],
      signed_pair_eigenvalues=eig.tolist(),signed_pair_trace_norm=trace_norm,
      unitary_complete_Cauchy_condition_required=True,independent_left_response_bounded=False,
      source_moment_norm_bounds=dict(n1=float(bounds[0]),n3=float(bounds[1]),n1_plus_n3=float(bounds[2])),
      source_bound_scope='Exact relative finite-pair one-body source on an isometrically realized complete canonical Cauchy domain; not inherited/native load, independent-left response, pointwise density, edge trace or physical realization.',
      normal_homogeneous_pole_flux='Zero on the owned finite-energy regular pole if the covariant flux has a trace; not zero on an entering/event port.',
      Hardy_squared_return_bound_constant='4/25',Hardy_energy_bound='integral |P|^2/k <= 4/(25 kappa_minus) integral |F_total|^2/rho^4',
      projected_wall_flux_squared_bound_factor=(16/15)*(math.pi/2)**5,
      projected_wall_flux_bound='||Q_20(W)||_2 <= sqrt(16/3)*W^(5/2)/sqrt(5)*||F_total||_L2(rho^-4); genuine regular pole and complete common angular domain only.',
      Hardy_domain_condition='k>=kappa_minus rho^6>0; compact real radial connection with unitary transport; F_total in L2(rho^-4); genuine regular pole; all angular/edge/source terms retained.',
      known_v66_forcing_pole_order=forcing_power,known_v66_flux_pole_order=flux_power,
      known_v66_weighted_source_integrability_exponent=exponent,
      known_v66_weighted_source_quadrature_min=float(weighted.min()),known_v66_weighted_source_quadrature_max=float(weighted.max()),
      known_v66_scaled_Hardy_quadrature_max=float(hardy_quadrature.max()),
      quadrature_scope='Existing 48-node diagnostic of known v66 direct-velocity component only; no continuum error certification or physical bound inferred.',
      complete_matched_source_weighted_norm=None,physical_kappa_minus=None,physical_entering_port_flux=None,
      physical_density_realized=False,physical_retained_released_load_realized=False,
      complete_matched_density_cancellation_proved=False,inherited_density_dependence_proved=False,
      physical_a_mu=None,total_physical_uncertainty=None,physical_guard=2e-10,method_tolerance=2e-11,temporal_baseline=2**-9,
      new_resolution=False,new_quadrature=False,new_heat_integrals=0,new_history_steps=0,
      exact_remaining_obstruction='The prescribed Cauchy isometry/columns and complete native-relative source are not realized on the event-generated retained/released trace graph. Consequently the total weighted forcing norm, actual entering-port trace and surface conormal cannot be evaluated. Regular-pole elimination and finite-pair normalization do not provide these quantities.')
    assert max(checks.values())<2e-11,checks
    a=dict(signed_pair_current4=S,conditional_moment_bounds3=bounds,known_forcing_weighted_norm2_4x8=weighted,
           known_forcing_scaled_Hardy_quadrature4x8=hardy_quadrature,known_forcing_component_norm2_4x20x4x8=component)
    return a,result
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Preserve old output')
    a,r=calculate();args.out.mkdir();npz(args.out/'pair_flux_domain.npz',a);save(args.out/'result.json',r)
    print(json.dumps({k:r[k] for k in ('maximum_numeric_defect','signed_pair_trace_norm','source_moment_norm_bounds','known_v66_weighted_source_quadrature_max','complete_matched_source_weighted_norm')}))
if __name__=='__main__':main()
