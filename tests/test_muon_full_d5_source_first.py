"""Independent literal-source, moving-test and real-Riesz controls.

These are off-shell coefficient controls, not physical E/B/tail derivatives.
The MP64 oracle differentiates the original unsquared D5 expression and
sigma-level-set normal directly; it does not call a coefficient jet owner.
"""
from __future__ import annotations
import copy
import sys
import unittest
import mpmath as mp
import numpy as np


from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_unsquared_weak_trace
from bhsm.interface.muon_full_d5_differential_form import full_d5_differential_coefficients, apply_full_d5_expression
from bhsm.interface.muon_full_d5_source_first import (full_d5_differential_source_first,
    apply_full_d5_source_first, full_d5_weak_source_first, full_d5_positive_source_first)


def fixture(t=0., q=2):
    """A smooth complex germ; slot1 is dt, slot0 is deliberately different."""
    s=np.linspace(.2,.65,q)
    bases=dict(lapse=1.3+.03*s,radial_coframe=1+.1*s,radius=1+.2*s,
        coordinate_shift=.05+.03*s,geometric_time_contact=.025+.01*s,
        geometric_radial_contact=.035+.02*s,surface_proper_clock_rate=.9+.02*s,
        eta_profile=.7+.13*s,eta_profile_radial=.13+.01*s,
        eta_profile_coordinate_time=.017+.002*s,sigma_radial=.5+.03*s,
        sigma_coordinate_time=.021+.003*s)
    slopes={k:(i+1)*(.003+.0004j)*(1+.2*s) for i,k in enumerate(bases)}
    slopes['lapse']=(.04+.007j)*(1+.2*s)
    c={k:np.asarray(v,complex)+t*slopes[k] for k,v in bases.items()}
    for k in bases:c[k+'_first']=np.array([slopes[k]*(-.31+.17j),slopes[k]])
    g=np.arange(q*20).reshape(q,5,4)
    gx=(.013-.017j)*(1+g/37)
    c['gauge_connection_material']=.001+g*(.0003+.0001j)+t*gx
    c['gauge_connection_material_first']=np.array([gx*(.21+.19j),gx])
    c['volume_density']=c['lapse']*c['radial_coframe']*c['radius']**3
    mu1=(c['lapse_first'][1]*c['radial_coframe']*c['radius']**3
        +c['lapse']*c['radial_coframe_first'][1]*c['radius']**3
        +3*c['lapse']*c['radial_coframe']*c['radius']**2*c['radius_first'][1])
    c['volume_density_first']=np.array([mu1*(-.31+.17j),mu1])
    c['eta_radial_contact']=-c['eta_profile_radial']/np.tan(c['eta_profile'])/c['radial_coframe']
    return c


def mpc(z):
    z=complex(z)
    return mp.mpc(str(z.real),str(z.imag))


def literal_mp_blocks(c0,E,f,branch,r,eps,pair,t):
    """4x4 spin entries of the original action for one carrier/angular pair."""
    ci,cj,ai,aj=pair;h=E.shape[-1]
    val=lambda k:mpc(c0[k][r])+t*mpc(c0[k+'_first'][1,r])
    N,C,R,z,h0,h4,ell=(val(k) for k in ('lapse','radial_coframe','radius',
        'coordinate_shift','geometric_time_contact','geometric_radial_contact','surface_proper_clock_rate'))
    G=[mp.matrix([[mpc(x) for x in row] for row in a]) for a in f['gamma5D_'+branch]]
    I=mp.eye(4);ident=int(ci==cj and ai==aj)
    gen=f['unitTr16_gauge_particle']
    if branch=='conjugate':gen=gen.conj()  # Fixed representation only.
    A=[]
    for mu in range(5):
        A.append(sum((mpc(c0['gauge_connection_material'][r,mu,k])
            +t*mpc(c0['gauge_connection_material_first'][1,r,mu,k]))
            *mpc(gen[k,ci,cj])*int(ai==aj) for k in range(4)))
    sr,st=val('sigma_radial'),val('sigma_coordinate_time')
    s0=(st-z*sr)/N;s4=sr/C;root=mp.sqrt(s4*s4-s0*s0)
    n0,n4=-s0/root,s4/root
    ff,ft,fr=val('eta_profile'),val('eta_profile_coordinate_time'),val('eta_profile_radial')
    normal_f=n0*(ft-z*fr)/N+n4*fr/C
    mass=-mp.cot(ff)*normal_f
    eta=mp.j*(-n0*G[0]+eps*n4*G[4])*mass*ident
    angular=sum((mp.j*G[a+1]*mpc(E[a,ai,aj])*int(ci==cj) for a in range(3)),mp.zeros(4))
    spin=-mp.mpf('1.5')*mp.j*G[1]*G[2]*G[3]*ident
    inside=mp.j*eps*G[4]*h4*ident+eta+(spin+angular)/R
    inside+=mp.j*eps*G[4]*A[1]/C
    inside+=sum((mp.j*G[a+1]*A[a+2]/R for a in range(3)),mp.zeros(4))
    dt=I*ident/N;dr=-z*I*ident/N;db=I*(h0*ident+(A[0]-z*A[1])/N)
    wr=-mp.j*eps*G[0]*G[4]*ident/C;wb=-G[0]*inside
    return dict(time=mp.j*G[0]*dt,radial=G[0]*(mp.j*dr-wr),body=G[0]*(mp.j*db-wb),
        energy=G[0]*ell*ident/N,Dtau_time=dt,Dtau_radial=dr,Dtau_body=db,
        W_radial=wr,W_body=wb,A_time=dt,A_radial=dr+wr,A_body=db+wb,
        A_energy=-mp.j*I*ell*ident/N,sigma_eta_contact=eta)


def literal_eta(c,gamma,h,eps):
    """Value-only normal, independently transcribed from its level-set definition."""
    N,C,z=c['lapse'],c['radial_coframe'],c['coordinate_shift']
    s0=(c['sigma_coordinate_time']-z*c['sigma_radial'])/N
    s4=c['sigma_radial']/C;root=np.sqrt(s4*s4-s0*s0)
    n0,n4=-s0/root,s4/root
    normal_f=n0*(c['eta_profile_coordinate_time']-z*c['eta_profile_radial'])/N+n4*c['eta_profile_radial']/C
    mass=-normal_f/np.tan(c['eta_profile'])
    G0,Gr=(np.kron(gamma[k],np.eye(16*h)) for k in (0,4))
    return 1j*(-n0[:,None,None]*G0+eps*n4[:,None,None]*Gr)*mass[:,None,None]


def legacy_full(c,E,V,Vr,Vt,L,w,energy,eps,f):
    h=E.shape[-1];d=64*h;out=np.empty_like(V);form=np.zeros((L.shape[1],V.shape[-1]),complex)
    for fam in range(3):
        for b,branch in enumerate(('particle','conjugate')):
            sl=slice((2*fam+b)*d,(2*fam+b+1)*d)
            gamma=f['gamma5D_'+branch];gen=f['unitTr16_gauge_particle']
            if branch=='conjugate':gen=gen.conj()
            a=d5_unsquared_weak_trace(c,w,gamma=gamma,carrier_generators=gen,
                angular_derivatives=E,right_values=V[:,sl],right_radial=Vr[:,sl],
                right_coordinate_time=Vt[:,sl],literal_left_values=L[:,:,sl],
                energy=energy,sheet_orientation=eps,eta_clifford_contact=literal_eta(c,gamma,h,eps))
            out[:,sl]=a['original_D5_on_trial'];form+=a['unsquared_trace_action']
    return out,form


def fd4(fun,step=.0002):
    return (fun(-2*step)-8*fun(-step)+8*fun(step)-fun(2*step))/(12*step)


class FullD5SourceFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full=full_d5_localized_lepton_trace()

    def test_mp64_literal_coefficient_derivatives(self):
        mp.mp.dps=64;c=fixture(q=1);maxerr=0.
        for n in (0,1):
            E=scalar_s3_discretization(n)['angular_derivative_matrices'];h=E.shape[-1]
            pairs=[(0,0,0,0),(6,7,0,0),(14,14,0,0)]
            if h>1:pairs.extend([(0,0,1,2),(7,7,4,4)])
            for eps in (-1,1):
                got=full_d5_differential_source_first(c,E,source_slot=1,sheet_orientation=eps,full_representation=self.full)
                for branch in ('particle','conjugate'):
                    for pair in pairs:
                        ci,cj,ai,aj=pair
                        rows=np.arange(4)*16*h+ci*h+ai;cols=np.arange(4)*16*h+cj*h+aj
                        for name in got['first']['blocks'][branch]:
                            ref=mp.diff(lambda t:literal_mp_blocks(c,E,self.full,branch,0,eps,pair,t)[name],mp.mpf(0))
                            expected=np.array(ref.tolist(),complex)
                            actual=got['first']['blocks'][branch][name][0][np.ix_(rows,cols)]
                            err=float(np.max(abs(actual-expected))/max(1.,float(np.max(abs(expected)))))
                            maxerr=max(maxerr,err)
                            np.testing.assert_allclose(actual,expected,rtol=4e-13,atol=4e-14)
        self.assertLess(maxerr,4e-13)

    def moving_maps(self,D,q=2):
        rng=np.random.default_rng(778629)
        z=lambda shape:(rng.normal(size=shape)+1j*rng.normal(size=shape))*.025
        return [z((q,D,2)) for _ in range(6)]+[z((q,3,D)) for _ in range(2)]

    def test_moving_trial_independent_left_density_and_phase_against_legacy(self):
        c=fixture();E=scalar_s3_discretization(0)['angular_derivative_matrices']
        V,Vr,Vt,Vx,Vrx,Vtx,L,Lx=self.moving_maps(384)
        w=np.array([.31,.47]);wx=np.array([.027,-.039]);energy=.27+.031j;ex=-.041+.023j
        for eps in (-1,1):
            germ=full_d5_differential_source_first(c,E,source_slot=1,sheet_orientation=eps,full_representation=self.full)
            kw=dict(value_first=Vx,radial_derivative_first=Vrx,time_derivative_first=Vtx,
                energy=energy,energy_first=ex,placement='lorentz')
            r=full_d5_weak_source_first(germ,V,Vr,Vt,independent_left=L,independent_left_first=Lx,
                coordinate_weights=w,coordinate_weights_first=wx,**kw)
            direct=lambda t:legacy_full(fixture(t),E,V+t*Vx,Vr+t*Vrx,Vt+t*Vtx,
                L+t*Lx,w+t*wx,energy+t*ex,eps,self.full)
            np.testing.assert_allclose(r['first'],fd4(lambda t:direct(t)[1]),rtol=2e-9,atol=3e-11)
            np.testing.assert_allclose(r['point_application']['first'],fd4(lambda t:direct(t)[0]),rtol=2e-9,atol=3e-11)
            self.assertGreater(np.linalg.norm(r['density_contact']),1e-5)
            self.assertGreater(np.linalg.norm(r['independent_left_contact']),1e-5)
            self.assertGreater(np.linalg.norm(r['point_application']['phase_frequency_contact']),1e-5)
            self.assertFalse(r['independent_analytic_left_conjugated'])
            # Anti-holomorphic substitution is numerically distinguishable.
            self.assertGreater(np.linalg.norm(r['first']-r['first'].conj()),.001)

    def test_real_axis_positive_form_including_moving_gram_and_density(self):
        c=fixture();E=scalar_s3_discretization(0)['angular_derivative_matrices'];d=64
        V,Vr,Vt,Vx,Vrx,Vtx,_,_=self.moving_maps(384)
        germ=full_d5_differential_source_first(c,E,source_slot=1,sheet_orientation=-1,full_representation=self.full)
        rng=np.random.default_rng(81235);Q=(rng.normal(size=(2,2,d,d))+1j*rng.normal(size=(2,2,d,d)))*.002
        G=np.broadcast_to(np.eye(d),(2,2,d,d)).copy().astype(complex)+Q.conj().swapaxes(-1,-2)@Q
        Qx=(rng.normal(size=Q.shape)+1j*rng.normal(size=Q.shape))*.003
        Gx=Qx+Qx.conj().swapaxes(-1,-2)
        w=np.array([.37,.51]);wx=np.array([.018,-.024]);energy=.19+.013j;ex=.029-.017j
        r=full_d5_positive_source_first(germ,V,Vr,Vt,value_first=Vx,radial_derivative_first=Vrx,
            time_derivative_first=Vtx,positive_coordinate_weights=w,coordinate_weights_first=wx,
            output_block_grams=G,output_block_grams_first=Gx,energy=energy,energy_first=ex,real_source_axis=True)
        def direct(t):
            ct=fixture(t);a=full_d5_differential_coefficients(ct,E,sheet_orientation=-1,full_representation=self.full,
                sigma_eta_contacts={b:literal_eta(ct,self.full['gamma5D_'+b],1,-1) for b in ('particle','conjugate')})
            out=apply_full_d5_expression(a,V+t*Vx,Vr+t*Vrx,Vt+t*Vtx,energy=energy+t*ex,placement='formal_product')
            ans=np.zeros((2,2),complex)
            for f in range(3):
                for b in range(2):
                    u=out[:,(2*f+b)*d:(2*f+b+1)*d]
                    ans+=sum((w[j]+t*wx[j])*u[j].conj().T@(G[j,b]+t*Gx[j,b])@u[j] for j in range(2))
            return ans
        np.testing.assert_allclose(r['first'],fd4(direct),rtol=2e-9,atol=3e-10)
        np.testing.assert_allclose(r['first'],r['first'].conj().T,atol=3e-13)
        self.assertGreater(np.min(np.linalg.eigvalsh(r['value'])),0.)
        self.assertFalse(r['full_native_domain_or_physical_outgoing_derivative_pass'])

    def test_exact_phase_partial_first_survives_huge_body(self):
        c=fixture(q=1);c['geometric_time_contact'][:]=1e20
        c['geometric_time_contact_first'][:]=1e19
        c['surface_proper_clock_rate'][:]=1e-18;c['surface_proper_clock_rate_first'][:]=2e-19
        E=np.zeros((3,1,1));g=full_d5_differential_source_first(c,E,source_slot=1,sheet_orientation=1,full_representation=self.full)
        V=np.zeros((1,384,1),complex);V[0,0,0]=1;Z=np.zeros_like(V)
        a=apply_full_d5_source_first(g,V,Z,Z,value_first=Z,radial_derivative_first=Z,
            time_derivative_first=Z,energy=0,energy_first=1,placement='lorentz')
        g0=g['value']['blocks']['particle']['gamma0'][32,0]
        expected=g0*(c['surface_proper_clock_rate_first'][1,0]/c['lapse'][0]
            -c['surface_proper_clock_rate'][0]*c['lapse_first'][1,0]/c['lapse'][0]**2)
        self.assertGreater(abs(expected),1e-20)
        np.testing.assert_allclose(a['phase_frequency_partial_first'][0,32,0],expected,rtol=3e-15,atol=1e-33)
        self.assertEqual((apply_full_d5_expression(g['value'],V,Z,Z,energy=1)
            -apply_full_d5_expression(g['value'],V,Z,Z,energy=0))[0,32,0],0)

    def test_missing_slot_and_source_and_positive_guards(self):
        c=fixture(q=1);E=np.zeros((3,1,1))
        for bad in (-1,True,2):
            with self.assertRaises(ValueError):full_d5_differential_source_first(c,E,source_slot=bad,sheet_orientation=1)
        bad=copy.deepcopy(c);del bad['gauge_connection_material_first']
        with self.assertRaisesRegex(ValueError,'explicit source first'):
            full_d5_differential_source_first(bad,E,source_slot=1,sheet_orientation=1)
        bad=copy.deepcopy(c);bad['sigma_radial_first'][1,0]=np.nan
        with self.assertRaises(ValueError):full_d5_differential_source_first(bad,E,source_slot=1,sheet_orientation=1)
        g=full_d5_differential_source_first(c,E,source_slot=1,sheet_orientation=1)
        Z=np.zeros((1,384,1),complex);G=np.broadcast_to(np.eye(64),(1,2,64,64)).copy()
        kw=dict(value_first=Z,radial_derivative_first=Z,time_derivative_first=Z,
            positive_coordinate_weights=[1],coordinate_weights_first=[.1],output_block_grams=G,
            output_block_grams_first=np.zeros_like(G),energy=0,energy_first=0,real_source_axis=True)
        with self.assertRaisesRegex(ValueError,'REAL source'):
            full_d5_positive_source_first(g,Z,Z,Z,**(kw|dict(real_source_axis=False)))
        Gn=G.copy();Gn[0,0,0,0]=-1
        with self.assertRaisesRegex(ValueError,'positive output Gram'):
            full_d5_positive_source_first(g,Z,Z,Z,**(kw|dict(output_block_grams=Gn)))

    def test_explicit_normal_contact_and_first_are_never_replaced(self):
        c=fixture(q=1);E=np.zeros((3,1,1))
        original=full_d5_differential_source_first(c,E,source_slot=1,sheet_orientation=-1)
        eta={b:original['value']['blocks'][b]['sigma_eta_contact'] for b in ('particle','conjugate')}
        dx={b:original['first']['blocks'][b]['sigma_eta_contact'] for b in eta}
        # Once an actual contact and its derivative are provided together,
        # this coefficient consumer must not invent a sigma continuation.
        supplied={k:v for k,v in c.items() if not k.startswith(('sigma_','eta_profile'))}
        got=full_d5_differential_source_first(supplied,E,source_slot=1,sheet_orientation=-1,
            eta_contacts=eta,eta_contacts_first=dx)
        for b in eta:
            for k in original['first']['blocks'][b]:
                np.testing.assert_array_equal(got['first']['blocks'][b][k],original['first']['blocks'][b][k])
        self.assertIn('explicit caller',got['eta_contact_owner'])
        with self.assertRaisesRegex(ValueError,'together'):
            full_d5_differential_source_first(c,E,source_slot=1,sheet_orientation=-1,eta_contacts=eta)


if __name__=='__main__':unittest.main()
