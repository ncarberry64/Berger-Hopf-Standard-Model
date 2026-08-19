# N6 relative-energy readout reconnaissance

## Result

The repository does not yet provide an executable N6 relative-energy or mass
readout. The v14.54 object is a conditional definition of the complete
composite-minus-matched-parent Noether/Hamiltonian charge and Floquet
quasi-energy. The current N6 artifact stores a child-only positive-duration
history, not the paired matched-parent history required to evaluate that
charge.

The executable reduced local diagnostic is

`H6_local(q,v,m) = v . d_v L6(q,v,m) - L6(q,v,m)`.

It is the local canonical constraint energy. It is not `Delta H6`, `Q_xi`, a
mass, or an absolute scale.

## Focused retained-action measurement

Using the repaired ordered-event N6 child and the unchanged ten-step
positive-duration evolution:

| action quadrature | initial `H6_local` | fine final `H6_local` | change |
| --- | ---: | ---: | ---: |
| 96 | `4.5075054799781356e-14` | `6.905587213168474e-14` | `2.398081733190338e-14` |
| 512 | `-5.0850306176464244e-5` | `-5.0790723922666814e-5` | `5.9582253797429985e-8` |
| 1024 | `-5.225228468819232e-5` | `-5.219106075737834e-5` | `6.122393081398059e-8` |

At 96 points the exact initial flow tangency is
`dH6_local/dt = 2.940769419650301e-11`, or
`6.957351198588555e-18` after normalization by the gradient/flow norms. This
validates autonomy at the fixed discrete action. The marked shift between 96,
512, and 1024 points shows that this diagnostic is not yet
quadrature-converged as a continuum readout.

## Existing contract and missing object

The retained downstream contract is

`Delta H6 = Q_xi[Phi_(P+C),6] - Q_xi[Phi_P,6 matched]`,

with one common generator/reference and all gravity, gauge, GHY, seam, corner,
and counterterm contributions. The exact next dependency is:

`DERIVE_AND_EVALUATE_THE_EXISTING_COMPLETE_COMPOSITE_MINUS_MATCHED_PARENT_NOETHER_HAMILTONIAN_Q_XI_ON_A_PAIRED_N6_PARENT_CHILD_HISTORY`

including quadrature convergence. Only afterward can the existing
gauge-reduced relative-periodic/Floquet BVP be closed. A physical mass claim
additionally requires a stable rest-frame relative-periodic cycle and the
already-declared `E_rel = m c^2` gate.

Family-cycle ownership is also open. Three charged-lepton quasi-energies count
only if the retained action produces three complete, persistent,
relative-periodic, action-inequivalent family cycles with a common clock and
returned family-sector map. C3-equivalent or degenerate cycles do not establish
a hierarchy. Frozen particle values may not select any cycle, branch, scale,
or ordering.

`FULL_BHSM_COMPLETE = FALSE`.
