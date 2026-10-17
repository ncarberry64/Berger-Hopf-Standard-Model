"""Literal original-owner, full-fibre and integration-by-parts controls."""
from __future__ import annotations
import sys
import unittest
import numpy as np


from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_unsquared_weak_trace,d5_sigma_foliation_eta
from bhsm.interface.muon_full_d5_differential_form import (full_d5_differential_coefficients,
    apply_full_d5_expression,full_d5_weak_trial_action,explicit_positive_trial_form)


def fields(s):
    s=np.asarray(s,float);q=len(s)
    c=dict(lapse=np.full(q,1.3),radial_coframe=1+.1*s,radius=1+.2*s,
        coordinate_shift=.05+.03*s,geometric_time_contact=.025+.01*s,
        geometric_radial_contact=.035+.02*s,surface_proper_clock_rate=.9+.02*s,
        eta_profile=.7+.13*s,eta_profile_radial=np.full(q,.13),
        eta_profile_coordinate_time=np.full(q,.017),sigma_radial=np.full(q,.5),
        sigma_coordinate_time=np.full(q,.021))
    c['volume_density']=c['lapse']*c['radial_coframe']*c['radius']**3
    c['eta_radial_contact']=-c['eta_profile_radial']/np.tan(c['eta_profile'])/c['radial_coframe']
    c['gauge_connection_material']=np.arange(q*20).reshape(q,5,4)*(.0003+.0001j)+.001
    # Explicit normal-source slots for the existing sigma owner; no value
    # depends on them in these declared coefficient-value controls.
    for key in tuple(c):
        if key!='gauge_connection_material':c[key+'_first']=np.full((1,q),.007)
    return c


class FullD5DifferentialTests(unittest.TestCase):
    def test_literal_original_ordered_owner_n0_n1_both_eta(self):
        f=full_d5_localized_lepton_trace();rng=np.random.default_rng(451635)
        for n in (0,1):
            E=scalar_s3_discretization(n)['angular_derivative_matrices'];h=E.shape[-1]
            c=fields([.21,.64]);q=2;d=64*h;D=6*d
            V=(rng.normal(size=(q,D,2))+1j*rng.normal(size=(q,D,2)))*.02
            Vr=(rng.normal(size=V.shape)+1j*rng.normal(size=V.shape))*.03
            Vt=(rng.normal(size=V.shape)+1j*rng.normal(size=V.shape))*.04
            L=(rng.normal(size=(q,3,D))+1j*rng.normal(size=(q,3,D)))*.02
            w=np.array([.3,.4]);energy=.27+.031j
            for eps in (-1,1):
                a=full_d5_differential_coefficients(c,E,sheet_orientation=eps,full_representation=f)
                out=full_d5_weak_trial_action(a,V,Vr,Vt,L,w,energy=energy)
                expected=np.zeros((3,2),complex);expectedE=expected.copy();point=np.empty_like(V)
                for family in range(3):
                    for b,branch in enumerate(('particle','conjugate')):
                        sl=slice((2*family+b)*d,(2*family+b+1)*d)
                        gamma=f['gamma5D_'+branch];gen=f['unitTr16_gauge_particle']
                        if branch=='conjugate':gen=gen.conj()
                        eta=d5_sigma_foliation_eta(c,gamma=gamma,carrier_count=16,angular_count=h,
                            sheet_orientation=eps)['sigma_normal_eta_contact']
                        ref=d5_unsquared_weak_trace(c,w,gamma=gamma,carrier_generators=gen,
                            angular_derivatives=E,right_values=V[:,sl],right_radial=Vr[:,sl],
                            right_coordinate_time=Vt[:,sl],literal_left_values=L[:,:,sl],
                            energy=energy,sheet_orientation=eps,eta_clifford_contact=eta)
                        expected+=ref['unsquared_trace_action'];expectedE+=ref['unsquared_trace_action_energy_first']
                        point[:,sl]=ref['original_D5_on_trial']
                np.testing.assert_allclose(out['action'],expected,atol=3e-13,rtol=3e-13)
                np.testing.assert_allclose(out['phase_frequency_first'],expectedE,atol=3e-13,rtol=3e-13)
                np.testing.assert_allclose(out['point_expression_on_trial'],point,atol=3e-13,rtol=3e-13)
                self.assertEqual(a['full_width'],384*h)
                self.assertFalse(out['source_left_conjugated'])
                self.assertFalse(a['physical_native_or_AE4_identification'])
                self.assertGreater(np.linalg.norm(a['blocks']['particle']['sigma_eta_contact']),.01)

    def test_covariant_split_and_native_phase_are_distinct(self):
        c=fields([.4]);a=full_d5_differential_coefficients(c,np.zeros((3,1,1)),sheet_orientation=1)
        for branch in ('particle','conjugate'):
            b=a['blocks'][branch];g=b['gamma0']
            np.testing.assert_allclose(b['time'],1j*g@b['Dtau_time'],atol=2e-15)
            np.testing.assert_allclose(b['radial'],g@(1j*b['Dtau_radial']-b['W_radial']),atol=2e-15)
            np.testing.assert_allclose(b['body'],g@(1j*b['Dtau_body']-b['W_body']),atol=2e-15)
            np.testing.assert_allclose(b['A_body'],b['Dtau_body']+b['W_body'],atol=2e-15)
            self.assertGreater(np.linalg.norm(b['A_body']-b['body']),.1)
            np.testing.assert_allclose(b['energy'],1j*g@b['A_energy'],atol=2e-15)
            self.assertGreater(np.linalg.norm(b['W_body']-b['W_body'].conj().swapaxes(-1,-2)),.01)

    def test_independent_bilinear_normal_Green_identity(self):
        # mu*a_rho is a polynomial. All full spin/gauge/eta bodies remain
        # in the expression and in its density formal adjoint, and cancel
        # exactly as the ordered Green formula requires.
        x,w=np.polynomial.legendre.leggauss(12);s=(x+1)/2;w=w/2;c=fields(s)
        a=full_d5_differential_coefficients(c,np.zeros((3,1,1)),sheet_orientation=-1)
        rng=np.random.default_rng(88019);D=384
        U=rng.normal(size=(4,D,2))+1j*rng.normal(size=(4,D,2))
        L=rng.normal(size=(3,2,D))+1j*rng.normal(size=(3,2,D))
        val=lambda t:sum(t**k*U[k] for k in range(4))
        der=lambda t:sum(k*t**(k-1)*U[k] for k in range(1,4))
        left=lambda t:sum(t**k*L[k] for k in range(3))
        leftd=lambda t:sum(k*t**(k-1)*L[k] for k in range(1,3))
        V=np.array([val(t) for t in s]);Vr=np.array([der(t) for t in s]);Lv=np.array([left(t) for t in s]);Ld=np.array([leftd(t) for t in s])
        for placement in ('lorentz','formal_product'):
            acted=apply_full_d5_expression(a,V,Vr,np.zeros_like(V),placement=placement)
            total=np.zeros((2,2),complex);prefix='' if placement=='lorentz' else 'A_'
            for family in range(3):
                for b,branch in enumerate(('particle','conjugate')):
                    sl=slice((2*family+b)*64,(2*family+b+1)*64);B=a['blocks'][branch]
                    g0=B['gamma0'];full=full_d5_localized_lepton_trace();gamma=full['gamma5D_'+branch]
                    gr=np.kron(gamma[4],np.eye(16));I=np.eye(64)
                    for j,t in enumerate(s):
                        N,C,R,z=1.3,1+.1*t,1+.2*t,.05+.03*t
                        mu=N*C*R**3;dm=N*(.1*R**3+3*C*R**2*.2)
                        if placement=='lorentz':da=-1j*g0*.03/N+1j*gr*.1/C**2
                        else:da=-I*.03/N-1j*g0@gr*.1/C**2
                        aa=B[prefix+'radial'][j];body=B[prefix+'body'][j]
                        density_left=-(dm*Lv[j,:,sl]@aa+mu*Ld[j,:,sl]@aa+mu*Lv[j,:,sl]@da)+mu*Lv[j,:,sl]@body
                        total+=w[j]*(mu*Lv[j,:,sl]@acted[j,sl]-density_left@V[j,sl])
            ends=fields([0.,1.]);ae=full_d5_differential_coefficients(ends,np.zeros((3,1,1)),sheet_orientation=-1)
            boundary=np.zeros((2,2),complex)
            for family in range(3):
                for b,branch in enumerate(('particle','conjugate')):
                    sl=slice((2*family+b)*64,(2*family+b+1)*64)
                    for j,t in enumerate((0.,1.)):
                        boundary+=(1 if j else -1)*ends['volume_density'][j]*left(t)[:,sl]@ae['blocks'][branch][prefix+'radial'][j]@val(t)[sl]
            np.testing.assert_allclose(total,boundary,atol=2e-11,rtol=2e-13)

    def test_explicit_positive_form_keeps_all_rows_without_AE4_claim(self):
        c=fields([.2,.7]);a=full_d5_differential_coefficients(c,np.zeros((3,1,1)),sheet_orientation=1)
        rng=np.random.default_rng(123);V=rng.normal(size=(2,384,2))+1j*rng.normal(size=(2,384,2))
        G=np.broadcast_to(np.eye(64),(2,2,64,64)).copy();G[:,1]*=1.7
        r=explicit_positive_trial_form(a,V,V*.13,V*.21,positive_coordinate_weights=[.3,.4],positive_output_block_grams=G)
        np.testing.assert_allclose(r['form'],r['form'].conj().T,atol=2e-11)
        self.assertGreater(np.min(np.linalg.eigvalsh(r['form'])),0)
        self.assertFalse(r['physical_native_or_AE4_identification'])
        self.assertEqual(r['full_fibre_count'],384)
        G[0,0,0,0]=-1
        with self.assertRaisesRegex(ValueError,'positive Hermitian'):
            explicit_positive_trial_form(a,V,V,V,positive_coordinate_weights=[.3,.4],positive_output_block_grams=G)

    def test_nonzero_phase_contact_survives_large_common_body(self):
        c=fields([.3]);c['geometric_time_contact'][:]=1e20
        c['surface_proper_clock_rate'][:]=1e-18
        a=full_d5_differential_coefficients(c,np.zeros((3,1,1)),sheet_orientation=1)
        V=np.zeros((1,384,1),complex);L=np.zeros((1,1,384),complex)
        V[0,0,0]=1;L[0,0,32]=1
        # The owned LR Gamma0 pairs the first spin slot with row32.
        Z=np.zeros_like(V)
        r=full_d5_weak_trial_action(a,V,Z,Z,L,[1.])
        expected=(c['volume_density'][0]*c['surface_proper_clock_rate'][0]/c['lapse'][0]
                  *a['blocks']['particle']['gamma0'][32,0])
        self.assertGreater(abs(expected),1e-20)
        np.testing.assert_allclose(r['phase_frequency_first'][0,0],expected,rtol=2e-15,atol=1e-32)
        # E=1 minus E=0 is exactly swallowed by the common1e20 body in
        # this control. The source coefficient path must never use it.
        subtract=(apply_full_d5_expression(a,V,Z,Z,energy=1)
                  -apply_full_d5_expression(a,V,Z,Z,energy=0))
        self.assertEqual(subtract[0,32,0],0)


if __name__=='__main__':unittest.main()
