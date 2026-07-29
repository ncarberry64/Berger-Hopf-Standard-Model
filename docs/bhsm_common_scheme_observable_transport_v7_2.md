# BHSM v7.2 common-scheme observable transport

## Result

The finite-input observable functor

\[
\mathcal T_{\rm obs}:
\left(S_{\rm BHSM}^{\rm strat},\Theta_{\rm BHSM},\ell_\star\right)
\longrightarrow\mathcal O_{\rm phys}
\]

is constructed on one declared perturbative domain. Its result is
`BHSM_COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR_CONSTRUCTED`.
This closes RB-13 and yields `BHSM_PHYSICAL_COMPLETE` in the precise sense
that every retained finite-input quantity has a scheme, scale,
normalization, and observable classification. It is not a parameter-free
prediction claim.

## Common scheme and reference scale

The unique convention is the non-GUT-normalized Standard Model
\(\overline{\mathrm{MS}}\) scheme with \(Y_H=1/2\). The universal reference
point is

\[
\mu_\star=\ell_\star^{-1},\qquad
\widehat\mu_\star=\mu_\star\ell_\star=1.
\]

The finite independent inputs at this point are

\[
g_1,\ g_2,\ g_3,\qquad
Y_u,\ Y_d,\ Y_e,\qquad
\widehat m_H^2,\ \lambda_H=\lambda_5 ,
\]

together with the already typed representation, projector, domain, and
retained Wilson data. None is advertised as predicted.
The equality \(\lambda_H(\mu_\star)=\lambda_5\) is the canonical retained
\(M_4\) Higgs normalization; it does not introduce a second quartic.

## RG transport

On the maximal connected fixed-active-content interval
\(I_{\rm active}(\mu_\star)\),

\[
\Theta(\mu)=
U_{\overline{\rm MS}}^{(1)}(\mu,\mu_\star)\Theta(\mu_\star).
\]

The implementation uses the full minimal-Standard-Model one-loop beta
functions for \(g_i,Y_u,Y_d,Y_e,\widehat m_H^2,\lambda_H\), with three
generations and one Higgs doublet. It introduces no neutrino mass operator.
The gauge convention is

\[
16\pi^2\beta_{g_i}=b_i g_i^3,\qquad
(b_1,b_2,b_3)=\left(\frac{41}{6},-\frac{19}{6},-7\right).
\]

The perturbative truncation is \(O((16\pi^2)^{-1})\). Numerical evolution is
fixed-step RK4 in \(\ln(\mu/\mu_\star)\), with its step count explicit.
No two-loop contribution is silently mixed into the map.

## Threshold prescription

Transport is valid below the declared \(M_4\) EFT cutoff and only until the
first active-content threshold. If a requested path crosses a running-mass
threshold, v7.2 returns
`EFT_MATCHING_REQUIRED_AT_FIRST_THRESHOLD` and stops. A separately declared
matched EFT is required beyond that point.

This is deliberately narrower than a fabricated all-scale map. In
particular, the repository's historical approximate QCD running scaffold is
not combined with the full electroweak map and called a precision result.
No pole-mass conversion is supplied. Quantities without a supported
conversion remain \(\overline{\mathrm{MS}}\) running observables at their
declared scale.

## Electroweak stationary branch

The retained convention is

\[
V(H)=m_H^2H^\dagger H+\lambda_H(H^\dagger H)^2 .
\]

The positive broken branch exists for \(m_H^2<0\), \(\lambda_H>0\), and is

\[
\widehat v^2=-\frac{\widehat m_H^2}{\lambda_H},
\qquad
v_{\rm phys}=\frac{\widehat v}{\ell_\star}.
\]

At a common running scale,

\[
m_W^{\overline{\rm MS}}(\mu)=\frac12g_2(\mu)v(\mu),
\qquad
m_Z^{\overline{\rm MS}}(\mu)=
\frac12\sqrt{g_1^2(\mu)+g_2^2(\mu)}\,v(\mu),
\]

\[
M_u^{\overline{\rm MS}}(\mu)=\frac{v(\mu)}{\sqrt2}Y_u(\mu),
\quad
M_d^{\overline{\rm MS}}(\mu)=\frac{v(\mu)}{\sqrt2}Y_d(\mu),
\quad
M_e^{\overline{\rm MS}}(\mu)=\frac{v(\mu)}{\sqrt2}Y_e(\mu).
\]

These are input-dependent running mass definitions, not pole predictions.

## Universal calibration

Exactly one dimensionful datum is exercised:

\[
v_{\rm phys}=(\sqrt2G_F)^{-1/2},
\qquad
\ell_\star=
\frac{\widehat v}{(\sqrt2G_F)^{-1/2}} .
\]

\(G_F\) is classified as
`ONE_UNIVERSAL_DIMENSIONFUL_CALIBRATION`. It is not a prediction. The same
\(\ell_\star\) is used in every sector. No second mass calibration, sector
scale, dimensionless adjustment, or later retuning is permitted.

## CKM transport

At the declared common scale,

\[
Y_u=U_u y_u W_u^\dagger,\qquad
Y_d=U_d y_d W_d^\dagger,\qquad
V_{\rm CKM}=U_u^\dagger U_d.
\]

Singular values are ordered increasingly as \((u,c,t)\) and \((d,s,b)\).
Degenerate singular values stop the construction because the mixing basis is
then ambiguous. The PDG chart is extracted from rephasing invariants:

\[
s_{13}=|V_{ub}|,\qquad
s_{12}=|V_{us}|/c_{13},\qquad
s_{23}=|V_{cb}|/c_{13},
\]

\[
J=\operatorname{Im}(V_{ud}V_{cs}V_{us}^\ast V_{cd}^\ast).
\]

The phase is obtained from \(J\) and \(|V_{cd}|\). CKM therefore follows
from independent Yukawa inputs and is not parameter-free. The historical
\(1/16\) screen is not used.

## Scalar and spectral classifications

Every retained quantity has exactly one physical classification:

| Quantity | Classification |
| --- | --- |
| Berger/Hopf eigenvalues and indices | dimensionless geometric result |
| Wilson coefficients and \(\lambda_5\) | action coefficient |
| \(g_i,Y_f,m_H^2,\lambda_H\) | running parameter |
| \(m_W,m_Z\), charged-fermion singular values | running mass |
| anomaly identities and \(V=U_u^\dagger U_d\) | structural identity |
| \(G_F,\ell_\star\) | calibration |
| \(1,2,7\), \(1/16\), \(\eta_\ell\), \(\rho_{\rm ch}\), overlap tables | historical screen |
| neutral/PMNS/neutrino-mass data | conditional extension |
| an unmapped eigenvalue called a particle mass | no physical observable |
| unsupported pole masses and widths | no physical observable |

A mass-type spectral relation is permitted only when its normalization and
running definition exist:

\[
m_n(\mu)=
\frac{Z_n^{-1/2}(\mu)\widehat m_n(\mu)}{\ell_\star}.
\]

## Finite benchmark manifest

The v7.2 benchmark manifest contains ten typed items:

| ID | Item | Class |
| --- | --- | --- |
| B72-01 | stratified-action covariance | structural identity |
| B72-02 | representation and anomaly identities | structural identity |
| B72-03 | common-scheme gauge identities | structural identity |
| B72-04 | electroweak mass relations | input-dependent calculation |
| B72-05 | CKM from Yukawa inputs | input-dependent calculation |
| B72-06 | charged-lepton running mass | input-dependent calculation |
| B72-07 | quark running mass | input-dependent calculation |
| B72-08 | fixed-\(h\) \(D_0\) result | structural identity |
| B72-09 | scalar quartic | parameterized relation |
| B72-10 | universal calibration consistency | calibration check |

No item depending on independent Standard Model inputs is called a BHSM
prediction.

## Falsification audit and release gate

After the v7.1 claim firewall, the surviving distinctive results are
mathematical or architectural: stratified-action covariance, the fixed-\(h\)
\(D_0\) result, and conditional representation/anomaly identities. The new
mass and CKM outputs depend on independent Standard Model inputs. The scalar
relations are parameterized; \(G_F\) is a calibration; the old numerical
relations are screens.

Consequently, no distinct action-derived falsifiable physical prediction
survives in the official claim set. RB-14 closes with the finite typed
benchmark manifest, but RB-15 is blocked by the singular object
`ABSENCE_OF_DISTINCT_ACTION_DERIVED_FALSIFIABLE_PREDICTION`. RB-16 remains
downstream and no external-review-ready release label is issued.

The exact release verdict is
`BHSM_RELEASE_COMPLETION_BLOCKED_BY_ABSENCE_OF_DISTINCT_ACTION_DERIVED_FALSIFIABLE_PREDICTION`.
