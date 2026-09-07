# AE3.1 current-C2 neutral semigroup response transport

The retained neutral family modes are `(0,0)`, `(3,0)`, and `(3,1)`. Applying
the already-frozen internal Berger generator and overlap width gives

```text
K_neutral = diag(0, 18.0489684572, 15.3387742730),
T_neutral = exp[-K_neutral/(4 pi)]
          = diag(1, 0.2378080903, 0.2950469233).
```

Thus a family-noncentral neutral response shape with two nonzero response gaps
does survive attachment over the current `C2` history. No particle or family
ledger is rebuilt. Its tensor lift commutes with the tested reset,
enclosure-restriction, and localization-carrier factors. This does not yet
prove the full rank-three neutral subbundle projector commutes with
`D_AE2^2` and the gauge/BRST action.

This does not yet produce neutrino oscillation. The charged-lepton and neutral
operators inhabit the same commutative family-projector algebra, so their
canonical mixing matrix is `I3`. The neutral response also commutes with a
canonical first-slot source projector. More basically, the internal slots are
ordered by the retained BHSM role ledger, while the capture gate's
`(nu_e,nu_mu,nu_tau)` basis is an abstract weak-flavor basis. Their physical
intertwiner has not been derived and cannot be assumed.

Finally, `exp(-s K)` is a positive Euclidean overlap contraction. It is not the
action-derived Lorentzian evolution `exp(-i integral H dt)`, a retarded neutral
Calderon map, or a physical mass matrix. Its two response gaps therefore cannot
be renamed measured or predicted `Delta m^2` values.

Promoted:

- retained neutral mode provenance on current `C2`;
- the neutral internal semigroup response shape;
- family noncentrality and two response gaps of that shape;
- the common-projector no-mixing theorem.

Still open:

- the weak-flavor/internal-family intertwiner;
- a returned Lorentzian neutral self-energy;
- noncommuting propagation monodromy, PMNS, and physical mass splittings.

`FULL_BHSM_COMPLETE = FALSE`.
