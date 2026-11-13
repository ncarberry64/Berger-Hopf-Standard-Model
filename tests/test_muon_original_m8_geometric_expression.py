"""Original-frame conventions, literal MP contacts and full Green identity."""
import unittest
import mpmath as mp
import numpy as np

from bhsm.interface.muon_original_m8_geometric_expression import (
    JETS, SCALARS, original_m8_clifford, original_left_maurer_coefficient_maps,
    original_m8_geometric_expression_jets, apply_original_m8_expression_jets,
    original_m8_ordered_weak_jets)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import (
    scalar_s3_discretization, scalar_section_labels, scalar_basis_values)


def gamma():
    return full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]]


def angular(n):
    a = scalar_s3_discretization(n)
    return original_left_maurer_coefficient_maps(a['angular_derivative_matrices'], a['scalar_labels'])


def jets(a):
    a = np.asarray(a, complex)
    return dict(value=a, x=np.zeros_like(a), y=np.zeros_like(a), xy=np.zeros_like(a))


def mc(x):
    z = complex(x)
    return mp.mpc(mp.mpf(z.real), mp.mpf(z.imag))


def mm(a):
    return mp.matrix([[mc(z) for z in row] for row in a])


def evaluate(a,x,y):
    return mc(a['value'][0])+x*mc(a['x'][0])+y*mc(a['y'][0])+x*y*mc(a['xy'][0])


def fixture():
    base = (1.1,.9,.8,1.2,.13,.027,.31,.81)
    return {name:dict(value=np.array([v]), x=np.array([.019*(i+1)+.003j]),
        y=np.array([-.013*(i+1)+.002j]), xy=np.array([.006-.0007j*(i+1)]))
        for i,(name,v) in enumerate(zip(SCALARS,base))}


def literal_blocks(c,U,V,G,pair,x,y):
    (ui,vi),(uj,vj)=pair
    hu,hv=U.shape[1],V.shape[1]
    I=mp.eye(16);zero=mp.zeros(16);delta=int(ui==uj and vi==vj)
    N,C,A,B,z,h0,hr,mu=(evaluate(c[k],x,y) for k in SCALARS)
    gg=[mm(a) for a in G]
    su=mp.j*mp.mpf('1.5')*gg[2]*gg[3]*gg[4]*delta
    sv=mp.j*mp.mpf('1.5')*gg[5]*gg[6]*gg[7]*delta
    for a in range(3):
        su+=mp.j*gg[a+2]*mc(U[a,ui,uj])*int(vi==vj)
        sv+=mp.j*gg[a+5]*mc(V[a,vi,vj])*int(ui==uj)
    spatial=mp.j*gg[1]*hr*delta+su/A+sv/B
    dt=I*delta/N;dr=-z*I*delta/N;db=h0*I*delta
    wr=-mp.j*gg[0]*gg[1]*delta/C;wb=-gg[0]*spatial
    return dict(time=mp.j*gg[0]*dt, radial=mp.j*gg[0]*dr+mp.j*gg[1]*delta/C,
        body=mp.j*gg[0]*db+spatial, A_time=dt, A_radial=dr+wr,A_body=db+wb)


class OriginalM8(unittest.TestCase):
    def test_left_maurer_matches_literal_right_SU2_flow(self):
        p=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
        q=(np.eye(2)+1j*(p[0]+2*p[1]+3*p[2]))/np.sqrt(15.)
        for n in (1,2):
            U=angular(n);values=scalar_basis_values(q[None],n)
            for a in range(3):
                step=2e-4
                def flow(t):
                    point=q@(np.cos(t)*np.eye(2)-1j*np.sin(t)*p[a])
                    return scalar_basis_values(point[None],n)
                fd=(flow(-2*step)-8*flow(-step)+8*flow(step)-flow(2*step))/(12*step)
                np.testing.assert_allclose(fd,values@U[a],atol=3e-12,rtol=3e-12)
        with self.assertRaises(ValueError):
            original_m8_geometric_expression_jets(fixture(),-angular(1),angular(0),gamma5_base=gamma())

    def test_all_original_spin16_coefficient_fourjets_against_MP(self):
        c=fixture();U,V=angular(1),angular(1)
        out=original_m8_geometric_expression_jets(c,U,V,gamma5_base=gamma())
        G=out['gamma8_original'];hu,hv=U.shape[1],V.shape[1]
        for pair in (((0,0),(0,0)),((1,2),(2,2)),((2,1),(2,2))):
            row=np.arange(16)*hu*hv+pair[0][0]*hv+pair[0][1]
            col=np.arange(16)*hu*hv+pair[1][0]*hv+pair[1][1]
            with mp.workdps(64):
                for name in ('time','radial','body','A_time','A_radial','A_body'):
                    f=lambda x,y:literal_blocks(c,U,V,G,pair,x,y)[name]
                    refs=dict(value=f(0,0),x=mp.diff(lambda x:f(x,0),0),
                        y=mp.diff(lambda y:f(0,y),0),xy=mp.diff(f,(0,0),(1,1)))
                    for key in JETS:
                        ref=np.array(refs[key].tolist(),complex)
                        got=out['coefficients'][name][key][0][np.ix_(row,col)]
                        np.testing.assert_allclose(got,ref,atol=2e-13,rtol=2e-13)
        self.assertFalse(out['native_statistics_or_SM_multiplicity_selected'])
        self.assertFalse(out['internal_twist_or_endomorphism_evaluated'])
        self.assertGreater(np.linalg.norm(out['original_u_spin_triple']),0)
        self.assertGreater(np.linalg.norm(out['original_v_spin_triple']),0)

    def test_moving_trials_left_weights_density_MP(self):
        c=fixture();U,V=angular(1),angular(0)
        out=original_m8_geometric_expression_jets(c,U,V,gamma5_base=gamma());d=out['width']
        source=(1,0);target=(2,0);hv=V.shape[1]
        cols=np.arange(16)*U.shape[1]*hv+source[0]*hv+source[1]
        rows=np.arange(16)*U.shape[1]*hv+target[0]*hv+target[1]
        rng=np.random.default_rng(161903)
        local=[{k:(rng.normal(size=(16,2))+1j*rng.normal(size=(16,2)))*.07 for k in JETS} for _ in range(3)]
        left={k:(rng.normal(size=(3,16))+1j*rng.normal(size=(3,16)))*.04 for k in JETS}
        maps=[]
        for a in local:
            m={k:np.zeros((1,d,2),complex) for k in JETS}
            for k in JETS:m[k][0,cols]=a[k]
            maps.append(m)
        L={k:np.zeros((1,3,d),complex) for k in JETS}
        for k in JETS:L[k][0][:,rows]=left[k]
        w=dict(value=np.array([.29]),x=np.array([.07]),y=np.array([-.05]),xy=np.array([.03]))
        G=out['gamma8_original']
        for placement in ('lorentz','plus_product'):
            got=original_m8_ordered_weak_jets(out,*maps,independent_left=L,coordinate_weights=w,placement=placement)
            with mp.workdps(64):
                def poly(a,x,y):return mm(a['value'])+x*mm(a['x'])+y*mm(a['y'])+x*y*mm(a['xy'])
                def literal(x,y):
                    b=literal_blocks(c,U,V,G,(target,source),x,y)
                    prefix='' if placement=='lorentz' else 'A_'
                    acted=sum((b[prefix+k]*poly(a,x,y) for k,a in zip(('body','radial','time'),local)),mp.zeros(16,2))
                    return evaluate(w,x,y)*evaluate(c['volume_density'],x,y)*(poly(left,x,y)*acted)
                ref=dict(value=literal(0,0),x=mp.diff(lambda x:literal(x,0),0),y=mp.diff(lambda y:literal(0,y),0),xy=mp.diff(literal,(0,0),(1,1)))
                for key in JETS:np.testing.assert_allclose(got[key],np.array(ref[key].tolist(),complex),atol=3e-13,rtol=3e-13)

    def test_density_weighted_full_green_identity(self):
        U,V=angular(0),angular(1);G8=original_m8_clifford(gamma());d=16*U.shape[1]*V.shape[1]
        G0=np.kron(G8[0],np.eye(d//16));Gc=np.kron(G8[1],np.eye(d//16))
        rng=np.random.default_rng(9031);a=rng.normal(size=d)+1j*rng.normal(size=d);b=rng.normal(size=d)+1j*rng.normal(size=d)
        def data(t,r):
            N,C,A,B=np.exp([.1+.07*r,.03+.04*t+.06*r,.08+.05*t-.03*r,-.02+.02*t+.09*r])
            z=.11+.03*r+.02*t;mu=N*C*A**3*B**3
            h0=(.04+3*.05+3*.02-z*(.06+3*(-.03)+3*.09)-.03)/(2*N)
            hr=(.07+3*(-.03)+3*.09)/(2*C)
            c={k:jets(np.array([v])) for k,v in zip(SCALARS,(N,C,A,B,z,h0,hr,mu))}
            p=(1+.13*t+.21*r+.03*t*r)*a;q=(1-.07*t+.17*r+.02*t*r)*b
            pt=(.13+.03*r)*a;pr=(.21+.03*t)*a
            qt=(-.07+.02*r)*b;qr=(.17+.02*t)*b
            return c,p,q,pt,pr,qt,qr
        nodes,weights=np.polynomial.legendre.leggauss(8);tt=.23+.11*nodes;rr=.39+.17*nodes
        total=0j
        for ti,t in enumerate(tt):
            for ri,r in enumerate(rr):
                c,p,q,pt,pr,qt,qr=data(t,r);op=original_m8_geometric_expression_jets(c,U,V,gamma5_base=gamma())
                def act(v,vr,vt):return apply_original_m8_expression_jets(op,jets(v[None,:,None]),jets(vr[None,:,None]),jets(vt[None,:,None]),placement='lorentz')['value'][0,:,0]
                total+=.11*.17*weights[ti]*weights[ri]*c['volume_density']['value'][0]*(np.vdot(q,G0@act(p,pr,pt))-np.vdot(act(q,qr,qt),G0@p))
        boundary=0j
        for ri,r in enumerate(rr):
            for t,sign in ((.12,-1),(.34,1)):
                c,p,q,*_=data(t,r);boundary+=.17*weights[ri]*sign*1j*c['volume_density']['value'][0]*np.vdot(q,p)/c['lapse']['value'][0]
        for ti,t in enumerate(tt):
            for r,sign in ((.22,-1),(.56,1)):
                c,p,q,*_=data(t,r);N,C,z=(c[k]['value'][0] for k in ('lapse','radial_coframe','coordinate_shift'))
                boundary+=.11*weights[ti]*sign*1j*c['volume_density']['value'][0]*np.vdot(q,(G0@Gc/C-z*np.eye(d)/N)@p)
        self.assertLess(abs(total-boundary)/max(1,abs(total),abs(boundary)),3e-12)


if __name__=='__main__':unittest.main()
