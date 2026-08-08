# BHSM v14.77 — Complementary-Bulk Cancellation and DtN Shape-\(D^4\) Gate

## Executive result

v14.76 showed that the constant-background eta \(p8\) term cannot supply the
missing Landau quartic and that stable interior-field elimination cannot
increase the isotropic stability combination \(3u+v\).

v14.77 continues the bare-\(D^4\) source hunt.

Two useful results emerge.

First, on the equal reflection branch, **pure fixed-background local bulk
domain motion contributes nothing at any order**.  This removes a large class
of apparent gravitational quartic sources.

Second, the exact two-sided Dirichlet-to-Neumann map has a genuinely different
shape derivative.  When the seam moves while total cap width is fixed, its
fourth-order shape coefficient is sign-indefinite and is **positive in a thin
cap regime**.

So a positive nonlocal shape-\(D^4\) mechanism exists mathematically inside
the already retained DtN architecture.  It is not yet the physical
\(\ell=2\) coefficient.

---

## 1. Complementary local bulk cancellation

Let a moving seam \(X\) divide a fixed manifold into

\[
M_+(X)\cup M_-(X)=M,
\]

with disjoint interiors.

If the two sides carry the same local density and coefficient,

\[
S_{\rm bulk}[X]
=
c\int_{M_+(X)}{\cal L}
+
c\int_{M_-(X)}{\cal L},
\]

then exactly

\[
\boxed{
S_{\rm bulk}[X]
=
c\int_M{\cal L}.
}
\]

Therefore

\[
\boxed{
D_X^nS_{\rm bulk}=0
\quad\text{for every }n\ge1.
}
\]

In particular,

\[
\boxed{D_X^4S_{\rm bulk}=0.}
\]

This theorem assumes the ambient metric and fields are held fixed.  It does
not say that the dynamical gravitational action has zero shape response after
the metric and matter fields are allowed to react.

For unequal coefficients,

\[
c_+\int_{M_+}{\cal L}
+
c_-\int_{M_-}{\cal L}
=
c_-\int_M{\cal L}
+
(c_+-c_-)\int_{M_+}{\cal L}.
\]

So any pure domain-motion dependence is proportional to an actual
coefficient/density mismatch.

No such mismatch is inserted here.

---

## 2. Internal GHY pair

On a smooth internal seam shared by reflection-related caps,

\[
n_-=-n_+,
\]

so

\[
K_-=-K_+.
\]

With the same induced metric and reflection-related Einstein/GHY coefficient,

\[
\boxed{
S_{\rm GHY,+}+S_{\rm GHY,-}=0.
}
\]

Thus the equal internal GHY pair also provides no independent pure
fixed-background \(D^4\).

The same complementary-domain statement applies to lifted \(M_8\) preimages
if moving the seam merely reallocates one fixed parent density between two
complementary preimages.

This sharpens the target:

\[
\boxed{
\text{local positive }D^4
\text{ must come from dynamic field/metric deformation, not partitioning alone.}
}
\]

---

## 3. Exact two-sided DtN seam-shape response

Now consider the v14.30 constant positive mode,

\[
q=\sqrt{H}>0,
\]

with equal half-width \(L\).

Move the common seam uniformly by \(\delta\), preserving total width:

\[
L_+=L+\delta,
\qquad
L_-=L-\delta.
\]

The exact two-sided DtN response is

\[
\boxed{
N(\delta)
=
q\tanh[q(L+\delta)]
+
q\tanh[q(L-\delta)].
}
\]

It is automatically even,

\[
N(\delta)=N(-\delta).
\]

Set

\[
x=qL,
\qquad
t=\tanh x.
\]

The exact expansion is

\[
\boxed{
N(\delta)
=
2qt
-2q^3t(1-t^2)\delta^2
+
\frac23q^5t(1-t^2)(2-3t^2)\delta^4
+O(\delta^6).
}
\]

Thus the quadratic coefficient is always negative for \(q,L>0\):

\[
a_2^{\rm DtN}
=
-2q^3t(1-t^2)<0.
\]

This is consistent with the possibility identified in v14.76 that nonlocal
response can help drive a quadratic instability.

---

## 4. Exact quartic sign threshold

The fourth-order coefficient is

\[
\boxed{
a_4^{\rm DtN}
=
\frac23q^5t(1-t^2)(2-3t^2).
}
\]

Since

\[
q>0,\qquad0<t<1,
\]

its sign is controlled only by

\[
2-3t^2.
\]

Therefore

\[
a_4^{\rm DtN}>0
\]

precisely when

\[
\tanh^2(qL)<\frac23.
\]

The threshold is

\[
\boxed{
qL
=
\operatorname{artanh}\sqrt{\frac23}
\approx 1.1462158347805889.
}
\]

Hence

\[
\boxed{
0<qL<1.1462158348
\Rightarrow
a_4^{\rm DtN}>0,
}
\]

while

\[
qL>1.1462158348
\Rightarrow
a_4^{\rm DtN}<0.
\]

So the exact retained DtN architecture contains a mathematical
**positive shape-quartic regime**.

---

## 5. Why this does not contradict v14.76

v14.76 proved

\[
-\frac18B^TK^{-1}B\le0
\]

for integrating out stable interior fields while differentiating an otherwise
fixed bare action.

v14.77 is doing something different.

Here the operator itself depends on the moving domain:

\[
N=N[X].
\]

Differentiating \(N[X]\) with respect to the geometry can have either sign.

Therefore

\[
\boxed{
\text{negative elimination correction}
\neq
\text{sign of geometric DtN shape derivative}.
}
\]

There is no contradiction.

---

## 6. This is not the old DtN `c4`

The coefficient called `c4` in v14.30 belongs to

\[
N(z)=m_0+Zz+c_4z^2+\cdots
\]

as a momentum/derivative expansion at fixed geometry.

The present coefficient is

\[
\partial_\delta^4N(\delta)\big|_{\delta=0},
\]

a **shape/domain derivative**.

They are distinct mathematical derivatives of the same exact DtN object.

The v14.30 `c4` firewall therefore remains intact.

---

## 7. Why this is not yet \(u,v\)

The uniform displacement \(\delta\) is the \(\ell=0\)-like width direction.

The physical locking proposal concerns a nonuniform nine-component
\(\ell=2\) deformation.

For that calculation one must replace the scalar \(q\) by the full
operator-valued tangential block and differentiate the Calderón/Weyl map under
a nonuniform moving boundary.

That derivative must include:

- change of cap lengths;
- induced metric variation;
- variation of the tangential Berger operator;
- connection transport;
- gauge and constraint projectors;
- zero modes;
- noncommuting mode mixing.

Only then may the two invariant rays

\[
Q_A=\operatorname{diag}(1,0,0),
\qquad
Q_B=\operatorname{diag}(1,1,0)
\]

be evaluated and converted into \(u,v\).

So the result is

\[
\boxed{
\text{positive nonlocal shape }D^4\text{ exists as a mechanism},
}
\]

not

\[
\text{BHSM physical }v>0.
\]

---

## Hindsight 20/20 ledger

### VALIDATED

- Fixed-background equal-coefficient complementary bulk action is seam
  independent to every order.
- Equal internal GHY cancels on the ideal reflection branch.
- Fixed-parent complementary \(M_8\) domain reallocation is not an independent
  bare quartic source.
- Exact two-sided DtN seam-width response is even.
- Its quadratic shape coefficient is negative.
- Its quartic shape coefficient has an exact sign threshold.
- A positive DtN shape-quartic regime exists for thin enough \(qL\).
- This geometric shape derivative is distinct from v14.30's low-energy `c4`.

### INVALIDATED

- Pure fixed-background local cap-volume reallocation as the missing positive
  \(D^4\).
- Equal GHY as an independent positive \(D^4\).
- The assumption that every mathematically stable nonlocal response quartic
  must be non-positive.

### RECLASSIFIED

The bare-\(D^4\) search now separates into:

1. **local fixed-background domain motion:** zero;
2. **local dynamical metric/field response:** open;
3. **nonlocal domain/operator shape response:** demonstrably sign-indefinite
   and capable of being positive.

---

## Completion state

`FIXED_BACKGROUND_EQUAL_CAP_LOCAL_BULK_D4 = ZERO`

`FIXED_BACKGROUND_EQUAL_CAP_GHY_D4 = ZERO`

`UNIFORM_TWO_SIDED_DTN_SHAPE_D4 = SIGN_INDEFINITE`

`POSITIVE_THIN_CAP_DTN_REGION = VALIDATED`

`PHYSICAL_ELL2_DTN_D4 = OPEN`

`PHYSICAL_R_U_V = OPEN`

`PHYSICAL_LOCKING_GATE = UNDECIDED`

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

No physical particle/flavor observable is emitted.
