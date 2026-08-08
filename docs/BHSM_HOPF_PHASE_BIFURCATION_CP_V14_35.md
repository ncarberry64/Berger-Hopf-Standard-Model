# BHSM v14.35 Hopf-phase bifurcation and CP-selection audit

## Primary verdict

```text
BHSM_V14_35_MINIMAL_FOUR_COMPONENT_MIXING_SEED_AND_FIVE_COMPONENT_CABIBBO_CP_TEXTURE_ARE_DERIVED_KINEMATICALLY_BUT_THE_PATH_B_ACTION_HAS_NOT_SELECTED_THE_NONAXISYMMETRIC_BIFURCATION_BRANCH_OR_SELF_ADJOINT_TOWER_RESOLVENT
```

Secondary verdict:

```text
THE_MARK_III_FLAVOR_GATE_IS_REDUCED_TO_THE_DEGREE_ONE_FULL_PREIMAGE_HESSIAN_SPECTRUM_PHASE_LOCKING_NORMAL_FORM_AND_ACTION_ATTACHMENT_OF_THE_EXISTING_RELATIVE_HOLONOMY_CHANNEL
```

No physical CKM matrix, CP phase, Jarlskog invariant, quark mass, or fitted coefficient is emitted.

## 1. Minimal mixing seed and Cabibbo-aligned CP extension

The frozen up and down Hopf weights are

\[
q_u=(8,6,0),\qquad q_d=(4,0,0),
\]

in the ordered bases \(u,c,t\) and \(d,s,b\). A bridge component
\((\ell,p)\) can contribute only if

\[
p=q_i^{(u)}-q_j^{(d)},
\]

\[
|k_i^{(u)}-k_j^{(d)}|\leq \ell\leq k_i^{(u)}+k_j^{(d)},
\]

with weight and parity compatibility.

An exhaustive search over all allowed frozen-ledger bridge components proves
that **four components are the minimum** for connected structural rank three.
The lowest-total-\(\ell\) representative is

\[
\boxed{(\ell,p)=(0,0),(2,2),(6,6),(10,8).}
\]

It has support

\[
K_{\rm mix}=\begin{pmatrix}
0&a_{8}^{(s)}&a_{8}^{(b)}\\
a_{22}&a_{66}^{(s)}&a_{66}^{(b)}\\
0&0&a_{00}
\end{pmatrix}.
\]

This seed is connected and generically full rank. However, its only graph
cycle uses the same \((10,8)\) amplitude on both up-row edges and the same
\((6,6)\) amplitude on both charm-row edges. With real Clebsch/radial
coefficients, the cycle phase cancels. It can generate nontrivial mixing but
not a physical CP phase at the one-amplitude-per-harmonic level.

A Cabibbo-aligned CP-capable extension is

\[
\boxed{(\ell,p)=(0,0),(2,2),(4,4),(6,6),(8,8).}
\]

Its normal form is

\[
\boxed{
K_{\rm CP}=\begin{pmatrix}
a_{44}&a_{88}&0\\
a_{22}&a_{66}^{(s)}&a_{66}^{(b)}\\
0&0&a_{00}
\end{pmatrix}.
}
\]

The same \((6,6)\) component contributes to both \(c\to s\) and
\(c\to b\), connecting the Cabibbo phase cycle to the third generation.
The determinant is

\[
\boxed{
\det K_{\rm CP}=a_{00}\left(a_{44}a_{66}^{(s)}-a_{88}a_{22}\right).
}
\]

Hence full rank is generic once the action produces nonzero amplitudes and
avoids the one algebraic cancellation surface. This five-component set is a
sufficient Cabibbo-aligned CP texture; global minimality is not claimed when
overlapping higher harmonics are allowed.

## 2. The physical phase invariant

The cycle phase is

\[
\boxed{
\Phi=\arg\!\left(K_{ud}K_{cs}K_{us}^{*}K_{cd}^{*}\right).
}
\]

It is invariant under independent up- and down-field rephasings. The associated
Hopf weights obey

\[
\boxed{4+6=8+2.}
\]

Thus the phase quartet is also a weight-neutral harmonic resonance. The
symmetry-reduced action is allowed to depend on \(\Phi\).

A generic CP-even phase normal form is

\[
V(\Phi)=c_1\cos\Phi+c_2\cos2\Phi+\cdots.
\]

One cosine alone locks \(\Phi\) to \(0\) or \(\pi\), which is CP conserving.
With competing terms,

\[
c_2>0,\qquad |c_1|<4c_2,
\]

gives the stable conjugate pair

\[
\cos\Phi=-\frac{c_1}{4c_2},\qquad \Phi\leftrightarrow-\Phi.
\]

Therefore a real action can support spontaneous CP breaking, but it does not
choose the sign of the phase without an oriented boundary condition or
holonomy. The coefficients \(c_1,c_2\) have not been computed from BHSM.

## 3. Why the current action has not selected the texture

Assume a smooth axisymmetric degree-one full-preimage stationary background.
Because it preserves the fiber \(U(1)\) symmetry, orthogonality removes linear
forcing in every nonzero-weight channel. Its self-adjoint Hessian decomposes
into angular blocks

\[
\mathcal H_*\simeq\bigoplus_{\ell,p}\mathcal H_{\ell,p}.
\]

A nonaxisymmetric flavor branch requires at least one of the relevant blocks

\[
(\ell,p)=(2,2),(4,4),(6,6),(8,8),(10,8)
\]

to satisfy one of the following:

1. a zero eigenvalue at an equivariant bifurcation;
2. a negative mode producing a nonlinear instability branch;
3. an explicit action-owned nonaxisymmetric boundary/source term.

If all relevant lowest eigenvalues are positive, the axisymmetric branch is
locally stable and does not produce the required texture.

The repository has not constructed the degree-one full-preimage stationary
solution, its self-adjoint cap domain, or this Hessian spectrum. The previously
validated constant-background Hessian cannot answer the flavor-bifurcation
question.

## 4. Exact finite-truncation obstruction

The Path-B eta equation contains

\[
\nabla_\mu\left[(\kappa_1+X^3)D^\mu\eta\right],
\qquad X=|D\eta|^2.
\]

The nonlinear \(X^3D\eta\) term contains seven harmonic factors. The mixing
seed starts from weights \(\{0,2,6,8\}\), while the CP texture starts from
\(\{0,2,4,6,8\}\). Both first generic nonlinear iterates produce

\[
\boxed{
\{-24,-22,\ldots,30,32\}.
}
\]

For the four-component mixing seed, \(\ell_{\max}=10\) and the generic
first-iterate bound is \(70\). For the Cabibbo CP texture,
\(\ell_{\max}=8\) and the bound is \(56\).

Therefore neither the four-component mixing seed nor the five-component CP
texture is an exact finite consistent truncation. They are finite diagnostic
seeds for the full tower. A physical reduction
requires the full self-adjoint tower or a proved invariant subspace.

The Feshbach map is legitimate only after proving

\[
E\in\rho(H_{QQ}),
\]

so that \((H_{QQ}-E)^{-1}\) exists on the declared domain.

## 5. Existing relative-holonomy route

The recovered BHSM lineage already contains conditional relative-rotation
channels, noncommuting up/down response witnesses, and a CP-odd relative
holonomy. This is the natural candidate for orienting the conjugate phase pair
without adding a new phase field.

It still requires:

- pullback to the Path-B/full-preimage common domain;
- action-normalized coupling to the mixing/CP harmonic amplitudes;
- the mixed second variation defining the up/down cross-Gram orientation;
- compatibility with the cap domain, tower resolvent, and no-double-counting
  subtraction.

Until this attachment is derived, the holonomy remains a conditional source,
not the physical CKM phase.

## 6. Hindsight 20/20 ledger

### Validated

- Four harmonic components are the exhaustive minimum for a connected,
  structurally full-rank mixing kernel; the five-component Cabibbo-aligned
  extension supplies an independent phase cycle.
- Their support has one independent rephasing cycle.
- The cycle phase is weight neutral through \(4+6=8+2\).
- A CP-even action with competing phase-locking terms can support conjugate
  nontrivial phases.
- The minimal texture necessarily generates an omitted nonlinear tower.

### Invalidated

- The v14.34 selection-rule proxy is already an action-selected CKM result.
- The four- or five-component harmonic seeds form an exact finite solution space.
- One real cosine interaction generates a physical CP phase.
- The constant-background Hessian establishes a nonaxisymmetric flavor branch.

### Open

- The degree-one full-preimage stationary background and self-adjoint cap
  domain.
- The \((2,2),(4,4),(6,6),(8,8),(10,8)\) Hessian spectra.
- Existence and stability of the nonaxisymmetric branch.
- Phase-locking coefficients and orientation selection.
- Action attachment of the conditional relative holonomy.
- Full tower resolvent, dressed embeddings, cross-Gram kernel, CKM and CP.

## Exact next object

```text
SELF_ADJOINT_DEGREE_ONE_FULL_PREIMAGE_HESSIAN_SPECTRUM_IN_ELL_P_CHANNELS_2_2_4_4_6_6_8_8_10_8_WITH_EQUIVARIANT_BIFURCATION_PHASE_LOCKING_AND_V12_RELATIVE_HOLONOMY_ACTION_ATTACHMENT
```

BHSM remains incomplete. Frozen predictions are unchanged.
