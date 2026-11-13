"""Independent full-frame controls; no physical/native carrier is chosen."""
from __future__ import annotations

import unittest
import mpmath as mp
import numpy as np

from bhsm.interface.muon_m8_original_hopf_spin_lift import m8_original_hopf_spin_lift_jets
from bhsm.interface.muon_original_m8_geometric_expression import original_left_maurer_coefficient_maps
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization


KEYS=('value','x','y','xy')


def gamma5():
    return full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]]


def profile(t,r,x,y):
    d=mp.mpf
    logs=(d('.03')*t-d('.02')*r-d('.01')*x+d('.012')*y-d('.005')*x*y+d('.006')*r*x,
        d('.04')*t+d('.07')*r+d('.02')*x-d('.015')*y+d('.009')*x*y+d('.007')*t*y,
        d('.12')*t+d('.14')*r+d('.08')*x-d('.09')*y+d('.04')*x*y+d('.018')*t*x-d('.012')*r*y+d('.006')*t*x*y,
        -d('.11')*t+d('.16')*r-d('.05')*x+d('.06')*y-d('.03')*x*y-d('.009')*t*y+d('.014')*r*x-d('.004')*r*x*y)
    beta=d('.12')+d('.04')*t-d('.03')*r+d('.008')*x+d('.006')*y+d('.002')*x*y+d('.003')*r*x*y
    return tuple(mp.exp(a)for a in logs)+(beta,)


def literal_fields(x,y):
    t,r=mp.mpf('.17'),mp.mpf('.29')
    val=profile(t,r,x,y)
    def dl(i,axis):
        return mp.diff(lambda u:mp.log(profile(u,r,x,y)[i]),t)if axis==0 else mp.diff(lambda u:mp.log(profile(t,u,x,y)[i]),r)
    return dict(zip(('N','C','A','B','beta'),val),
        np=dl(0,1),cp=dl(1,1),ap=dl(2,1),bp=dl(3,1),
        la=dl(2,0),lb=dl(3,0),lc=dl(1,0),
        betap=mp.diff(lambda u:profile(t,u,x,y)[4],r))


def mp_jets(fun):
    z=mp.mpf(0)
    return dict(value=fun(z,z),x=mp.diff(lambda x:fun(x,z),z),
        y=mp.diff(lambda y:fun(z,y),z),xy=mp.diff(lambda x:mp.diff(lambda y:fun(x,y),z),z))


def fixture_fields():
    with mp.workdps(64):
        return {name:{k:complex(v)for k,v in mp_jets(lambda x,y,name=name:literal_fields(x,y)[name]).items()}
            for name in literal_fields(0,0)}


def structure_coefficients(f):
    """Independent Lie brackets, not a KK or spin-conjugation formula."""
    N,C,A,B,beta=(f[k]for k in('N','C','A','B','beta'))
    L=mp.sqrt(A*A+B*B);r=A*B/L;lam=A*A/(L*L)
    Lt=lam*f['la']+(1-lam)*f['lb'];Lr=lam*f['ap']+(1-lam)*f['bp']
    rt=f['la']+f['lb']-Lt;rr=f['ap']+f['bp']-Lr
    q={}
    def put(c,a,b,v):q[c,a,b]=v;q[c,b,a]=-v
    put(0,0,1,f['np']/C);put(1,0,1,-(f['lc']-beta*f['cp']-f['betap'])/N)
    for a in range(3):
        put(a+2,0,a+2,-(rt-beta*rr)/N);put(a+5,0,a+5,-(Lt-beta*Lr)/N)
        put(a+2,1,a+2,-rr/C);put(a+5,1,a+5,-Lr/C)
        lt=2*lam*(1-lam)*(f['la']-f['lb']-beta*(f['ap']-f['bp']))/N
        lr=2*lam*(1-lam)*(f['ap']-f['bp'])/C
        put(a+5,0,a+2,-L*lt/r);put(a+5,1,a+2,-L*lr/r)
    for a in range(3):
        for b in range(a+1,3):
            c=3-a-b;sign=1 if(a,b,c)in((0,1,2),(1,2,0),(2,0,1))else-1
            put(c+2,a+2,b+2,2*(1-2*lam)*sign/r)
            put(c+5,a+2,b+2,2*L*lam*(1-lam)*sign/(r*r))
            put(c+5,a+5,b+5,2*sign/L)
    for a in range(3):
        for b in range(3):
            if a==b:continue
            c=3-a-b;sign=1 if(a,b,c)in((0,1,2),(1,2,0),(2,0,1))else-1
            put(c+2,a+5,b+2,2*sign/L)
    return q


def koszul_body(c,G):
    eta=np.array([1]+[-1]*7)
    body=np.zeros((16,16),complex)
    for a in range(8):
        for b in range(8):
            for k in range(8):
                w=(eta[a]*c.get((a,k,b),0)-eta[k]*c.get((k,b,a),0)+eta[b]*c.get((b,a,k),0))/2
                if w:body+=.25j*complex(w)*G[k]@G[a]@G[b]
    return body


class M8OriginalHopfSpinTests(unittest.TestCase):
    def test_full_adapted_Koszul_and_all_independent_MP64_contacts(self):
        f=fixture_fields();out=m8_original_hopf_spin_lift_jets(f,gamma5_base=gamma5());G=out['gamma_original_and_fixed_adapted_slots']
        with mp.workdps(64):
            coeff={index:mp_jets(lambda x,y,index=index:structure_coefficients(literal_fields(x,y))[index])
                for index in structure_coefficients(literal_fields(0,0))}
            expected={k:koszul_body({i:v[k]for i,v in coeff.items()},G)for k in KEYS}
            angles=mp_jets(lambda x,y:mp.atan(literal_fields(x,y)['A']/literal_fields(x,y)['B']))
        for k in KEYS:
            np.testing.assert_allclose(out['adapted_Cartan_KK_body'][k],expected[k],rtol=2e-14,atol=7e-15)
            np.testing.assert_allclose(out['angle'][k],complex(angles[k]),rtol=2e-14,atol=1e-16)
            self.assertLess(np.max(abs(out['transformed_body_minus_adapted_body'][k])),7e-15)
            self.assertLess(np.max(abs(out['transformed_principal_minus_adapted'][k])),7e-15)
        self.assertGreater(np.linalg.norm(out['vertical_horizontal_spin_connection_body']['value']),1)
        self.assertLess(np.max(abs(out['finite_gamma_ordered_product_difference'])),2e-15)

    def test_literal_MP64_spin_product_with_complex_independent_sources(self):
        f=fixture_fields()
        # Complex analytic axes must be differentiated, not conjugated.
        for n in f:f[n]['y']*=1+.4j;f[n]['xy']*=1+.4j
        out=m8_original_hopf_spin_lift_jets(f,gamma5_base=gamma5())
        biv=out['boost_free_spatial_generators']
        with mp.workdps(64):
            bm=[mp.matrix(a.tolist())for a in biv];ident=mp.eye(16)
            def literal_entry(x,y,i,j):
                ff=literal_fields(x,(1+mp.mpf('.4')*1j)*y);theta=mp.atan(ff['A']/ff['B'])
                S=ident
                for b in bm:S=S*(mp.cos(theta/2)*ident+mp.sin(theta/2)*b)
                return S[i,j]
            # The complete matrix follows the same three commuting factors;
            # check every nonzero support entry and an explicit zero guard.
            support=np.argwhere(abs(out['S']['value'])>0).tolist()+[[0,1]]
            for i,j in support:
                expected=mp_jets(lambda x,y:literal_entry(x,y,i,j))
                for k in KEYS:self.assertLess(abs(out['S'][k][i,j]-complex(expected[k])),4e-15)
        for k in KEYS:self.assertLess(np.max(abs(out['spin_inverse_rows'][k])),4e-15)
        self.assertGreater(np.max(abs(out['analytic_inverse']['y']-out['S']['y'].conj().T)),1e-3)

    def test_full_left_Peter_Weyl_differential_without_projection(self):
        f=fixture_fields();o=m8_original_hopf_spin_lift_jets(f,gamma5_base=gamma5());G=o['gamma_original_and_fixed_adapted_slots']
        # Different complete u/v cutoffs expose both tensor axes, not a
        # constant fibre mode; this tests application, not a physical cutoff.
        eu=scalar_s3_discretization(2);ev=scalar_s3_discretization(1)
        U=original_left_maurer_coefficient_maps(eu['angular_derivative_matrices'],eu['scalar_labels'])
        V=original_left_maurer_coefficient_maps(ev['angular_derivative_matrices'],ev['scalar_labels'])
        hu,hv=U.shape[1],V.shape[1]
        rng=np.random.default_rng(931);q=rng.normal(size=(16,hu,hv))+1j*rng.normal(size=(16,hu,hv))
        qt=rng.normal(size=q.shape)+1j*rng.normal(size=q.shape);qr=rng.normal(size=q.shape)+1j*rng.normal(size=q.shape)
        sm=lambda M,q:np.einsum('ab,buv->auv',M,q)
        du=lambda E,q:np.einsum('ij,ajv->aiv',E,q)
        dv=lambda E,q:np.einsum('ij,auj->aui',E,q)
        S,T=o['S']['value'],o['analytic_inverse']['value'];orig=sm(T,q)
        orig_t=sm(T,qt)+sm(o['spin_connection_time']['value']@T,q)
        orig_r=sm(T,qr)+sm(o['spin_connection_chi']['value']@T,q)
        A,B=f['A']['value'],f['B']['value']
        literal=sm(o['time_coordinate_principal']['value'],orig_t)+sm(o['chi_coordinate_principal']['value'],orig_r)+sm(o['original_body']['value'],orig)
        expected=sm(o['time_coordinate_principal']['value'],qt)+sm(o['chi_coordinate_principal']['value'],qr)+sm(o['adapted_Cartan_KK_body']['value'],q)
        for a in range(3):
            literal+=sm(1j*G[a+2]/A,du(U[a],orig))+sm(1j*G[a+5]/B,dv(V[a],orig))
            expected+=sm(o['unit_U_principal']['value'][a],du(U[a],q))+sm(o['unit_V_principal']['value'][a],dv(V[a],q))
        np.testing.assert_allclose(sm(S,literal),expected,rtol=1e-13,atol=9e-14)
        self.assertEqual((hu,hv),(14,5))
        self.assertFalse(o['associated_mode_projection_selected']);self.assertFalse(o['complement_set_zero'])
        self.assertFalse(o['physical_state_or_outgoing_domain_selected'])

    def test_explicit_complete_contacts_and_real_base_guards(self):
        f=fixture_fields();bad={n:dict(v)for n,v in f.items()};del bad['A']['xy']
        with self.assertRaisesRegex(ValueError,'explicit'):m8_original_hopf_spin_lift_jets(bad,gamma5_base=gamma5())
        for n,value in(('A',-.1),('B',.1+.01j),('N',0)):
            bad={n:dict(v)for n,v in f.items()};bad[n]['value']=value
            with self.assertRaisesRegex(ValueError,'positive'):m8_original_hopf_spin_lift_jets(bad,gamma5_base=gamma5())


if __name__=='__main__':unittest.main()
