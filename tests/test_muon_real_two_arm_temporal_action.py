from __future__ import annotations
import sys
import unittest
import json
from pathlib import Path
import numpy as np

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'src'))
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_real_two_arm_temporal_action import (
    paired_temporal_layout,pack_temporal_state,real_two_arm_temporal_action)


def lift():
    labels=[dict(radial=r,field=f,internal=a) for r in range(4)
            for f in ('A_tau','A_rho','A_1','A_2','A_3') for a in range(4)]
    return generic_coordinate_lift(labels)['lift']


class PolynomialOwners:
    """Independent analytic all-coordinate action fixture with source curvature."""
    def __init__(self):
        self.d=np.linspace(.7,1.4,268);self.l=np.sin(np.arange(268)+.3)/50
        self.a=np.cos(np.arange(268)*.17)/np.sqrt(268)
        self.b=np.sin(np.arange(268)*.13+.2)/np.sqrt(268)
    def parent(self,r):
        return dict(value=.5*(self.d*r)@r+self.l@r,
            raw_gradient=self.d*r+self.l,raw_hessian=np.diag(self.d))
    def value(self,r):
        p,c=r;s=self.a@p;t=self.b@c
        return self.parent(p)['value']+.5*(self.d*c)@c-.4*self.l@c+.7*s*s*t*t
    def joint(self,r,ref):
        p,c=r;s=self.a@p;t=self.b@c
        g=np.r_[self.d*p+self.l+1.4*s*t*t*self.a,
                 self.d*c-.4*self.l+1.4*t*s*s*self.b]
        H=np.zeros((536,536));H[:268,:268]=np.diag(self.d)+1.4*t*t*np.outer(self.a,self.a)
        H[268:,268:]=np.diag(self.d)+1.4*s*s*np.outer(self.b,self.b)
        H[:268,268:]=2.8*s*t*np.outer(self.a,self.b);H[268:,:268]=H[:268,268:].T
        return dict(value=self.value(r),raw_gradient=g,raw_hessian=H)


class TemporalActionTests(unittest.TestCase):
    def setUp(self):
        self.P=lift();self.layout=paired_temporal_layout(self.P,[-.9,-.4,0.],[0.,.2,.85])
        self.owner=PolynomialOwners();self.refs=np.zeros((2,2,268))
        size=self.layout['size'];self.z=.03*np.sin(np.arange(size)*.11)
    def evaluate(self,z,**kw):
        return real_two_arm_temporal_action(z,self.layout,self.refs,{},nu_squared_action=4.,
            joint_action_evaluator=self.owner.joint,parent_action_evaluator=self.owner.parent,
            source_clock_incidence_bound=True,**kw)
    def literal(self,z):
        # Direct raw construction, without the assembler's local maps.
        l=self.layout;sx=l['position_size'];x=z[:sx].reshape(l['x_shape']);y=z[sx:].reshape(l['y_shape']);total=0.
        for k,hs in enumerate(l['steps']):
            r=np.array([self.P@np.r_[(x[k,a]+x[k+1,a])/2,(x[k+1,a]-x[k,a])/hs[a],y[k,a]] for a in range(2)])
            wp,wc=hs;total+=wc*self.owner.value(r)+(wp-wc)*self.owner.parent(r[0])['value']
        return total
    def test_full_history_literal_action_derivative_and_crossblocks(self):
        a=self.evaluate(self.z);d=np.cos(np.arange(len(self.z))*.07);d/=np.linalg.norm(d);h=2e-5
        finite=(self.literal(self.z+h*d)-self.literal(self.z-h*d))/(2*h)
        self.assertLess(abs(finite-a['gradient']@d),2e-9)
        gp=self.evaluate(self.z+h*d)['gradient'];gm=self.evaluate(self.z-h*d)['gradient']
        self.assertLess(np.max(abs((gp-gm)/(2*h)-a['hessian']@d)),2e-9)
        self.assertAlmostEqual(a['value'],self.literal(self.z),places=13)
        self.assertGreater(np.linalg.norm(a['hessian'][:106,106:212]),1e-8)
        self.assertEqual(a['algebraic_rows'].shape,(2,2,40))
        self.assertFalse(a['background_gradient_subtracted']);self.assertIsNone(a['complete_physical_mean_residual'])
    def test_all_canonical_faces_and_signed_independent_clocks(self):
        a=self.evaluate(self.z);faces=np.zeros(self.layout['x_shape'])
        faces[:-1]+=a['cell_initial_cotangents'];faces[1:]+=a['cell_final_cotangents']
        np.testing.assert_allclose(faces,a['position_cotangents'],atol=3e-16,rtol=3e-15)
        reverse=paired_temporal_layout(self.P,[0.,-.4,-.9],[0.,.2,.85])
        b=real_two_arm_temporal_action(self.z,reverse,self.refs,{},nu_squared_action=4.,
            joint_action_evaluator=self.owner.joint,parent_action_evaluator=self.owner.parent,
            source_clock_incidence_bound=True)
        self.assertTrue(np.all(b['coordinate_action_weights'][:,0]<0))
        self.assertFalse(np.allclose(a['gradient'],b['gradient']))
        self.assertIsNone(a['native_application']);self.assertFalse(a['native_quantum_force_computed'])
    def test_actual_nonlocal_and_moving_constraint_contacts_are_added(self):
        n=len(self.z);q=np.linspace(-.3,.4,n);lam=np.array([.73])
        def native(z):
            s=q@z;return dict(value=.5*s*s,gradient=s*q,hessian=np.outer(q,q))
        def boundary(z):
            return dict(value=.07*z[-1],gradient=np.r_[np.zeros(n-1),.07],hessian=np.zeros((n,n)))
        def constraints(z,m):
            C=np.zeros((1,n));C[0,0]=z[-1];C[0,-1]=z[0];H=np.zeros((n,n));H[0,-1]=H[-1,0]=m[0]
            return dict(residual=np.array([z[0]*z[-1]-.2]),jacobian=C,multiplier_hessian=H)
        a=self.evaluate(self.z,native_application=native,boundary_application=boundary,
            constraint_application=constraints,constraint_multipliers=lam)
        base=self.evaluate(self.z)
        np.testing.assert_allclose(a['hessian']-base['hessian'],np.outer(q,q),atol=2e-15)
        f=lambda z:self.evaluate(z,native_application=native,boundary_application=boundary,
            constraint_application=constraints,constraint_multipliers=lam)['constraint_KKT']['residual']
        d=np.sin(np.arange(n)*.23);d/=np.linalg.norm(d);h=3e-5
        expected=a['constraint_KKT']['jacobian']@np.r_[d,0.]
        self.assertLess(np.max(abs((f(self.z+h*d)-f(self.z-h*d))/(2*h)-expected)),3e-9)
        self.assertIsNone(a['complete_physical_mean_residual'])
    def test_rejects_complex_cast_zero_steps_and_incomplete_native(self):
        with self.assertRaises(ValueError):self.evaluate(self.z.astype(complex))
        with self.assertRaises(ValueError):paired_temporal_layout(self.P,[0.,0.],[0.,1.])
        with self.assertRaises(KeyError):self.evaluate(self.z,native_application=lambda z:dict(value=0.))
        with self.assertRaisesRegex(ValueError,'already-bound source-clock'):
            real_two_arm_temporal_action(self.z,self.layout,self.refs,{},nu_squared_action=4.,
                joint_action_evaluator=self.owner.joint,parent_action_evaluator=self.owner.parent)
    def test_actual_real_two_arm_owner_against_independent_literal_action(self):
        from bhsm.interface.muon_birth_attached_phase import enriched_representation_from_values
        from bhsm.interface.muon_birth_finite_normal_trace_graph import (
            finite_normal_trace_graph_action_value,pointwise_finite_normal_action)
        folder=REPO/'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1'
        receipt=json.loads((folder/'result.json').read_bytes())
        with np.load(folder/'application.npz',allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
        # A NEW declared tiny numerical quadrature tests the unchanged literal
        # source action; it does not replay the saved solve or claim convergence.
        rep=enriched_representation_from_values(receipt,arrays,radial_points=3,cap_points=24)
        raw=arrays['updated_raw_pair'];ref=arrays['reference_raw_pair'];P=generic_coordinate_lift(rep['gauge_labels'])['lift']
        layout=paired_temporal_layout(P,[-2e-6,0.],[0.,2e-6]);eta=np.array([P.T@r for r in raw]);hs=layout['steps'][0]
        x=np.array([[eta[a,:106]-hs[a]*eta[a,106:212]/2 for a in range(2)],
                    [eta[a,:106]+hs[a]*eta[a,106:212]/2 for a in range(2)]])
        state=pack_temporal_state(layout,x,eta[:,212:][None]);params=receipt['action_parameters']
        a=real_two_arm_temporal_action(state,layout,ref[None],rep,**params)
        direction=np.zeros_like(state);dx=direction[:layout['position_size']].reshape(layout['x_shape'])
        # Nonzero geometry, gauge and Higgs variations on BOTH arms; equal
        # endpoint shifts hold their coordinate velocities, without deleting At.
        for arm in range(2):
            dx[:,arm,25]=.002*(arm+1);dx[:,arm,40]=.03;dx[:,arm,103]=-.04*(arm+1)
        direction[layout['position_size']+24]=.003
        def literal(z):
            sx=layout['position_size'];xx=z[:sx].reshape(layout['x_shape']);yy=z[sx:].reshape(layout['y_shape']);rr=[]
            for arm,h in enumerate(hs):rr.append(P@np.r_[(xx[0,arm]+xx[1,arm])/2,(xx[1,arm]-xx[0,arm])/h,yy[0,arm]])
            rr=np.array(rr);return hs[1]*finite_normal_trace_graph_action_value(rr,ref,rep,**params)+(hs[0]-hs[1])*pointwise_finite_normal_action(rr[0],rep,**params)['value']
        h=2e-4;finite=(literal(state+h*direction)-literal(state-h*direction))/(2*h)
        analytic=a['gradient']@direction
        self.assertLess(abs(finite-analytic)/max(1.,abs(analytic)),2e-8)
        self.assertAlmostEqual(a['value'],literal(state),places=11)
        self.assertGreater(np.linalg.norm(a['hessian'][:106,106:212]),1e-20)
        unequal=paired_temporal_layout(P,[-2e-6,0.],[0.,3e-6])
        with self.assertRaisesRegex(ValueError,'source-rate pullback'):
            real_two_arm_temporal_action(state,unequal,ref[None],rep,**params)
    def test_original_profile_clock_pullback_requires_rate_chain_rule(self):
        from bhsm.interface.muon_exact_material_response import exact_geometric_connection_coefficient_jets
        folder=REPO/'artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
        with np.load(folder/'application.npz',allow_pickle=False) as f:raw=f['initial_pair'][0].copy()
        r=-1.7;S=np.ones(100);S[37:74]=r;S[99]=r;changed=raw.copy();changed[:100]*=S
        rho=np.array([.31])
        def rows(x):
            return exact_geometric_connection_coefficient_jets(12,x[:37],x[37:74],x[74:98],rho,
                source_value=x[98],source_rate=x[99])['rows'][0]
        base=rows(raw);scaled=rows(changed)
        for key,factor in (('connection_lambda',1.),('lambda_rho',1.),('lambda_tau',r)):
            a=base[key];b=scaled[key]
            self.assertLess(abs(b.value-factor*a.value),3e-15)
            np.testing.assert_allclose(b.gradient*S,factor*a.gradient,atol=2e-12,rtol=2e-12)
            np.testing.assert_allclose(S[:,None]*b.hessian*S[None,:],factor*a.hessian,atol=3e-11,rtol=3e-11)
        # Inherited temporal source is not made covariant by changing an
        # integration weight alone; the actual nonzero rate changes by r.
        self.assertGreater(abs(scaled['lambda_tau'].value-base['lambda_tau'].value),1e-7)


if __name__=='__main__':unittest.main()
