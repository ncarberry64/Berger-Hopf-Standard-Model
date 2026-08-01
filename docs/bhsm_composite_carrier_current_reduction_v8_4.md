# BHSM composite-carrier and weak-current reduction v8.4

## Result

This sprint combines four previously separate BHSM structures without adding a
new family factor or fitting a matrix:

1. the frozen three-slot charged-sector ledgers;
2. the exact Berger associated blocks;
3. the existing common C3 triality and G2/SU3 polarization architecture;
4. the Finkelstein--Rubinstein (FR) sign line.

The strongest supported result is

`BHSM_COMPOSITE_CARRIER_AND_WEAK_CURRENT_REPRESENTATION_CLOSURE_DERIVED_CONDITIONALLY`.

The exact remaining blocker is

`BHSM_MASS_AND_CKM_BLOCKED_BY_NO_ACTION_SELECTED_BERGER_MULTIPLET_STATES_AND_NO_ACTION_OWNED_LINEAR_COMBINATION_OF_NORMALIZED_WEAK_CURRENT_INTERTWINERS`.

No physical mass, CKM entry, fitted coefficient, or new primitive is emitted.

## 1. Frozen Berger block carrier

For every frozen mode `(k,j)`, define

```text
q = k - 2j,
J = k/2,
m = q/2.
```

The exact associated eigenspace is denoted `H_(J,m)` and has rank

```text
rank H_(J,m) = 2J+1 = k+1.
```

The block-level composite carrier is

```text
H_(J,m)
  tensor P_triality,slot
  tensor E_G2/SU3
  tensor L_FR
  tensor E_SM,sector.
```

This is a block carrier, not a rank-one physical state. Triality realizes the
same three family slots through the existing Fourier intertwiner; it is not a
second multiplicative family factor. The FR factor is a flat Z2 sign line and
adds no continuous coefficient.

The frozen ranks are:

| sector | base | excitation 1 | excitation 2 |
|---|---:|---:|---:|
| charged lepton | 1 | 6 | 10 |
| up | 1 | 7 | 11 |
| down | 1 | 7 | 9 |

Thus only the base blocks are intrinsically one dimensional.

## 2. Component-selection obstruction

For `J>0`, an irreducible Sp(1) carrier has no invariant vector:

```text
Hom_Sp(1)(C,V_J) = 0.
```

Consequently the labels `(J,m)` select an eigenspace but do not select a
unique normalized state in it. A rank-one state requires an additional
mechanism such as an action-selected polarization/coherent state, localized
profile, symmetry-reduction quotient, or collective-coordinate ground-state
theorem.

This is why a block-central scalar operator can determine a diagonal spectral
number while remaining insufficient for transition matrix elements.

## 3. Exact weak-current selection rules

Let a block-level weak-current component transform as `T^(L,r)`, with left
Sp(1) tensor rank `L` and right U(1) weight `r`. A matrix element between a
down block `(J_d,m_d)` and an up block `(J_u,m_u)` can be nonzero only if

```text
|J_u-J_d| <= L <= J_u+J_d,
r = m_u-m_d,
|r| <= L.
```

The frozen quark blocks are

```text
U0=(0,0), U1=(3,3), U2=(5,4),
D0=(0,0), D1=(3,0), D2=(4,2).
```

The minimum allowed channels are:

| | D0 | D1 | D2 |
|---|---:|---:|---:|
| U0 | (0,0) | (3,0) | (4,-2) |
| U1 | (3,3) | (3,3) | (1,1) |
| U2 | (5,4) | (4,4) | (2,2) |

For each entry, the exact right-weight Clebsch--Gordan coefficient

```text
<J_d,m_d;L,r|J_u,m_u>
```

is nonzero. In row-major order the coefficients are

```text
1, -sqrt(7)/7, 1/3,
1, -sqrt(6)/6, 1/6,
1, 2 sqrt(455)/65, -sqrt(105)/15.
```

Thus the table is not merely a necessary-rule screen: every listed minimal
right-weight coupling is representation-theoretically realized. The left
component and its normalized physical state remain action-selection data.

The three diagonal pairs require three distinct irreducible channels:

```text
S = (0,0),
B = (3,3),
A = (2,2).
```

Therefore one irreducible weak current cannot connect all three frozen
diagonal pairs.

## 4. Normalized Peter--Weyl intertwiner library

Normalize Haar measure on SU(2) to total volume one and use

```text
Y^J_(n,m) = sqrt(2J+1) D^J_(n,m).
```

Multiplication by a normalized current harmonic `Y^L_(p,r)`, followed by
projection from the down block to the up block, has matrix element

```text
<J_u,n_u,m_u|M_(L,p,r)|J_d,n_d,m_d>
 = sqrt((2L+1)(2J_d+1)/(2J_u+1))
   CG(J_d n_d,L p|J_u n_u)
   CG(J_d m_d,L r|J_u m_u).
```

In the convention where the left Wigner--Eckart coefficient carries
`1/sqrt(2J_u+1)`, the exact normalized reduced element is

```text
R_ud^(L,r)
 = sqrt((2L+1)(2J_d+1))
   CG(J_d m_d,L r|J_u m_u).
```

For the nine minimal channels, the row-major reduced-element matrix is

```text
[ 1,        -sqrt(7),             3              ]
[ sqrt(7),  -7 sqrt(6)/6,         sqrt(3)/2      ]
[ sqrt(11),  42 sqrt(65)/65,     -sqrt(21)       ].
```

Its entrywise squares are

```text
[ 1, 7,       9       ]
[ 7, 49/6,    3/4     ]
[11, 1764/65, 21      ].
```

The formal matrix has rank three. This removes a purely kinematic
normalization ambiguity: an exact normalized intertwiner exists for every
minimal channel. It is not a physical CKM matrix because each entry belongs
to a different current harmonic. The action has not selected the coefficients,
relative phases, or component states with which these intertwiners are to be
combined.

## 5. Cubic nonlinear representation closure

Take the primitive channels

```text
S=(0,0), A=(2,2), B=(3,3)
```

and their Hermitian adjoints. SU(2) tensor-product addition and U(1) weight
addition give witnesses for every entry of the 3 by 3 table:

| transition | target | witness | degree |
|---|---:|---|---:|
| U0-D0 | (0,0) | S | 0 |
| U0-D1 | (3,0) | B tensor B-dagger | 2 |
| U0-D2 | (4,-2) | A-dagger tensor B tensor B-dagger | 3 |
| U1-D0 | (3,3) | B | 1 |
| U1-D1 | (3,3) | B | 1 |
| U1-D2 | (1,1) | B tensor A-dagger | 2 |
| U2-D0 | (5,4) | B tensor B tensor A-dagger | 3 |
| U2-D1 | (4,4) | A tensor A | 2 |
| U2-D2 | (2,2) | A | 1 |

Hence the frozen up/down representation content closes through cubic order.
BHSM does not require nine unrelated current representations.

This is a representation-content theorem only. It does not prove that the
current action generates nonzero `S`, `A`, or `B` coefficients, nor does it
fix any reduced matrix element.

## 6. FR, triality, and common G2 no-go results

### FR

The FR holonomy group is `Z2`, so its only values are `+1` and `-1`. It can
supply fermionic rotation/exchange signs, but it cannot supply three
continuous mixing angles or a continuous CP phase.

### Common triality

If the same exact triality Fourier intertwiner `F` acts in the up and down
sectors and the current is family central, then

```text
F-dagger I3 F = I3.
```

The common basis change cancels. Discrete permutations or phases can produce
at most a monomial matrix, not a generic CKM matrix.

### Common G2/SU3 polarization

The common G2/SU3 polarization acts on the internal polarization/color carrier.
When the same section is carried across the three triality slots, it remains
family central and does not select different up/down family vectors.

Thus continuous CKM data must come from component-resolved up/down geometric
states and a noncentral weak-current kernel.

## 7. Mass-basis mismatch criterion

The effective weak current may remain universal in an abstract gauge-family
basis. Let the action-selected physical embeddings be

```text
U_u: C3_family -> H_up,physical,
U_d: C3_family -> H_down,physical.
```

Then the charged-current matrix in the physical mass bases is

```text
V_CKM = U_u-dagger U_d.
```

If the same triality/G2/FR embedding is used in both sectors, then

```text
U_u = U_d  =>  V_CKM = I3
```

up to discrete monomial relabelings. A nontrivial CKM matrix therefore
requires action-selected inequivalent up/down component isometries. In an
equivalent mass-operator statement, the Hermitian sector responses

```text
H_u=M_u M_u-dagger,
H_d=M_d M_d-dagger
```

must not be simultaneously diagonalizable; in particular `[H_u,H_d]` must
be nonzero. With nondegenerate spectra, CP violation additionally requires a
nonzero imaginary rephasing invariant of this mismatch.

This confirms that a common block-central spectral function cannot by itself
produce CKM, even when it produces different diagonal eigenvalues in the two
sectors.

## 8. Separable-current rank theorem

For a current sampled at one internal point or represented by one separable
channel,

```text
V_ij = a_i^* b_j.
```

This is an outer product, so

```text
rank(V) <= 1.
```

A sum of `N` separable channels obeys `rank(V)<=N`. Therefore a full-rank
three-family CKM matrix requires at least three independent separable channels,
or one genuinely extended nonseparable kernel.

A single point-localized topographic sample cannot generate physical CKM.

## 9. Spectral hierarchy boundary

For any scalar function of the exact Berger operator,

```text
f(O_Berger)|H_(J,m) = f(lambda_(J,m)) I.
```

The historical exponential candidate

```text
exp[-S_overlap lambda_(J,m)]
```

can conditionally encode a diagonal hierarchy after its physical attachment
and `S_overlap` are derived. It cannot select a vector within a degenerate
block, and a common block-central function cannot generate CKM mixing.

The action still does not derive

```text
S_overlap = 1/(4 pi)
```

or the map from the internal transfer amplitude to a physical pole mass.

## Validated

- exact block labels `J=k/2`, `m=(k-2j)/2` and ranks `k+1`;
- one block-level composite carrier per frozen slot;
- exact minimum weak-current channel table;
- three primitive current irreps close all nine channels through cubic order;
- FR cannot generate continuous CKM data;
- a common triality transform cannot generate generic mixing;
- one separable current channel has rank at most one;
- nontrivial CKM requires inequivalent up/down physical embeddings or noncommuting sector response operators.

## Invalidated

- FR sign as the source of continuous CKM angles or CP phase;
- one irreducible current as the complete weak kernel;
- one point-localized current as a rank-three CKM source;
- a block-central spectral function as a physical component selector;
- treating triality as a second independent triplication.

## Open

- an action-selected normalized state in every nontrivial Berger block;
- action generation of the primitive `S`, `A`, and `B` current components;
- action-selected coefficients and phases for the normalized intertwiner library;
- an action-selected complex phase source for a nonzero Jarlskog invariant;
- physical mass attachment and derivation of `S_overlap=1/(4pi)`.

## Next exact construction

`ACTION_DERIVED_COMPONENT_SELECTION_AND_CURRENT_COEFFICIENT_FUNCTIONAL_ON_NORMALIZED_BERGER_INTERTWINERS`

That object must select the physical component states, derive the primitive
current terms from the action, and fix the coefficients and phases multiplying
the already normalized Peter--Weyl intertwiners. Only then can the existing observable transport convert the result
to masses and CKM invariants.

