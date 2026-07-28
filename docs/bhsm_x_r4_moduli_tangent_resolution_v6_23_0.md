# BHSM v6.23.0 X-to-R4 normalization and M4 response type

Primary normalization theorem:
`BHSM_X_TO_R4_ACTION_NORMALIZATION_DERIVED`.

Primary response-type theorem:
`BHSM_M4_X_RESPONSE_REQUIRES_LOCAL_CONSTRAINT_SOLVE`.

The v6.20 local scalar-curvature right-inverse target is
`BHSM_V6_20_LOCAL_RIGHT_INVERSE_TARGET_REJECTED_BY_CALCULATION`.

## Scope

This sprint resolves the v6.22 normalization obstruction without changing
the frozen action or historical evidence. It distinguishes:

- the homogeneous closed-FRW invariant \(X_{\rm FRW}\);
- the four-dimensional scalar curvature \(R_4\);
- a derivative of a one-parameter homogeneous metric family;
- an independently varied four-dimensional metric;
- a hypothetical scalar-curvature Green operator.

No local field \(X_{\rm FRW}(x)\), measured input, fitted coefficient, new
action, scale, primitive, or boundary parameter is introduced.

## Provenance ledger

The relevant repository chain is

\[
q\longrightarrow \delta X_{\rm FRW}
\longrightarrow \hbox{homogeneous background curvature},
\qquad
\delta h_{\mu\nu}\longrightarrow \delta S .
\]

The two arrows after \(q\) are not one action-level identification.

| Symbol | Repository meaning |
| --- | --- |
| \(X_{\rm FRW}\) | \(H^2+a^{-2}\), a homogeneous closed-FRW invariant and on-shell branch coordinate |
| \(A_{\rm FRW}\) | \(N_\partial^{-1}\dot H+H^2\) |
| \(R_4\) | \(6(A_{\rm FRW}+X_{\rm FRW})\) |
| \(\mu\) | \(-A_5/Z_5\), the external fold/action control |
| \(\epsilon\) | signed scalar amplitude |
| \(r\) | \(|\epsilon|\), the one-sided Puiseux amplitude |
| \(s\) | \(\operatorname{sign}\epsilon\), the scalar sign |
| \(\tau\) | the upper/lower curvature-sheet label |
| \(q\) | \(r\) on a fixed sheet, promoted as the collective field |
| \(\chi_1\) | the positive leading curvature-sheet coefficient |

In the normalized representative
\(q_5=\kappa_1=Z_5=1\), \(q\) is dimensionless. The fold relation is

\[
X_{\rm FRW}(q)=2+\tau\chi_1q+O(q^2).
\]

Thus

\[
\left.\frac{dX_{\rm FRW}}{dq}\right|_{q=0}
=\tau\chi_1,
\qquad
\delta X_{\rm FRW}
=\tau\chi_1q+O(q^2).
\]

The first formula is the tangent component per unit \(q\); the second is its
linear variation. They are not competing normalizations.

The scalar-wall calculation solves \(X_{\rm FRW}\), the warp profile, lapse,
and endpoint on a homogeneous branch. Its Lyapunov--Schmidt ledger says that
\(X_{\rm FRW}\) is eliminated separately on the \(\tau\) sheets. It does not
declare \(X_{\rm FRW}(x)\) as an off-shell field.

By contrast, the frozen action varies the P1 metric and the intrinsic B1
metric independently. The matcher

\[
S_{\rm match}
=\int_{\mathrm{B1}}\sqrt{-h}\,
\Lambda^{\mu\nu}(h_{\mu\nu}-\iota^*g_{\mu\nu})
\]

imposes \(h_{\mu\nu}=\iota^*g_{\mu\nu}\) only after variation and multiplier
elimination. This independent metric variation selects the response type.

## Action-selected normalization

The scalar-wall action convention is

\[
\operatorname{Ric}_{\mu\nu}(h)
=3X_{\rm FRW}h_{\mu\nu}.
\]

Tracing in four dimensions gives

\[
R_4
=h^{\mu\nu}\operatorname{Ric}_{\mu\nu}
=4(3X_{\rm FRW})
=12X_{\rm FRW}.
\]

Therefore the homogeneous scalar-wall branch obeys

\[
\left.\frac{dR_4}{dq}\right|_{q=0}
=12\tau\chi_1,
\qquad
\delta R_4
=12\tau\chi_1q+O(q^2).
\]

This is the action-selected normalization. It is a homogeneous background
identity, not a local differential equation for arbitrary \(q(x)\).

The separate critical static branch has

\[
H=A_{\rm FRW}=0,\qquad a=X_{\rm FRW}^{-1/2},
\]

and hence

\[
R_4=6X_{\rm FRW},
\qquad
\left.\frac{dR_4}{dq}\right|_{q=0}
=6\tau\chi_1.
\]

There is no contradiction. The maximally symmetric dS4 metric and the
static \(\mathbb R\times S^3\) metric are distinct homogeneous junction
branches even where both have \(X_{\rm FRW}=2q_5\). The scalar-wall
regulator uses the former.

## Status of the v6.20 coefficient-one target

The v6.20 target was

\[
D R_h[\mathcal T^{(X)}]
=\delta X_{\rm FRW}
=\tau\chi_1q.
\]

No historical artifact stores a redefinition
\(X_R=R_4\) or \(x_R=R_4/12\). The same v6.20 ledger inherits
\(X_{\rm FRW}=H^2+a^{-2}\). The coefficient-one equation is therefore not
an implicit normalized-curvature convention. It is a later attempted local
right-inverse completion ansatz with an \(X_{\rm FRW}\)-to-\(R_4\)
normalization error.

The v6.20 and v6.22 artifacts remain unchanged. This v6.23 ledger
supersedes only the proposed missing-object diagnosis.

## Route A: homogeneous family derivative

For the stored closed-dS4 family,

\[
ds_4^2
=-du^2
+X_{\rm FRW}^{-1}
\cosh^2\!\left(\sqrt{X_{\rm FRW}}(u-u_0)\right)d\Omega_3^2,
\]

set
\[
z=\sqrt{X_{\rm FRW}}(u-u_0).
\]

At fixed dimensional time \(u\),

\[
K^{(u)}_{uu}=0,
\]

\[
K^{(u)}_{ij}
=X_{\rm FRW}^{-2}
\left[z\sinh z\cosh z-\cosh^2z\right]\gamma_{ij}.
\]

At fixed \(z\),

\[
ds_4^2
=X_{\rm FRW}^{-1}
\left[-dz^2+\cosh^2z\,d\Omega_3^2\right],
\qquad
K^{(z)}_{\mu\nu}
=-\frac1{X_{\rm FRW}}h_{\mu\nu}.
\]

Fixed conformal time gives the same conformal representative. The two
derivatives satisfy

\[
K^{(u)}_{\mu\nu}-K^{(z)}_{\mu\nu}
=\mathcal L_\xi h_{\mu\nu},
\qquad
\xi
=\frac{u-u_0}{2X_{\rm FRW}}\partial_u.
\]

The relation holds componentwise. The vector is smooth on every finite-\(u\)
chart for \(X_{\rm FRW}>0\) and does not change \(u_0\).

For a homogeneous conformal perturbation \(k_{\mu\nu}=c h_{\mu\nu}\),

\[
D R_h[k]=-cR_4.
\]

With \(c=-1/X_{\rm FRW}\), the dS4 family therefore gives

\[
D R_h[K^{(z)}]=12.
\]

For the static family

\[
ds_4^2=-du^2+X_{\rm FRW}^{-1}d\Omega_3^2,
\]

the fixed-\(u\) derivative is

\[
K_{uu}=0,\qquad
K_{ij}=-X_{\rm FRW}^{-2}\gamma_{ij},
\]

and differs from \(-h/X_{\rm FRW}\) by the same time-rescaling Lie
derivative. It gives \(D R_h[K]=6\).

These derivatives are unique within the stated one-parameter family and a
chosen coordinate identification. They are not unique solutions of a
general scalar-curvature equation.

The intrinsic diffeomorphism preserves the whole B1 and the matcher when it
acts simultaneously on \(h\) and \(\iota^*g\). However, \(\xi\) vanishes
only at \(u=u_0\). It does not preserve generic fixed-\(u\) regulator
endpoints, and the repository stores no coordinate-level M4 regulator
boundary. Consequently no boundary-canonical homogeneous representative is
selected. The fixed-conformal-time representative is retained only as an
algebraic diagnostic.

## Route B: local scalar-curvature right inverse

The action never introduces an independent \(X_{\rm FRW}(x)\). Moreover,

\[
D R_h[k]=f
\]

is only one scalar contraction of the metric equation. Gauge tensors and,
on the Einstein branch, transverse-traceless tensors lie in its kernel.
The equation neither fixes the tensor response nor supplies the B1/matcher
domain.

The independently varied Einstein and junction equations provide the
missing tensor equations. Adding a separate Green operator
\((D R_h)^{-1}\) would impose an extra relation and double count the metric
variation. Route B is therefore rejected by calculation; no Green operator
is constructed.

## Route C: local promotion diagnostic

Although it is not action-selected, the fixed-conformal-coordinate ansatz

\[
h_{\mu\nu}(q)=\frac{X_0}{X_{\rm FRW}(q)}h^{(0)}_{\mu\nu}
\]

shows why a local promotion cannot obey only
\(\delta R_4=12\delta X_{\rm FRW}\). The exact conformal formula gives

\[
R_4[h(q)]
=12X_{\rm FRW}(q)
+\frac{X_{\rm FRW}}{X_0}
\left[
3\Box\ln X_{\rm FRW}
-\frac32(D\ln X_{\rm FRW})^2
\right].
\]

Writing
\[
X_{\rm FRW}'(0)=\alpha,\qquad
X_{\rm FRW}''(0)=\beta,
\]

the derivative terms at \(q=0\) are

\[
C_1=\frac{3\alpha}{X_0},
\qquad
C_2=\frac{3\beta}{X_0}
-\frac{9\alpha^2}{2X_0^2}.
\]

Here \(\alpha=\tau\chi_1\), whereas the first-order fold tangent does not fix
\(\beta\). This calculation is diagnostic only; it is not inserted into the
action.

## Route D: independent metric plus collective field

The frozen action selects Route D. After radial reduction its appropriate
off-shell structure is

\[
S_J
=\int\sqrt{-h}
\left[
\frac12F(q)R_4[h]
-\frac12K_J(q)(Dq)^2
-V_J(q)
\right],
\]

with \(h_{\mu\nu}\) and \(q\) independent. The homogeneous relation
\(X_{\rm FRW}(q)\) is recovered only after solving the background metric and
junction equations.

For local \(q(x)\), the M4 response must be obtained by solving the
linearized Einstein equation together with the radial ADM constraints, B1
junction equation, matcher, and endpoint conditions. The scalar-curvature
variation is then a consequence of that tensor solution, not its defining
right-inverse equation.

Thus:

`BHSM_M4_X_RESPONSE_REQUIRES_LOCAL_CONSTRAINT_SOLVE`.

## Moduli/constraint no-double-counting theorem

The radial homogeneous profiles may be represented as affine terms in the
metric scalar variables:

\[
N=N_0+\tau N_1q+\delta N_{\rm constraint},
\qquad
a=a_0+\tau a_1q+\delta a_{\rm constraint}.
\]

Let \(Y\) denote the lapse/Weyl/longitudinal constraint variables. For

\[
S_{\rm deriv}^{(2)}
=\frac12K(Dq)^2
+(Dq)\langle J,Y\rangle
+\frac12\langle Y,LY\rangle,
\]

the affine redefinition \(Y=Z+vq\) gives

\[
K'=K+2\langle J,v\rangle+\langle v,Lv\rangle,
\qquad
J'=J+Lv.
\]

On one fixed quotient domain where \(L^{-1}\) exists,

\[
K'-\langle J',L^{-1}J'\rangle
=K-\langle J,L^{-1}J\rangle.
\]

Therefore the homogeneous radial profile can be placed either in the direct
term/source or in an affine shift of the constraint variables, never both.
No additional \(K_{\mu\nu}^{(X)}\) is added to the independently varied M4
metric.

The inherited Einstein-frame contribution

\[
K_{\rm Weyl}
=\frac{3\chi_1^2(4-\pi)^2}{16\pi}
\]

is generated once by \(g_E=(F/F_0)h\) after the Jordan reduction and is
counted once.

## Action and Schur status

The conceptual response-type obstruction is resolved, but the fold Schur
reduction is not yet reopened. The existing repository fixes:

- two reflected P1 caps and one common B1;
- capwise GHY cancellation;
- exact matcher elimination;
- the v6.18 threading response;
- the v6.20 principal lapse--Weyl block;
- \(K_{\rm scalar}\ge2\);
- the single Einstein-frame \(K_{\rm Weyl}\) term.

It does not yet contain the complete local scalar metric operator and source:

- the lower-order radial blocks;
- the full \(q\)-metric source;
- the x-dependent scalar B1 junction projections;
- the moving-endpoint longitudinal condition;
- the resulting operator and adjoint domains;
- kernel, adjoint kernel, and compatibility.

The missing object is no longer a metric family or a scalar-curvature Green
operator. It is the complete local Einstein/radial-ADM/B1/matcher constraint
operator, source, and moving-endpoint domain derived from the frozen action.

The exact Schur verdict is
`BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_INCOMPLETE_LOCAL_CONSTRAINT_OPERATOR_AND_B1_DOMAIN`.

The kinetic verdict is
`BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_INCOMPLETE_LOCAL_CONSTRAINT_OPERATOR_AND_B1_DOMAIN`.

No Schur number, total \(k_q^E\), kinetic sign, physical mass, ghost,
tachyon, nonlinear-stability, sheet-selection, production, or white-hole
dynamics claim is emitted.
