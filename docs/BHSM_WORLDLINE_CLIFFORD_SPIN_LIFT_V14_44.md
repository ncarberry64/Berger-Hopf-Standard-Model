# BHSM v14.44 — Worldline Clifford and parent spin-lift audit

## Question

Can the retained Path B eta action, its bosonic collective-coordinate mechanics,
and the flat Finkelstein–Rubinstein sign line generate the local first-order
spacetime Dirac operator needed for the v14.42 vacuum-polarization program?
If not, can the existing parent geometry at least select the core–wall spinor
matcher and the spinor-harmonic branches entering the `L=2,3` Kosmann vertex?

## 1. Bosonic collective mechanics does not contain an odd supercharge

The retained collective reduction has the bosonic normal form

\[
L_{\rm mod}
=
-M_\eta+\frac12G_{AB}(q)\dot q^A\dot q^B+\cdots .
\]

Its canonical Hamiltonian has scalar principal symbol

\[
H_{\rm mod}^{(2)}
=
\frac12G^{AB}p_Ap_B\,I.
\]

The FR line changes the allowed global holonomy of wavefunctions around a
nontrivial loop. It does not add Grassmann variables, an odd symplectic form, or
an odd Noether charge. Hence it cannot alter the local scalar principal symbol
into a Clifford-linear one.

The minimal `N=1` supersymmetric completion on the moduli space would be

\[
S_{\rm SQM}
=
\int dt\left[
\frac12G_{AB}\dot q^A\dot q^B
+\frac i2G_{AB}\psi^A D_t\psi^B
\right],
\]

with

\[
Q_{\rm mod}=\psi^A\pi_A,
\qquad
Q_{\rm mod}^2=H_{\rm mod}
\]

up to the standard connection and curvature completion. Quantization yields a
Hodge–Dirac operator on forms over configuration/moduli space.

This is a valid coefficient-fixed square root **after** the odd variables are
adjoined. Those odd variables are not present in the Path B action. The result
is therefore a candidate supersymmetric extension, not an action-derived BHSM
fermion sector.

## 2. Spacetime spinning particle is a distinct extension

A first-quantized spacetime Dirac constraint follows from a locally
supersymmetric spinning-particle action containing

\[
x^\mu(\tau),\quad \psi^a(\tau),\quad e(\tau),\quad \chi(\tau).
\]

Its odd constraint is

\[
Q_{M_4}
=
\psi^a e_a{}^\mu\pi_\mu,
\]

and canonical quantization sends

\[
\psi^a\longmapsto \frac1{\sqrt2}\gamma^a,
\]

so `Q_{M4} Psi=0` is the local Dirac equation.

The FR line can tensor this spinor bundle and supply the global `-1` holonomy of
the odd sector. It still does not generate the local `psi^a`, the worldline
gravity multiplet `(e,chi)`, or the Clifford module.

Therefore the shortest honest routes are:

1. explicitly adopt a foundational local fermion/spinning-particle action; or
2. derive an odd collective sector from a larger parent action containing the
   necessary graded variables.

The present bosonic Path B action does neither.

## 3. Product superconnection theorem

If a local spacetime Dirac operator `D_M4` and the moduli Hodge–Dirac `D_mod`
are both independently available, define

\[
\mathbb D
=
D_{M_4}\otimes1
+\Gamma_{M_4}\otimes D_{\rm mod},
\]

where

\[
\{\Gamma_{M_4},D_{M_4}\}=0.
\]

Then

\[
\boxed{
\mathbb D^2
=
D_{M_4}^2\otimes1
+1\otimes D_{\rm mod}^2.
}
\]

This is a clean superconnection architecture. It proves that the FR/moduli
sector and the local spacetime spinor sector can coexist without a mixed
principal-symbol ambiguity.

It does **not** derive `D_M4` from `D_mod`. The two operators live over different
base spaces and retain different principal symbols.

## 4. Full Clifford seam matching

The v14.43 normal-current condition required

\[
U_{cw}^\dagger\alpha_n^{w}U_{cw}
=
\alpha_n^{c}.
\]

For a four-component complex spinor, the normal symbol has two positive and two
negative eigenspaces. Its complex commutant has dimension eight, corresponding
to the unitary class

\[
U(2)_+\times U(2)_-.
\]

This condition is necessary for self-adjoint flux cancellation but is too weak
to select a physical seam identification.

Require instead full Clifford compatibility:

\[
U_{cw}\,c_c(v)
=
c_w(\Lambda v)\,U_{cw}
\qquad
\text{for every retained Clifford vector }v.
\]

For an irreducible complex spacetime Clifford module, Schur's lemma gives

\[
\operatorname{Comm}_{\mathbb C}(\mathrm{Cl}_{1,3})
=
\mathbb C I.
\]

The implemented matrix audit finds

\[
\dim_{\mathbb C}\operatorname{Comm}(\alpha_n)=8,
\qquad
\dim_{\mathbb C}\operatorname{Comm}(\gamma^0,\gamma^1,\gamma^2,\gamma^3)=1.
\]

Thus full Clifford compatibility reduces the spinor matcher to one common
phase before gauge, FR, and family factors are included.

### Parent spin-lift theorem

Suppose the core and wall coframes are restrictions of one oriented,
time-oriented parent spin coframe, and let `Lambda` be their seam Lorentz-frame
map. Then

\[
U_{cw}=\rho(\widetilde\Lambda)
\]

for a spin lift `widetilde Lambda`, unique up to the double-cover sign. A fixed
global spin structure on a connected seam fixes that lift up to one overall
common sign/phase.

This is the correct mechanism for selecting the spin part of the matcher.
However, the retained parent action is expressed in metric variables and does
not yet provide the matched parent coframe and its spin lift. Metric continuity
alone therefore does not close the matcher-selection gate.

Moreover, a universal spin lift acts identically on the three family slots. It
is family central and cannot generate CKM by itself. Any physical relative
flavor holonomy must come from noncentral gauge/attachment/response data rather
than the universal spin lift.

## 5. Spinor branch audit for the orbital `L=2,3` library

The orbital Berger blocks used by v12.1 must be tensored with spin `1/2`:

\[
j\otimes\frac12
=
\left(j-\frac12\right)\oplus\left(j+\frac12\right).
\]

For an orbital tensor `T^(L)`, the reduced spinor factor is

\[
\begin{aligned}
&\langle(j_t,\tfrac12)\mathcal J_t
\Vert T^{(L)}\Vert
(j_s,\tfrac12)\mathcal J_s\rangle\\
&=
(-1)^{j_t+1/2+\mathcal J_s+L}
\sqrt{(2\mathcal J_t+1)(2\mathcal J_s+1)}
\begin{Bmatrix}
 j_t&\mathcal J_t&\tfrac12\\
 \mathcal J_s&j_s&L
\end{Bmatrix}
\langle j_t\Vert T^{(L)}\Vert j_s\rangle.
\end{aligned}
\]

The exact branch audit gives:

- both heavy–middle `L=3` spinor branches are nonzero;
- the up middle–light `j=3 -> 5`, `L=2` edge has three nonzero branch pairs and
  one exact zero:

\[
\mathcal J_s=\frac52
\longrightarrow
\mathcal J_t=\frac{11}2;
\]

- all four down middle–light `j=3 -> 4`, `L=2` branch pairs are nonzero.

Hence the orbital-tensor part supports

\[
3\times4=12
\]

connected combined up/down branch choices out of sixteen.

This is not yet the full Kosmann result. The spin-connection term

\[
-\frac i4(D_i\beta_j)\gamma^{ij}
\]

has its own reduced elements, and the radial/collar integrals, chirality,
normalization, coexact harmonic norm, and selected seam matcher are still
missing.

## 6. Consequence for the determinant route

The v14.42 nonpositive filled-sea transition theorem remains valid for any
completed self-adjoint Dirac Hamiltonian. This sprint does not supply that
Hamiltonian from the bosonic action.

The determinant cannot be evaluated by inserting the conditional v14.5 normal
form as though it were action-derived. The required promotion is now explicit:

1. add or derive the graded worldline/local-fermion action;
2. obtain the parent spin coframe and seam spin lift;
3. select normalized spinor-harmonic branches;
4. calculate both orbital and spin pieces of the `L=2,3` Kosmann matrix
   elements;
5. only then perform the regulated vacuum-polarization sum and renormalized
   zero-crossing test.

## Verdicts

Primary:

`BHSM_BOSONIC_PATH_B_FR_DATA_DO_NOT_GENERATE_THE_GRASSMANN_WORLDLINE_VARIABLES_OR_LOCAL_SUPERCHARGE_REQUIRED_FOR_A_SPACETIME_DIRAC_OPERATOR`

Secondary:

`FULL_CLIFFORD_SEAM_COMPATIBILITY_REDUCES_THE_CORE_WALL_MATCHER_TO_A_COMMON_PHASE_TIMES_RETAINED_BUNDLE_INTERTWINERS_BUT_DOES_NOT_SELECT_RELATIVE_FLAVOR_HOLONOMY`

Spinor branch:

`THE_ORBITAL_L2_L3_LIBRARY_HAS_TWELVE_OF_SIXTEEN_CONNECTED_SPINOR_BRANCH_PAIRS_BEFORE_THE_KOSMANN_SPIN_TERM_AND_RADIAL_REDUCTION_ARE_INCLUDED`

## Hindsight 20/20

### Validated

- `N=1` worldline supersymmetry provides a coefficient-fixed first-order square
  root after odd variables are introduced.
- The canonical moduli Hodge–Dirac acts on the wrong base for the physical
  spacetime fermion.
- The graded product superconnection squares without cross terms.
- Full Clifford compatibility reduces the seam commutant from complex
  dimension eight to one.
- A parent spin coframe would select the spin lift up to a common sign/phase.
- Twelve of sixteen orbital-tensor spinor-branch choices remain connected.

### Invalidated

- FR parity as a generator of local gamma matrices.
- Deriving worldline Grassmann variables from the current bosonic action merely
  by taking a formal square root.
- Treating normal-current matching as a unique seam matcher.
- Treating the universal parent spin lift as a source of relative family
  holonomy.
- Treating the orbital recoupling table as the complete Kosmann determinant
  vertex.

### Open

- Foundational or parent-derived graded fermion action.
- Parent coframe and spin-lift attachment.
- Gauge/FR/family seam intertwiners.
- Spinor branch selection and normalized radial/collar modes.
- Complete `L=2,3` Kosmann reduced matrix elements.
- Renormalized determinant crossing, CKM, CP, masses, and full completion.

## Completion status

BHSM is not complete. Frozen predictions are unchanged. No determinant,
`Pi_2`, `Pi_3`, CKM matrix, CP phase, mass, coupling, radius, or dimensional
scale is emitted. The USB remains untouched.
