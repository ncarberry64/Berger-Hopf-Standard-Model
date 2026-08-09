# BHSM v15.4 foundational event algebra, positive state, and GNS gate

Primary verdict:

`BHSM_V15_4_EVENT_COMPOSITION_AND_IDENTITIES_DEFINE_A_COMPLEX_LINEAR_CATEGORY_SKELETON_BUT_EXISTING_BHSM_DOES_NOT_SELECT_ITS_PHYSICAL_MORPHISM_SET_REVERSAL_DAGGER_LOOP_RELATIONS_OR_POSITIVE_STATE;_EVEN_AFTER_STRENGTHENING_THE_Z2_AND_Z3_WITNESSES_TO_FINITE_TRANSITIVE_DAGGER_GROUPOIDS_OVER_THE_EXACT_FOUR_VERTEX_BHSM_INCIDENCE_DIAMOND_BOTH_HAVE_FAITHFUL_POSITIVE_GNS_REALIZATIONS_AND_THE_SAME_INCIDENCE_QUOTIENT_WHILE_REMAINING_STAR_NONISOMORPHIC_WITH_GNS_RANKS_32_AND_48;_CAP_REFLECTION_AND_MAXIMAL_CYCLIC_RELABELING_LEAVE_CONTINUOUS_FAITHFUL_INVARIANT_STATE_FAMILIES_SO_NORMALIZED_TRACE_TRACIALITY_FAITHFULNESS_AND_SYMMETRY_DO_NOT_SELECT_A_PHYSICAL_FOUNDATIONAL_TRIPLE`

Primary outcome:

`OUTCOME_G_Z2_Z3_OBSTRUCTION_SURVIVES_ALL_CURRENTLY_DERIVED_PRINCIPLES`.

Refinement:

`OUTCOME_H_ACTION_DERIVED_EVENT_REVERSAL_LOOP_SPECTRUM_AND_STATE_SELECTION_PRINCIPLE_REQUIRED`.

The answer to the controlling question is **no**. Existing BHSM structure does
not select a unique pregeometric dagger event algebra and distinguished
faithful positive state. This is proved with fixed, incidence-compatible,
positive finite witnesses rather than inferred from missing documentation.

## 1. Pregeometric firewall

The foundational event generators are not functions on spacetime. No v15.4
definition uses as primitive data

\[
C^\infty(M),\quad x^\mu,\quad t,\quad g_{\mu\nu},\quad
d^nx,\quad\sqrt{|g|},\quad E,\quad\rho_E,
\]

a preferred frame, an observed particle count, or a measured physical datum.
The older regular support, boundary, finite-algebra, and Calderon structures
remain downstream reconstructed data unless an action-derived functor proves
otherwise.

## 2. What an event is in the retained architecture

The v15.0 object is most naturally categorical. An event has source and target
objects, an internal correspondence word, additive process depth, and a parent
invariant signature. If

\[
\alpha:A\rightarrow B,
\qquad
\beta:B\rightarrow C,
\]

then the architecture owns

\[
\beta\alpha=\beta\circ\alpha.
\]

Events with mismatched middle objects or invariant signatures do not compose.
After complex linearization, this partial product becomes an everywhere
defined product by assigning zero to noncomposable pairs. Composition is
associative and every event object has an identity morphism.

Thus BHSM derives a complex-linear category span. It does not yet select:

- the complete physical morphism set;
- which formal paths are identified;
- loop or backtracking relations;
- a group, groupoid, path, or convolution completion;
- reversal of every event.

It is therefore premature to force the architecture into a one-object group
algebra.

## 3. Candidate classification

| Candidate | Strength | Foundational obstruction |
|---|---|---|
| finite group algebra `C[G]` | simple positive witness | erases source/target objects |
| finite groupoid algebra | retains event endpoints and reversal | groupoid and isotropy are not selected |
| path/incidence algebra | closest to derived directed composition | no dagger until paths are doubled or inverted |
| finite-dimensional C-star algebra | classifies positive finite completions | block sizes and state remain inputs |
| dagger category/convolution algebra | correct categorical ordering | reversal functor is absent |
| historical BHSM finite algebra | has downstream boundary blocks | cannot be copied upstream without a reconstruction functor |

The architecture-retained object is the category span, not any one candidate
completion. A finite groupoid algebra is used below only because it provides
the strongest incidence-compatible kill screen.

## 4. Incidence-compatible finite groupoid witnesses

Use the exact four regular incidence labels

\[
\mathcal O=\{M_8,M_{5,+},M_{5,-},M_4\}
\]

and the distinguished diamond generators

\[
M_8\leftrightarrow M_{5,+}\leftrightarrow M_4,
\qquad
M_8\leftrightarrow M_{5,-}\leftrightarrow M_4.
\]

For a fixed cyclic isotropy group `Z_n`, define groupoid arrows

\[
(i,g,j):j\longrightarrow i,
\]

with product

\[
(i,g,j)(k,h,l)
=\delta_{jk}(i,g+h,l).
\]

The identity is

\[
1=\sum_i(i,0,i).
\]

The finite algebra is

\[
\mathcal A_n\cong M_4(\mathbb C[Z_n])
\cong\bigoplus_{k=0}^{n-1}M_4(\mathbb C).
\]

This completion contains composites and reverses of the distinguished diamond
edges. Forgetting cyclic isotropy while retaining those generators reproduces
the same four-object incidence grammar for every `n`. The quotient is an
explicit conditional reconstruction witness, not an action-derived core-to-
geometry map.

## 5. Dagger gate

Once the groupoid is declared, reversal gives

\[
(i,g,j)^\dagger=(j,-g,i).
\]

Antilinear extension verifies

\[
(a^\dagger)^\dagger=a,
\qquad
(ab)^\dagger=b^\dagger a^\dagger,
\]

and

\[
(\lambda a+\mu b)^\dagger
=\bar\lambda a^\dagger+\bar\mu b^\dagger.
\]

So a compatible dagger exists on both finite witnesses.

This does not close physical dagger selection. The historical BHSM orientation
involution `Iota^2=1` is a conditional regular-boundary grading that selects a
minimal balanced `(+,-)` sector. It is not a contravariant reversal functor on
all core events. Likewise the self-adjoint seam adjoint is defined only after
a regular Hilbert pairing and operator domain are supplied.

No theorem identifies the candidate dagger with physical time reversal, CP,
CPT, or complex conjugation alone. The correct status is

`DAGGER_EXISTS_CONDITIONALLY_BUT_IS_NOT_ACTION_OR_ARCHITECTURE_SELECTED`.

## 6. Positive and faithful state cones

In the Fourier decomposition

\[
\mathcal A_n\cong\bigoplus_{k=0}^{n-1}M_4(\mathbb C),
\]

every normalized positive state has density blocks

\[
\rho_k\succeq0,
\qquad
\sum_k\operatorname{Tr}\rho_k=1,
\]

and

\[
\omega_\rho(a)=\sum_k\operatorname{Tr}(\rho_k a_k).
\]

The state space is a compact spectrahedron of real affine dimension

\[
16n-1.
\]

The faithful states have

\[
\rho_k\succ0
\]

for every block. They form the relative open interior with the same manifold
dimension. Therefore faithfulness removes the boundary of the state cone but
does not select one point.

For the two witnesses:

| isotropy | full state dimension | faithful dimension | tracial simplex dimension |
|---:|---:|---:|---:|
| `Z_2` | 31 | 31 | 1 |
| `Z_3` | 47 | 47 | 2 |

The normalized regular trace is represented by

\[
\rho_k=\frac1{4n}I_4.
\]

It is positive, faithful, and normalized. It is not declared physical.

A second fixed state uses, in every Fourier block,

\[
\rho_k=\frac1{8n}\operatorname{diag}(1,2,2,3).
\]

It is also positive, faithful, normalized, cap-reflection invariant, and
cyclic-relabeling invariant, but is nontracial. No continuous parameter is
introduced into either fixed witness.

## 7. Automorphism and invariant-state gate

Without distinguished incidence data,

\[
\operatorname{Aut}(\mathcal A_n,\dagger)
\simeq PU(4)^n\rtimes S_n.
\]

Invariance under this entire group uniquely selects the normalized regular
trace because inner automorphisms force scalar density blocks and block
permutations force equal weights.

That statement is mathematical, not physical: BHSM does not derive the rule
that every abstract C-star algebra automorphism is a physical event symmetry.

The retained symmetric regular incidence branch supplies at most the cap
reflection `M5_plus <-> M5_minus`. It supplies no action-owned automorphism
group on the pregeometric core. Even granting the stronger witness grammar

\[
Z_2^{\rm cap}\times\operatorname{Aut}(Z_n),
\]

the invariant faithful state set remains continuous. Its affine dimension is
19 for both fixed `Z_2` and `Z_3` kill-screen witnesses when cyclic inversion
is imposed. With cap reflection alone the dimensions are respectively 19 and
29.

Therefore symmetry invariance does not currently select `omega_A`.

## 8. Faithfulness, purity, and traciality

Faithfulness implies

\[
\omega(a^\dagger a)=0\Rightarrow a=0,
\]

so the GNS null ideal vanishes and the representation is faithful. This is a
useful distinguishability condition, but v15.0 finite relational
distinguishability does not prove that one distinguished state must separate
every event. A nonfaithful null ideal might instead encode a physical gauge
quotient. BHSM has not chosen between those interpretations.

Neither purity nor maximal mixing is derived. Traciality

\[
\omega(ab)=\omega(ba)
\]

does not follow from cyclic action terms, absence of a preferred order, or
closed-event loops. For fixed `A_n`, tracial states already form a simplex of
dimension `n-1`; the regular trace is only one point.

The fixed nontracial faithful states also demonstrate conditional modular
structure. Their finite modular ratio spectrum is nontrivial, while the
regular trace has trivial modular operator. This is not a derivation of time,
a KMS state, or a clock.

## 9. GNS construction

For each retained state,

\[
\mathcal N_\omega
=\{a:\omega(a^\dagger a)=0\},
\]

\[
\mathcal H_\omega^{(0)}
=\mathcal A_n/\mathcal N_\omega,
\qquad
\langle[a],[b]\rangle
=\omega(a^\dagger b).
\]

For every faithful finite witness,

\[
\mathcal N_\omega=0.
\]

The left action is faithful, `[1]` is cyclic, and the dimensions are

\[
\dim\mathcal H_{\omega,2}=32,
\qquad
\dim\mathcal H_{\omega,3}=48.
\]

On one fixed finite algebra, faithful GNS representations are bare left-
regular representations and are unitarily equivalent as unpointed
representations. The physical datum is the pointed triple

\[
[\mathcal H_\omega,\pi_\omega,\Omega_\omega].
\]

The regular-trace and fixed nontracial density spectra differ, so their
pointed triples are not related by the allowed state-preserving automorphisms.
Thus even fixing the algebra does not select the physical GNS datum.

## 10. Strengthened `Z_2/Z_3` kill screen

The two fixed triples are

\[
(\mathcal A_2,\dagger_2,\tau_2),
\qquad
(\mathcal A_3,\dagger_3,\tau_3),
\]

with

\[
\mathcal A_2=M_4(\mathbb C[Z_2]),
\qquad
\mathcal A_3=M_4(\mathbb C[Z_3]).
\]

Both have:

- associative event composition and object identities;
- a reversal dagger;
- a normalized faithful positive state;
- exact GNS construction;
- the same distinguished four-object incidence quotient;
- cap-reflection and cyclic-relabeling invariance;
- no fitted data, continuous tuning, spacetime primitive, or preferred frame.

They are nevertheless inequivalent:

| invariant | `Z_2` witness | `Z_3` witness |
|---|---:|---:|
| algebra dimension | 32 | 48 |
| center dimension | 2 | 3 |
| irreducible blocks | 2 | 3 |
| faithful GNS rank | 32 | 48 |

Consequently no star isomorphism, event relabeling, or structure-preserving
GNS unitary can identify them.

The older conditional boundary result that `2` is the minimal orientation
order and `3` the minimal non-involutive cyclic order does not remove either:
it describes two distinct downstream primitive sectors and does not state
which order is the isotropy of a universal pregeometric event category.

## 11. Incidence and regular-algebra reconstruction

Both witnesses recover the exact BHSM diamond grammar by the same conditional
forgetful quotient. Hence incidence reconstruction does not distinguish them.

There is also an augmentation

\[
M_4(\mathbb C[Z_n])\longrightarrow M_4(\mathbb C)
\]

that forgets cyclic isotropy. It is not a map to the historical regular BHSM
finite algebra, and BHSM does not canonically select it as the physical
reconstruction functor.

The historical finite algebra

\[
(\mathbb C\oplus M_3(\mathbb C))
\otimes
(M_2(\mathbb C)\oplus\mathbb C\oplus\mathbb C)
\]

is conditional on the regular boundary closure hierarchy. It is a downstream
reconstruction candidate, not an allowed upstream definition of `A_A`.

Thus `Pi_alg` remains unproved.

## 12. Dirichlet-form readiness

Every finite faithful GNS space admits dense closed invariant quadratic forms.
Both the zero form and nonzero cyclic-Laplacian lifts are available, so

`DIRICHLET_FORM_EXISTENCE = TRUE_CONDITIONALLY`.

Their coexistence proves

`DIRICHLET_FORM_UNIQUENESS = FALSE`.

No Laplacian, Markov generator, spectral gap, recurrence, or relational
Hamiltonian is selected in v15.4.

## 13. T1--T17 result

| Gate | Result |
|---|---|
| T1 composition | categorical multiplication derived |
| T2 associativity | proved |
| T3 identities | one per event object |
| T4 dagger existence | yes on conditional groupoid completions |
| T5 dagger uniqueness | reversal functor not action selected |
| T6 positive-state cone | finite spectrahedra computed |
| T7 faithful-state cone | continuous open interiors |
| T8 invariant states | continuous under strengthened grammar group |
| T9 distinguished state | not unique |
| T10 traciality | not derived |
| T11 GNS | constructed for both witnesses |
| T12 GNS uniqueness | false as physical pointed data |
| T13 kill screen | `Z_2` and `Z_3` both survive |
| T14 incidence | same exact diamond quotient conditionally |
| T15 regular algebra | no canonical reconstruction map |
| T16 Dirichlet readiness | existence yes, uniqueness no |
| T17 foundation | physical triple set undefined; new principle required |

The exact residual ambiguity is:

`AT_LEAST_TWO_DISCRETE_STAR_NONISOMORPHIC_ALGEBRAS_EACH_WITH_CONTINUOUS_FAITHFUL_INVARIANT_STATE_FAMILIES`.

## Hindsight 20/20

### VALIDATED

- Category composition and object identities are architecture derived.
- Groupoid reversal gives a valid dagger after a reversible completion is
  declared.
- Positive and faithful state cones are explicit finite spectrahedra.
- Faithful states give zero GNS null ideal and faithful left-regular
  representations.
- Both incidence-compatible `Z_2` and `Z_3` dagger groupoids reconstruct the
  same BHSM diamond.
- The witnesses remain star nonisomorphic with GNS ranks 32 and 48.

### INVALIDATED

- Normalized trace is automatically physical.
- The smallest finite algebra is physically preferred.
- `Z_3` is preferred because there are three generations.
- Event orientation automatically fixes an action-owned unique dagger.
- Positivity fixes a unique state.
- Faithfulness fixes a unique state.
- Symmetry invariance fixes a unique state.
- All pointed finite faithful GNS triples are physically equivalent.
- A group algebra is automatically the correct parent structure.

### RECLASSIFIED

- `core Hilbert space` becomes the GNS representation of a selected state.
- `core observable` becomes an element of a selected event dagger algebra.
- `adjoint` becomes event reversal or reciprocity only after a reversal
  functor is derived.
- `core probability` becomes a positive functional, not a spacetime
  probability density.

### OPEN

Exactly one next irreducible object:

`ACTION_OR_ARCHITECTURE_DERIVED_PRIMITIVE_EVENT_REVERSAL_LOOP_SPECTRUM_AND_RECONSTRUCTION_FUNCTOR_THAT_FIXES_THE_PHYSICAL_DAGGER_CATEGORY_AND_AUTOMORPHISM_GROUP_AND_THEN_PROVES_OR_REFUTES_UNIQUENESS_OF_A_NORMALIZED_FAITHFUL_INVARIANT_POSITIVE_STATE`

## Completion boundary

```text
EVENT_MULTIPLICATION_DERIVED = TRUE
EVENT_ALGEBRA_UNIQUELY_SELECTED = FALSE
COMPATIBLE_DAGGER_EXISTS = TRUE_CONDITIONALLY
PHYSICAL_DAGGER_UNIQUELY_SELECTED = FALSE
DISTINGUISHED_POSITIVE_STATE_SELECTED = FALSE
TRACIALITY_DERIVED = FALSE
GNS_REPRESENTATION_UNIQUELY_SELECTED = FALSE
Z2_SURVIVES = TRUE
Z3_SURVIVES = TRUE
OUTCOME = OUTCOME_G_Z2_Z3_OBSTRUCTION_SURVIVES_ALL_CURRENTLY_DERIVED_PRINCIPLES
FULL_BHSM_COMPLETE = FALSE
MARK_III = NOT_REACHED
USB_SYNCHRONIZATION_ELIGIBLE = FALSE
```

Frozen predictions and official prediction logic remain unchanged. No new
continuous parameter, primitive dynamical field, empirical input, preferred
frame, or USB operation enters v15.4.
