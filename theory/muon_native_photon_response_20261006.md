# Actual-current primitive photon response; native owner application unresolved

6 October 2026. Starting PR #465 head:
`e2e047795410c09d6ae9cccc0c16a4216ec51fc7`.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.

## New evaluated object and limits

The signed primitive **angular density** resolvent was evaluated on the actual
retained fermion/photon current at the material point of the saved C2 step1222
cut. It keeps all 240 spatial/carrier coefficients at n1+n3, curvature contacts,
the full pointwise event weight, and all 224 external/output fermion labels.
The residual-directed space grew 8 ->16 ->24 ->32. No isolated eight-mode
resolvent, free curl replacement, finite heat model, or new endpoint condition
was used. Six new cache-based checks passed.

**The requested complete native photon response was not obtained.** This
component is an executed operator diagnostic and potential preconditioner,
not the user's acceptable native partial result. It has no native-domain,
BRST, temporal/radial, completion, or physical-error claim. Neither a physical
`a_mu` nor `g_mu` is inferred. The existing family/time jets, parent solution,
local QED/Higgs/weak contributions, and optional seam proposal are untouched.

## Action and pairing actually applied

The saved transported sources are stacked as S: C^8 ->C^240, with
S^dagger S=(16/3)I8. The n1 and n3 spectator Wigner indices stay intact.
`muon_matched_mechanical_source.angular_blocks` supplies the actual C,T,B
matrices in the right coframe and unit primitive-Tr16 internal basis. At the
saved point,

    rho = pi/2
    lambda = 0.5066207222913062
    W = Lambda(1+X_eta^3) = 6.708224570486777
    d = 1334.6139541462244  (per kappa1)

the applied form is

\[
 \widehat K_{\rm ang}=-{d\over16/3}
 [(C+(\lambda-1)T)^\dagger(C+(\lambda-1)T)
       +4\lambda(\lambda-1)B].
\]

The Lorentz minus sign is preserved. Positive spectral shifts make these
particular *shifted* systems well conditioned; this does not make K positive.
The background-curvature B contact is included. K_Q=(2/3)K_component is already
inside d. Dividing by Tr16 Q^2 converts the unit-trace carrier basis once;
there is no second mode/family factor or vertex multiplier. Agreement of the
complete K S output with the old saved primitive weak rows has absolute
binary64 residual 3.424315e-12. No old weak-row production was repeated.

The one-form geometric Gram comes from the actual angular metric/pairing:

\[
 m_{\rm ang}=2\pi^2\nu C rT_b^2={\nu C r\over R_b}
             =0.959045109007034.
\]

Here a=T_b b in the unit-S3 coframe, beta=T_b b and
T_b^2=1/(2 pi^2 R_b). The metric factor r^-2 contracts the one-form, so the
volume factor r^3 leaves r. This M is neither the electric Hessian nor the
charged-lepton mass matrix. It is the local geometric one-form Gram; it is
not asserted to be the complete native direct-sum mass form.

The saved family source maps have their unit-angular normalization. Their
actual cut b-vertex conversion is applied once:

\[
 C_\gamma=f_R\Gamma_{\rm bar},\quad f_R=T_b/R_b
             =0.22680626023337117,
\]
\[
 J_b=S(S^\dagger S)^{-1},\quad J=J_b C_\gamma,
 \qquad S^\dagger J=C_\gamma.
\]

All solves use the dual load, without multiplying it by M again. Source
duality residual is 2.393982e-16. The 224 labels include 32 nonzero current
columns and their exact zero companions. No conjugate-charge doubling of the
physical trace is introduced. This is a covector-preserving angular extension
of the saved current, not an assertion that its full stratified continuation
has no other dual components.

The flat transported-reference coexact check gives
||G_ref^dagger S||=1.155572e-15. In contrast,
||G_ref^dagger K_ang S||=10475.613247140414. The primitive angular application
therefore has nonzero **flat-reference** scalar constraint output. This is
not a measurement of the lambda-dependent physical covariant constraint.
Reference coexactness alone
does **not** establish the physical covariant BRST quotient or justify deleting
those responses. The ambient calculation retains them. Neither this check
nor a local Ward residual is a new background-selection argument.

## Executed source-directed solves and consumed error

The primitive coefficient kappa1 remains symbolic. The recorded solves are

\[
 (\widehat K_{\rm ang}+\widehat\zeta m_{\rm ang})\widehat u=J,
 \qquad \zeta=\kappa_1\widehat\zeta,
 \quad u_{\rm primitive}=\widehat u/\kappa_1.
\]

No kappa1=1 physical choice is made. The shifts are 1.25,2,4 times a
Frobenius conditioning bound for the whitened angular action. They are
spectral parameters, with no p^2, q^2, photon mass, or observable interpretation.
The frame is explicitly M-orthonormal, and residual images of the actual
primitive K generate enrichment. An independent 240-dimensional solve checks
the final consumed return. There is no full operator eigenspectrum campaign.

The reported trace is **Tr(J^dagger u_hat)** in this angular component, with
units/factors inherited from the saved geometric normalization; it is not
dimensionless g-2 and must still be divided by symbolic kappa1 for the
primitive response. It is neither the native heat coefficient nor F2(0).

| zeta/kappa1 | component trace Tr(J^dagger u_hat) | certified consumed-matrix Frobenius error |
|---:|---:|---:|
| 93420.48007025628 | 3.5391356579032634e-6 | 1.565760e-14 |
| 149472.76811241003 | 2.1894811648609800e-6 | 5.789518e-16 |
| 298945.53622482007 | 1.0855589761340900e-6 | 1.175984e-17 |

These are **certified arithmetic bounds for the exact stored Hermitian
binary64 component matrix**. They do not enclose the analytic-coefficient
rounding, source-representation, geometry/history, continuum, physical input,
domain, or omitted native action errors. An initial certificate bounded the
solution contribution; the appended `return_certificate_completion` also
encloses final output-multiplication rounding and per-column relative
residuals. It reused the saved solutions and performed zero further solves.
The first execution/source version and all original certificates are retained.

For H=Khat+zeta_hat M, a 192-bit Arb calculation proves
alpha=zeta_hat m-||Khat||_F>0. With the exact factorized current J_b C_gamma,
the residual bound for a stored current solution column is

\[
 \rho_j\le\|H U_b-J_b\|_F\|(C_\gamma)_j\|
       +\|H\|_F\|(U-U_bC_\gamma)_j\|,
\]
\[
 \|J^\dagger(u_j-u_j^{\rm exact})\|
 \le \|J\|_F\rho_j/\alpha.
\]

The certified output-multiplication rounding is then added. This is an error
in the **consumed contraction**, not only a projection or equation residual.
All 224 current-column bounds are saved. The maximum relative residual bound
on nonzero columns is 3.213889e-10; zero columns are marked explicitly rather
than dividing by a zero norm. The final-frame M-Gram residual is 2.609562e-15.
The source-only eight-dimensional approximation has consumed basis-error
estimate 5.874440e-7; enrichment reduces that to 9.511818e-15. Thus its
replacement by an eight-mode response was not justified.

## First unexecuted native action, with its consumer

The first unavailable *contracted* action is

\[
 \mathcal R_{\rm ind}(v,j)
 =\delta_v\delta_j\Gamma_{\rm AE4}[0]
  -H_{\rm local,already\ owned}(v,j)
\]

on the actual current directions and their generated complement. It is the
same-owner induced matching remainder, not another determinant or Wilson
coefficient. At fixed length and a common-domain source pullback its bulk
part is explicitly

\[
 {1\over2}\int_{\ell_*^2}^{\infty}dt\,
      \operatorname{STr}(e^{-tP_0}P_{vj})
 -{1\over2}\int_{\ell_*^2}^{\infty}dt\int_0^tdu\,
      \operatorname{STr}(e^{-(t-u)P_0}P_v e^{-uP_0}P_j).
\]

Relative-zeta/eta completion and applicable moving Gram, length, domain and
source-map derivatives belong to this same functional. The generalized
mixed jet retains

    A_vj = solve(M, K_vj - M_vj A - M_v A_j - M_j A_v).

The saved scalar moment weights in `ae4_stratified_dirac_zeta_induced_owner`
do not evaluate these two contracted terms. `HeatPencil` can assemble them
from supplied K,M/jets, but generates neither those operands nor the source
domain. The old AE3 shape constructs curl-2 blocks and the stop/BRST witness
constructs a three-mode scalar boundary response; neither is substituted for
the reached source action. The actual original local `photon_body.py` is a
Lambda-only radial primitive, explicitly not a canonical quantum kernel, and
was inspected without replaying it.

This identifies an uncomputed application of the adopted owner, **not** a
new missing common-A coupling, jmath index, eta profile, seam postulate, or
full-history reconstruction demand. Only the required contact/resolvent
contractions need be supplied. The native length first enters their lower
integration limit ell_star^2; no helper default ell=1 is used.

The saved temporal/radial/moving-frame rows and inherited reset/material/stop
traces are known pieces that still require native weak assembly. They are not
silently suppressed. The single first-unavailable action above should not be
read as a claim that all later native/domain/state operands have been solved.

The consumer is the completed photon form action on J_b and its connected
response before the full (K0Q+zeta M0Q) solve. The current angular action
retains the Lorentz sign and is only a density subterm; it cannot be inserted into the
positive generalized native heat pencil. Native heat calls and physical
signed-transfer evaluations are both zero. Every full paired ledger entry
remains UNEVALUATED; the previously proved direct fixed-frame mass/photon
contact zero is preserved as its specific subterm only. Strong terms remain
a subset of native, never an extra addend.

## Reproducibility and continuation

Accepted arrays: `artifacts/muon_native_photon_response_20261006/run_1/`.
Accepted final rounding/relative-residual certificates:
`run_1/return_certificate_completion/`. The source/domain equations, actual
hashes, contribution ledger and compact checkpoint accompany them.
The preserved first executed source snapshot verifies the original run hash.

Reproduce the new component alone in a fresh directory:

```powershell
python scripts/replay_muon_native_photon_response.py --output <unused-directory>
python -m pytest --noconftest -q tests/test_muon_native_photon_response.py
```

The current replay directly includes the completed return-rounding bound;
the separate completion script records what was actually executed in this
milestone. No old family checks or production calculations were repeated.
The standalone local launcher is saved in Downloads. Git provenance records
the starting commit, intended diff, publication commit and verified PR head.

Next: evaluate the two same-owner contact/paired heat contractions defining
R_ind on the reached current/response directions, with the matching subtraction
and required completion, and consume that action in the full photon weak solve.
