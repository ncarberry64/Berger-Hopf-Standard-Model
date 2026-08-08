# BHSM v14.76 — Landau Source Exhaustion and Response-Sign Theorem

## Executive result

v14.75 established an exact geometric area contribution to the \(\ell=2\)
Landau action, but it failed the locking cone and did not determine the
physical BHSM coefficients.

v14.76 narrows the remaining source problem.

The strongest results are

\[
\boxed{
\text{constant-background eta }p8
\text{ begins at eighth fluctuation order}
}
\]

and

\[
\boxed{
\text{stable eliminated-field response cannot increase }3u+v.
}
\]

Therefore neither the constant-background \(p8\) term nor the quadratic DtN
coefficient called `c4` can be used as the missing quartic stabilizer.

A distinct positive bare fourth variation from an action-owned sector is
required if the v14.74 locking phase is to occur.

## 1. Constant eta \(p2+p8\) order count

The retained parent eta density is

\[
F(X)=\frac{\kappa_1}{2}X+\frac18X^4,
\qquad
X=|D\eta|^2.
\]

On the v14.30 constant background,

\[
D\eta_0=0.
\]

For a linear tangent perturbation,

\[
X(t)=x_2t^2.
\]

Hence

\[
F(X(t))
=
\frac{\kappa_1x_2}{2}t^2
+
\frac{x_2^4}{8}t^8.
\]

The \(p8\) contribution therefore satisfies

\[
D^3F_{p8}(0)=D^4F_{p8}(0)=\cdots=D^7F_{p8}(0)=0,
\]

and

\[
\boxed{
D^8F_{p8}(0)=5040x_2^4.
}
\]

Thus the retained \(p8\) nonlinearity cannot supply \(u\) or \(v\) on the
constant v14.30 branch.

## 2. Degree-one background activation

This conclusion is branch-specific.

For

\[
F'=\frac{\kappa_1}{2}+\frac12X^3,\quad
F''=\frac32X^2,\quad
F^{(3)}=3X,\quad
F^{(4)}=3,
\]

a general nonzero background \(X_0\) gives

\[
D^2F=F'x_2+F''x_1^2,
\]

\[
D^3F=F'x_3+3F''x_1x_2+F^{(3)}x_1^3,
\]

\[
D^4F
=
F'x_4+4F''x_1x_3+3F''x_2^2
+6F^{(3)}x_1^2x_2+F^{(4)}x_1^4.
\]

So on the missing degree-one full-preimage stationary background, \(p8\) can
enter \(D^2,D^3,D^4\) immediately.

The absence of that background is therefore a direct coefficient obstruction,
not just a provenance bookkeeping issue.

## 3. DtN `c4` firewall

The v14.30 DtN action is quadratic,

\[
S_{\rm DtN}
=
\frac12\langle\phi,N(H)\phi\rangle.
\]

Its low-energy operator expansion is

\[
N(z)=m_0+Zz+c_4z^2+\cdots.
\]

The stored reference

\[
c_4=-0.10901441699630973
\]

is a coefficient of \(z^2\), i.e. a **four-derivative quadratic operator
term**.

It is not a field-amplitude quartic.

At fixed operator/background,

\[
D_\phi^3S_{\rm DtN}=D_\phi^4S_{\rm DtN}=0.
\]

Hence

\[
\boxed{
c_4^{\rm DtN}\neq u,\ v.
}
\]

## 4. Reflection cubic selection rule

On the equal-cap branch,

\[
Q\to-Q.
\]

Therefore

\[
\boxed{D^3_{QQQ}\Gamma=0.}
\]

But an even interior response variable can couple as

\[
y_{\rm even}Q^2.
\]

So reflection does not eliminate the mixed cubic response that later feeds
the quartic Schur correction.

## 5. Quartic response-sign theorem

After quadratic Schur reduction,

\[
a_{4,\rm eff}(q)
=
a_{4,\rm bare}(q)
-
\frac18B(q,q)^TK^{-1}B(q,q).
\]

If

\[
K>0
\]

on the eliminated physical complement, then

\[
\boxed{\Delta a_4(q)\le0}
\]

for every ray \(q\).

For the isotropic locking ray,

\[
Q=sI,
\]

\[
a_4(sI)=\frac34(3u+v)s^4.
\]

Therefore

\[
\boxed{
\Delta(3u+v)\le0.
}
\]

Stable cubic response cannot repair a negative isotropic quartic combination.

This makes the role of the different orders precise.

At quadratic order,

\[
H_{\rm eff}=H_{bb}-H_{bi}K^{-1}H_{ib},
\]

so stable response can lower \(r\) and could in principle drive the
quadratic instability.

At quartic order, the same stability property works in the opposite strategic
direction: it makes stabilization harder.

Thus a locked phase needs:

\[
\boxed{\text{enough negative quadratic response to obtain }r<0}
\]

and independently

\[
\boxed{\text{enough positive bare }D^4\text{ to obtain }3u+v>0,\ v>0.}
\]

## 6. Exact singlet and quintet examples

For an even scalar response

\[
B_s=g_sI_2,
\]

with stiffness \(k_s>0\),

\[
\Delta u=-\frac{g_s^2}{2k_s},\qquad
\Delta v=0,
\]

so

\[
\boxed{
\Delta(3u+v)
=
-\frac{3g_s^2}{2k_s}<0.
}
\]

For the traceless-Gram quintet,

\[
B_5
=
g_5
\left(
Q^TQ-\frac{I_2}{3}I
\right),
\]

\[
\left\|
Q^TQ-\frac{I_2}{3}I
\right\|^2
=
I_4-\frac13I_2^2.
\]

Elimination gives

\[
\Delta u=\frac{g_5^2}{6k_5},
\]

\[
\Delta v=-\frac{g_5^2}{2k_5},
\]

and

\[
\boxed{3\Delta u+\Delta v=0.}
\]

So the quintet can redistribute anisotropy between \(u\) and \(v\), but it
cannot improve the isotropic stability combination.

## 7. Source exhaustion

The current constant branch now has no known action-complete positive bare
quartic source.

The round area witness is exact but not independently action-owned and fails
the cone. Constant eta \(p2\) is quadratic. Constant eta \(p8\) starts at
order eight. The fixed-background DtN theory is quadratic. Ideal equal-cap
GHY cancels. Stable interior response can only lower the quartic ray
coefficient.

The remaining eligible classes are therefore:

1. nonlinear \(M_8/M_5\) gravity and scalar geometry;
2. the actual nonconstant degree-one eta background;
3. intrinsic \(M_4\) background response;
4. the physical nonlocal spectral determinant.

These are the sectors that must now be evaluated, rather than revisiting the
constant-background proxies.

## Hindsight 20/20 ledger

### VALIDATED

- Constant-background \(p8\) starts at eighth fluctuation order.
- It contributes no \(D^3,D^4\) Landau term there.
- Nonconstant \(X_0\) can activate \(p8\) already at \(D^2,D^3,D^4\).
- DtN `c4` is derivative order, not field quartic.
- Reflection kills pure \(Q^3\).
- Even-interior \(yQ^2\) response survives.
- Quadratic stable response can lower \(r\).
- Quartic stable response is non-positive on every ray.
- It cannot increase \(3u+v\).
- Singlet response worsens \(3u+v\).
- Traceless-Gram quintet response preserves \(3u+v\).

### INVALIDATED

- Constant-branch eta \(p8\) as the missing Landau quartic.
- v14.30 DtN `c4` as \(u\) or \(v\).
- Stable interior response as a cure for negative isotropic quartic.
- Hessian-only phase closure.

### RECLASSIFIED

The physical locking problem now requires two separately sourced effects:
a quadratic destabilization and a bare quartic stabilization.

## Completion state

`CONSTANT_ETA_P8_LANDAU_QUARTIC = INVALIDATED`

`QUADRATIC_DTN_C4_AS_LANDAU_QUARTIC = INVALIDATED`

`STABLE_RESPONSE_EFFECT_ON_R = CAN_LOWER`

`STABLE_RESPONSE_EFFECT_ON_3U_PLUS_V = CANNOT_INCREASE`

`POSITIVE_BARE_D4_SOURCE = REQUIRED`

`PHYSICAL_R_U_V = OPEN`

`PHYSICAL_LOCKING_GATE = UNDECIDED`

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

No physical observable is emitted.
