"""Action-owned temporal charge insertion and v66 photon-dual application.

No physical sections, occupations, native bulk current or boundary flux are assigned.
The saved initializer supplies local coefficients, not an admitted Cauchy solution.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,math
import numpy as np
from prepare_evidence import npz,save

HERE=Path(__file__).resolve().parent;W=math.pi/2
EPS=np.zeros((3,3,3));EPS[0,1,2]=EPS[1,2,0]=EPS[2,0,1]=1
EPS[0,2,1]=EPS[2,1,0]=EPS[1,0,2]=-1
PAULI=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])
def ad(a):
    a=np.asarray(a);z=np.zeros(a.shape[:-1]+(4,4))
    z[...,:3,:3]=np.einsum('ijk,...j->...ik',EPS,a[...,:3])/np.sqrt(2)
    return z
def bracket(a,b):return np.einsum('...cd,...d->...c',ad(a),b)
def comm(a,b):return a@b-b@a
def integral(coeff,alpha,rho):
    powers=alpha+np.arange(4)+1;x=np.asarray(rho)/W
    return np.einsum('...m,mc->...c',W*(1-x[...,None]**powers)/powers,coeff)
def alignment(h):
    H=h[:2]+1j*h[2:];P=np.outer(H,H.conj())/np.vdot(H,H).real
    s=np.r_[-np.sqrt(2)*np.einsum('aij,ji->a',PAULI,P).real,np.sqrt(10/3)]
    Q=np.zeros((18,18),complex);Q[:12,:12]=-np.kron(P,np.eye(6));Q[12:,12:]=-np.eye(6)
    return s,Q
def maximum(x):return float(np.max(abs(x)))

def calculate():
    path=HERE/'evidence/inputs.npz';prov=json.loads((HERE/'evidence/provenance.json').read_text())
    assert sha256(path.read_bytes()).hexdigest()==prov['input_sha256']
    b=dict(np.load(path,allow_pickle=False));old=json.loads((HERE/'evidence/v66_result.json').read_text())
    rho=b['radial_nodes49'];weights=b['radial_weights'];n=len(weights)
    s=np.sqrt(16/3)*b['stabilizer_value'];sg=np.sqrt(16/3)*b['stabilizer_gradient']
    G=b['gauge36'];Jnormal=b['J36'];G18=G[:,:18,:18]
    U=b['source_return_kernel49x4x4'];J=b['kernel_integral49x4x4'];Ar=b['radial_connection49']
    phi=np.einsum('ncd,c->nd',U,s);delta_phi=np.einsum('ncd,d->nc',J,s)
    phi_in=b['inherited_transfer4x4'].T@s
    V=1j*np.einsum('nc,cij->nij',phi,G18)
    V36=1j*np.einsum('nc,cij->nij',phi,G)
    Vwall=1j*np.einsum('c,cij->ij',s,G18)
    recovered_s,Q=alignment(b['theta22'][18:22])
    Ar_rep=np.einsum('nc,cij->nij',Ar,G18)
    phi_prime=-np.einsum('ncd,d->nc',ad(Ar),s)
    Vprime=1j*np.einsum('nc,cij->nij',phi_prime,G18)
    Dphi=phi_prime+bracket(Ar,phi)
    Dv=Vprime+comm(Ar_rep,V)
    checks={
        'same_H_selected_axis':maximum(s-recovered_s),
        'gauge_antihermitian':maximum(G+G.conj().swapaxes(-1,-2)),
        'two_equal_diagonal_normal_blocks':maximum(G[:,:18,:18]-G[:,18:,18:]),
        'normal_cross_upper_zero':maximum(G[:,:18,18:]),
        'normal_cross_lower_zero':maximum(G[:,18:,:18]),
        'gauge_normal_partner_commutator':maximum(comm(G,Jnormal)),
        'temporal_Gamma0_cancellation':maximum(b['Gamma36'][0]@b['Gamma36'][0]-np.eye(36)),
        'wall_charge_from_original_H':maximum(Vwall-Q),
        'wall_negative_projector':maximum(Q@Q+Q),
        'transported_charge_hermitian':maximum(V-V.conj().swapaxes(-1,-2)),
        'normal_sum_insertion':maximum(V36[:,:18,:18]-V),
        'dual_coefficient_recovery':maximum(phi-s-delta_phi),
        'central_covector_exact':maximum(phi[:,3]-s[3]),
        'covariant_transport_defect_identity':maximum(Dv-1j*np.einsum('nc,cij->nij',Dphi,G18)),
    }
    # Check the owned representation rather than assuming SU(2) normalization.
    lie=[]
    for c in range(4):
        for d in range(4):
            unit=np.eye(4)
            lie.append(maximum(comm(G[c],G[d])-np.einsum('a,aij->ij',bracket(unit[c],unit[d]),G)))
    checks['owned_Lie_algebra']=max(lie)
    # A block identity proves the contraction for arbitrary independent left/right
    # and arbitrary normal-pair covariance; no test density is manufactured.
    block=np.zeros_like(V36);block[:,:18,:18]=V;block[:,18:,18:]=V
    checks['all_normal_channel_insertion_identity']=maximum(V36-block)
    checks['charge_insertion_commutes_normal_J']=maximum(comm(V36,Jnormal))

    # Exact all-harmonic angular nonconstancy. Numeric Gram is initializer-only.
    M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    Ai=b['gauge_values49x5x4'][:,2:]+(b['density49x8'][:,5]-1)[:,None,None]*M
    E=b['E'];lap=-np.einsum('ikl,ilj->kj',E,E)
    Dangular=bracket(Ai,phi[:,None,:])
    gram=np.einsum('nc,nc->n',phi,phi)[:,None,None]*lap
    gram=gram+np.einsum('nic,nic->n',Dangular,Dangular)[:,None,None]*np.eye(20)
    central=s[3]**2*lap
    evals=np.linalg.eigvalsh(lap)
    expected=np.r_[np.full(4,3.),np.full(16,15.)]
    checks['original_scalar_harmonic_eigenvalues']=maximum(evals-expected)
    checks['angular_E_skew']=maximum(E+E.swapaxes(-1,-2))
    checks['angular_connection_cross_term']=maximum(np.einsum('nc,nic->ni',phi,Dangular))
    # Explicit coefficient application at every saved radial point, linear size.
    for j in range(len(rho)):
        L=np.einsum('c,ihk->ichk',phi[j],E)+np.einsum('ic,hk->ichk',Dangular[j],np.eye(20))
        checks.setdefault('angular_Gram_direct_application',0.)
        checks['angular_Gram_direct_application']=max(checks['angular_Gram_direct_application'],maximum(np.einsum('ichk,ichl->kl',L,L)-gram[j]))
    # The old eight-source radial return is consumed, not recomputed.
    K=b['known_canonical_Gauss_load49x4x20x4x8']
    projected_first=-np.einsum('n,nc,nchpA->hpA',weights,delta_phi[:n],K[:n])
    checks['v66_eight_source_dual_application']=maximum(projected_first-b['photon_return_first_order'])
    checks['v66_full_affine_dual_application']=maximum(-np.einsum('n,nc,nchpA->hpA',weights,phi[:n],K[:n])-np.einsum('c,chpA->hpA',s,b['known_return']))

    # The 189 LOCAL coefficient derivatives; total physical Y needs its actual
    # background direction, independent section jets and moving-domain terms.
    phig=np.zeros((189,len(rho),4));in_g=np.zeros((189,4));angular_g=np.zeros((189,len(rho),3,4))
    P=b['pole_basis_polynomials'];alpha=float(b['alpha']);basis=b['radial_basis49x4']
    for j in range(189):
        ds=np.zeros(4);dp=np.zeros((4,4));dAi=np.zeros_like(Ai)
        if j<100:dAi=b['density_gradient49x8x100'][:,5,j,None,None]*M
        elif j<180:
            profile,local=divmod(j-100,20);field,c=divmod(local,4)
            if field==1:dp[:,c]=P[profile]
            elif field>=2:dAi[:,field-2,c]=basis[:,profile]
        elif 184<=j<188:ds=sg[:,j-184]
        dJ=ad(integral(dp,alpha,rho));dJ0=ad(integral(dp,alpha,0.))
        phig[j]=np.einsum('ncd,c->nd',U,ds)-np.einsum('ncd,c->nd',dJ,s)
        in_g[j]=b['inherited_transfer4x4'].T@ds-dJ0.T@s
        angular_g[j]=bracket(dAi,phi[:,None,:])+bracket(Ai,phig[j,:,None,:])
    B=b['orbit_value'];Bg=b['orbit_gradient']
    checks['direct_boundary_Higgs_photon_range']=maximum(B@s)
    checks['total_boundary_Higgs_range_motion']=maximum(np.einsum('acj,c->aj',Bg,s)+B@sg)
    # Independent central finite differences only for the new nontrivial axes.
    def covector_at(poly,h):
        st,_=alignment(h)
        return np.einsum('ncd,c->nd',np.eye(4)-ad(integral(poly,alpha,rho)),st)
    fd={}
    for j in (104,105,106,107,124,145,184,185,186,187):
        dp=np.zeros((4,4));dh=np.zeros(4)
        if j<180:
            profile,local=divmod(j-100,20);field,c=divmod(local,4)
            if field==1:dp[:,c]=P[profile]
        else:dh[j-184]=1
        step=2**-10
        def centered(h):
            return (covector_at(b['radial_connection_polynomial']+h*dp,b['theta22'][18:22]+h*dh)-covector_at(b['radial_connection_polynomial']-h*dp,b['theta22'][18:22]-h*dh))/(2*h)
        f=(4*centered(step/2)-centered(step))/3
        # Numerical derivative error is reported separately from exact algebra checks.
        fd[str(j)]=maximum(f-phig[j])
    tail=float(old['omitted_Dyson_orders_norm_upper'])
    rep_bound=math.sqrt(sum(np.linalg.norm(gc,2)**2 for gc in G18))
    op_tail=rep_bound*np.linalg.norm(s)*tail
    charge_eigen=np.linalg.eigvalsh(Vwall)
    result=dict(schema='bhsm.muon-propagated-photon-charge.v67',classification='EVALUATED_INITIALIZER_PHOTON_DUAL_AND_D5_TEMPORAL_INSERTION',
        consistency_checks=checks,maximum_consistency_defect=max(checks.values()),finite_difference_checks=fd,
        finite_difference_tolerance=2e-11,finite_difference_max=max(fd.values()),
        radial_nodes=len(rho),angular_modes=20,local_response_coordinates=189,
        wall_charge_eigenvalues=charge_eigen.tolist(),charged_rank18=int(np.count_nonzero(charge_eigen<-.5)),
        neutral_rank18=int(np.count_nonzero(abs(charge_eigen)<.5)),
        transported_negative_projector_floating_defect=maximum(V@V+V),
        normal_cross_channels_at_temporal_insertion=False,
        normal_diagonal_sum_still_requires_both_sections=True,
        inherited_covector=phi_in.tolist(),inherited_covector_change_norm=float(np.linalg.norm(phi_in-s)),
        inherited_flux_contraction=None,complete_bulk_current_contraction=None,complete_boundary_load_contraction=None,
        angular_central_Gram_eigenvalues=np.linalg.eigvalsh(central).tolist(),
        full_sphere_central_lower_bound=10.,
        initializer_wall_angular_Gram_eigenvalues=np.linalg.eigvalsh(gram[-1]).tolist(),
        initializer_min_angular_Gram_eigenvalue=float(np.linalg.eigvalsh(gram).min()),
        first_order_charge_operator_remainder_bound=op_tail,
        bound_scope='Omitted transport orders for the frozen v66 polynomial only, excludes floating input/source representation, quadrature, physical-state and domain errors.',
        complete_matched_Ward_cancellation_proved=False,physical_density_dependence_proved=False,
        v66_symmetry_reduced_photon_return_norm=float(np.linalg.norm(projected_first)),
        physical_guard=2e-10,temporal_baseline=2**-9,physical_event_domain_realized=False,
        physical_reconnection_proved=False,physical_a_mu=None,total_physical_uncertainty=None,
        new_resolution=False,new_quadrature=False,new_heat_integrals=0,new_history_steps=0,
        next_operand='Prescribed dressed independent-left/right diagonal normal-pair charge moments against chi_h V_phi, inherited canonical normal-flux projection, and matched retained/released boundary load on one constrained Cauchy domain; no assigned density or flux.')
    assert max(checks.values())<2e-11,checks
    assert max(fd.values())<result['finite_difference_tolerance'],fd
    arrays=dict(radial_nodes49=rho,photon_covector49x4=phi,photon_covector_first_correction=delta_phi,
        inherited_covector4=phi_in,temporal_charge_insertion49x18x18=V,wall_charge18=Vwall,
        covariant_radial_first_order_defect49x4=Dphi,
        photon_covector_gradient189x49x4=phig,inherited_covector_gradient189x4=in_g,
        angular_covector_connection49x3x4=Dangular,angular_covector_connection_gradient189x49x3x4=angular_g,
        angular_test_Gram49x20x20=gram,central_angular_test_Gram20x20=central,
        v66_projected_known_return=projected_first)
    return arrays,result

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Preserve previous output')
    a,r=calculate();args.out.mkdir();npz(args.out/'propagated_photon_charge.npz',a);save(args.out/'result.json',r)
    print(json.dumps({k:r[k] for k in ('maximum_consistency_defect','finite_difference_max','charged_rank18','neutral_rank18','initializer_min_angular_Gram_eigenvalue','first_order_charge_operator_remainder_bound','complete_bulk_current_contraction')}))

if __name__=='__main__':main()
