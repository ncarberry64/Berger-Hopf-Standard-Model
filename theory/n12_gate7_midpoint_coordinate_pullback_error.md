# Midpoint coordinate error through the complete stored Hessian

Status: a proved perturbation inequality and tested 512-bit Arb implementation.
The all-370 production certificate requires the completed supplemental tensor
campaign and has not been materialized. Gate 7 remains active and
`FULL_BHSM_COMPLETE = FALSE`.

The prerequisite basis and coordinate-solve verification has now executed on
all 370 stored midpoint inputs, with two byte-identical materializations per
certificate. The maximum stored-coordinate error upper bound is
`8.043318260186595e-8` in matrix row-sum norm. This completed prerequisite
does not substitute for the still-pending full-tensor pullback certificate.

The committed reports bind the recovered midpoint and mixed-transport input
shards by hash. Those generated NPZ caches are not included in these JSON
reports; reproducing them requires the corresponding documented upstream
campaigns or the matching retained input caches. All 13 non-cache inputs in
their combined manifest match the mainline source and geometry files.

## Operand and inequality

For each midpoint let the exact values of the stored binary64 matrices be
`S=[U C]`, `M`, and the numerical solution `Xhat`. The stored-basis inverse and
coordinate-solve verifier establish nonsingularity and

\[
 X=S^{-1}M,\quad E=X-\widehat X,\quad
 \|E\|_\infty\leq\epsilon.
\]

Here the matrix infinity norm is the maximum absolute **row sum**, including
all 148 endpoint-pair columns. With `n=99` coordinate rows,

\[
 \|E\|_F^2=\sum_i\|E_{i,:}\|_2^2
 \leq\sum_i\|E_{i,:}\|_1^2\leq n\epsilon^2.
\]

For each of the 99 outputs the full stored Hessian is

\[
 Q_o=\begin{pmatrix}Q_{UU,o}&Q_{CU,o}^{T}\\
                      Q_{CU,o}&Q_{CC,o}\end{pmatrix}.
\]

Both cross legs are retained. Its stacked Frobenius norm satisfies

\[
 q^2=\sum_o\|Q_o\|_F^2
 =\|Q_{UU}\|_F^2+2\|Q_{CU}\|_F^2+\|Q_{CC}\|_F^2.
\]

Expanding the exact perturbation gives

\[
 X^TQ_oX-\widehat X^TQ_o\widehat X
 =E^TQ_o\widehat X+\widehat X^TQ_oE+E^TQ_oE.
\]

The Frobenius product inequality, the triangle inequality, and then summation
of squared output bounds yield

\[
 \|Q[X,X]-Q[\widehat X,\widehat X]\|_F
 \leq q(2xe+e^2),\qquad
 x=\|\widehat X\|_F,\quad e=\sqrt n\,\epsilon.
\]

This remains valid after symmetrization, an orthogonal projection for the
Frobenius norm. A supplied exact stored output map `L` permits the additional
factor `||L||_2 <= ||L||_F`. The all-370 runner reports the **unmapped** bound;
it does not silently infer or evaluate a causal output map. The error estimate
does not replace the signed center calculation or take component norms before
center cancellation. It bounds only the perturbation to that center.

## Arithmetic and provenance

`src/bhsm/interface/current_green_midpoint_coordinate_error.py` evaluates all
squares, sums, products, and square roots using Arb at 512 bits. Every
binary64 operand is converted exactly; the result is converted from the ball
upper endpoint to binary64 with an additional outward step. Exact structural
zeros stay zero. Positive bounds below the smallest binary64 subnormal round
up to that subnormal. Unrepresentable finite-output bounds fail closed.
The caller's Arb precision is restored on success and failure.

The low-level function requires an independently verified epsilon. The
campaign runner `scripts/certify_n12_gate7_current_green_midpoint_coordinate_pullback.py`
does that verification itself, using the existing stored-basis and solve
certifiers. It first revalidates all 370 supplemental aggregates, all 9,620
restart rows, their exact value correspondence, the rectangular UU identity,
and the campaign fingerprint. It then checks each stored `U,C` against the
completion used for the solve and binds all six operands by canonical
binary64 SHA256. Files are hashed before evaluation and checked again after;
the supplemental aggregate manifest must still equal its validated value.
No incomplete campaign can produce the all-370 report.

Once the input campaign is complete, run the certifier twice and compare the
output bytes. The default result is
`artifacts/flagship_integration/BHSM_N12_GATE7_MIDPOINT_COORDINATE_PULLBACK.json`.
There is deliberately no placeholder production report containing control
data or an unexecuted success claim.

Tests compare complete signed, multi-output, rectangular-coordinate
contractions with independent exact-rational answers. They include a zero
approximate solution where the quadratic error term is indispensable, a
pure cross-block tensor, output maps, extreme exponents, singular solves,
input rejection, and precision restoration. Those controls verify the
implementation; they do not substitute for production data.

## Remaining outward operands

The theorem treats `S`, `M`, `Q`, and any supplied `L` as their exact stored
binary64 values. It does not enclose their physical construction. In
particular the following remain separate:

- physical direction and midpoint-map construction errors;
- action/eigenline/bordered-response errors in Hessian contractions;
- rounding when assembling the signed binary64 pullback;
- physical construction and rounding of causal maps and accumulation;
- the unchanged physical-neighborhood remainder and final radius test.

No tensor norm here is a physical mass, a prediction interval, or a
certificate that any remaining smallness condition passes. No action,
direction, domain, precision of the running contractions, or campaign
fingerprint is changed by this separate verifier.
