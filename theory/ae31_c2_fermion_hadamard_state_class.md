# AE3.1 current-C2 fermion Hadamard-state class

## Existence result

The current-C2 charged-lepton operator is already a Dirac-type operator with
a smooth bounded family mass endomorphism on every certified finite-core
globally hyperbolic member,

```text
M4 = I_tau x S3,
h = -d tau^2 + R4(tau)^2 dOmega3^2,
R4(tau) > 0.
```

The causal theorem previously supplied unique advanced and retarded Green
operators for compact sources. The corresponding CAR algebra therefore has a
nonempty quasifree Hadamard state class on the open development of every such
member. Each chosen Hadamard state defines a time-ordered Feynman two-point
distribution.

This advances existence, not selection. Any two Hadamard two-point functions
for the same operator differ by a smooth bisolution. The action and principal
symbol determine the universal short-distance singularity class, but the
smooth state-dependent part remains free until BHSM supplies a state
covariance.

## Exact missing datum

On a constant-`tau` Cauchy surface, a quasifree fermion state is specified by
a covariance `C` on the completed Dirac Cauchy-data space satisfying

```text
0 <= C <= I,
C + Gamma C Gamma = I,
```

with `C^2=C` for a pure state and the Hadamard positive-frequency principal
symbol modulo smoothing terms. Current BHSM already owns the Dirac inner
product, causal evolution, and CAR pairing. A selected covariance must also
obey

```text
C_child = U_R C_event U_R^dagger
```

across the AE2 reset and preserve the frozen family projectors. No such
covariance or equivalent complex structure is present in AE3.1.

## Why the retained structures do not select it

- The AE2 reset lift selects the spin--gauge trace domain, not a
  positive-frequency splitting.
- The unique forward time orientation labels causal support and advanced
  versus retarded propagation; it does not choose a complex structure.
- The Hadamard microlocal condition fixes the singularity class, not the
  smooth bisolution part.
- Instantaneous Hamiltonian diagonalization would require an action-selected
  Cauchy slice and time-dependent complex structure.
- A finite-order adiabatic prescription requires an order, reference slice,
  and smooth completion not supplied by the action.
- A KMS state requires stationary time flow and an owned inverse temperature.
- A Euclidean state requires an owned Euclidean continuation, cap domain, and
  reflection-positive prescription.
- In/out vacua require a maximal continuation with asymptotic stationarity.
- The proper-history resolvent coordinate `z` is not physical `p^2` and
  contains no state covariance.

No temperature, Bogoliubov coefficient, adiabatic order, cutoff, or vacuum is
inserted.

## External theorem provenance

The existence and microlocal statements used here are standard curved-
spacetime Dirac-field results, not new BHSM dynamics. Stefan Hollands,
*Adiabatic Hadamard States for Dirac Quantum Fields on Curved Space*
(arXiv:gr-qc/9901069), constructs a pure quasifree state on a general globally
hyperbolic Lorentzian spin spacetime and proves it Hadamard in Theorem VI.1.
Christian Gerard and Theo Stoskopf, *Hadamard states for quantized Dirac
fields on Lorentzian manifolds of bounded geometry* (arXiv:2108.11630), also
construct pure Hadamard states and give constructions for arbitrary spin
spacetimes. Hollands records the self-dual CAR covariance conditions and
explains why instantaneous positive-frequency diagonalization is not a
canonical prescription on a general time-dependent globally hyperbolic
spacetime.

## Claim boundary

Derived:

- a nonempty finite-core current-C2 Hadamard state class, member by member;
- existence of a Feynman two-point distribution conditional on choosing a
  member of that class;
- the state-independent local Hadamard singularity class;
- the exact covariance datum and reset compatibility still required.

Not derived:

- one action-selected current-C2 Hadamard state;
- an action-owned Feynman two-point function;
- global frequency diagonalization on the nonstationary finite history;
- dressed charged-lepton poles, a physical muon pole, or muon `F2(0)`.

The exact next object is one action-selected current-C2 Cauchy covariance or
equivalent complex structure compatible with AE2 reset and current-C2
evolution, or a maximal asymptotic-stationarity theorem that selects it.
