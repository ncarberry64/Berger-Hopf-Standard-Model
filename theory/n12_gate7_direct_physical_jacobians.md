# Direct derivatives at physical Hermite–Simpson points

The stored replay midpoint and the midpoint constructed from newly verified
endpoint rates differ. A derivative enclosure at the former cannot serve as
a derivative enclosure at the latter without an additional neighborhood
bound. This producer evaluates the unchanged retained rate derivative graph
directly at the physical point enclosure.

The input is the complete, independently reproduced 741-point direct-value
campaign. Each derivative point checks its value and endpoint dependencies
against that campaign's exact file inventory. Endpoints use the original
binary64 raw state. Midpoints retain the full rational weighted-state ball,
including endpoint-value uncertainty, and divide by exact stored weights in
Arb. All 99 weighted augmented coordinate directions are explicit Arb unit
vectors; the parent graph therefore also performs direction scaling in Arb.

The derivative graph runs at 256 bits. Its proposed eigenvector center is
normalized, and a separate 512-bit inclusion and inertia calculation verifies
the normalized eigenpair and index 24. Stored-reference orientation remains
mandatory. Sparse mixed jets omit only algebraically exact zero products
with finite other factors. Point-only factored state shortcuts are not used.

Each result exports the complete 99 by 99 ambient DF, recomputed value, and
evaluation state as rational balls. The recomputed value must overlap the
paired direct value; overlap is a consistency check, not a substitute for
the derivative graph or eigenpair verification. Source files, runtime,
precision, point dependencies, and hashes are recorded. Independent repetition
re-evaluates every point and requires identical scientific JSON and NPZ bytes.
Failures preserve candidate evidence and never overwrite successful results.

Run a bounded selected campaign only after the existing numerical pool has
finished. For example:

```
python scripts/derive_n12_gate7_direct_physical_jacobians.py --midpoints 13 --workers 3 --worker-hour-cap 0.25
python scripts/derive_n12_gate7_direct_physical_jacobians.py --midpoints 13 --workers 3 --worker-hour-cap 0.25 --recompute
```

Measure the actual pilot before budgeting a full campaign. `--all-points`
selects all 371 endpoints and 370 midpoints; the worker-hour cap is a total
allocation divided by the selected worker count. A timeout preserves already
completed points and terminates only this producer's own workers.

For the residual convention

```
M = (z0+z1)/2 + h*(f0-f1)/8
r = z1-z0-h*(f0+4*f(M)+f1)/6
```

the exact chain rule is

```
M0 = I/2 + h*DF0/8
M1 = I/2 - h*DF1/8
r0 = -I - h*DF0/6 - (2*h/3)*DFM*M0
r1 =  I - h*DF1/6 - (2*h/3)*DFM*M1
```

`direct_physical_hs_jacobian.physical_hs_blocks` evaluates these expressions
outwardly at 512 bits. Matrix order is essential. The optional fixed-frame
operation encloses `R^-1 T rj E` using an Arb solve, without assuming that
trial or test frames are orthonormal. A fixed initial endpoint must receive
a zero trial frame when those blocks enter a finite-history operator.

These are pointwise derivative and algebraic assembly tools. They do not
establish physical mode selection, branch continuation, the intrinsic
physical quotient, state-dependent frame derivatives, a neighborhood bound,
or the complete causal `Z1` bound. No physical contraction or Gate 7 closure
is claimed, and no observable prediction follows from this campaign alone.
