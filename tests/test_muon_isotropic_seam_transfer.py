"""Independent literal MP64 Cayley controls of the conditional local graph."""
from __future__ import annotations

import unittest

import mpmath as mp
import numpy as np

from bhsm.interface.muon_isotropic_seam_transfer import KEYS, isotropic_seam_transfer_jets


POWERS = {"value": (0,0), "x": (1,0), "y": (0,1), "xy": (1,1)}


def _polynomial_product(a, b):
    # Exact ordered polynomial convolution, independent of helper jet code.
    out = {}
    for (i,j), av in a.items():
        for (k,l), bv in b.items():
            p = (i+k,j+l)
            v = av@bv
            out[p] = out[p]+v if p in out else v.copy()
    return out


def control_family():
    """Six full rows, rank-two wall trace, two untouched complementary rows.

    J=L J0 R, C=L C0 E, B=F B0 R guarantee B J^-1 C=0 for
    the entire literal polynomial family, with independent analytic L/R.
    Only the value point has the declared Hermitian/Riesz specialization;
    the complex source germs are not claimed to be a physical real family.
    """
    rng = np.random.default_rng(1445156916)
    def factor(n):
        return {(0,0): np.eye(n, dtype=complex), **{
            p: .06*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))
            for p in ((1,0),(0,1),(1,1))}}
    L,R,E,F = factor(6),factor(6),factor(2),factor(2)
    J0 = np.block([[np.zeros((3,3)),np.eye(3)],[-np.eye(3),np.zeros((3,3))]])
    B0 = np.zeros((2,6),complex);B0[:2,:2]=np.eye(2)
    C0 = B0.T.copy()
    T = factor(2)
    T[(0,0)] = np.array([[.37,.16+.11j],[.16-.11j,-.24]])
    J = _polynomial_product(_polynomial_product(L,{(0,0):J0}),R)
    C = _polynomial_product(_polynomial_product(L,{(0,0):C0}),E)
    B = _polynomial_product(_polynomial_product(F,{(0,0):B0}),R)
    jets = tuple({key:p[power] for key,power in POWERS.items()} for p in (J,C,T,B))
    return jets, (L,R,E,F,T), J0,B0,C0


def _mp_matrix(a):
    return mp.matrix([[mp.mpc(mp.mpf(float(v.real)),mp.mpf(float(v.imag)))
                       for v in row] for row in np.asarray(a,complex)])


def literal_mp_family(factors, J0, B0, C0):
    matrices = [{power:_mp_matrix(v) for power,v in p.items()} for p in factors]
    j0,b0,c0 = (_mp_matrix(v) for v in (J0,B0,C0))
    def polynomial(p,x,y):
        out = mp.zeros(p[(0,0)].rows,p[(0,0)].cols)
        for (i,j),v in p.items():
            out += x**i*y**j*v
        return out
    def data(x,y):
        L,R,E,F,T = [polynomial(p,x,y) for p in matrices]
        return L*j0*R, L*c0*E, T, F*b0*R, R
    def cayley(x,y):
        J,C,T,B,_ = data(x,y)
        V=C*T*B
        # Independent literal symmetric distributional prescription.  Its
        # equality to I+N follows from isotropy, not the implementation.
        return (J-V/2)**-1*(J+V/2)
    return data,cayley


def mp_jets(fun):
    zero=mp.mpf(0)
    values = dict(value=fun(zero,zero),
        x=mp.diff(lambda x:fun(x,zero),zero),
        y=mp.diff(lambda y:fun(zero,y),zero),
        xy=mp.diff(lambda x:mp.diff(lambda y:fun(x,y),zero),zero))
    return {key:np.array(value.tolist(),complex) for key,value in values.items()}


def run_independent_controls():
    inputs,factors,J0,B0,C0=control_family()
    result=isotropic_seam_transfer_jets(*inputs)
    with mp.workdps(64):
        data,cayley=literal_mp_family(factors,J0,B0,C0)
        expected=mp_jets(cayley)
        inverse=mp_jets(lambda x,y:cayley(x,y)**-1)
        Z0=mp.zeros(6,2);Z0[2,0]=1;Z0[5,1]=1
        # These moving common-fibre coordinates lie in ker B exactly and
        # represent the two complementary canonical directions.
        complement=mp_jets(lambda x,y:(cayley(x,y)-mp.eye(6))*(data(x,y)[4]**-1)*Z0)
    errors={key:float(np.max(abs(result["transfer"][key]-expected[key]))) for key in KEYS}
    inverse_errors={key:float(np.max(abs(result["inverse_transfer"][key]-inverse[key]))) for key in KEYS}
    residual_keys=("isotropy","original_jump_rows","trace_continuity_rows",
        "nilpotence_rows","inverse_graph_rows","reverse_inverse_graph_rows",
        "independent_bilinear_green_rows")
    residuals={name:{key:float(np.max(abs(result[name][key]))) for key in KEYS}
               for name in residual_keys}
    J,C,T,B=inputs
    physical_value_only=result["transfer"]["value"].conj().T@J["value"]@result["transfer"]["value"]-J["value"]
    return dict(independent_literal_MP64_Cayley_errors=errors,
        independent_literal_MP64_inverse_errors=inverse_errors,
        original_residual_jets=residuals,
        independent_literal_moving_complement_errors={key:float(np.max(abs(complement[key]))) for key in KEYS},
        nonzero_mixed_transfer_norm=float(np.linalg.norm(result["transfer"]["xy"])),
        noncommuting_surface_contacts_norm=float(np.linalg.norm(T["x"]@T["y"]-T["y"]@T["x"])),
        independent_left_source_not_right_dagger_norm=float(np.linalg.norm(C["x"]-B["x"].conj().T)),
        conditional_value_only_Hermitian_Green_rows=float(np.max(abs(physical_value_only))),
        full_fibre_count=6,wall_trace_count=2,untouched_canonical_complement_count=2,
        physical_control_state=False,physical_real_source_family_claimed=False,
        physical_domain_adoption=None,source_conjugation_used=False)


class IsotropicSeamTransferTests(unittest.TestCase):
    def test_independent_literal_moving_Cayley_MP64(self):
        r=run_independent_controls()
        self.assertLess(max(r["independent_literal_MP64_Cayley_errors"].values()),2e-13)
        self.assertLess(max(r["independent_literal_MP64_inverse_errors"].values()),2e-13)
        self.assertLess(max(r["independent_literal_moving_complement_errors"].values()),1e-50)
        self.assertLess(max(v for row in r["original_residual_jets"].values() for v in row.values()),2e-13)
        self.assertLess(r["conditional_value_only_Hermitian_Green_rows"],1e-13)
        self.assertGreater(r["nonzero_mixed_transfer_norm"],.01)
        self.assertGreater(r["noncommuting_surface_contacts_norm"],.001)
        self.assertGreater(r["independent_left_source_not_right_dagger_norm"],.1)

    def test_nonisotropic_input_is_reported_without_physical_admission(self):
        jets,*_=control_family()
        J,C,T,B=({k:v.copy() for k,v in j.items()} for j in jets)
        C["value"][3,0]+=.2
        result=isotropic_seam_transfer_jets(J,C,T,B)
        self.assertGreater(np.max(abs(result["isotropy"]["value"])),.1)
        self.assertGreater(np.max(abs(result["nilpotence_rows"]["value"])),.001)
        self.assertLess(np.max(abs(result["original_jump_rows"]["value"])),1e-13)
        self.assertIsNone(result["physical_domain_adoption"])
        self.assertEqual(result["full_fibre_rows_deleted"],0)

    def test_independent_C_source_is_not_conjugated(self):
        jets,*_=control_family()
        result=isotropic_seam_transfer_jets(*jets)
        J,C,T,B=jets
        wrong={key:B[key].conj().T for key in KEYS}
        conjugated=isotropic_seam_transfer_jets(J,wrong,T,B)
        self.assertGreater(np.linalg.norm(result["transfer"]["x"]-conjugated["transfer"]["x"]),.01)
        self.assertFalse(result["source_left_coefficients_conjugated"])

    def test_explicit_jet_and_singular_J_guards(self):
        jets,*_=control_family()
        broken={key:value for key,value in jets[1].items() if key!="xy"}
        with self.assertRaisesRegex(ValueError,"explicit value/x/y/xy"):
            isotropic_seam_transfer_jets(jets[0],broken,jets[2],jets[3])
        singular={key:np.zeros_like(value) for key,value in jets[0].items()}
        with self.assertRaises((np.linalg.LinAlgError,Warning)):
            isotropic_seam_transfer_jets(singular,*jets[1:])


if __name__=="__main__":
    unittest.main()
