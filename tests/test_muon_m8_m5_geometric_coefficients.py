"""MP64 integrable coframe germs; controls are not physical BHSM solutions."""
from __future__ import annotations

import unittest

import mpmath as mp
import numpy as np

from bhsm.interface.muon_m8_m5_geometric_coefficients import (
    FIELD_NAMES,KEYS,m8_m5_geometric_coefficient_jets,
)


T0,CHI0=mp.mpf(".17"),mp.mpf(".31")


def profiles(t,c,x,y):
    # Actual smooth functions of coordinate time and chi, so the supplied
    # log-derivatives and their source contacts form one integrable germ.
    logs=(
        mp.mpc(".13",".01")+.04*t+.07*c+.02*t*c
          +x*(.03+.02*t-.01*c)+y*(.02*c+.01j*t)+x*y*(.013+.007*t*c),
        mp.mpc(".05","-.02")+.03*t-.04*c+.01*t*c
          +x*(.01j+.02*c)+y*(.04-.01*t)+x*y*(.009+.005*c),
        mp.mpc(".21",".03")+.08*t+.12*c+.03*t*c
          +x*(.07+.03*t+.01j*c)+y*(-.04+.02*c)+x*y*(.021+.006*t*c),
        mp.mpc("-.14","-.01")-.03*t+.09*c-.02*t*c
          +x*(-.02+.01*c)+y*(.05+.01j*t)+x*y*(-.015+.004*c),
    )
    beta=.11+.04*t-.02*c+.03*t*c+x*(.02+.01*t)+y*(.03j-.01*c)+x*y*(.012+.003*t*c)
    return tuple(mp.exp(a) for a in logs)+(beta,)


def fields_at(x,y):
    t,c=T0,CHI0
    N,C,A,B,beta=profiles(t,c,x,y)
    def dlog(index,axis):
        if axis==0:return mp.diff(lambda tt:mp.log(profiles(tt,c,x,y)[index]),t)
        return mp.diff(lambda cc:mp.log(profiles(t,cc,x,y)[index]),c)
    return dict(N=N,C=C,A=A,B=B,beta=beta,np=dlog(0,1),cp=dlog(1,1),
        ap=dlog(2,1),bp=dlog(3,1),la=dlog(2,0),lb=dlog(3,0),lc=dlog(1,0),
        betap=mp.diff(lambda cc:profiles(t,cc,x,y)[4],c))


def _source_jets(fun):
    zero=mp.mpf(0)
    vals=dict(value=fun(zero,zero),x=mp.diff(lambda x:fun(x,zero),zero),
        y=mp.diff(lambda y:fun(zero,y),zero),
        xy=mp.diff(lambda x:mp.diff(lambda y:fun(x,y),zero),zero))
    return {key:complex(v) if not isinstance(v,mp.matrix) else np.array(v.tolist(),complex)
            for key,v in vals.items()}


def control_inputs():
    with mp.workdps(64):
        inputs={name:_source_jets(lambda x,y,name=name:fields_at(x,y)[name])
                for name in FIELD_NAMES}
        f=fields_at(0,0);L=mp.sqrt(f["A"]**2+f["B"]**2)
        radius,logvalue=complex(L),complex(mp.log(L))
    return inputs,radius,logvalue


LITERAL_KEYS=("LF","r","lambda","h0_M8","hchi_M8","h0_M5","hchi_M5",
    "fiber_norm_Lm32","E0_lambda","Echi_lambda","mu8","mu5","fiber_volume",
    "vertical_DF_coefficient","original_u_spin_triple_coefficient","original_v_spin_triple_coefficient",
    "original_time_principal_coefficient","original_chi_Gamma0_principal_coefficient",
    "F0scalar","Fchiscalar","Fabscalar","KK0scalar","KKchiscalar","KKabscalar",
    "direct_normalized_mean_cancel_0","direct_normalized_mean_cancel_chi")


def literal_coefficients(x,y):
    t,c=T0,CHI0
    def geom(tt,cc):
        N,C,A,B,beta=profiles(tt,cc,x,y)
        L=mp.sqrt(A*A+B*B);r=A*B/L
        return N,C,A,B,beta,L,r,A*A/(L*L),L**mp.mpf("-1.5")
    N,C,A,B,beta,L,r,lam,norm=geom(t,c)
    def dt(fun):return mp.diff(lambda tt:fun(*geom(tt,c)),t)
    def dc(fun):return mp.diff(lambda cc:fun(*geom(t,cc)),c)
    # Independent divergence/coframe-volume formulas rather than the
    # implementation's expanded log-derivative formulas.
    spatial8=C*A**3*B**3
    spatial5=C*r**3
    h08=(dt(lambda N,C,A,B,b,L,r,lam,u:C*A**3*B**3)
        -dc(lambda N,C,A,B,b,L,r,lam,u:b*C*A**3*B**3))/(2*N*spatial8)
    hc8=dc(lambda N,C,A,B,b,L,r,lam,u:N*A**3*B**3)/(2*N*C*A**3*B**3)
    h05=(dt(lambda N,C,A,B,b,L,r,lam,u:C*r**3)
        -dc(lambda N,C,A,B,b,L,r,lam,u:b*C*r**3))/(2*N*spatial5)
    hc5=dc(lambda N,C,A,B,b,L,r,lam,u:N*r**3)/(2*N*C*r**3)
    E0lam=(dt(lambda N,C,A,B,b,L,r,lam,u:lam)-beta*dc(lambda N,C,A,B,b,L,r,lam,u:lam))/N
    Echilam=dc(lambda N,C,A,B,b,L,r,lam,u:lam)/C
    F0,Fchi,Fab=E0lam/r,Echilam/r,-2*lam*(1-lam)/(r*r)
    norm0=(dt(lambda N,C,A,B,b,L,r,lam,u:u)-beta*dc(lambda N,C,A,B,b,L,r,lam,u:u))/(N*norm)
    normchi=dc(lambda N,C,A,B,b,L,r,lam,u:u)/(C*norm)
    vals=(L,r,lam,h08,hc8,h05,hc5,norm,E0lam,Echilam,N*C*A**3*B**3,
        N*C*r**3,2*mp.pi**2*L**3,1/L,3j/(2*A),3j/(2*B),1/N,-beta/N,
        F0,Fchi,Fab,-1j*L*F0/8,-1j*L*Fchi/8,-1j*L*Fab/8,
        h08-h05+norm0,hc8-hc5+normchi)
    return mp.matrix(vals)


def run_independent_controls():
    f,L,logL=control_inputs()
    out=m8_m5_geometric_coefficient_jets(f,fiber_radius_value=L,fiber_log_value=logL)
    with mp.workdps(64):expected=_source_jets(literal_coefficients)
    errors={key:{} for key in KEYS}
    for key in KEYS:
        actual=[]
        for name in LITERAL_KEYS:
            if name=="F0scalar":v=out["F_0a"][key][0,0]
            elif name=="Fchiscalar":v=out["F_chia"][key][0,0]
            elif name=="Fabscalar":v=out["F_ab"][key][0,1,2]
            elif name=="KK0scalar":v=out["KK_full_ordered"][key][0,0,2]
            elif name=="KKchiscalar":v=out["KK_full_ordered"][key][0,1,2]
            elif name=="KKabscalar":v=out["KK_full_ordered"][key][0,3,4]
            elif name=="direct_normalized_mean_cancel_0":v=out["mean_contact_cancellation_0"][key]
            elif name=="direct_normalized_mean_cancel_chi":v=out["mean_contact_cancellation_chi"][key]
            else:v=out[name][key]
            actual.append(v)
        for i,name in enumerate(LITERAL_KEYS):
            errors[key][name]=float(abs(actual[i]-expected[key][i,0]))
    identities={name:{key:float(abs(out[name][key])) for key in KEYS}
        for name in ("coarea_density_rows","analytic_fiber_normalization_rows",
                     "mean_contact_cancellation_0","mean_contact_cancellation_chi")}
    return dict(MP64_literal_coefficient_errors=errors,geometric_identity_rows=identities,
        nonzero_curvature_norm=float(np.linalg.norm(out["F_full"]["value"])),
        nonzero_mixed_KK_norm=float(np.linalg.norm(out["KK_full_ordered"]["xy"])),
        vertical_DF_coefficient_abs=float(abs(out["vertical_DF_coefficient"]["value"])),
        physical_control_state=False,source_coefficients_conjugated=False,
        Clifford_or_SM_carrier_selected=False)


class M8M5CoefficientTests(unittest.TestCase):
    def test_round_S7_full_factor_two_curvature(self):
        # Arbitrary geometric control scale, with genuine moving radius
        # and chi source germs.  This is not a physical scale assignment.
        def round_fields(x,y):
            R=mp.mpf("1.7")*mp.exp(.03*x+.04*y+.01*x*y)
            chi=mp.mpf(".37")+.02*x-.01*y+.003*x*y
            return dict(N=1,C=R,A=R*mp.cos(chi),B=R*mp.sin(chi),beta=0,
                np=0,cp=0,ap=-mp.tan(chi),bp=mp.cot(chi),betap=0,la=0,lb=0,lc=0)
        with mp.workdps(64):
            f={name:_source_jets(lambda x,y,name=name:round_fields(x,y)[name])
                for name in FIELD_NAMES}
            R=complex(round_fields(0,0)["C"])
            expected=_source_jets(lambda x,y:-2/round_fields(x,y)["C"]**2)
        out=m8_m5_geometric_coefficient_jets(f,fiber_radius_value=R,fiber_log_value=np.log(R))
        for key in KEYS:
            np.testing.assert_allclose(out["F_chia"][key],expected[key]*np.eye(3),atol=2e-15,rtol=2e-14)
            self.assertAlmostEqual(abs(out["F_ab"][key][0,1,2]-expected[key]),0,delta=2e-15)
            np.testing.assert_allclose(out["F_0a"][key],0,atol=1e-15)
            self.assertAlmostEqual(abs(out["mean_contact_cancellation_0"][key]),0,delta=2e-15)
            self.assertAlmostEqual(abs(out["mean_contact_cancellation_chi"][key]),0,delta=2e-15)
            self.assertAlmostEqual(abs(out["LF"][key]-f["C"][key]),0,delta=2e-15)

    def test_independent_integrable_germ_MP64(self):
        r=run_independent_controls()
        self.assertLess(max(v for q in r["MP64_literal_coefficient_errors"].values() for v in q.values()),2e-13)
        self.assertLess(max(v for q in r["geometric_identity_rows"].values() for v in q.values()),2e-13)
        self.assertGreater(r["nonzero_curvature_norm"],.1)
        self.assertGreater(r["nonzero_mixed_KK_norm"],.001)
        self.assertGreater(r["vertical_DF_coefficient_abs"],.1)

    def test_all_spatial_curvature_and_ordered_contact_components(self):
        f,L,logL=control_inputs()
        out=m8_m5_geometric_coefficient_jets(f,fiber_radius_value=L,fiber_log_value=logL)
        for key in KEYS:
            F=out["F_full"][key]
            np.testing.assert_array_equal(F+F.swapaxes(1,2),0)
            np.testing.assert_array_equal(F[:,0,1],0)
            self.assertEqual(out["original_seven_spatial_principal_coefficients"][key].shape,(7,))
        self.assertFalse(out["vertical_DF_set_to_zero"])
        self.assertFalse(out["Clifford_or_SM_carrier_selected"])

    def test_explicit_chart_branch_and_source_guards(self):
        f,L,logL=control_inputs()
        with self.assertRaisesRegex(ValueError,"source-chart square root"):
            m8_m5_geometric_coefficient_jets(f,fiber_radius_value=L*1.1,fiber_log_value=logL)
        with self.assertRaisesRegex(ValueError,"logLF"):
            m8_m5_geometric_coefficient_jets(f,fiber_radius_value=-L,fiber_log_value=logL)
        opposite=m8_m5_geometric_coefficient_jets(f,fiber_radius_value=-L,fiber_log_value=logL+1j*np.pi)
        self.assertEqual(opposite["LF"]["value"],-L)
        bad={name:dict(j) for name,j in f.items()};del bad["A"]["xy"]
        with self.assertRaisesRegex(ValueError,"explicit value/x/y/xy"):
            m8_m5_geometric_coefficient_jets(bad,fiber_radius_value=L,fiber_log_value=logL)


if __name__=="__main__":unittest.main()
