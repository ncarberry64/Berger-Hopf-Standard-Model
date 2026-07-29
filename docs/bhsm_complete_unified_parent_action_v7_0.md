# BHSM complete unified-parent-action attempt v7.0

## Decisive result

The complete repository-wide attempt does not justify a closed unified
parent action. It produces the maximal consistent action complex

\[
\mathfrak S_{\rm BHSM}^{\max}=
\left[
S_8\xrightarrow{\mathcal R_{8\to5}}
S_{5|4}^{\rm caps+GHY+B1+match}
\xrightarrow{\mathcal R_{5\to4}}
S_4^{\rm EFT}
\right],
\]

but neither reduction arrow is supplied by the repository. The exact result
is

`BHSM_UNIFIED_PARENT_ACTION_BLOCKED_BY_MISSING_COVARIANT_BULK_BOUNDARY_REDUCTION_FUNCTOR_SOURCE`.

This is not an assertion that no such map can exist. It is the stronger
claim-safe statement proved by the present evidence: all independent
sectors have been audited, all levelwise coefficients can be finitely
typed, and the single remaining common parent-action object is the
covariant reduction functor.

## The three action levels

The immutable provisional eight-dimensional action is

\[
S_8=\int_{M_8}\sqrt{-G}\left[
\frac{\kappa_1}{2}R_8-\frac{\kappa_0}{2}
-\frac{Z_\chi}{2}(1+g\sigma^2)|d\chi|^2
-\frac{Z_\sigma}{2}|d\sigma|^2
-\frac{A_0}{2}\sigma^2-\frac{G_0}{4}\sigma^4
\right],
\]

on \(M_8=\mathbb R_t\times S^7\). It is a finite classical
higher-dimensional EFT family, not an action selected by an established
BHSM principle.

The constrained-gravity chain uses

\[
\begin{aligned}
S_{5|4}={}&
\sum_{\epsilon=\pm}\int_{M_{5,\epsilon}}\sqrt{-g_\epsilon}
\left[\frac{\kappa_1}{2}R_5-\frac{\kappa_0}{2}
-\frac{Z_5}{2}|d\sigma|^2-U_5(\sigma)\right]\\
&+\sum_{\epsilon=\pm}\epsilon\kappa_1
\int_{B_1}\sqrt{-\gamma_\epsilon}\,K_\epsilon\\
&+\int_{B_1}\sqrt{-h}\,
\left[C_\partial R_4+\mathcal L_{B_1,\rm matter}\right]\\
&+\sum_{\epsilon=\pm}\int_{B_1}
\Lambda_\epsilon^{ab}(h_{ab}-\gamma_{\epsilon ab}).
\end{aligned}
\]

The outward-normal signs give one coefficient-locked GHY completion per
cap. The intrinsic \(B_1\) term is not a second copy of the cap
Einstein-Hilbert term, and the matcher is an auxiliary constraint rather
than propagating dynamics. This action has a valid strict fixed-\(h\) D0
restriction and recovers the v6.30 KKT operator and reduced scalar
potential.

The strongest honest four-dimensional action is a finite-input EFT,

\[
\begin{aligned}
S_4^{\rm EFT}=\int_{M_4}\sqrt{-h}\bigg[
&-\sum_i\frac{1}{4g_i^2}{\rm Tr}(F_i^2)
+i\bar\Psi\gamma^\mu D_\mu\Psi
+|D H|^2-V(H;\lambda_5)\\
&-\bar Q_LY_dHd_R-\bar Q_LY_u\widetilde H u_R
-\bar L_LY_eHe_R+\mathrm{h.c.}
+\mathcal L_{\rm neu,eff}
\bigg]+\Delta S_{\rm BHSM}.
\end{aligned}
\]

The gauge couplings, Yukawa matrices, selected sector/mode projectors, and
neutral-response coefficients are finite independent theory inputs.
Consequently, this is not a parameter-free derivation of the Standard
Model.

## Why the arrows are mathematical data

A covariant reduction functor must supply:

1. base maps from \(M_8\) to the cap/collar description and from the caps
   and \(B_1\) to \(M_4\);
2. pullback and pushforward maps for metrics, spinors, gauge connections,
   scalar fields, and finite projectors;
3. a normalized fiber/collar measure with orientation and physical units;
4. intertwiners of variational, boundary, adjoint, and gauge-fixed domains;
5. a finite coefficient pushforward;
6. a Hessian intertwiner preserving the D0 KKT block and gauge/Dirac
   quotients.

Without these data, substituting one historical action into another is
neither dimensional reduction nor an equivalence theorem.

## Sector decisions

### Geometry and gravity

The \(M_8\) P1 family and the \(M_5|B_1\) two-cap relative action are each
well defined on their declared domains. They are not summed. No existing
map derives the latter from the former.

### Gauge

The normalized \(SU(3)\times SU(2)\times U(1)\) Yang-Mills action is a
consistent four-dimensional EFT term with independent \(g_1,g_2,g_3\).
Representation traces \(10/3,2,2\) are exact for the retained chiral
ledger. The historical active-generator counts \(1,2,7\) are not action
trace weights and remain screen-only.

### Fermions

The four-dimensional Dirac and Yukawa action is Hermitian on a declared
maximal-isotropic/self-adjoint domain. The v6.7 Clifford action supports
levelwise variation but does not derive a bulk spinor branching or a unique
boundary domain. Yukawa matrices are independent EFT inputs.

### Scalar/topographic

The cap scalar action, strict D0 reduction, field-normalization invariant

\[
\lambda_5=\frac{\kappa_1G_5}{Z_5^2},
\]

canonical quartic, and conditional local-stability inequality are
recovered. No value or sign of \(\lambda_5\) is selected.

### Charged current

The charged current is already contained in the \(SU(2)\) covariant
derivative. A separate \(g_{\rm ch}\) term would double count it and is
removed. CKM is \(U_u^\dagger U_d\) for independent Yukawa matrices. The
historical ratio-based CKM rule remains a frozen screen, not an action
consequence.

### Neutral and neutrino

The Standard Model neutral current is contained in the covariant
derivative. A real auxiliary response EFT may be retained in
\(\Delta S_{\rm BHSM}\) with finite inputs \(Z_{\rm neu},A_{\rm neu}\), and
\(g_{\rm neu}\). Its nonnegative response cone remains conditional. No
licensed physical neutrino mass operator or scale is derived.

### Projectors and generations

Spin(8) triality projectors are exact representation algebra conditional on
the carrier choice. Sector and mode projectors can be finite independent
inputs fixed before comparison. The target-rule implementation is
redundant once the projector ledger is explicit.

### Scale

No Planck, electroweak, Higgs, or particle mass is imported into the
action. No universal dimensionful calibration is exercised. Physical scale
and observable transport therefore remain Tier-B obstructions even if the
reduction functor is later supplied.

## Input corrections

- `alpha_inv_low_energy`: excluded from action; comparison/screen data only.
- `geometry_a`: independent dimensionless geometric input.
- `mode_ledger`: finite independent projector input.
- `omega_target_rules`: removed as redundant from the action.
- `ckm_screen_law`: screen-only, rejected as an action consequence.
- `gauge_trace_weights=1,2,7`: rejected as representation trace
  coefficients.
- gauge normalization: independent EFT couplings.
- Higgs scale screen: comparison-only; no physical scale claim.

## Completion consequence

RB-01 is not closed. It is sharpened from a broad provenance problem to one
exact missing object. Tier A remains blocked; Tiers B and C remain
ineligible. RB-02 remains only a parameter-free-extension blocker under the
v6.30.8 policy.

No v7.1 scientific campaign is entered here.
