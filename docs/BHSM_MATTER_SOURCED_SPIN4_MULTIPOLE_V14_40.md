# BHSM v14.40 — Matter-Sourced Spin(4) Multipole and Universality Audit

## Primary verdict

`BHSM_RIGID_FR_ETA_ROTOR_STATIC_WILSON_INSERTIONS_AND_DIAGONAL_FAMILY_OCCUPATIONS_DO_NOT_SUPPLY_THE_UNIVERSAL_CONNECTED_L2_L3_COEXACT_SHIFT_REQUIRED_FOR_CKM`

## Secondary verdict

`OFF_DIAGONAL_FAMILY_COHERENCE_CAN_KINEMATICALLY_SOURCE_THE_REQUIRED_SPIN4_CHANNELS_BUT_USING_SUCH_COHERENCE_TO_DERIVE_MIXING_IS_CIRCULAR_UNTIL_THE_COLLECTIVE_DIRAC_ACTION_AND_BACKGROUND_STATE_ARE_ACTION_SELECTED`

## 1. Question

v14.39 proved that the static degree-one eta background has zero ADM momentum density. The shortest proposed continuation was therefore a fermion-, Wilson-, or collective-rotation-sourced coexact shift with the `L=2` and `L=3` components required by the v12.1 Spin(4) family-selection theorem.

This audit asks whether any presently owned source actually supplies those components and whether the resulting backreaction could define a universal CKM geometry.

## 2. Compact-cap momentum equation

After gauge fixing and projection onto divergence-free one-forms, the required equation has the form

\[
\mathcal L_{\rm shift}\,\beta_i^\perp
=\kappa_{\rm grav}\,P_{\rm coex}J_i^{\rm total}.
\]

For normalized coexact harmonics,

\[
\beta_{Lr}^{\epsilon}
=
\frac{\kappa_{\rm grav}}{\lambda_L^{\rm shift}}
J_{Lr}^{\epsilon}.
\]

BHSM does not yet possess the physical compact-cap eigenvalues, seam conditions, normalized source, or matched tetrad. The current step is therefore a source-character theorem, not a numerical shift solution.

## 3. Rigid FR eta rotor

The v13.3 eta-knot construction supplies a finite collective inertia and permits a time-dependent orientation coordinate. Such a rotor can carry nonzero momentum, unlike the static branch.

For the currently constructed radially equivariant degree-one profile,

\[
\eta=(\cos f,\sin f\,n),
\]

and a constant target-plane generator `T_ab`, the source one-form is

\[
\langle T_{ab}\eta,d\eta\rangle
=c(r)K_{ab}^{\flat},
\]

where `K_ab` is the angular Killing vector. Hence the rigid rotor source has only

\[
\boxed{L=1}.
\]

It can produce rigid frame dragging, but v12.1 already proved that `L=1` is family diagonal. The rotor does not activate the required connected `L=2\oplus L=3` family graph. Higher multipoles require a nonaxisymmetric collective deformation that the action has not selected.

## 4. Stationary fermion source

For a local Dirac normal form, the symmetric stress tensor gives a momentum density schematically

\[
J_i^{\psi}
=-n^\mu h_i{}^\nu T_{\mu\nu}^{\psi},
\qquad
T_{\mu\nu}^{\psi}
=\frac{i}{4}\bar\psi\gamma_{(\mu}
\overleftrightarrow D_{\nu)}\psi.
\]

A stationary spinning state can have nonzero `J_i`; this route is not identically zero. But the physical collective Dirac action, normalized one-knot Hilbert bundle, and self-adjoint domain remain underived.

There is an additional exact family-selection obstruction. For an irreducible tensor source,

\[
\langle J_t m_t|T_r^{(L)}|J_s m_s\rangle\neq0
\quad\Rightarrow\quad
r=m_t-m_s.
\]

A diagonal occupation density contains only `t=s`, hence

\[
\boxed{r=0\text{ only}.}
\]

The v12.1 connected edges require

\[
\begin{array}{c|c|c}
\text{sector}&\text{edge}&(L,r)\\ \hline
u\text{-type up}&H\leftrightarrow M&(3,3)\\
& M\leftrightarrow L&(2,1)\\
\text{down}&H\leftrightarrow M&(3,0)\\
& M\leftrightarrow L&(2,2)
\end{array}
\]

so diagonal stationary occupations can support only the down-sector heavy-middle `r=0` edge. Neither sector forms a connected three-slot graph.

Off-diagonal density-matrix entries can carry `r=3,1,2`, but inserting those coherences before the collective action or response operator selects them assumes the family superposition that CKM is intended to explain. That is circular.

## 5. Wilson source

The Wilson loop

\[
W(C)=\frac13\operatorname{Tr}\,\mathcal P
\exp\left(i\oint_C A\right)
\]

is a gauge-invariant observable. It is not by itself a dynamical worldline or string action. A distributional stress tensor requires an owned dynamical source action and variation of its embedding.

In the ideal static color-electric branch,

\[
T_{0i}^{\rm YM}\propto(E\times B)_i=0,
\]

so a static Wilson source does not generate a coexact shift. A rotating loop or flux tube may carry momentum, but its angular velocity, contour, and orientation are external state or boundary data.

## 6. Universality obstruction

CKM is a universal interaction-basis mismatch. A metric shift

\[
\beta=\beta[\rho_{\rm state},C_{\rm loop}]
\]

that changes with the occupied hadron, spin orientation, or prescribed Wilson contour is state-dependent gravitational backreaction. It cannot by itself define one universal CKM matrix.

A universal route would require one of:

1. an action-selected family-independent nonaxisymmetric relative-frame background;
2. a collective-fermion effective action whose vacuum determinant generates a universal `L=2,L=3` kernel;
3. a compact-cap stationary geometry with nonzero coexact background selected without external occupation data.

None is presently derived.

## 7. Hindsight 20/20

### Validated

- Time-dependent eta collective rotation can carry momentum.
- The current equivariant eta rotor supplies only an `L=1` Killing source.
- Diagonal family occupations carry only `r=0`.
- Off-diagonal family bilinears can kinematically carry the required transfers.
- Static Wilson observables do not supply a universal coexact momentum source.

### Invalidated

- Rigid FR rotor frame dragging as the missing `L=2,L=3` background.
- Static Wilson insertion as the missing Spin(4) source.
- Diagonal stationary family occupation as a connected three-generation source.

### Reclassified

- Off-diagonal fermion coherence is a possible downstream state response, not an upstream explanation until selected by an action-owned collective operator.
- Matter-sourced frame dragging is state-dependent and cannot automatically be identified with universal flavor geometry.

### Open

- A family-independent action-selected nonaxisymmetric relative frame.
- Collective Dirac action and determinant on the compact cap.
- Matched tetrad and spin connection.
- Normalized common-domain Dirac modes.
- Action-derived up/down responses, CKM and CP.

## Exact next object

`ACTION_DERIVED_FAMILY_INDEPENDENT_NONAXISYMMETRIC_RELATIVE_FRAME_BACKGROUND_OR_COLLECTIVE_FERMION_EFFECTIVE_ACTION_WITH_L2_L3_COEXACT_COMPONENTS_ON_THE_COMPACT_CAP_MATCHED_TO_THE_TETRAD_SPIN_CONNECTION`

BHSM remains incomplete. Frozen predictions are unchanged. No physical CKM, CP phase, mass, scale, or compact-cap eigenvalue is emitted.
