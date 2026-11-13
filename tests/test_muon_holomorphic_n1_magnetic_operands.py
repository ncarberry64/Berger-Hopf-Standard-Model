import numpy as np
from bhsm.interface.muon_holomorphic_n1_magnetic_operands import signed_n1_magnetic_point_operands
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_matched_mechanical_source import epsilon
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP


def _fixture():
    rng=np.random.default_rng(61287)
    names=('A_tau','A_rho','A_1','A_2','A_3');unit=np.eye(20).reshape(20,5,4)
    phi=np.array([[.3,.7,.2,.4],[.4,.5,.6,.7]])
    pr=np.array([[-.1,.3,.2,-.1],[.4,.1,.2,.3]]);wv=np.array([.2,-.1,.4,1.])
    labels=[dict(field=names[f],internal=c)for r in range(4)for f in range(5)for c in range(4)]
    at=[j for j,l in enumerate(labels)if l['field']=='A_tau']
    ids=np.array(at+[j for j in range(80)if j not in at]+list(range(80,84)))
    rep=dict(gauge_labels=labels,radial_quadrature=np.array([.4,.6]),
        gauge_basis=np.array([np.concatenate([v*unit for v in r])for r in phi])[:,:,None],
        gauge_radial_basis=np.array([np.concatenate([v*unit for v in r])for r in pr])[:,:,None],
        wall_trace_map=np.concatenate([v*np.eye(20)for v in wv],axis=1).reshape(5,4,80))
    draw=lambda shape:.04*(rng.normal(size=shape)+.3j*rng.normal(size=shape))
    row=dict(A=draw((2,5,4)),At=draw((2,5,4)),Ar=draw((2,5,4)),
        densities=np.array([[1.1+.02j,.9-.01j,.8+.01j,1.2-.03j,.07+.02j],
            [1.2-.01j,.8+.02j,.9+.03j,1.1+.04j,-.04+.01j]]),
        wall_A=draw((5,4)),H=np.array([1.1+.03j,.4-.02j,.07+.01j,.03-.01j]),
        Hdot=draw((4,)),weights=np.array([.9+.01j,1.1-.02j,.7+.005j]),lambda_H=.129,nu_squared_action=4.)
    b=dict(row=row,lifts=chronological_n0_field_lifts(rep,ids),value_permutation=ids)
    a=scalar_s3_discretization(3);labels=a['real_basis_labels']
    even=np.flatnonzero([l[0]in(0,2)for l in labels]);odd=np.flatnonzero([l[0]==1 for l in labels])
    E=a['real_angular_derivative_matrices'];Y=a['real_basis_values'];w=a['haar_weights']
    Ee=E[:,even][:,:,even];Eo=E[:,odd][:,:,odd]
    G=np.einsum('pe,p,po,ps->eos',Y[:,even],w,Y[:,odd],Y[:,odd],optimize=True)
    return rng,b,Ee,Eo,G,Y[:,even],Y[:,odd],w


def _literal_action(binding,Ys,Es,weights,directions):
    """Original unsquared signed Maxwell/H value, independent of D3 APIs."""
    row,l=binding['row'],binding['lifts'];npnt=len(weights);nr=len(l['P'])
    A=np.broadcast_to(row['A'],(npnt,nr,5,4)).copy()
    At=np.broadcast_to(row['At'],A.shape).copy();Ar=np.broadcast_to(row['Ar'],A.shape).copy()
    angular=np.zeros((3,npnt,nr,5,4),complex)
    Aw=np.broadcast_to(row['wall_A'],(npnt,5,4)).copy()
    H=np.broadcast_to(row['H'],(npnt,4)).copy();Hd=np.broadcast_to(row['Hdot'],H.shape).copy()
    dH=np.zeros((3,npnt,4),complex)
    for (field,rate),Y,E in zip(directions,Ys,Es):
        n=Y.shape[1];f=field.reshape(84,n);t=rate.reshape(84,n)
        values=Y@f.T;time=Y@t.T
        # Owned derivative_values=Y@E: derivatives act coefficient by E a.
        deriv=np.array([(Y@e)@f.T for e in E])
        A+=np.einsum('ram,pm->pra',l['P'],values).reshape(A.shape)
        At+=np.einsum('ram,pm->pra',l['Pt'],time).reshape(A.shape)
        Ar+=np.einsum('ram,pm->pra',l['Pr'],values).reshape(A.shape)
        angular+=np.einsum('ram,ipm->ipra',l['P'],deriv).reshape(angular.shape)
        Aw+=(values@l['W'].T).reshape(npnt,5,4)
        H+=values@l['hv'].T;Hd+=time@l['hv'].T
        dH+=deriv@l['hv'].T
    def bracket(a,b):
        out=np.zeros_like(np.broadcast_arrays(a,b)[0]);out[...,:3]=np.cross(a[...,:3],b[...,:3])/np.sqrt(2)
        return out
    X=At[:,:,1]-Ar[:,:,0]+bracket(A[:,:,0],A[:,:,1])
    Ft=At[:,:,2:].copy();Fr=Ar[:,:,2:].copy();B=2*A[:,:,2:].copy();eps=epsilon()
    for i in range(3):
        Ft[:,:,i]+=-angular[i,:,:,0]+bracket(A[:,:,0],A[:,:,2+i])
        Fr[:,:,i]+=-angular[i,:,:,1]+bracket(A[:,:,1],A[:,:,2+i])
    for i,j,k in np.argwhere(eps):
        B[:,:,i]+=eps[i,j,k]*(angular[j,:,:,2+k]+.5*bracket(A[:,:,2+j],A[:,:,2+k]))
    e,r,d,k,beta=row['densities'].T
    Y=Ft-beta[None,:,None,None]*Fr
    maxwell=.5*(k[None]*np.sum(X*X,axis=-1)+e[None]*np.sum(Y*Y,axis=(-2,-1))
        -r[None]*np.sum(Fr*Fr,axis=(-2,-1))-d[None]*np.sum(B*B,axis=(-2,-1)))
    maxwell=MAXWELL_TO_CAP*(maxwell@l['radial_weights'])
    T=higgs_u2_real_representation()['real_generators'];O=np.einsum('pfc,cij->pfij',Aw,T)
    temporal=Hd+np.einsum('pij,pj->pi',O[:,0],H)
    spatial=dH+np.einsum('pfij,pj->fpi',O[:,2:],H)
    wt,ws,wv=row['weights'];potential=row['lambda_H']*(np.sum(H*H,axis=1)-row['nu_squared_action'])**2
    scalar=(wt*np.sum(temporal*temporal,axis=1)-ws*np.sum(spatial*spatial,axis=(0,2))-wv*potential)/(2*np.pi**2)
    return weights@(maxwell+scalar)


def test_signed_D3_matches_independent_unsquared_complex_Haar_polarization():
    rng,b,Ee,Eo,G,Ye,Yo,w=_fixture();draw=lambda n:.025*(rng.normal(size=n)+.4j*rng.normal(size=n))
    source=np.column_stack([draw(336)for _ in range(3)]);rate=np.column_stack([draw(336)for _ in range(3)])
    a=signed_n1_magnetic_point_operands(b,source,rate,Ee,Eo,Eo,G)
    ev,et,ov,ot=draw(840),draw(840),draw(336),draw(336)
    for axis in(0,1):
        predicted=ev@a['delta_K'][axis]@ov+ev@a['delta_B_forward'][axis]@ot
        predicted+=et@a['delta_B_reverse'][axis]@ov+et@a['delta_M'][axis]@ot
        actual=0j
        for s in(-1,1):
            for e in(-1,1):
                for o in(-1,1):
                    actual+=s*e*o*_literal_action(b,(Yo,Ye,Yo),(Eo,Ee,Eo),w,
                        ((s*source[:,axis],s*rate[:,axis]),(e*ev,e*et),(o*ov,o*ot)))/8
        np.testing.assert_allclose(predicted,actual,rtol=2e-8,atol=3e-14)
    assert np.linalg.norm(a['source_H'])>0
    assert np.linalg.norm(a['source_H_coordinate_time'])>0
    assert np.linalg.norm(a['intrinsic_off_shell_DH_delta_K'])>1e-5
    assert a['delta_K'].shape==(3,840,336)
    assert np.linalg.norm(a['delta_B_forward'])>1e-5
    assert np.linalg.norm(a['delta_B_reverse'])>1e-5
    # Fixed geometry field derivative has no rate/rate coefficient motion;
    # this is an evaluated identity, not zero physical metric response.
    np.testing.assert_allclose(a['delta_M'],0,atol=1e-16)


def test_source_orientation_and_complex_linearity_are_not_adjoint_shortcuts():
    rng,b,Ee,Eo,G,Ye,Yo,w=_fixture()
    f=.03*(rng.normal(size=(336,3))+1j*rng.normal(size=(336,3)));ft=.02*f
    a=signed_n1_magnetic_point_operands(b,f,ft,Ee,Eo,Eo,G)
    z=signed_n1_magnetic_point_operands(b,1j*f,1j*ft,Ee,Eo,Eo,G)
    for key in('delta_K','delta_B_forward','delta_B_reverse','delta_M'):
        np.testing.assert_allclose(z[key],1j*a[key],rtol=2e-14,atol=2e-15)
    assert np.linalg.norm(a['delta_K'].imag)>1e-4
    assert a['source_only_derivative_orientation_adapter']
    assert not a['source_coefficients_conjugated']
