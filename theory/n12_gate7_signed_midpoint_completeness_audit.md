# Signed midpoint chain-rule completeness

The frozen componentwise screen already stores the midpoint longitudinal
coordinate and frame-normal operator norms. Reading that validated,
hash-matched artifact requires no new action evaluation. All 370 retained
midpoints have nonzero values in both diagnostics:

| Diagnostic | Minimum | Maximum | Maximum interval |
| --- | ---: | ---: | ---: |
| Midpoint longitudinal coordinate norm | 0.09115120971071458 | 1.370355215301623 | 9 |
| Frame-normal residual norm | 2.7710542280370988e-6 | 3.486887565189012e-5 | 1 |

These are binary64 direction diagnostics. They do not quantify the omitted
Hessian response and are not outward enclosures.

For an endpoint-transverse input, its Hermite--Simpson midpoint image can be
written w = ell*g + t + n, where g is the midpoint axis, t its tangent
complement, and n the frame-normal component. Bilinearity gives

~~~
D2F[w,w] = ell^2 D2F[g,g] + 2 ell D2F[g,t] + D2F[t,t]
           + 2 D2F[ell*g+t,n] + D2F[n,n].
~~~

Every displayed term scales quadratically with the endpoint-transverse
input. Midpoint longitudinal terms therefore belong in the global
transverse-input coefficient; the separately retained global central and
mixed radius coefficients do not restore them automatically.

The exact two-dimensional witness uses axes e1, endpoint input e2,
a midpoint map interchanging e1,e2, and Hessian diag(1,0). Its full
quadratic value is 1; after midpoint-transverse projection it is 0.
This disproves generic complement preservation. The retained diagnostics
independently show that a zero midpoint-axis or normal map is not the
implemented BHSM center representation.

Existing local central and mixed contractions can be reused only with
their actual ambient directions and normalization. In particular, a mixed
map evaluated on the sum of endpoint-induced columns is not automatically
the Hessian on the 73-column recovered transverse basis. Normal components
cannot be discarded by relabeling them as rounding error.

The corrected assembly must retain all signed contributions supported by
provenance-matched source data. Missing normal or directional contractions
must stop full-center promotion until evaluated or bounded. The signed
transverse recovery tensors remain reusable. No action, center, mesh,
precision, preconditioner, coefficient ball, worker setting, or compute
ceiling is changed by this audit.

The radius search is a finite search. A positive result supplies radii for
certification; a negative grid result does not prove that no feasible pair
exists between samples.

Reproduce the deterministic audit:

~~~bash
python scripts/audit_n12_gate7_signed_midpoint_completeness.py
python -m pytest tests/test_n12_gate7_signed_midpoint_completeness_audit.py -q
~~~

The result is
artifacts/current_semantics/BHSM_N12_GATE7_SIGNED_MIDPOINT_COMPLETENESS_AUDIT.json.
It records the source-data hash, all-node diagnostic summaries, and exact
algebraic witness. Gate 7, the outward operator, root nonexistence,
physical instability, and full BHSM completion are not promoted.
