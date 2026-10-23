"""Prospective v2 checks, independent of the measured outcomes."""
import copy
import numpy as np
import pytest
from scipy.linalg import cholesky,solve_triangular
from bhtracker.joint_mass_v2 import JointModel,fit_joint,amplification,trajectory,centroid_unit,KAPPA_MAS_MSUN
from test_joint_mass import synthetic_document


def document():
    d=synthetic_document()
    d['analysis']={'bounds':{'t0_jd_tdb':[2455700.,2455830.],'tE_days':[20.,2000.],'u0_heliocentric':[-1.,1.],'pi_E':[0.,1.],'theta_E_mas':[.01,40.],'relative_frame_source_parallax_mas':[-1.,1.]},'initial_guess':{'t0_jd_tdb':2455765.,'tE_days':250.,'u0_absolute':.06,'pi_E':.1}}
    return d


@pytest.mark.parametrize('fraction',[0.,.2,.95])
def test_complete_marginal_ou_objective_matches_dense(fraction):
    d=document();d['photometry']=d['photometry'][:7]
    times=[2455700.,2455700.01,2455700.01,2455701.,2455702.,2455710.,2455750.]
    for i,row in enumerate(d['photometry']):row['time_jd_tdb']=times[i];row['magnitude_error']=.01+i*.003;row['magnitude']+=i*.001
    m=JointModel(d,gp=True);x=np.array(next(m.seeds(1)));x[-2]=fraction;x[-1]=np.log(2.4)
    detail=m.evaluate(x,details=True);r=np.array(detail['photometric_residuals_magnitude']);sigma=m.sp
    corr=(1-fraction)*np.eye(len(r))+fraction*np.exp(-abs(m.tp[:,None]-m.tp[None,:])/2.4)
    covariance=sigma[:,None]*corr*sigma[None,:]
    np.testing.assert_allclose(np.diag(covariance),sigma*sigma,rtol=2e-16)
    z=solve_triangular(cholesky(covariance,lower=True),r,lower=True)
    determinant=np.linalg.slogdet(covariance)[1]-2*np.log(sigma).sum()
    assert detail['photometric_innovation_chi2']==pytest.approx(z@z,rel=5e-13)
    assert detail['GP_log_determinant_ratio_to_native_diagonal']==pytest.approx(determinant,abs=8e-14)
    assert detail['objective_deviance']==pytest.approx(z@z+determinant+detail['astrometric_chi2'],rel=5e-13)
    assert m.evaluate(x)@m.evaluate(x)-detail['optimization_constant_offset']==pytest.approx(detail['objective_deviance'],abs=1e-10)
    if fraction==0:assert determinant==pytest.approx(0.,abs=1e-13)
    else:assert determinant<0


def test_time_origin_changes_no_physical_predictions():
    a=document();b=copy.deepcopy(a);b['analysis']['numerical_time_center_jd_tdb']=2455750.
    ma,mb=JointModel(a),JointModel(b)
    xa=np.array(next(ma.seeds(1)));xb=xa.copy();xb[0]+=ma.time_origin_jd_tdb-mb.time_origin_jd_tdb
    da,db=ma.evaluate(xa,details=True),mb.evaluate(xb,details=True)
    assert da['parameters']==db['parameters']
    np.testing.assert_array_equal(da['photometric_predictions_magnitude'],db['photometric_predictions_magnitude'])
    np.testing.assert_array_equal(da['astrometric_predictions_NE_mas'],db['astrometric_predictions_NE_mas'])
    assert abs(xa[0])<1 and abs(xb[0])<20


def test_v2_unknown_targets_require_explicit_domain_and_seeds():
    with pytest.raises(ValueError,match='future targets'):JointModel(synthetic_document())
    assert len(list(JointModel(document()).seeds(16)))==16


@pytest.mark.parametrize('fraction,k,floor',[(0.,1.,0.),(.2,.9,.003),(.95,.5,0.),(.95,2.,.02)])
def test_calibration_hypothesis_full_gaussian_objective(fraction,k,floor):
    d=document();d['photometry']=d['photometry'][:8]
    m=JointModel(d,gp=True,noise_model='calibrated_marginal_ou');x=np.array(next(m.seeds(1)));x[-4:]=[np.log(k),floor,fraction,np.log(2.4)]
    original=[r['magnitude_error'] for r in d['photometry']];detail=m.evaluate(x,details=True);r=np.array(detail['photometric_residuals_magnitude'])
    effective=np.sqrt((k*m.sp)**2+floor**2);corr=(1-fraction)*np.eye(len(r))+fraction*np.exp(-abs(m.tp[:,None]-m.tp[None,:])/2.4);c=effective[:,None]*corr*effective[None,:]
    z=solve_triangular(cholesky(c,lower=True),r,lower=True);determinant=np.linalg.slogdet(c)[1]-2*np.log(m.sp).sum()
    assert determinant+m.objective_offset>=-1e-12
    assert detail['objective_deviance']==pytest.approx(z@z+determinant+detail['astrometric_chi2'],rel=5e-13)
    assert [r['magnitude_error'] for r in m.data.document['photometry']]==original


def test_browser_json_roundtrip_preserves_v2_numeric_hash():
    import json,shutil,subprocess
    from bhtracker.joint_mass_v2 import JointData
    node=shutil.which('node')
    if node is None:pytest.skip('Node unavailable for actual browser-JSON semantics test')
    d=document();d['metadata']['non_integer']=1e-7;d['metadata']['boolean']=True
    returned=subprocess.run([node,'-e',"let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(JSON.parse(s))));"],input=json.dumps(d),text=True,capture_output=True,check=True)
    back=json.loads(returned.stdout)
    assert isinstance(back['reference_jd_tdb'],int)
    assert JointData(d).sha256==JointData(back).sha256
