# AE3.1 event-to-child Hadamard-state transport

## Result

The selected AE2 reset lift is a unitary spin--gauge bundle isomorphism on
the last regular event trace and first regular child trace. The AE3.1 family
mass operator acts on the separate frozen family factor. Therefore

```text
U_reset = U_R tensor I_F,
[U_reset,P_f] = [U_reset,M_l] = 0.
```

For any upstream self-dual CAR covariance `C_event`, define

```text
C_child = U_reset C_event U_reset^dagger.
```

Unitary conjugation preserves `0<=C<=I`. Because the reset lift intertwines
the event and child CAR conjugations, it also preserves

```text
C + Gamma C Gamma = I.
```

If the state is pure, `C^2=C` is preserved. Conjugation by `U_reset^dagger`
is the inverse, so this is a bijection of quasifree covariance classes, not a
lossy trace attachment.

The reset map is a smooth spin--gauge bundle isomorphism and becomes the
identity in the common reset frame up to the global spin sign and gauge frame.
Its Lorentz spin lift intertwines the event and child Dirac principal symbols
and maps future-null event covectors to future-null child covectors. It
therefore transports the Dirac Hadamard wavefront set and its polarization.
Every admissible upstream Hadamard state thus reaches the first regular child
trace and propagates through the globally hyperbolic current-C2 enclosure by
the already derived causal evolution.

## Physical identification consequence

This closes the state-transport part of the identification bridge:

```text
upstream family-labelled Hadamard particle state
    -> AE2 unitary reset transport
    -> same family-labelled state on the child trace
    -> AE3.1 current-C2 local enclosure.
```

No particle family or spectrum is reconstructed. The retained family
projectors, semigroup weights, mass endomorphism, current attachment, and
topological data are reused unchanged.

Transport is not selection. The reset sends each admissible upstream
covariance to exactly one child covariance, but the action still supplies no
unique upstream covariance. Nor does this theorem define a second preferred
positive-frequency splitting with which to compute Bogoliubov particle
production.

## Claim boundary

Derived:

- bijective AE2 reset transport of self-dual quasifree covariances;
- preservation of positivity, purity, and the Hadamard singularity class;
- preservation of every frozen family projector and the AE3.1 mass block;
- conditional transport of any upstream Hadamard particle state into the
  current-C2 local enclosure.

Not derived:

- one action-selected upstream or child state;
- a Bogoliubov particle number;
- dressed charged-lepton poles, a physical muon pole, or `F2(0)`.

The next missing object is an action-selected upstream Cauchy covariance or a
maximal asymptotic state selector. Once supplied, its reset image can enter the
dressed charged-lepton two-point operator without any new state parameter.
