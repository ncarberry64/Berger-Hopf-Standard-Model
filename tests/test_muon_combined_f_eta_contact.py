"""Independent normalized-normal and MP64 source-derivative controls."""
import unittest
import mpmath as mp
import numpy as np
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_combined_f_eta_contact import combined_f_eta_contact

def inputs():
    def values(x):
        return [mp.exp(mp.mpf(".1")+.03*x),mp.exp(mp.mpf("-.2")-.02*x),.07+.01*x,
            mp.mpf(".71")+.04*x,.08+.017*x,.63-.013*x]
    with mp.workdps(64):
        names=("lapse","radial_coframe","coordinate_shift","eta_profile","eta_profile_coordinate_time","eta_profile_radial")
        c={k:np.array([complex(values(0)[j])])for j,k in enumerate(names)}
        c.update({k+"_first":np.array([[complex(mp.diff(lambda x:values(x)[j],0))]])for j,k in enumerate(names)})
    return c,values

class CombinedEtaTests(unittest.TestCase):
    def test_exact_material_wall_overlap(self):
        from bhsm.interface.muon_holomorphic_d5_trace_action import d5_wall_material_eta
        from bhsm.interface.muon_parent_retarded_hypercharge import WALL
        c,_=inputs();U=.21
        c["eta_profile_coordinate_time"]=c["coordinate_shift"]*c["eta_profile_radial"]-c["lapse"]*U*c["eta_profile_radial"]/c["radial_coframe"]
        c.update(material_wall_velocity=np.array([U]),radial_points=np.array([WALL]),
            eta_radial_contact=-c["eta_profile_radial"]/c["radial_coframe"]/np.tan(c["eta_profile"]))
        G=full_d5_localized_lepton_trace()["gamma5D_particle"]
        for eps in(-1,1):
            a=combined_f_eta_contact(c,gamma=G,carrier_count=16,angular_count=1,sheet_orientation=eps)
            b=d5_wall_material_eta(c,gamma=G,carrier_count=16,angular_count=1,sheet_orientation=eps)
            np.testing.assert_allclose(a["combined_f_eta_contact"][-1],b["actual_wall_material_eta_contact"],atol=3e-15,rtol=3e-15)
    def test_literal_regular_normal_product_and_all_full_rows(self):
        c,_=inputs();f=full_d5_localized_lepton_trace()
        for branch in("particle","conjugate"):
            G=f["gamma5D_"+branch]
            for eps in(-1,1):
                a=combined_f_eta_contact(c,gamma=G,carrier_count=16,angular_count=2,sheet_orientation=eps)
                f0,f4=a["f_timelike_derivative"][0],a["f_radial_derivative"][0]
                root=np.sqrt(f4*f4-f0*f0);n0,n4=-f0/root,f4/root
                mass=-(n0*f0+n4*f4)/np.tan(c["eta_profile"][0])
                literal=1j*mass*np.kron(-n0*G[0]+eps*n4*G[4],np.eye(32))
                np.testing.assert_allclose(a["combined_f_eta_contact"][0],literal,atol=3e-15,rtol=3e-15)
                self.assertEqual(literal.shape,(128,128))
    def test_MP64_literal_first_source_and_null_crossing(self):
        c,values=inputs();G=full_d5_localized_lepton_trace()["gamma5D_particle"]
        a=combined_f_eta_contact(c,gamma=G,carrier_count=1,angular_count=1,sheet_orientation=-1)
        with mp.workdps(64):
            g0,g4=mp.matrix(G[0].tolist()),mp.matrix(G[4].tolist())
            def literal(x):
                N,C,z,f,ft,fr=values(x);u=(ft-z*fr)/N;v=fr/C
                root=mp.sqrt(v*v-u*u);n0,n4=-u/root,v/root;m=-(n0*u+n4*v)/mp.tan(f)
                return 1j*m*(-n0*g0-n4*g4)
            expected=np.array(mp.diff(literal,0).tolist(),complex)
        np.testing.assert_allclose(a["combined_f_eta_contact_first"][0,0],expected,atol=3e-15,rtol=3e-15)
        # At Q=0 no unit normal exists; the COMBINED coefficient is finite.
        c["lapse"][:]=1;c["radial_coframe"][:]=1;c["coordinate_shift"][:]=0
        c["eta_profile_coordinate_time"][:]=c["eta_profile_radial"]
        z=combined_f_eta_contact(c,gamma=G,carrier_count=1,angular_count=1,sheet_orientation=1)
        np.testing.assert_array_equal(z["f_gradient_spacelike_square"],0)
        self.assertTrue(np.isfinite(z["combined_f_eta_contact"]).all())
        self.assertGreater(np.linalg.norm(z["combined_f_eta_contact"]),.1)
        c["eta_profile_coordinate_time"]*=2
        y=combined_f_eta_contact(c,gamma=G,carrier_count=1,angular_count=1,sheet_orientation=1)
        self.assertLess(y["f_gradient_spacelike_square"][0].real,0)
        self.assertTrue(np.isfinite(y["combined_f_eta_contact"]).all())
    def test_no_polar_or_missing_source_assignment(self):
        c,_=inputs();G=full_d5_localized_lepton_trace()["gamma5D_particle"]
        c["eta_profile"][:]=0
        with self.assertRaisesRegex(ValueError,"polar"):
            combined_f_eta_contact(c,gamma=G,carrier_count=1,angular_count=1,sheet_orientation=1)

if __name__=="__main__":unittest.main()
