# Uniform integration width refinements, 12 September 2026

The same complete physical derivatives and frozen Hermite–Simpson operator
now admit narrower local interval enclosures by applying the fixed
preconditioner before uncertain matrix products. Interval 13 was computed
twice in independent invocations with byte-identical record and data.

| Local block | Previous maximum radius | Preconditioned maximum radius |
| --- | ---: | ---: |
| DL | 486.432636 | 312.201364 |
| DR | 485.949672 | 304.658736 |

These are uncertainty radii, not measured physical observables. The fixed C
block retains its original enclosure. Each entry is selected from four
algebraically equivalent interval evaluations according to its radius;
every candidate encloses the same frozen operator entry. The physical
domain, action, trial radii, step, frames and all 99 derivative directions
remain unchanged. This is a local numerical improvement of about 36–37%,
not a full-path contraction certificate. Gate 7 remains open.

The paired record hash is
`51E4F5BC8A929505585D2740E98459DCA40FB198E29C011B8AF27F293EC4BCA3`;
data hash is
`C32EA168B42AD6E366390461EB4D59058C5874586843C2C1A605EAE49F50C9F0`.
The compact evidence artifact records the independent reproduction receipt,
entry-selection counts, diagnostic source hashes and comparison values.
Displayed decimal radii are rounded summaries of the saved rational radii.

## Where the remaining width comes from

A diagnostic that artificially replaces selected interval columns with
their midpoints helps attribute uncertainty; those counterfactual matrices
are explicitly not physical enclosures. Making only descriptor column 98
exact barely changes DL/DR (about 486/485). Making all state columns exact
leaves radii about 0.00594/0.00586. Thus the state-direction widths dominate
this local bound, even though descriptor column 98 has the largest single
entry radius in the full derivative matrix.

A genuine, but unreproduced, refinement of the paired primal response
reduces the descriptor derivative radius from about 620 to 65 at endpoint
13, and 1966 to 1320 at the actual midpoint. Substituting those two refined
columns changes local DL/DR only to about 486.37/485.90, with endpoint 14
unchanged. This does not justify a full descriptor-only campaign.

Combining the selected-eigenline projection inside the signed third-action
contraction is algebraically valid and tested against an independent
polynomial contraction. Its endpoint/midpoint column-0 radii are 3.71562
and 6.53848, slightly wider than the existing component-centered values
3.69392 and 6.41226. These are unreproduced one-column diagnostics; the
projection variant is not selected for production.

## Mixed second derivatives

The complete original seven-solve physical Hessian graph was evaluated on
the paired endpoint-13 tube for one scaled longitudinal direction and
transverse column 0, retaining the original fifth-action scalar terms.
Its uniform enclosure contains the verified point Hessian, whose maximum
absolute value is about 8.18e-5, but the uniform maximum radius is about
12209.9. All seven intermediate solves and all scalar variations are saved
with the source bindings, permitting normalization refinements without
repeating the costly action contractions.

The common-border second-derivative helper differentiates the equivalent
normalized physical field after using the same-family normalization and
orthogonality identities. Its derivation and identity requirements are in
`theory/n12_gate7_coupled_second_normalization.md`. Independent Arb Taylor
series tests cover both border signs and nonzero mixed terms. The saved
diagnostic consumer verifies exact serialized domain strings before
outward interval reconstruction; mutual containment after reconstruction
would wrongly reject the tiny additional rounding width.

The first saved-domain consumer did reject that representation difference
before evaluating the normalization. Its failure and original source are
preserved locally. The revised consumer checks the canonical saved strings
and then requires the reconstructed box to contain the original input.
This changes the representation check, not the physical domain.

The revised saved-data calculation completed: the normalized Hessian
maximum radius is 167.65755, about 73 times narrower than the original
12209.9151, and it still contains the verified point result and overlaps
the original uniform enclosure entrywise. This is an unreproduced
transformation of the saved, unreproduced one-direction diagnostic. It
does not establish a sufficiently small uniform derivative remainder.

No full affine-direction coverage, physical quotient identification,
higher-remainder bound, empirical prediction, Museum observable, manuscript
completion, or BHSM completion follows from these local diagnostics.
