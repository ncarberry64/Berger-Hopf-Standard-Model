# BHSM v6.5.0: topological matter action and global spectrum

Primary result:
`BHSM_TOPOLOGICAL_MATTER_ACTION_SOURCE_AND_GLOBAL_SPECTRUM_REMAIN_CONDITIONAL`.

This sprint begins from merged `main` SHA
`8330c7e78cb2cd59d883eadd82c385e7e717c946`. PRs #162, #163, and #164
were merged with history-preserving merge commits after their required
Python, native, and ROOT checks passed. Their scientific commits remain in
`main`, and their remote branches were retained.

## Outcome

The sprint makes real progress by separating four questions that were
previously bundled together:

1. whether configuration-space quantization can supply a first-order matter
   carrier;
2. whether an invariant in the frozen action actually generates it;
3. whether the action dynamically selects the G2/SU(3) polarization;
4. whether the available local data define a complete compact/global
   spectrum.

The answer is conditional in every case. The mathematical templates exist,
but the frozen P1+GHY+B1 theory does not define the topological configuration
component, its fundamental group and symplectic normalization, a
configuration-space-to-local-M4 transgression, a polarization-locking bundle
morphism, or the complete self-adjoint global operators.

## Configuration space and Finkelstein–Rubinstein map

The formal fixed-sector configuration space is

```text
Q_N = C_N/G_0,
```

where `C_N` is a fixed topological component and `G_0` is the based
gauge/diffeomorphism redundancy. Its formal tangent is the kernel of the
linearized constraints modulo infinitesimal redundancies. A collective metric
and Berry form would be obtained only after a field ontology, zero modes, and
normalization kernel are specified.

The code validates the established `Z2` Finkelstein–Rubinstein sign-character
template and a nondegenerate closed symplectic-form template. This does not
identify `pi1(Q_N)` with `Z2` for BHSM. The repository has not yet defined
`C_N` well enough to compute `pi1(Q_N)`, and a first-order Berry term on a
finite-dimensional moduli space is not automatically a local M4 field
action.

## First-order source audit

The complete source classification gives:

- P1 Einstein–Hilbert plus GHY supplies gravitational boundary variation but
  no collective matter carrier or `sigma Gamma_star` invariant.
- B1 is bosonic and contains neither a Clifford carrier nor the required odd
  invariant.
- an eta invariant is circular as the source because it presupposes a
  self-adjoint first-order operator;
- torsion is absent from the declared connection and is not introduced;
- gauge Chern–Simons transgression does not supply the representation carrier
  or wall-odd mass;
- a configuration-space Berry/FR route remains possible, but requires the
  missing `Q_N` construction and local transgression.

The smallest classified extension is

```text
S_eff,F =
  integral_M4 sqrt(|h|)
  <Psi_coll,[i C_BHSM + y_sigma sigma Gamma_star]Psi_coll>.
```

`Psi_coll` is an effective collective-coordinate/configuration-space carrier,
not an elementary bulk spinor. Canonical normalization removes the overall
kinetic coefficient but does not fix the ratio `y_sigma`. The FR character
fixes a sign, and the wall index depends only on an asymptotic sign change.
Neither fixes the magnitude. No frozen invariant relates it to `G5`, `Z5`, or
Berger stiffness. Thus one dimensionless primitive remains if this extension
is adopted.

No physical bulk Dirac parent law is introduced.

## Dynamic polarization theorem

For a unit section `u`, the fiber is the homogeneous space
`G2/SU3 = S6`. Because G2 acts transitively, every G2-invariant scalar
potential made from `u` alone is constant. Its tangent Hessian is zero.
Therefore G2 invariance alone cannot dynamically select `u`.

A composite

```text
V = lambda [1 - (u dot v)^2]
```

has stationary sections `u=+v` and `u=-v` and tangent Hessian
`2 lambda I_6`, but it requires a second section `v` of the same rank-seven
bundle or a derived bundle morphism. The Berger orientation lies in a
rank-three Sp(1) adjoint bundle, while the spacetime normal is a line-bundle
section. The frozen construction supplies no canonical transition-function
compatible identification among these bundles.

The direct locking proposal is therefore rejected in the declared bundle
data, while a future composite locking theorem remains possible.

Result: `BHSM_POLARIZATION_SECTION_FLAT_DIRECTION_REMAINS`.

## Compact first-order diagnostic

The implemented compact test uses

```text
C = [[0,A^dagger],[A,0]],
A = partial_rho + y_sigma sigma,
```

with a rectangular maximal-isotropic discretization. With `n` selected
chirality nodes and `n-1` opposite-chirality nodes, the exact discrete index
is one. The zero-mode residual converges to numerical zero, its norm is one,
and the first massive singular value converges across 81, 161, and 321
points.

This is a domain and numerical-method validation. It is not the full B1 cap
spectrum. The frozen action does not select the maximal-isotropic domain, and
the full v6.1.7 scalar/metric profiles have not been exported into every
constraint-reduced normal operator.

On a compact interval both signs of the wall mass are square integrable. With
the fixed selected domain, one sign is center-localized and the reversed sign
is boundary-localized. Consequently complete-line nonnormalizability alone
does not prove compact vectorlike exclusion. Orientation, the boundary form,
and leakage must be derived together.

## Upper and lower fold sheets

The tensor, connection, sigma/Berger, orientation, junction-bending,
first-order matter, and boundary-domain ledgers retain the healthy v6.4 local
principal signs where proved. None has a complete action-derived global
normal operator and B1 boundary form. The representative compact diagnostic
is sheet symmetric.

No global spectral difference was manufactured:

- the upper sheet is not newly derived as unique;
- the lower sheet is not excluded;
- the adopted spacetime-facing upper-sheet axiom is preserved;
- global continuation of the complete constrained operators remains the
  required test.

## Connection transfer

The exact representation data remain

```text
I1_raw = 10/3,
eta_Y = 3/5,
I1_normalized = I2 = I3 = 2.
```

The transfer formula is

```text
1/g_i^2 = I_i [tau_i,intrinsic + Z_A,i N_i].
```

P1 fixes the intrinsic Sp(1) and nested U(1) Hopf terms and preserves

```text
tau_nested/tau_transverse = exp(2 beta).
```

The SU(3) intrinsic transfer, every full cap/wall overlap `N_i`, and the
ratios involving `Z_A,i` remain independent. `Z_g=Z_A,i` is not assumed.
The rejected `1:2:7` representation theorem is not restored, and no measured
couplings are inserted.

## Scalar, gauge, and neutral sectors

The retained scalar coordinates are `(sigma,beta)` with positive
representative kinetic metric

```text
diag(Z_sigma,(6/7)Z_Berger).
```

The code validates generalized eigenvalue machinery but labels all numerical
coefficients representative. The physical Schur-complement coefficients have
not been derived, so the Higgs-like radial eigenmode remains undetermined.

The conditional gauge mass matrix continues to have two equal charged
eigenvalues, one massive neutral eigenvalue, and exactly one `Q_em` null
direction. Its global normalization remains open.

For an energy-independent Hermitian neutral connection,

```text
U_neutral(gamma) = P exp(i integral_gamma A_neutral)
```

is unitary and path reversal gives its adjoint. Its phase scales as `L E^0`,
not `L/E`. An action-derived dispersive `1/E` term would be required to
recover that law. No measured oscillation differences are fitted.

## Scale and scalar-wall status

The absolute-scale relation remains symbolic:

```text
L_i^2 =
  (Z_g/Z_A,i) 2/(I_i g_i^2 Mbar_Pl^2)
```

after dimensionless transfer closure. No numerical unit or particle mass is
claimed.

The scalar-wall cusp

```text
Gamma_tau-Gamma_c = tau(nu1/12)r^3 + O(r^4)
```

with `nu1/12=9.138890145035...` is preserved. No new fourth-order component
is claimed, and the retired flat-kink `27/35` target is not revived.

## Classification

Established mathematics:

- FR sign representations and moduli-space Berry terms;
- homogeneous-space transitivity and invariant-potential consequences;
- self-adjoint boundary forms and rectangular Fredholm index diagnostics;
- unitary holonomy for Hermitian connections.

BHSM identifications:

- a prospective topological component `C_N`;
- a collective boundary carrier `Psi_coll`;
- the polarized SU(3) boundary bundle and triality family action.

Derived or numerically validated here:

- the exact source and coefficient-dependency null theorems;
- the G2-only flat-direction theorem;
- the declared bundle mismatch for direct locking;
- the convergent compact domain/index diagnostic;
- the retained symbolic connection dependency graph;
- the `L E^0` neutral phase law for the declared connection.

Rejected:

- claiming P1/GHY/B1 already generates the matter action;
- circular eta sourcing, ad hoc torsion, and hidden monopole structure;
- direct identification of G2, Berger, and spacetime-normal sections;
- a compact no-doubling theorem from complete-line behavior alone;
- a global sheet selector from local principal symbols;
- an `L/E` claim from an energy-independent connection.

Active construction targets:

- define `C_N`, compute `pi1(Q_N)`, and derive its symplectic normalization;
- derive or reject the configuration-space-to-M4 transgression;
- derive a polarization bundle morphism or retain the modulus;
- construct every B1 self-adjoint domain and complete global operator;
- close connection overlaps, scalar Schur complement, order `r^4`, and scale.

Completion gate:
`V6_5_0_CONFIGURATION_SPACE_PARENT_SOURCE_DYNAMIC_POLARIZATION_AND_COMPLETE_GLOBAL_SPECTRUM_OPEN`.

`FULL_BHSM_NOT_COMPLETE`.

## Reproduce

```powershell
python scripts/materialize_topological_matter_action_global_spectrum_v6_5_0.py
python -m pytest -q tests/test_bhsm_topological_matter_action_global_spectrum_v6_5_0.py
python -m bhsm.interface topological-matter-global-spectrum-status --format markdown
```
