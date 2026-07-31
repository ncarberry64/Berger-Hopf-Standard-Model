"""Canonical term registry and maximal consistent action complex."""

from __future__ import annotations

from .common import MISSING_OBJECT, VERDICT, envelope


S8 = (
    "S8=int_M8 sqrt(-G)[kappa1 R8/2-kappa0/2"
    "-Zchi(1+g sigma^2)|dchi|^2/2-Zsigma|dsigma|^2/2"
    "-A0 sigma^2/2-G0 sigma^4/4]"
)
S5_REL = (
    "S5|4=sum_{eps=+,-}{int_M5_eps sqrt(-g_eps)"
    "[kappa1 R5/2-kappa0/2-Z5|dsigma|^2/2-U5(sigma)]"
    "+eps*kappa1 int_B1 sqrt(-gamma_eps) K_eps}"
    "+int_B1 sqrt(-h)[C_partial R4+L_B1,matter]"
    "+sum_eps int_B1 Lambda_eps^{ab}(h_ab-gamma_eps,ab)"
)
S4_EFT = (
    "S4eff=int_M4 sqrt(-h)[-sum_i Tr(F_i^2)/(4 g_i^2)"
    "+i barPsi gamma^mu D_mu Psi"
    "-barQ_L Y_d H d_R-barQ_L Y_u Htilde u_R-barL_L Y_e H e_R+h.c."
    "+|D H|^2-V(H;lambda5)+L_neu,eff]+DeltaS_BHSM"
)
ACTION_COMPLEX = (
    "S_BHSM^max := [ S8 --R_8to5--> S5|4 "
    "--R_5to4--> S4eff ]; R_8to5 and R_5to4 are not sourced"
)
CONDITIONAL_CC_INTERFACE = (
    "L_cc^CG=-(g2/sqrt(2))[W_mu^+ bar(u_L) gamma^mu U_CG d_L"
    "+W_mu^- bar(d_L) gamma^mu U_CG^dagger u_L]"
)


def conditional_interface_rows() -> list[dict]:
    """Constructions that are admissible interfaces but not derived S8 terms."""

    return [
        {
            "term_id": "T4_C3_G2_charged_interface_candidate",
            "level": "S_compatibility,current on M4",
            "expression": CONDITIONAL_CC_INTERFACE,
            "operation": "replace I3 in the existing SU2 raising/lowering generators",
            "coefficient": "existing g2/sqrt(2)",
            "new_continuous_coefficient": False,
            "Hermitian": True,
            "SU2_algebra_closed_when_U_CG_unitary": True,
            "neutral_current_family_central": True,
            "abstract_kernel": "U_CG=Pol(K_CG)",
            "K_CG_derived_from_S8": False,
            "classification": "CONDITIONAL_INTERFACE_CONSTRUCTION_NOT_ACTIVE_PARENT_TERM",
        }
    ]


def term_rows() -> list[dict]:
    return [
        {"term_id": "T8_EH", "level": "S8", "expression": "int sqrt(-G) kappa1 R8/2", "fields": ["G_AB"], "coefficient": "kappa1", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "E8_AB=0"},
        {"term_id": "T8_vacuum", "level": "S8", "expression": "-int sqrt(-G) kappa0/2", "fields": ["G_AB"], "coefficient": "kappa0", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "vacuum stress"},
        {"term_id": "T8_carrier", "level": "S8", "expression": "-int sqrt(-G) Zchi(1+g sigma^2)|dchi|^2/2", "fields": ["G_AB", "chi", "sigma"], "coefficient": "Zchi,g", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "chi and sigma equations"},
        {"term_id": "T8_scalar", "level": "S8", "expression": "-int sqrt(-G)[Zsigma|dsigma|^2/2+A0 sigma^2/2+G0 sigma^4/4]", "fields": ["G_AB", "sigma"], "coefficient": "Zsigma,A0,G0", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "bulk scalar equation"},
        {"term_id": "T5_caps", "level": "S5|4", "expression": "sum_eps int_M5_eps sqrt(-g_eps)[kappa1 R5/2-kappa0/2-Z5|dsigma|^2/2-U5]", "fields": ["g_eps", "sigma"], "coefficient": "kappa1,kappa0,Z5,A5,G5", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "cap Einstein/scalar equations"},
        {"term_id": "T5_GHY", "level": "S5|4", "expression": "sum_eps eps kappa1 int_B1 sqrt(-gamma_eps) K_eps", "fields": ["g_eps"], "coefficient": "kappa1", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "normal-derivative cancellation and canonical momentum"},
        {"term_id": "T4_B1", "level": "S5|4", "expression": "int_B1 sqrt(-h)[C_partial R4+L_B1,matter]", "fields": ["h_ab", "A_i", "Psi", "sigma"], "coefficient": "C_partial plus typed EFT inputs", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "intrinsic B1 equations"},
        {"term_id": "T4_matcher", "level": "S5|4", "expression": "sum_eps int_B1 Lambda_eps^{ab}(h_ab-gamma_eps,ab)", "fields": ["Lambda_eps", "h_ab", "g_eps"], "coefficient": "redundant multiplier normalization", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "exact metric matching and reaction"},
        {"term_id": "T4_gauge", "level": "S4eff", "expression": "-int sqrt(-h) sum_i Tr(F_i^2)/(4 g_i^2)", "fields": ["A_i", "h_ab"], "coefficient": "g1,g2,g3", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "Yang-Mills equations and stress"},
        {"term_id": "T4_fermion", "level": "S4eff", "expression": "int sqrt(-h) i barPsi gamma^mu D_mu Psi", "fields": ["Psi", "A_i", "h_ab"], "coefficient": "canonical", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "Dirac equations and currents"},
        {"term_id": "T4_Yukawa", "level": "S4eff", "expression": "-int sqrt(-h)[barQ_L Y_d H d_R+barQ_L Y_u Htilde u_R+barL_L Y_e H e_R+h.c.]", "fields": ["Psi", "H"], "coefficient": "Y_u,Y_d,Y_e", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "fermion and scalar sources"},
        {"term_id": "T4_scalar", "level": "S4eff", "expression": "int sqrt(-h)[|D H|^2-V(H;lambda5)]", "fields": ["H", "A_i"], "coefficient": "lambda5 and quadratic input", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "scalar equation and reduced quartic"},
        {"term_id": "T4_neutral_aux", "level": "DeltaS4", "expression": "int sqrt(-h)[Z_neu|D N|^2/2-A_neu N^2/2+g_neu N.R]", "fields": ["N_neu", "Psi", "sigma"], "coefficient": "Z_neu,A_neu,g_neu", "real": True, "gauge_invariant": True, "mass_dimension_closed": True, "variation_used": "conditional neutral response equation"},
    ]


def latex() -> str:
    return r"""\[
\mathfrak S_{\rm BHSM}^{\max} =
\left[
S_{8}
\xrightarrow{\;\mathcal R_{8\to5}\;}
S_{5|4}^{\rm caps+GHY+B1+match}
\xrightarrow{\;\mathcal R_{5\to4}\;}
S_{4}^{\rm EFT}
\right].
\]
\[
S_8=\int_{M_8}\!\sqrt{-G}\left[
\frac{\kappa_1}{2}R_8-\frac{\kappa_0}{2}
-\frac{Z_\chi}{2}(1+g\sigma^2)|d\chi|^2
-\frac{Z_\sigma}{2}|d\sigma|^2
-\frac{A_0}{2}\sigma^2-\frac{G_0}{4}\sigma^4\right].
\]
\[
\begin{aligned}
S_{5|4}={}&\sum_{\epsilon=\pm}\int_{M_{5,\epsilon}}\sqrt{-g_\epsilon}
\left[\frac{\kappa_1}{2}R_5-\frac{\kappa_0}{2}
-\frac{Z_5}{2}|d\sigma|^2-U_5(\sigma)\right]\\
&+\sum_{\epsilon=\pm}\epsilon\kappa_1\int_{B_1}\sqrt{-\gamma_\epsilon}K_\epsilon
+\int_{B_1}\sqrt{-h}\,[C_\partial R_4+\mathcal L_{B_1,\rm matter}]\\
&+\sum_{\epsilon=\pm}\int_{B_1}\Lambda_\epsilon^{ab}
(h_{ab}-\gamma_{\epsilon ab}).
\end{aligned}
\]
\[
\begin{aligned}
S_4^{\rm EFT}=\int_{M_4}\sqrt{-h}\bigg[
&-\sum_i\frac{1}{4g_i^2}{\rm Tr}(F_i^2)
+i\bar\Psi\gamma^\mu D_\mu\Psi+|D H|^2-V(H;\lambda_5)\\
&-\bar Q_LY_dHd_R-\bar Q_LY_u\widetilde H u_R
-\bar L_LY_eHe_R+\mathrm{h.c.}
+\mathcal L_{\rm neu,eff}\bigg]+\Delta S_{\rm BHSM}.
\end{aligned}
\]
The two reduction arrows are required data, not identities established by
the repository.  Therefore the displayed object is the maximal consistent
action complex, not a closed unified parent action.
"""


def payload() -> dict:
    return envelope(
        "BHSM_unified_master_action_v7_0",
        action_complex=ACTION_COMPLEX,
        levels={"S8": S8, "S5_relative": S5_REL, "S4_effective": S4_EFT},
        terms=term_rows(),
        quantum_EFT_classification={
            "S8": "classical higher-dimensional provisional EFT",
            "S5_relative": "classical constrained-gravity relative action",
            "S4_effective": "classical four-dimensional EFT",
            "quantum_fundamental_claim": False,
            "cutoff_required_for_higher_dimension_operators": True,
        },
        maps={"R_8to5": None, "R_5to4": None},
        master_action_closed=False,
        exact_missing_object=MISSING_OBJECT,
        verdict=VERDICT,
    )
