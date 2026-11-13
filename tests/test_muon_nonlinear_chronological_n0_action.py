import numpy as np
from bhsm.interface.muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch,nonlinear_chronological_n0_action,chronological_field_KKT_blocks
from bhsm.interface.muon_nonlinear_n0_field_action import analytic_constant_maxwell_jet,nonlinear_n0_field_action


def test_batched_complex_literal_jet_retains_every_curvature_contact():
    rng=np.random.default_rng(693);z=lambda s:rng.normal(size=s)+.12j*rng.normal(size=s)
    A,At,Ar=[z((4,5,4))for _ in range(3)];d=z((4,5));q=analytic_constant_maxwell_batch(A,At,Ar,d)
    for r in range(4):
        a=analytic_constant_maxwell_jet(A[r],At[r],Ar[r],d[r])
        for key in('value','gradient','hessian','curvature_contact'):np.testing.assert_allclose(q[key][r],a[key],rtol=3e-14,atol=4e-14)


def test_complete_directed_neighbor_action_and_original_Gauss_match_dense_literal_application():
    rng=np.random.default_rng(825);z=lambda s:rng.normal(size=s)*.05+.01j*rng.normal(size=s)
    rep=dict(gauge_basis=rng.normal(size=(2,80,1,5,4))*.1,gauge_radial_basis=rng.normal(size=(2,80,1,5,4))*.2,
        wall_trace_map=rng.normal(size=(5,4,80))*.1,radial_quadrature=np.array([.3,.7]),
        gauge_labels=[dict(field='A_tau',internal=j%4)for j in range(16)]+
            [dict(field='A_rho'if 16<=j<20 else'A_space',internal=j-16 if 16<=j<20 else 0)for j in range(16,80)])
    # Exactly four distinct central frame slices, as in the original map.
    for j in range(16,20):rep['gauge_labels'][j]['internal']=3
    rows=[]
    for edge in range(3):
        rows.append(dict(A=z((2,5,4)),At=z((2,5,4)),Ar=z((2,5,4)),densities=z((2,5)),wall_A=z((5,4)),
            H=z((4,)),Hdot=z((4,)),weights=np.array([2,3,4])+.03j,lambda_H=.2,nu_squared_action=4,
            N=1.3+.01j,right_clock=.8+.2j,measure=.2+.01j,rows=((edge,.4,-1.2),(edge+1,.6,1.2))))
    x=z((3,84));a=nonlinear_chronological_n0_action(x,rows,rep,temporal_nodes=4,value_permutation=np.arange(84))
    b=nonlinear_n0_field_action(x.ravel(),rows,rep,temporal_nodes=4,value_permutation=np.arange(84))
    from bhsm.interface.muon_chronological_clifford_graph import chronological_dense_blocks
    H=chronological_dense_blocks(dict(K_diagonal=a['Hessian_diagonal'],K_upper=a['Hessian_upper'],K_lower=a['Hessian_lower']))
    np.testing.assert_allclose(a['gradient'].ravel(),b['gradient'],rtol=1e-13,atol=8e-14)
    np.testing.assert_allclose(H,b['hessian'],rtol=1e-13,atol=8e-14)
    np.testing.assert_allclose(a['value'],b['value'],rtol=1e-13,atol=8e-14)
    k=chronological_field_KKT_blocks(a)
    assert k['diagonal'].shape==(3,88,88)and k['At_Gauss_rows_inside_original84']
    np.testing.assert_array_equal(k['diagonal'][:,:84,:84],a['Hessian_diagonal'])
    assert len(a['Gauss_indices_per_node'])==16 and np.linalg.norm(a['initial_face_gradient'])>0
