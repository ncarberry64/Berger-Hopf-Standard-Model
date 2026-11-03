"""Action pole graph -> local weighted current product; no physical section chosen."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import argparse,json,math
import numpy as np
from prepare_evidence import save,npz
HERE=Path(__file__).resolve().parent

def add(a,b):
    out=[Q(0)]*max(len(a),len(b))
    for p in (a,b):
        for j,x in enumerate(p):out[j]+=x
    return out
def mul(a,b):
    out=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out
def shifted(p,start):
    out=[Q(0)]*len(p)
    for n,c in enumerate(p):
        for j in range(n+1):out[j]+=c*math.comb(n,j)*Q(start)**(n-j)
    return out
def exact_checks():
    # Polynomial certificates on all n>=n0, not a finite harmonic screen.
    branches=[('n+1',0,[1,1]),('-n-2',0,[-2,-1]),('n',1,[0,1]),('-n-1',1,[-1,-1])]
    certificates={}
    for name,start,a in branches:
        ap1=add(a,[Q(3,4)]);gap=add([48*x for x in mul(ap1,ap1)],[0,-50,-25])
        coefficients=shifted(gap,start)
        assert all(x>=0 for x in coefficients)
        certificates[name]=dict(n_min=start,coefficients_in_n_minus_nmin=[str(x) for x in coefficients])
        # |A+1/2| <= (6/5)|A+3/4|, all four branches.
        ratio=add([36*x for x in mul(ap1,ap1)],[-25*x for x in mul(add(a,[Q(1,2)]),add(a,[Q(1,2)]))])
        shifted_ratio=shifted(ratio,start)
        assert all(x>=0 for x in shifted_ratio)
        certificates[name]['angular_remainder_ratio_certificate']=[str(x) for x in shifted_ratio]
    # Q=partial_r-(A-1/4)/r, gap min |A+3/4|=5/4.
    # Aterm+B=||Qw||^2; radial energy<=Aterm+(16/25)B,
    # angular energy<=(48/25)B. Thus gradient^2 <= (64/25)||Qw||^2.
    checks={
        'radial_cross_integration':Q(1)-Q(2)+Q(1),
        'cone_gradient_bound_constant':Q(16,25)+Q(48,25)-Q(64,25),
        'weighted_conjugated_indicial_shift':Q(3,4)-Q(1)+Q(1,4),
        'weighted_gradient_constant':Q(64,25)-Q(8,5)**2,
        # Talenti m4,p2 extremizer integral on normalized Haar, not a physical state.
        'Sobolev_Haar_constant_squared':Q(1,12)/Q(2,3)**2-Q(3,16),
        'weighted_product_constant_squared':Q(3,16)*Q(8,5)**4-Q(768,625),
        'canonical_density_weight_match':Q(2)*3-4-(3-Q(1)),
        'weak_native_scalar_dual_Hardy_constant':Q(2,5)**2-Q(4,25),
    }
    # u_eps=r^-1 scaling of arbitrary smooth compact annular core sections.
    # These are operator homogeneities, never a manufactured physical packet.
    dilation=dict(L2_squared=Q(4)-2,first_graph_squared=Q(4)-4,
                  current_weighted_squared=Q(3)-4,weighted_graph_squared=Q(4)-Q(1,2)-4)
    assert dilation==dict(L2_squared=Q(2),first_graph_squared=Q(0),current_weighted_squared=Q(-1),weighted_graph_squared=Q(-1,2))
    assert all(v==0 for v in checks.values())
    return {k:str(v) for k,v in checks.items()},certificates,{k:str(v) for k,v in dilation.items()}

def calculate():
    e=HERE/'evidence';prov=json.loads((e/'provenance.json').read_text())
    assert sha256((e/'inputs.npz').read_bytes()).hexdigest()==prov['input_sha256']
    b=dict(np.load(e/'inputs.npz',allow_pickle=False));r=b['radial_nodes49']
    N,R,C,beta=b['original_coframe49x4'].T
    m=C*R**3/r**3;delta=r*C/R-1;theta_angular=1.5*abs(delta)
    # No V0 bound is supplied: theta_angular is only a lower bound for theta.
    refined=HERE/'refined_evidence';rp=json.loads((refined/'provenance.json').read_text())
    assert sha256((refined/'inputs.npz').read_bytes()).hexdigest()==rp['input_sha256']
    extra=dict(np.load(refined/'inputs.npz',allow_pickle=False));profile=extra['profile_coefficients51x17'][:49]
    assert np.array_equal(extra['points51'][:49],r)
    f,ft,fr,st,sr=profile[:,10],profile[:,11],profile[:,12],profile[:,13],profile[:,14]
    h4=profile[:,7];s0=(st-beta*sr)/N;s4=sr/C
    normal_square=s4*s4-s0*s0;valid=(normal_square>0)&(s4>0)
    # No continuation of a positive real norm through a null/timelike sigma normal.
    n0=np.full(49,np.nan);n4=np.full(49,np.nan);mass=np.full(49,np.nan)
    root=np.sqrt(normal_square[valid]);n0[valid]=-s0[valid]/root;n4[valid]=s4[valid]/root
    f0=(ft-beta*fr)/N;f4=fr/C
    mass[valid]=-(n0[valid]*f0[valid]+n4[valid]*f4[valid])/np.tan(f[valid])
    G=extra['gauge36'];Gamma=b['Gamma36'];I=np.eye(36)
    M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    Ai=extra['gauge_values49x5x4'][:,2:]+(b['density49x8'][:,5]-1)[:,None,None]*M
    Ar=extra['gauge_values49x5x4'][:,1]
    Gar=np.einsum('nc,cij->nij',Ar,G);Gai=np.einsum('nac,cij->naij',Ai,G)
    V=np.zeros((2,49,36,36),complex);nu=np.zeros((2,49))
    recombination=0.;eta_recombination=0.
    for j,eps in enumerate((-1,1)):
        for k in range(49):
            # The retained action uses the combined eta contact through the
            # sigma-null transitions; no unit-grad-sigma chart is substituted.
            eta=-1j/np.tan(f[k])*(Gamma[0]*f0[k]+eps*Gamma[4]*f4[k])
            inverse=1j*eps*C[k]*Gamma[4]
            reduced_eta=eps*C[k]/np.tan(f[k])*Gamma[4]@Gamma[0]*f0[k]-C[k]/np.tan(f[k])*f4[k]*I
            eta_recombination=max(eta_recombination,float(np.max(abs(inverse@eta-reduced_eta))))
            angular=sum(Gamma[a+1]@Gai[k,a] for a in range(3))
            gauge=Gar[k]-eps*C[k]/R[k]*Gamma[4]@angular
            V[j,k]=C[k]*h4[k]*I+inverse@eta-I/(2*r[k])+gauge
            nu[j,k]=r[k]*np.linalg.norm(V[j,k],2)
            spin=Gamma[1]@Gamma[2]@Gamma[3]
            A0=-I/2-1.5*eps*Gamma[4]@spin
            actual=C[k]*h4[k]*I+inverse@eta+Gar[k]-eps*C[k]/R[k]*Gamma[4]@(angular-1.5*spin)
            recovered=-A0/r[k]-delta[k]*(A0+I/2)/r[k]+V[j,k]
            recombination=max(recombination,float(np.max(abs(actual-recovered))))
    eta_angular=1.2*abs(delta);eta_full=eta_angular[None]+.8*nu
    fail=np.flatnonzero(np.any(eta_full>=1,axis=0))
    d=b['density49x8'];c=np.sqrt(d[:,3]/d[:,0]);nr=np.sqrt(d[:,2]/d[:,0])
    checks=dict(owned_time_to_radius=float(np.max(abs(N/R-c))),
                owned_time_to_radial=float(np.max(abs(N/C-nr))),
                volume_ratio_positive=float(max(0.,-m.min())))
    checks.update(profile_coframe_match=float(np.max(abs(profile[:,:4]-b['original_coframe49x4']))),
       sigma_normal_unit=float(np.max(abs(n0[valid]**2-n4[valid]**2+1))),
       complete_saved_spatial_body_recombination=recombination,
       combined_eta_material_time_placement=eta_recombination)
    assert max(checks.values())<2e-11
    exact,cert,dilation=exact_checks()
    result=dict(schema='bhsm.muon-weighted-current-regularity.v69',
      classification='LOCAL_WEIGHTED_D5_CURRENT_PRODUCT_CONSTRUCTION_AND_GRAPH_LIMITATION',
      exact_identity_checks=exact,all_degree_angular_certificates=cert,
      dilation_exponents=dilation,numeric_checks=checks,maximum_numeric_defect=max(checks.values()),
      normalized_Haar_Sobolev_L4_squared_constant=math.sqrt(3)/4,
      cone_weighted_product_coefficient=16*math.sqrt(3)/25,
      source_formula='j_phi=m rho^3 v V_phi u; ||j_phi||_L2(rho^-4) <= m_plus sqrt(3)/4 H(v) H(u), H(u)=||grad(rho^-1/4 u)||_L2(rho^3).',
      right_graph_bound='H(u)<=8/[5(1-eta)] ||rho^-1/4 P u||, eta=(6/5)delta_sup+(4/5)nu_sup<1; alternatively retain V0u as a lower-order source without requiring its smallness.',
      independent_left_graph_estimate_transferred=False,
      unweighted_first_graph_uniformly_controls_current=False,
      physical_current_norm=None,physical_native_remainder_norm=None,
      geometry_sample_m_min=float(m.min()),geometry_sample_m_max=float(m.max()),
      geometry_sample_delta_max=float(abs(delta).max()),geometry_sample_theta_angular_max=float(theta_angular.max()),
      geometry_sample_refined_angular_relative_max=float(eta_angular.max()),
      sigma_normal_spacelike_on_saved_nodes=bool(np.all(valid)),sigma_normal_invalid_indices=np.flatnonzero(~valid).tolist(),
      combined_eta_used_on_all_nodes=True,sigma_chart_failure_not_a_causal_obstruction=True,
      geometry_sample_full_relative_max=float(np.nanmax(eta_full)),
      geometry_sample_spatial_V0_norm_max=float(np.nanmax(nu/r[None])),
      angular_only_criterion_failure_indices=fail.tolist(),
      first_sample_angular_obstruction_rho=None if not len(fail) else float(r[fail[0]]),
      whole_saved_cap_sufficient_criterion_excluded=bool(len(fail)),
      sample_scope='Initializer samples only, both orientation signs; original combined eta used through both known sigma-null transitions. Failures exclude only the all-small-remainder sufficient criterion. The inhomogeneous V0u estimate remains available. Passing samples are not continuum suprema or physical admission.',
      native_source_contract='The strong radial-return route would require the complete bulk a-div b in weighted L2. The original weak-form alternative below avoids that extra requirement. Actual edge conormal b.nu plus event/product-domain/relative contacts remains separate.',
      strong_native_density_norm_is_required_by_physics=False,
      alternative_native_weak_source_bound='On the regular zero-trace electric core, ||J_native||_V* <= 2/(5 sqrt(kappa_min)) ||a||_L2(rho^-4) + ||(b_r/sqrt(k),b_i/sqrt(e))||_L2; actual graph/edge contacts require their own trace-dual norm. This avoids demanding derivatives of b in strong L2.',
      physical_columns_realized=False,physical_event_graph_realized=False,complete_matched_residual=None,
      physical_guard=2e-10,method_tolerance=2e-11,temporal_baseline=2**-9,physical_a_mu=None,total_physical_uncertainty=None,
      new_resolution=False,new_quadrature=False,new_history_steps=0,new_heat_integrals=0,
      next_obligation='Construct the weighted material-time/entering jets of the prescribed columns and independent left data on the actual trace graph; then apply the full same-domain native kernel/current and edge contacts. This local product estimate neither constructs those data nor declares a new physical selection rule.')
    return dict(radial_nodes49=r,density_ratio49=m,cone_angular_deviation49=delta,
                angular_remainder_lower_bound49=theta_angular,refined_angular_relative49=eta_angular,
                sigma_normal_square49=normal_square,sigma_normal_valid49=valid,
                complete_saved_spatial_V0_2x49x36x36=V,spatial_V0_scaled_norm2x49=nu,
                full_relative_bound_sample2x49=eta_full),result
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Preserve previous output')
    a,r=calculate();args.out.mkdir();npz(args.out/'weighted_current_regularities.npz',a);save(args.out/'result.json',r)
    print(json.dumps({k:r[k] for k in ('maximum_numeric_defect','cone_weighted_product_coefficient','geometry_sample_refined_angular_relative_max','geometry_sample_full_relative_max','sigma_normal_spacelike_on_saved_nodes','whole_saved_cap_sufficient_criterion_excluded')}))
if __name__=='__main__':main()
