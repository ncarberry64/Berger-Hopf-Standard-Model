"""Independent numerical/analytic controls for the separate mass likelihood."""
import copy
import numpy as np
import pytest
from scipy.linalg import cholesky,solve_triangular
from bhtracker.joint_mass import (ou_whiten,centroid_unit,amplification,trajectory,
    project_ne,KAPPA_MAS_MSUN,JointData,JointModel,fit_joint,JOINT_SCHEMA)


def test_ou_matches_dense_gaussian_and_conditional_mean():
    t=np.array([0.,.01,.01,.5,9.,9.1,40.]);sigma=np.array([.01,.02,.03,.015,.012,.011,.04])
    r=np.array([.01,-.02,.03,.01,-.01,.04,.001]);a=.023;tau=2.4
    covariance=a*a*np.exp(-abs(t[:,None]-t[None,:])/tau)+np.diag(sigma*sigma)
    dense=cholesky(covariance,lower=True);z=solve_triangular(dense,r,lower=True)
    white,logdet,mean=ou_whiten(t,sigma,r,a,tau,True)
    assert white@white==pytest.approx(z@z,rel=2e-13)
    assert logdet==pytest.approx(np.linalg.slogdet(covariance)[1]-2*np.log(sigma).sum(),abs=2e-13)
    expected=(covariance-np.diag(sigma*sigma))@np.linalg.solve(covariance,r)
    np.testing.assert_allclose(mean,expected,rtol=2e-13,atol=1e-15)


def test_ou_amplitude_cannot_remove_determinant_cost():
    t=np.arange(10.);sigma=np.full(10,.01);r=np.zeros(10)
    z,penalty=ou_whiten(t,sigma,r,.1,1.)
    assert z@z==0 and penalty>40


@pytest.mark.parametrize('g',[0.,.2,4.])
def test_centroid_independent_two_images_with_lens_light(g):
    # Lens at origin. Solve scalar image equation x^2-u*x-1=0,
    # weight signed image magnifications by absolute photon flux.
    q=np.array([[.1,.2],[2.,-.3],[-8.,4.]])
    u=np.linalg.norm(q,axis=1);direction=q/u[:,None]
    xp=(u+np.sqrt(u*u+4))/2;xm=(u-np.sqrt(u*u+4))/2
    total=(u*u+2)/(u*np.sqrt(u*u+4));fp=(total+1)/2;fm=(total-1)/2
    image_centroid=(fp*xp+fm*xm)/(total+g)
    expected=(image_centroid-u)[:,None]*direction
    np.testing.assert_allclose(centroid_unit(q,g),expected,rtol=2e-12,atol=1e-14)
    np.testing.assert_allclose(amplification(q),fp+fm,rtol=1e-15)


def test_ne_basis_and_source_minus_lens_parallax_sign():
    # At RA=Dec=0, east=y and north=z.
    np.testing.assert_allclose(project_ne(np.eye(3),0,0),[[0,0],[0,1],[1,0]],atol=1e-16)
    t=np.array([2455700.,2455800.]);earth=np.array([[.2,.5],[-.3,.8]])
    p={'t0_jd_tdb':2455700.,'tE_days':100.,'u0_heliocentric':.2,'angle_source_minus_lens_rad':.7,'pi_E':.13}
    no=dict(p,pi_E=0.)
    theta=4.;piS=.12;piL=piS+theta*p['pi_E']
    # Independent individual apparent position shifts are -piS*Earth,
    # -piL*Earth. Their difference gives +theta*piE*Earth.
    individual=(-piS*earth)-(-piL*earth)
    np.testing.assert_allclose(theta*(trajectory(t,p,earth)-trajectory(t,no,earth)),individual,atol=5e-16)
    for step in [1e-4,1e-6]:
        plus=dict(p,pi_E=p['pi_E']+step);minus=dict(p,pi_E=p['pi_E']-step)
        np.testing.assert_allclose((trajectory(t,plus,earth)-trajectory(t,minus,earth))/(2*step),earth,atol=8e-11)
    assert KAPPA_MAS_MSUN==pytest.approx(8.14385327673037,rel=2e-14)


def synthetic_document():
    # Long sparse angular baseline and a separately dense photometric peak.
    times=np.r_[np.linspace(2455480,2456100,80),np.linspace(2455740,2455790,70)]
    astro=np.linspace(2455780,2459700,24)
    return {'schema':JOINT_SCHEMA,'time_coordinate':'JD_TDB','reference_jd_tdb':2456500.,'ra_deg':267.91745833,'dec_deg':-29.89063889,
      'metadata':{'time_and_frame_provenance':'synthetic exact clock/control only','ra_axis':'EAST_TANGENT_ALPHA_COS_DEC'},
      'photometry':[{'time_jd_tdb':float(t),'magnitude':20.,'magnitude_error':.01,'instrument':'OGLE','source_row_id':f'p{i}'} for i,t in enumerate(times)],
      'astrometry':[{'exposure_midpoints_jd_tdb':[float(t)],'north_mas':0.,'east_mas':0.,'north_error_mas':.03,'east_error_mas':.03,'filter':'F814W','visit_id':str(i),'source_row_id':f'a{i}'} for i,t in enumerate(astro)]}


def test_noiseless_injection_recovery_and_zero_parallax_mass_unavailable():
    d=synthetic_document();model=JointModel(d)
    x=np.array([5760.,np.log(240.),-.08,1.7,.12,20.,.05])
    p=model.decode(x);theta=4.8
    magnitudes=20.-2.5*np.log10(1+.05*(amplification(trajectory(model.tp,p,model.ep))-1))
    pos=np.array([3.,-4.])+((model.ta-model.ref)/365.25)[:,None]*np.array([-2.,3.])-.13*(model.ea-model.eref)+theta*centroid_unit(trajectory(model.ta,p,model.ea))
    for row,y in zip(d['photometry'],magnitudes):row['magnitude']=float(y)
    for row,y in zip(d['astrometry'],pos):row.update(north_mas=float(y[0]),east_mas=float(y[1]))
    fit=fit_joint(d,initial_states=[x+np.array([.1,.001,.001,.001,.001,.001,.0001])],max_nfev=120)
    assert fit['objective_deviance']<1e-14
    assert fit['parameters']['mass_msun']==pytest.approx(theta/(KAPPA_MAS_MSUN*.12),rel=2e-8)
    assert fit['parameters']['relative_frame_source_parallax_mas']==pytest.approx(.13,abs=1e-8)
    assert fit['unavailable']['lens_distance_pc'] is None
    zero=JointModel(d);x[4]=0
    assert zero.evaluate(x,details=True)['parameters']['mass_msun'] is None


def test_explicit_native_clock_and_axis_required():
    d=synthetic_document();d['metadata']['ra_axis']='RA_ANGLE_UNSPECIFIED'
    with pytest.raises(ValueError,match='east tangent'):JointData(d)


def test_invalid_public_math_and_window_inputs_rejected():
    with pytest.raises(ValueError):ou_whiten(np.arange(2.),np.ones(2),np.ones(2),np.nan,1.)
    with pytest.raises(ValueError):ou_whiten(np.arange(2.),np.array([0.,1.]),np.ones(2),1.,1.)
    with pytest.raises(ValueError):centroid_unit([[np.nan,1.]])
    with pytest.raises(ValueError):centroid_unit([[1.,1.]],np.inf)
    d=synthetic_document();d['astrometry'][0]['exposure_window_jd_tdb']=[float('nan'),2459999.]
    with pytest.raises(ValueError,match='exposure window'):JointData(d)
    d=synthetic_document()
    for row in d['photometry']:row['instrument']='other'
    with pytest.raises(ValueError,match='OGLE instrument'):JointModel(d,gp=True)
