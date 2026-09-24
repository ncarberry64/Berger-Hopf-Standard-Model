# Uniform selected-box rate pilot for direct physical HS neighborhoods

The paired frozen-affine endpoint-domain construction supplies coordinate
boxes containing z_i + E_i(e_i l_i+t_i). This pilot evaluates the original
physical field on both endpoint boxes of one selected interval, followed by
the actual Hermite-Simpson midpoint box. It uses unchanged conditional trial
radii, not measured data or newly certified contraction radii.

The canonical consumed domain is the outward reconstruction of each weighted
endpoint box. Raw state coordinates are divided by the exact positive frozen
weights anew, preserving any reconstruction inflation. The separately exported
raw geometry array is not silently assumed to contain this new reconstruction.
The descriptor remains the final coordinate without rescaling.

The retained physical kernel computes interval action jets, proposes an
eigenpair, and solves the bordered response. Independent normalized-eigenpair
inclusion must succeed for every matrix in the action-Hessian enclosure.
Independent symmetric inertia checks must isolate zero-based index 24 and
the stored reference must establish orientation. Floating eigensolvers and
gaps supply proposals only. The original rate function and all input/source
bindings are verified; no uncertain state coordinate is converted to a float.
Every output coordinate must be finite. The original field normalization and
its interval arithmetic remain unchanged.

The V2 proposal refines only the midpoint matrix when constructing an approximate
eigenpair center. This avoids asking an uncertain bordered matrix to produce a
center before a box has been proposed. The complete uncertain action Hessian is
then used for every residual, normalized eigenpair inclusion, and index check.
Coordinate radii start from the preconditioned interval residual; failed rows
may enlarge their proposed radii. Radius growth supplies no proof by itself.
The existing independent verifier must prove strict inclusion and contraction
on the whole matrix family, followed by the unchanged orientation and inertia
checks. No midpoint-only certificate is transferred to the uncertain domain.
The legacy gap diagnostic makes no positive gap claim; it is not a proof input.
The proposal search stops if a vector-coordinate radius exceeds one, retaining
the last finite failed inclusion report. This is a computational search limit,
not a proof that a larger eigenpair box or another enclosure method cannot work.
It changes neither the physical input domain nor the trial radii.

The original interval-proposal failure is retained as failed-method evidence.
The separately bound proposal module is installed only in the uniform value
and derivative pilots. Completed pointwise value, Jacobian, and Hessian
campaigns retain their original implementation and certificates. The derivative
pilot constructs and proves a fresh base on its entire consumed outer box.

With uniform endpoint rate enclosures F(Z_0) and F(Z_1), the midpoint box is

    M = (Z_0 + Z_1)/2 + h (F(Z_0) - F(Z_1))/8.

The same verified field evaluation is then applied on the entire M box.
Endpoint rates evaluated only at centers cannot be used in this formula.
Losing dependency between endpoint states and rates enlarges the domain and
is conservative. Overlap with independently paired center rate enclosures
is an additional consistency check, not the source of uniform validity.

All three point records contain their full weighted and raw evaluation boxes,
uniform rates, eigenpair proof, and source bindings. A failed evaluation keeps
its attempted domain and diagnostic separately; it establishes failure of
this coordinate-box method, not singularity of the correlated affine domain.
The complete pilot is recomputed in a separate invocation, including all three
field evaluations, and must reproduce data and record bytes. Receipts from
earlier attempts are archived before another run and differing candidates are
preserved. No failed or incomplete evaluation can produce a paired pilot.

Run `python scripts/certify_n12_gate7_uniform_physical_value_pilot.py
--interval 13 --preflight` to verify inputs without computing action jets.
When numerical capacity is free, omit `--preflight`, then rerun with
`--recompute`. Each invocation is sequential and uses one numerical process.

A successful pilot covers the selected two endpoint boxes and their actual
midpoint box. It does not establish complete-history coverage, uniform DF or
Hessian bounds, a remainder estimate, an intrinsic constraint chart, physical
quotient, contraction, or continuum existence. Those dependencies and Gate7
remain open.
