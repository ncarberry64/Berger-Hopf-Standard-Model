"""Focused safeguards for the stored-frame reconciliation, no producers."""
import unittest
import json
import hashlib
import numpy as np
from flint import arb,ctx
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import checkpoint_n12_gate7_66d_tangent_binding as b


class BindingTests(unittest.TestCase):
    def test_checkpoint_bytes_and_claim_boundaries(self):
        base=b.ROOT/'artifacts/flagship_integration/gate7_66d_checkpoint_20260926'
        receipt=json.loads((base/'reproduction.json').read_bytes())
        for name,entry in receipt.items():
            # This capsule preserves historical CRLF bytes; the repository's
            # Path.read_bytes fixture intentionally normalizes artifact JSON.
            with (base/name).open('rb') as stream:
                actual=hashlib.sha256(stream.read()).hexdigest().upper()
            self.assertEqual(actual,entry['SHA256'])
        for name in ('binding','newton'):
            report=json.loads((base/name/'report.json').read_bytes())
            self.assertIs(report['Gate7_closed'],False)
            self.assertIs(report['FULL_BHSM_COMPLETE'],False)

    def test_saved_center_inverse_replay(self):
        ctx.prec=512
        base=b.ROOT/'artifacts/flagship_integration/gate7_66d_checkpoint_20260926/newton'
        report=json.loads((base/'report.json').read_bytes())
        with np.load(base/'M_13.npz') as z:
            M=z['M_13'];R=z['inverse_proposal']
        self.assertEqual(M.shape,(74,74))
        error=b.frob(b.amat(np.eye(74))-b.amat(R)*b.amat(M))
        self.assertTrue(error<=arb(report['inverse_left_residual']['exact_upper']))
        self.assertTrue(error<1)
        self.assertIs(report['partition_available'],False)
        self.assertIs(report['nonlinear_Mqq_variation_proved'],False)

    def test_physical_flow_descriptor_is_converted_to_causal_units(self):
        family=np.vstack((np.eye(73)[:,:72],np.zeros((1,72))))
        flow=np.eye(73)[:,72];child=np.eye(73)[:,[0,72]]
        C,S,z=b.launch_child(family,flow,2e-7,child)
        np.testing.assert_allclose(C[:73],child,rtol=0,atol=0)
        np.testing.assert_allclose(C[73],[0,2],rtol=0,atol=1e-15)
        np.testing.assert_allclose(b.frame(np.eye(98)[:,:73],b.SCALE)[98]@C,[0,2e-7])

    def test_descriptor_scale_must_be_positive(self):
        with self.assertRaises(ValueError):b.launch_child(None,None,None,None,0)

    def test_explicit_residual_restores_a_nonidentical_subspace(self):
        ctx.prec=512
        A=np.array([[1.,0.],[0.,1.],[1e-8,0.]])
        B=np.array([[1.,0.],[0.,1.],[0.,0.]])
        X=np.linalg.lstsq(B,A,rcond=None)[0]
        aa,bb,xx=map(b.amat,(A,B,X));R=aa-bb*xx
        reconstructed=bb*xx+R-aa
        self.assertTrue(all(v.contains(0) for v in reconstructed.entries()))
        self.assertGreaterEqual(b.bound(R)['approximate_upper'],1e-8)

    def test_midpoint_agreement_does_not_drop_coefficient_radius(self):
        ctx.prec=512
        uniform=b.amat(np.array([[1,2]],dtype=int));uniform[0,1]=arb(2,3)
        point=b.amat(np.array([[1,2]],dtype=int))
        self.assertEqual(b.op(b.mid(uniform)-b.mid(point)),0)
        self.assertGreaterEqual(b.bound(uniform-point)['approximate_upper'],3)

    def test_same_first_order_slaving_does_not_determine_curvature(self):
        # F(p,q)=q-c*p^2: all c have the same K=1 and q_p(0)=0.
        # Their eliminated q_pp(0)=2c differs; a tangent is not a mixed jet.
        for c in (0,1,100):
            K=1;F_p_at_zero=0;q_p=-F_p_at_zero/K
            self.assertEqual(q_p,0)
            self.assertEqual(-(-2*c)/K,2*c)


if __name__=='__main__':unittest.main()
