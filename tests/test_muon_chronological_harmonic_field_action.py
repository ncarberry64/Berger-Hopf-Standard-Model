import numpy as np
from bhsm.interface.muon_chronological_harmonic_field_action import analytic_homogeneous_original_field_forms
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts,nonlinear_n0_point_jet
from bhsm.interface.muon_literal_euclidean_wall_action import natural_wall_lorentz_forms
from bhsm.interface.muon_chronological_spectral_blocks import homogeneous_scalar_degree_reduction


def sample():
    rng=np.random.default_rng(1104);phi=rng.normal(size=(3,4));phir=rng.normal(size=(3,4));tracephi=rng.normal(size=4)
    basis=np.array([np.concatenate([a*np.eye(20).reshape(20,5,4)for a in p])for p in phi])[:,:,None]
    radial=np.array([np.concatenate([a*np.eye(20).reshape(20,5,4)for a in p])for p in phir])[:,:,None]
    wall=np.concatenate([a*np.eye(20)for a in tracephi],axis=1).reshape(5,4,80)
    labels=[dict(field=('A_tau','A_rho','A_1','A_2','A_3')[f],internal=c)for p in range(4)for f in range(5)for c in range(4)]
    at=[j for j,l in enumerate(labels)if l['field']=='A_tau'];dy=[j for j,l in enumerate(labels)if l['field']!='A_tau']
    ids=np.r_[at,dy,np.arange(80,84)]
    rep=dict(gauge_basis=basis,gauge_radial_basis=radial,wall_trace_map=wall,gauge_labels=labels,radial_quadrature=np.array([.15,.2,.25]))
    row=dict(A=.13*rng.normal(size=(3,5,4)),At=.04*rng.normal(size=(3,5,4)),Ar=.03*rng.normal(size=(3,5,4)),
        densities=np.tile([1.3,.8,.7,1.1,.12],(3,1)),wall_A=.12*rng.normal(size=(5,4)),
        H=np.array([.2,.8,.07,-.03]),Hdot=.02*rng.normal(size=4),weights=np.array([1.2,.7,.9]),lambda_H=.129,nu_squared_action=4.)
    return row,rep,ids,chronological_n0_field_lifts(rep,ids)


def test_original_complete_real_harmonic_rows_match_independent_literal_action():
    row,rep,ids,lifts=sample();d=homogeneous_scalar_degree_reduction(1);E=d['full_real_angular_derivatives'];z=np.zeros(84)
    a=analytic_homogeneous_original_field_forms(row,z,z,lifts,E)
    bg=dict(background_values=row['A'],background_time_derivatives=row['At'],background_radial_derivatives=row['Ar'],positive_two_form_densities=row['densities'])
    b=natural_wall_lorentz_forms(bg,rep,E,wall_connection=row['wall_A'],H=row['H'],Hdot=row['Hdot'],metric_weights=row['weights'],lambda_H=row['lambda_H'],nu_squared_action=row['nu_squared_action'])
    for x,y in zip((a['M'],a['B_forward'],a['K']),b['forms']):np.testing.assert_allclose(x,y,rtol=2e-13,atol=2e-13)
    np.testing.assert_allclose(a['B_reverse'],a['B_forward'].T,rtol=0,atol=2e-13)


def test_complex_action_coefficients_and_spectator_similarity_keep_original_dual():
    row,rep,ids,lifts=sample();rng=np.random.default_rng(2104);v=.003*(rng.normal(size=84)+1j*rng.normal(size=84));t=.002*(rng.normal(size=84)+1j*rng.normal(size=84))
    row=dict(row);row['A']=row['A']+.04j;row['densities']=row['densities']+.013j
    zero=analytic_homogeneous_original_field_forms(row,v,t,lifts,np.zeros((3,1,1)))
    literal=nonlinear_n0_point_jet(row,v,t,lifts)
    for key in('K','M'):np.testing.assert_allclose(zero[key],literal[key],rtol=2e-13,atol=2e-13)
    np.testing.assert_allclose(zero['B_forward'],literal['B'],rtol=2e-13,atol=2e-13)
    d=homogeneous_scalar_degree_reduction(1);U=np.kron(np.eye(84),d['real_to_complex_coefficient_map'])
    full=analytic_homogeneous_original_field_forms(row,v,t,lifts,d['full_real_angular_derivatives'])
    reduced=analytic_homogeneous_original_field_forms(row,v,t,lifts,d['angular_derivatives'])
    for key in('K','M','B_forward','B_reverse'):
        # Complex harmonic ordering is m-major, k spectator. Each k is the
        # same original168 field action, even on nonreal coefficient germs.
        all_complex=U@full[key]@U.conj().T
        for k in range(2):
            ix=(np.arange(84)[:,None]*4+np.arange(2)[None]*2+k).ravel()
            other=(np.arange(84)[:,None]*4+np.arange(2)[None]*2+1-k).ravel()
            np.testing.assert_allclose(all_complex[np.ix_(ix,ix)],reduced[key],rtol=3e-13,atol=3e-13)
            assert np.max(abs(all_complex[np.ix_(ix,other)]))<3e-13
    # The analytic reverse is not obtained by transposing the m-block.
    assert np.linalg.norm(reduced['B_reverse']-reduced['B_forward'].T)>1e-3
