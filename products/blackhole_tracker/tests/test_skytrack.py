"""Prospectively fixed invented angular-track controls; no native observations."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.stats import chi2

from bhtracker.skytrack import (INPUT_SCHEMA, fit_skytrack, validate_skytrack,
                               synthetic_example, replay_skytrack, export_skytrack)


def document(times=None, noise=True):
    """Independent literal measurement construction, not a production predictor."""
    times = [0., 182.625, 547.875, 913.125, 1461., 2008.875] if times is None else times
    offsets = [[.15,-.08],[-.12,.23],[.07,-.2],[-.19,.13],[.1,-.17],[-.04,.09]]
    rows = []
    for i, time in enumerate(times):
        dt = (time-730.5)/365.25; error = offsets[i % 6] if noise else [0.,0.]
        rows.append({'source_row_id':f'invented:{i}', 'source_file_sha256':'a'*64,
                     'source_reference':'INVENTED fixture, no observation source', 'lens_id':'INVENTED-LENS',
                     'native_time':time, 'position_mas':[12.+8.*dt+error[0],-8.-3.*dt+error[1]],
                     'covariance_mas2':[[.04,.01],[.01,.09]]})
    return {'schema':INPUT_SCHEMA,'lens_id':'INVENTED-LENS','position_role':'LENS_ANGULAR_POSITION',
            'position_origin':'DIRECT_LENS_ASTROMETRY','association_evidence':'Invented test association.',
            'frame':{'name':'Invented inertial frame','kind':'INERTIAL_TANGENT_PLANE','axes':['east','north'],
                     'angular_unit':'mas','reference_origin':'Invented tangent origin','absolute_frame':False,
                     'calibration_source':'Invented calibration','parallax_treatment':'NOT_MODELED_CONDITIONAL_RECTILINEAR',
                     'parallax_source':'No parallax in invented signal.'},
            'time':{'native_unit':'day','numeric_origin':2450000.,'convention':'JD_TDB minus numeric_origin',
                    'scale':'TDB','source':'Invented epochs'},
            'noise':{'distribution':'GAUSSIAN_KNOWN_SUPPLIED_COVARIANCE','covariance_kind':'PER_EPOCH_2X2',
                     'covariance_unit':'mas^2','covariance_source':'Invented matrices',
                     'cross_epoch_independence':{'assumed':True,'justification':'Explicit invented control assumption'}},
            'rows':rows,'full_covariance_mas2':None,'metadata':{'kind':'synthetic','unknown':None}}


def reference_gls(data, reference, covariance):
    # A separate, well-conditioned toy normal-equation solve checks the
    # production centered QR, including its complete reference covariance.
    t = (np.array([r['native_time'] for r in data['rows']])-reference)/365.25
    A = np.zeros((2*len(t),4)); A[0::2,0]=1; A[1::2,1]=1; A[0::2,2]=t; A[1::2,3]=t
    y = np.array([r['position_mas'] for r in data['rows']]).ravel()
    normal = A.T @ np.linalg.solve(covariance,A)
    theta = np.linalg.solve(normal,A.T @ np.linalg.solve(covariance,y))
    return theta,np.linalg.solve(normal,np.eye(4)),float((y-A@theta)@np.linalg.solve(covariance,y-A@theta))


class SkyTrackTests(unittest.TestCase):
    def test_large_signal_replay_tail_and_status_coherence_is_not_q_tolerance(self):
        d=synthetic_example()
        for row in d['rows']:row['position_mas']=[v*1e8 for v in row['position_mas']]
        r=fit_skytrack(d,reference_native_time=6000.,significance_alpha=.01)
        self.assertEqual(r['diagnostics']['stationary_null_probability'],0.)
        self.assertGreater(replay_skytrack(r)['numerical_comparison']['chi_square_comparison_budget'],1.)
        for key,value in (('stationary_null_probability',.9),('chi_square_lower_probability',1.-1e-10)):
            bad=deepcopy(r);bad['diagnostics'][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'saved_tail_coherence'):replay_skytrack(bad)
        exact=document(noise=False)
        for row in exact['rows']:row['position_mas']=[v*1e8 for v in row['position_mas']]
        r=fit_skytrack(exact,significance_alpha=.01)
        self.assertEqual(r['status'],'RECTILINEAR_NOISE_UNDERDISPERSED')
        bad=deepcopy(r);diag=bad['diagnostics'];df=diag['degrees_of_freedom'];diag['chi_square']=8.
        diag['chi_square_upper_probability']=float(chi2.sf(8.,df));diag['chi_square_lower_probability']=float(chi2.cdf(8.,df))
        diag['chi_square_two_sided_probability']=min(1.,2*min(diag['chi_square_upper_probability'],diag['chi_square_lower_probability']))
        with self.assertRaisesRegex(ValueError,'saved_status_coherence'):replay_skytrack(bad)

    def test_replay_natural_diagnostic_ranges_are_not_softened_by_budget(self):
        d=document()
        for row in d['rows']:row['position_mas']=[12.,-8.]
        r=fit_skytrack(d)
        invalid={'chi_square':-1e-15,'stationary_null_delta_chi_square':-1e-15,
                 'chi_square_upper_probability':1.+1e-15,'chi_square_lower_probability':-1e-15,
                 'chi_square_two_sided_probability':-1e-15,'stationary_null_probability':1.+1e-15,
                 'stationarity_residual':-1e-15,'rank_tolerance':-1e-15,'condition_number':.5,
                 'singular_values':[0.,0.,0.,0.]}
        for key,value in invalid.items():
            bad=deepcopy(r);bad['diagnostics'][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'range'):replay_skytrack(bad)
        small_raw=deepcopy(r);small_raw['diagnostics']['stationary_null_delta_before_roundoff_clip']=-1e-15
        self.assertTrue(replay_skytrack(small_raw)['passed'])

    def test_full_covariance_does_not_silently_claim_epoch_independence(self):
        d=document();n=len(d['rows']);d['noise']['covariance_kind']='FULL_2N'
        d['full_covariance_mas2']=np.kron(np.eye(n),[[.04,.01],[.01,.09]]).tolist()
        for row in d['rows']:row.pop('covariance_mas2')
        with self.assertRaisesRegex(ValueError,'cross_epoch_independence=null'):validate_skytrack(d)

    def test_numerical_failure_guards_are_unresolved_not_physical_exclusion(self):
        with patch('bhtracker.skytrack.np.linalg.svd',side_effect=np.linalg.LinAlgError('invented convergence failure')):
            with self.assertRaisesRegex(ValueError,'SVD did not converge'):fit_skytrack(document())
        with patch('bhtracker.skytrack.np.linalg.qr',side_effect=np.linalg.LinAlgError('invented convergence failure')):
            with self.assertRaisesRegex(ValueError,'QR solve'):fit_skytrack(document())
        with patch('bhtracker.skytrack.solve_triangular',side_effect=lambda _factor,array,**kwargs:np.full_like(array,np.inf)), \
             patch('bhtracker.skytrack.np.linalg.svd') as svd:
            with self.assertRaisesRegex(ValueError,'weighted numerical design'):fit_skytrack(document())
            svd.assert_not_called()
        with np.errstate(over='ignore',invalid='ignore'):
            with self.assertRaisesRegex(ValueError,'reporting-reference'):fit_skytrack(document(),reference_native_time=1e308)

    def test_portable_engineering_budget_keeps_exact_status_and_null_gates(self):
        r=fit_skytrack(document(),reference_native_time=730.5)
        close=deepcopy(r);close['parameters']['position_mas'][0]+=1e-14
        close['parameter_covariance']=(np.asarray(close['parameter_covariance'])*(1+1e-14)).tolist()
        check=replay_skytrack(close)
        json.dumps(check,allow_nan=False)
        self.assertTrue(check['passed']);self.assertFalse(check['exact_numeric_match'])
        self.assertLessEqual(check['numerical_comparison']['relative_budget'],1e-6)
        for key,value in (('status','RECTILINEAR_TRACK_NOT_REJECTED'),('unavailable',dict(r['unavailable'],mass_msun=0.))):
            bad=deepcopy(close);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):replay_skytrack(bad)
        bad=deepcopy(r);bad['dataset_input']['metadata']['unknown']=False
        with self.assertRaisesRegex(ValueError,'parsed observation values'):replay_skytrack(bad)
        bad=deepcopy(r);bad['diagnostics']['condition_number']=True
        with self.assertRaisesRegex(ValueError,'non-boolean'):replay_skytrack(bad)
        bad=deepcopy(r);bad['parameters']['position_mas']=0.
        with self.assertRaisesRegex(ValueError,'array shape'):replay_skytrack(bad)

    def test_replay_precision_refusal_does_not_inflate_supplied_covariance(self):
        d=document()
        for row in d['rows']:row['covariance_mas2']=[[1e-10,0.],[0.,1.]]
        original=deepcopy(d);r=fit_skytrack(d)
        self.assertEqual(d,original);self.assertEqual(r['dataset_input'],original)
        with self.assertRaisesRegex(ValueError,'precision cap'):replay_skytrack(r)

    def test_irregular_correlated_epoch_recovery_matches_independent_gls(self):
        data=document(); before=deepcopy(data); result=fit_skytrack(data,reference_native_time=730.5)
        C=np.kron(np.eye(len(data['rows'])),np.array([[.04,.01],[.01,.09]]))
        theta,cov,q=reference_gls(data,730.5,C)
        np.testing.assert_allclose(result['parameters']['position_mas']+result['parameters']['angular_motion_mas_per_Julian_year'],theta,rtol=2e-12,atol=2e-12)
        np.testing.assert_allclose(result['parameter_covariance'],cov,rtol=2e-12,atol=2e-12)
        self.assertAlmostEqual(result['diagnostics']['chi_square'],q,places=11)
        self.assertEqual(data,before); self.assertEqual(result['status'],'RECTILINEAR_FIT_STATISTICS_ONLY')
        self.assertEqual(result['diagnostics']['motion_screen'],'NOT_REQUESTED')
        self.assertTrue(all(v is None for v in result['unavailable'].values()))

    def test_full_cross_epoch_covariance_matches_independent_gls(self):
        data=document(); n=len(data['rows']); C=np.kron(np.eye(n),[[.04,.01],[.01,.09]])
        C+=.003*np.outer(np.linspace(-1,1,2*n),np.linspace(-1,1,2*n))
        data['noise']['covariance_kind']='FULL_2N';data['noise']['cross_epoch_independence']=None
        data['position_origin']='INFERRED_LENS_POSITION_FROM_IDENTIFIED_JOINT_MODEL'
        data['full_covariance_mas2']=C.tolist()
        for row in data['rows']:row.pop('covariance_mas2')
        actual=fit_skytrack(data,reference_native_time=730.5);theta,cov,q=reference_gls(data,730.5,C)
        np.testing.assert_allclose(actual['parameters']['position_mas']+actual['parameters']['angular_motion_mas_per_Julian_year'],theta,rtol=2e-12,atol=2e-12)
        np.testing.assert_allclose(actual['parameter_covariance'],cov,rtol=2e-12,atol=2e-12)
        self.assertAlmostEqual(actual['diagnostics']['chi_square'],q,places=11)

    def test_reference_transform_preserves_full_covariance_and_predictions(self):
        data=document();a=fit_skytrack(data,reference_native_time=730.5);b=fit_skytrack(data,reference_native_time=1230.5)
        T=np.eye(4);T[0,2]=T[1,3]=500/365.25
        old=np.array(a['parameters']['position_mas']+a['parameters']['angular_motion_mas_per_Julian_year'])
        new=np.array(b['parameters']['position_mas']+b['parameters']['angular_motion_mas_per_Julian_year'])
        np.testing.assert_allclose(new,T@old,rtol=2e-13,atol=2e-13)
        np.testing.assert_allclose(b['parameter_covariance'],T@np.array(a['parameter_covariance'])@T.T,rtol=2e-13,atol=2e-13)
        self.assertEqual(a['predictions_mas'],b['predictions_mas']);self.assertEqual(a['diagnostics']['chi_square'],b['diagnostics']['chi_square'])

    def test_large_native_clock_and_numeric_origin_are_computational_choices(self):
        data=document();a=fit_skytrack(data,reference_native_time=730.5);shifted=deepcopy(data);shift=2.**40
        for row in shifted['rows']:row['native_time']+=shift
        shifted['time']['numeric_origin']-=shift
        b=fit_skytrack(shifted,reference_native_time=730.5+shift)
        self.assertEqual(a['parameters'],b['parameters']);self.assertEqual(a['parameter_covariance'],b['parameter_covariance'])
        self.assertEqual(a['predictions_mas'],b['predictions_mas'])

    def test_declared_julian_year_units_do_not_change_motion(self):
        data=document([0.,365.25,730.5,1095.75],noise=False);a=fit_skytrack(data,reference_native_time=730.5)
        other=deepcopy(data);other['time']['native_unit']='Julian_year';other['time']['numeric_origin']/=365.25
        for row in other['rows']:row['native_time']/=365.25
        b=fit_skytrack(other,reference_native_time=2.)
        np.testing.assert_allclose(a['parameters']['angular_motion_mas_per_Julian_year'],[8.,-3.],atol=1e-13)
        self.assertEqual(a['parameters'],b['parameters']);self.assertEqual(a['parameter_covariance'],b['parameter_covariance'])

    def test_two_unique_epochs_have_no_goodness_or_motion_classification(self):
        for times in ([0.,365.25],[0.,365.25,365.25]):
            with self.subTest(times=times):
                r=fit_skytrack(document(times),significance_alpha=.01)
                self.assertEqual(r['status'],'TWO_EPOCH_FIT_UNTESTED');self.assertFalse(r['diagnostics']['goodness_of_fit_testable'])
                self.assertIsNone(r['diagnostics']['chi_square_two_sided_probability'])
                self.assertEqual(r['diagnostics']['motion_screen'],'NOT_CLASSIFIED_TWO_EPOCH_FIT')

    def test_explicit_two_sided_threshold_rejects_curvature_not_black_hole_identity(self):
        data=document()
        for row in data['rows']:row['position_mas'][0]+=8*((row['native_time']-730.5)/365.25)**2
        r=fit_skytrack(data,significance_alpha=.01)
        self.assertEqual(r['status'],'RECTILINEAR_MODEL_OR_NOISE_INADEQUATE')
        self.assertLessEqual(r['diagnostics']['chi_square_two_sided_probability'],.01)
        self.assertTrue(all(v is None for v in r['unavailable'].values()))
        self.assertIn('parallax', ' '.join(r['qualifications']))

    def test_underdispersion_and_stationary_null_remain_separate(self):
        exact=fit_skytrack(document(noise=False),significance_alpha=.01)
        self.assertEqual(exact['status'],'RECTILINEAR_NOISE_UNDERDISPERSED')
        data=document()
        for i,row in enumerate(data['rows']):row['position_mas']=[12.+(.1 if i%2 else -.1),-8.+(.2 if i%2 else -.2)]
        r=fit_skytrack(data,significance_alpha=.01)
        self.assertGreater(r['diagnostics']['stationary_null_probability'],.01)
        self.assertEqual(r['diagnostics']['motion_screen'],'STATIONARY_NULL_NOT_REJECTED')

    def test_source_event_roles_association_and_missing_covariance_refuse(self):
        changes=[('position_role','SOURCE_EVENT_DIRECTION'),('position_origin','UNRESOLVED_SOURCE_CENTROID'),('association_evidence','')]
        for key,value in changes:
            d=document();d[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_skytrack(d)
        for mutation in ('other_lens','duplicate_id','missing_independence','missing_covariance'):
            d=document()
            if mutation=='other_lens':d['rows'][1]['lens_id']='OTHER'
            if mutation=='duplicate_id':d['rows'][1]['source_row_id']=d['rows'][0]['source_row_id']
            if mutation=='missing_independence':d['noise']['cross_epoch_independence']=None
            if mutation=='missing_covariance':d['rows'][0].pop('covariance_mas2')
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):fit_skytrack(d)

    def test_asymmetric_singular_or_nonfinite_covariance_and_time_rank_refuse(self):
        for covariance in ([[1.,1.],[1.,1.]],[[1.,.1],[.2,1.]],[[True,0.],[0.,1.]],[[float('inf'),0.],[0.,1.]]):
            d=document();d['rows'][0]['covariance_mas2']=covariance
            with self.subTest(covariance=covariance),self.assertRaises(ValueError):fit_skytrack(d)
        d=document()
        for row in d['rows']:row['native_time']=1.
        with self.assertRaisesRegex(ValueError,'time rank'):fit_skytrack(d)
        d=document()
        for row in d['rows']:row['covariance_mas2']=[[1e-200,0.],[0.,1e200]]
        with self.assertRaisesRegex(ValueError,'rank4'):fit_skytrack(d)

    def test_raw_json_null_unknown_fields_and_duplicates(self):
        d=document();d['rows'][1]['unused_annotation']={'unknown':None}
        text=json.dumps(d,indent=3).replace('\n','\r\n')
        r=fit_skytrack(text)
        self.assertEqual(r['dataset_input_json'],text);self.assertEqual(r['dataset_input'],d)
        self.assertEqual(r['input_utf8_sha256'],hashlib.sha256(text.encode()).hexdigest())
        self.assertTrue(replay_skytrack(r)['passed'])
        with self.assertRaisesRegex(ValueError,'duplicate'):validate_skytrack('{"schema":1,"schema":2}')
        for alpha in (True,0.,.5,float('nan')):
            with self.subTest(alpha=alpha),self.assertRaises(ValueError):fit_skytrack(d,significance_alpha=alpha)

    def test_replay_tampering_and_exports_do_not_replace_originals(self):
        r=fit_skytrack(document(),reference_native_time=730.5,significance_alpha=.01)
        for key in ('parameters','parameter_covariance','diagnostics','unavailable','input_utf8_sha256','method_source_sha256'):
            bad=deepcopy(r)
            if key=='parameters':bad[key]['position_mas'][0]+=1
            elif key=='parameter_covariance':bad[key][0][0]*=2
            elif key=='diagnostics':bad[key]['motion_screen']='BLACK_HOLE_IDENTIFIED'
            elif key=='unavailable':bad[key]['mass_msun']=8.
            else:bad[key]='0'*64
            with self.subTest(key=key),self.assertRaises(ValueError):replay_skytrack(bad)
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'fresh';check=export_skytrack(r,dest)
            self.assertTrue(check['passed']);self.assertEqual((dest/'dataset.json').read_bytes(),r['dataset_input_json'].encode())
            with self.assertRaises(FileExistsError):export_skytrack(r,dest)
        self.assertEqual(r,fit_skytrack(document(),reference_native_time=730.5,significance_alpha=.01))

    def test_synthetic_demo_and_cli_are_unmistakably_invented(self):
        d=synthetic_example();self.assertEqual(d['metadata']['kind'],'synthetic');self.assertFalse(d['metadata']['known_black_hole'])
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'invented.json';result=Path(temp)/'result.json';check=Path(temp)/'check.json'
            source.write_bytes(json.dumps(d).encode())
            for args in (['validate',str(source)],['fit',str(source),'--output',str(result)],['replay',str(result),'--output',str(check)]):
                completed=subprocess.run([sys.executable,'-B','-m','bhtracker','skytrack',*args],capture_output=True,text=True)
                self.assertEqual(completed.returncode,0,completed.stderr)
            self.assertTrue(json.loads(check.read_bytes())['passed'])


if __name__=='__main__':unittest.main()
