# Selected eigenvalue index from outward inertia

A normalized eigenpair enclosure alone does not identify its spectral
index. For every real symmetric H in the entrywise Arb enclosure, the
number of negative eigenvalues of H-tI equals the number of eigenvalues
of H below t, provided zero is excluded. Two verified inertias at exact
thresholds a<b therefore count the eigenvalues in (a,b).

The helper accepts a fixed binary64 change of basis B. It encloses its
determinant in Arb and requires zero exclusion, then evaluates the congruence
`B^T (H-tI) B`. Sylvester's law of inertia preserves the counts for each
fixed real H. B need not be exactly orthogonal: approximate eigenvectors
only improve conditioning and are never evidence for a gap or index.

At each elimination step a symmetric permutation selects a diagonal pivot
whose Arb interval has a strict sign. The identity

```
inertia([[d,v^T],[v,C]]) = inertia(d) + inertia(C-v v^T/d)
```

holds for nonzero d. The interval Schur update encloses every possible
remaining symmetric matrix, so induction certifies the pivot sign count.
If no signed scalar pivot is available the strategy reports unresolved;
this is not a proof of singularity. All permutations are congruences.
The two mirrored entry intervals are intersected with outward rounding;
an empty symmetric domain is rejected.

The value producer requires 24 negative eigenvalues below the proposed
eigenvalue interval and 25 above it. Together with independently verified
normalized-eigenpair inclusion, this identifies that enclosed eigenpair as
the retained Hessian's zero-based index 24. Reference overlap fixes its
orientation. No action, eigenvalue ordering rule, coefficient or empirical
calibration changes. This verifies the frozen rule; it does not derive a
physical selection rule from the ontology or observable data.

The saved point-13 Hessian passed both counts in a bounded test using its
original eigenvalue target endpoints. The all-point value producer now
requires these counts at every newly computed endpoint and physical HS
midpoint. Full production coverage is established only by its completed
manifest and independent reproduction receipt.

Pointwise isolation does not prove continuation between state boxes,
neighborhood gap bounds, continuum spectral convergence, the physical
quotient, or completion of Gate 7. These remain separate requirements.
