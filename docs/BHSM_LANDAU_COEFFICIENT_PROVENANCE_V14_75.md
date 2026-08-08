# BHSM v14.75 — \(\ell=2\) Landau Coefficient Provenance and Fourth-Variation Gate

## Executive result

v14.74 reduced the possible three-channel locking phase to a clean no-fit
test,

\[
r<0,\qquad v>0,\qquad 3u+v>0,
\]

for

\[
V(Q)=\frac r2 I_2+\frac u4I_2^2+\frac v4I_4,
\]

with

\[
I_2=\operatorname{Tr}(Q^TQ),
\qquad
I_4=\operatorname{Tr}[(Q^TQ)^2].
\]

v14.75 attacks the coefficients themselves.

The result has two parts:

1. one complete geometric fourth-order contribution can be calculated exactly;
2. the physical BHSM coefficients still cannot be obtained from the current
   authoritative archive because the required global \(D^3\Gamma\) and
   \(D^4\Gamma\) tensors do not exist there.

The exact geometric contribution is the round-equator normal-graph area
functional.  It gives

\[
\boxed{
r_{\rm area}=\frac53,\qquad
u_{\rm area}=-\frac{83}{15},\qquad
v_{\rm area}=\frac{43}{30}.
}
\]

It does **not** trigger the v14.74 phase:

\[
r_{\rm area}>0,
\]

and

\[
\boxed{
3u_{\rm area}+v_{\rm area}
=
-\frac{91}{6}<0.
}
\]

So the simple round-area geometry stabilizes the round seam at quadratic
order and its quartic truncation is not in the locked-phase stability cone.

Crucially, this is not promoted to the full BHSM result.  The authoritative
stratified action does not contain an independently declared seam-tension
area term, and several other action sectors contribute to the actual shape
effective action.

---

## 1. Exact \(\ell=2\) Haar moment calculus

Represent the real \(\ell=2\) harmonic by

\[
f_Q(q)
=
\operatorname{Tr}(Q^T R(q)),
\]

where \(q\in SU(2)\simeq S^3\) and \(R(q)\in SO(3)\) is the adjoint rotation.

With normalized Haar measure,

\[
\langle f_Q^2\rangle
=
\frac13I_2.
\]

Because \(\ell=2\),

\[
-\Delta f_Q=8f_Q,
\]

so

\[
\langle|\nabla f_Q|^2\rangle
=
\frac83I_2.
\]

The exact quartic identities are

\[
\boxed{
\langle f_Q^4\rangle
=
\frac{2I_2^2-I_4}{5},
}
\]

\[
\boxed{
\langle
f_Q^2|\nabla f_Q|^2
\rangle
=
\frac8{15}(2I_2^2-I_4),
}
\]

and

\[
\boxed{
\langle|\nabla f_Q|^4\rangle
=
\frac{176}{15}I_2^2
-\frac{16}{5}I_4.
}
\]

These identities are encoded directly in the executable artifact.

---

## 2. Round-equator normal-graph area

For a unit \(S^4\),

\[
ds^2=d\chi^2+\sin^2\chi\,ds_{S^3}^2.
\]

Write a normal graph as

\[
\chi
=
\frac\pi2+t f.
\]

The induced area density, normalized by the round equatorial density, is

\[
\cos^3(tf)
\sqrt{
1+\sec^2(tf)t^2|\nabla f|^2
}.
\]

Its expansion is

\[
1
+t^2
\left[
\frac12|\nabla f|^2-\frac32f^2
\right]
\]

\[
+t^4
\left[
\frac78f^4
-\frac14f^2|\nabla f|^2
-\frac18|\nabla f|^4
\right]
+O(t^6).
\]

On the \(\ell=2\) sector the quadratic coefficient is

\[
\frac56I_2,
\]

so in Landau normalization

\[
\frac r2I_2
\]

we obtain

\[
\boxed{r_{\rm area}=\frac53.}
\]

Using the Haar moments, the quartic coefficient is

\[
-\frac{83}{60}I_2^2
+\frac{43}{120}I_4.
\]

Hence

\[
\boxed{
u_{\rm area}=-\frac{83}{15},
\qquad
v_{\rm area}=\frac{43}{30}.
}
\]

The implementation checks four independent invariant rays exactly.

For a physical sphere of radius \(a\), the complete area carries the expected
overall factor \(2\pi^2a^3\), together with any action-owned coefficient.
That overall multiplier does not change the dimensionless sign pattern.

---

## 3. This does not equal the physical BHSM \(r,u,v\)

This distinction is essential.

The v7.1 authoritative architecture owns separate:

- \(M_8\) parent action;
- two \(M_5\) cap actions;
- GHY completion;
- intrinsic localized \(M_4\) action;
- compatibility/KKT system.

Their Wilson data are independently typed.

There is no separate retained seam-tension term whose coefficient licenses us
to identify the normal-graph area functional with the full physical action.

Thus the exact result above is classified as

\[
\boxed{
\text{GEOMETRIC JACOBI/AREA WITNESS},
}
\]

not

\[
\text{PHYSICAL BHSM LANDAU COEFFICIENTS}.
\]

---

## 4. Why the Hessian is insufficient

A more important correction emerged from pushing the effective-action
calculation to fourth order.

Work after the quadratic boundary/interior Schur reduction.  Let \(x\) be the
physical \(\ell=2\) shape coordinate and \(y\) an eliminated interior field.

Write

\[
\Gamma
=
\frac12r(x,x)
+
\frac12\langle y,Ky\rangle
+
\frac12\langle y,B(x,x)\rangle
+
\frac1{24}T_4(x,x,x,x)+\cdots .
\]

The interior equation gives

\[
y_\star
=
-\frac12K^{-1}B(x,x)+O(x^3).
\]

For \(x=tq\),

\[
\boxed{
a_{4,\mathrm{eff}}(q)
=
\frac1{24}T_4(q,q,q,q)
-
\frac18
B(q,q)^T K^{-1}B(q,q).
}
\]

When \(K\) is positive on the eliminated physical complement, the second term
is non-positive.

Therefore the physical quartic action does not depend only on the bare fourth
variation.

It also depends on

\[
\boxed{D^3\Gamma.}
\]

This means the previous quadratic Hessian work cannot possibly determine
\(u\) and \(v\) by itself.

The deterministic finite-dimensional witness reproduces the formula by direct
substitution to machine precision.

---

## 5. Exact coefficient extractor

Once the physical action is evaluable, there is no ambiguity in extracting the
three Landau coefficients.

Choose

\[
Q_A=\operatorname{diag}(1,0,0),
\]

for which

\[
I_2=1,\qquad I_4=1.
\]

If

\[
\Gamma(tQ_A)
=
a_{2A}t^2+a_{4A}t^4+\cdots,
\]

then

\[
a_{2A}=\frac r2,
\qquad
a_{4A}=\frac{u+v}{4}.
\]

Next choose

\[
Q_B=\operatorname{diag}(1,1,0),
\]

with

\[
I_2=2,\qquad I_4=2.
\]

Then

\[
a_{2B}=r,
\]

and

\[
a_{4B}=u+\frac v2.
\]

Therefore

\[
\boxed{
r=2a_{2A}=a_{2B},
}
\]

\[
\boxed{
u=2a_{4B}-4a_{4A},
}
\]

\[
\boxed{
v=8a_{4A}-2a_{4B}.
}
\]

This extraction map is implemented and reconstructs the exact area witness
with zero numerical ambiguity.

It is ready for the physical action once the missing variations exist.

---

## 6. GHY clarification

On an exactly smooth reflection-related two-cap gluing,

\[
n_-=-n_+,
\]

and hence

\[
K_-=-K_+.
\]

With the same induced metric and equal reflection-related Einstein/GHY
coefficient,

\[
S_{\rm GHY,+}+S_{\rm GHY,-}=0.
\]

So on that ideal branch GHY acts as variational completion rather than an
independent seam-tension potential.

If the two cap coefficients or geometries differ, this cancellation cannot be
used and the full variation must be evaluated.

---

## 7. Repository provenance gate

The current archive prevents the remaining calculation from being filled in
by inference.

The v14.29 View-2 master-action audit records

\[
\boxed{\text{authoritative action}=\texttt{None}}
\]

for that common-domain candidate and explicitly states that the
\(M_8\)-to-collar reduction remains missing.

The v14.30 matching audit separately marks the nonlinear parent \(p=8\)
coefficient/reduction as

\[
\boxed{\texttt{NOT\_DERIVED}}.
\]

That matters because a nonlinear fourth-order reduction is exactly what the
Landau \(u,v\) calculation needs.

So the present status is

\[
\boxed{
r_{\rm BHSM}=\text{OPEN},\quad
u_{\rm BHSM}=\text{OPEN},\quad
v_{\rm BHSM}=\text{OPEN}.
}
\]

No placeholder or proxy values are inserted.

---

## 8. Hindsight 20/20 ledger

### VALIDATED

- Exact \(\ell=2\) Haar moments through fourth order.
- Exact round-equator area contribution through fourth order.
- \(r_{\rm area}=5/3\).
- \(u_{\rm area}=-83/15\).
- \(v_{\rm area}=43/30\).
- Area contribution fails the locking cone.
- Exact two-ray coefficient extraction.
- Effective quartics require cubic response tensors.
- Positive-complement interior elimination lowers the quartic ray coefficient.
- Equal-cap GHY cancellation on the ideal reflection-symmetric gluing.

### INVALIDATED

- Pure round-area geometry drives the v14.74 locked phase.
- The known Hessian is sufficient to compute physical \(u,v\).
- The v14.29 eta \(p2+p8\) candidate can simply be reinterpreted as the seam
  Landau action.
- The structural existence of the locking phase means BHSM has entered it.

### RECLASSIFIED

The coefficient blocker is now

\[
\boxed{
D^2\Gamma+D^3\Gamma+D^4\Gamma,
}
\]

not merely the second-shape Hessian.

The no-fit phase test itself is complete; the physical inputs to the test are
what remain absent.

---

## 9. Exact next object

Evaluate on **one globally stationary full-preimage background**:

\[
D^2\Gamma_{\rm BHSM},
\qquad
D^3\Gamma_{\rm BHSM},
\qquad
D^4\Gamma_{\rm BHSM},
\]

including

\[
S_8,\quad
S_{5,+}+S_{5,-},\quad
S_{\rm GHY},\quad
S_{4,\rm localized},\quad
S_{\rm compatibility/KKT},\quad
\Gamma_{\rm nonlocal}.
\]

Then eliminate the physical interior complement and evaluate the two invariant
rays above.

Only then can the no-fit question

\[
\boxed{
r<0,\qquad
v>0,\qquad
3u+v>0
}
\]

be answered.

---

## Completion state

`GEOMETRIC_AREA_R_U_V = DERIVED`

`GEOMETRIC_AREA_LOCKING_CONE = FAIL`

`PHYSICAL_BHSM_R_U_V = OPEN`

`PHYSICAL_LOCKING_GATE = UNDECIDED`

`PHYSICAL_EXECUTION = BLOCKED`

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

No physical mass, mixing matrix, splitting, coupling, width, or probability is
emitted.
