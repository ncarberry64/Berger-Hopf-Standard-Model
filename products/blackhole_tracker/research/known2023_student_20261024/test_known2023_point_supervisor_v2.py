"""Invented supervisor and independent generator-factor controls; no model calls."""
import copy
import json
from pathlib import Path
import tempfile
import io
import unittest
from unittest.mock import patch
import numpy as np
import run_known2023_point_v2 as runner
from make_actual_cadence_control_v2 import chronological_cholesky_apply, checked_generation_configuration, SEED

class Controls(unittest.TestCase):
    def test_01_covariance_factor_independent_dense_reference(self):
        times = np.array([0.,0.,.001,1.,30.])
        for fraction,tau in [(0.,1.),(.2,2.7),(.95,.05),(.6,100.)]:
            expected = np.linalg.cholesky((1-fraction)*np.eye(len(times))+fraction*np.exp(-np.abs(times[:,None]-times[None,:])/tau))
            actual = np.column_stack([chronological_cholesky_apply(times,np.eye(len(times))[:,j],fraction,tau) for j in range(len(times))])
            np.testing.assert_allclose(actual,expected,atol=3e-14,rtol=3e-14)
            np.testing.assert_allclose(actual@actual.T,expected@expected.T,atol=4e-14,rtol=4e-14)

    def test_02_cholesky_time_origin_and_units(self):
        times=np.array([0.,.3,.31,10.]); z=np.array([1.,-.2,3.,-.4])
        ref=chronological_cholesky_apply(times,z,.3,4.)
        np.testing.assert_allclose(chronological_cholesky_apply(times+100,z,.3,4.),ref,rtol=1e-13,atol=1e-13)
        np.testing.assert_allclose(chronological_cholesky_apply(times*10,z,.3,40.),ref,rtol=1e-13,atol=1e-13)

    def test_03_cholesky_bad_support(self):
        for times,z,f,tau in [([1.,0.],[1.,2.],.2,1.),([0.],[float('nan')],.2,1.),([0.],[1.],1.,1.),([0.],[1.],.2,0.)]:
            with self.assertRaises((ValueError,TypeError)):
                chronological_cholesky_apply(times,z,f,tau)

    def test_04_relative_heights_are_log_density_heights(self):
        rows=[{'deviance':-10.,'start_index':0,'phase':'A','numerically_eligible':True},{'deviance':-8.,'start_index':1,'phase':'B','numerically_eligible':False}]
        self.assertEqual([r['log_relative_likelihood_height'] for r in runner.relative_heights(rows)],[0.,-1.])
        self.assertEqual(runner.relative_heights([]),[])

    def test_05_exact_deadline(self):
        self.assertFalse(runner.expired(10.,2.,now=11.999))
        self.assertTrue(runner.expired(10.,2.,now=12.))

    def test_06_existing_output_no_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'existing';out.mkdir();(out/'prior').write_bytes(b'unchanged')
            freeze={'purpose':'WHOLLY_INVENTED','input':{'sha256':'x'},'configuration':{'supervisor_wall_seconds':1.}}
            argv=['runner','--freeze','unused','--freeze-sha256','x','--output',str(out)]
            with patch('sys.argv',argv),patch.object(runner,'binding',return_value=(freeze,b'{}')),patch.object(runner,'admission',return_value=None),patch.object(runner.subprocess,'Popen') as popen:
                with self.assertRaises(FileExistsError): runner.main()
                popen.assert_not_called()
            self.assertEqual({p.name:p.read_bytes() for p in out.iterdir()},{'prior':b'unchanged'})

    def test_07_preflight_deadline_no_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'fresh'; freeze_path=Path(tmp)/'freeze';freeze_path.write_bytes(b'{}')
            freeze={'purpose':'WHOLLY_INVENTED','input':{'sha256':'x'},'configuration':{'supervisor_wall_seconds':1.}}
            argv=['runner','--freeze',str(freeze_path),'--freeze-sha256','x','--output',str(out)]
            with patch('sys.argv',argv),patch.object(runner,'binding',return_value=(freeze,b'{}')),patch.object(runner,'admission',return_value=None),patch.object(runner.time,'monotonic',side_effect=[0.,2.]),patch.object(runner.subprocess,'Popen') as popen:
                self.assertEqual(runner.main(),1);popen.assert_not_called()
            terminal=json.loads((out/'SUPERVISOR_TERMINAL_v1.json').read_text())
            self.assertFalse(terminal['execution_complete']);self.assertEqual(len(json.loads((out/'ALL16_INITIAL_LEDGER_v1.json').read_text())),16)

    def test_08_native_requires_separate_exact_admission(self):
        class Args: admission=None;admission_sha256=None
        with self.assertRaises(ValueError):runner.admission(Args(),{'purpose':'AUTHENTIC2023'})

    def test_09_identity_cannot_be_replaced(self):
        good={'start_index':0,'purpose':'WHOLLY_INVENTED','input_sha256':'x'}
        self.assertIs(runner.validated_start_record(good,0,'WHOLLY_INVENTED','x'),good)
        for change in [{'start_index':True},{'start_index':1},{'purpose':'AUTHENTIC2023'},{'input_sha256':'y'}]:
            with self.assertRaises(ValueError):runner.validated_start_record(dict(good,**change),0,'WHOLLY_INVENTED','x')

    def test_10_point_requires_all16_and_null_acceptance(self):
        good={'schema':'bhsm.known2023.ST6.point_outcome.v1','purpose':'WHOLLY_INVENTED','input_sha256':'x','accepted_mass_interval':None,'known_black_hole_recovery_accepted':False,'all16_starts':[{'start_index':k,'purpose':'WHOLLY_INVENTED','input_sha256':'x'}for k in range(16)]}
        self.assertIs(runner.validated_point_outcome(good,'WHOLLY_INVENTED','x'),good)
        for mutation in ['missing_null','mass_claim','missing_start','duplicate_start','recovery_claim']:
            bad=copy.deepcopy(good)
            if mutation=='missing_null':del bad['accepted_mass_interval']
            if mutation=='mass_claim':bad['accepted_mass_interval']=[1,2]
            if mutation=='missing_start':bad['all16_starts'].pop()
            if mutation=='duplicate_start':bad['all16_starts'][1]['start_index']=0
            if mutation=='recovery_claim':bad['known_black_hole_recovery_accepted']=True
            with self.assertRaises(ValueError):runner.validated_point_outcome(bad,'WHOLLY_INVENTED','x')

    def test_11_latched_budget_retains_unrecorded_lower_trial(self):
        stream=io.StringIO();audit=runner.JournalLatch(stream,4)
        lower={'event':'VALID_EVALUATION','deviance':-99.,'physical_state':[1.]}
        with self.assertRaises(runner.AuditFailure):audit.append(lower)
        self.assertIs(audit.unrecorded_event,lower)
        self.assertFalse(audit.permits_resolution())
        with self.assertRaises(runner.AuditFailure):audit.before_model_call()
        with self.assertRaises(runner.AuditFailure):audit.append({'deviance':0.})
        self.assertIs(audit.unrecorded_event,lower)
        self.assertEqual(stream.getvalue(),'')

    def test_12_latched_write_failure(self):
        class Broken(io.StringIO):
            def write(self,*args):raise OSError('invented disk failure')
        audit=runner.JournalLatch(Broken(),1000)
        with self.assertRaises(runner.AuditFailure):audit.append({'deviance':1.})
        self.assertFalse(audit.permits_resolution())
        with self.assertRaises(runner.AuditFailure):audit.before_model_call()

    def test_13_generation_purpose_seed_runtime_bound_before_draw(self):
        runtime={'python':'3.11.9','numpy':'1.26.4','scipy':'1.12.0','astropy':'6.0.0'}
        good={'purpose':'ACTUAL_CADENCE_GENERATION','random_seed':SEED,'runtime':runtime}
        self.assertEqual(checked_generation_configuration(good,runtime)['random_seed'],SEED)
        for change in [{'purpose':'AUTHENTIC2023'},{'random_seed':True},{'random_seed':SEED+1},{'runtime':dict(runtime,python='3.14.3')}]:
            with self.assertRaises(ValueError):checked_generation_configuration(dict(good,**change),runtime)

if __name__=='__main__':unittest.main()
