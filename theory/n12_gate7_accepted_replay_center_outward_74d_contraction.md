# Accepted-replay-center Gate-7 curvature localization and adjudication

Status: `PROOF_COORDINATE_CURVATURE_AMPLIFICATION`.

The frozen accepted one-shot replay center does **not** admit the current
Gate-7 contraction certificate in the retained causal 74-dimensional block
norm with the frozen preconditioner.  The obstruction is a proof-coordinate
curvature amplification, not a claim of physical spacetime instability.

The accepted theorem uses

\[
  Y+Z_1r+Z_2r^2<r,
  \qquad Z_1+2Z_2r<1.
\]

The center residual and Jacobian calculations give the outward bounds

\[
  6.157770409566150\times10^{-7}
  \leq Y \leq
  6.157770409566172\times10^{-7},
  \qquad
  Z_1\leq0.4493650871145146.
\]

It is unnecessary to construct a dense upper tensor for `Z2`.  Every valid
same-center `Z2` must dominate the derivative at the center of the
preconditioned Jacobian in each unit causal direction.  Numerical
reconnaissance localized the owner, after which the certificate evaluated
only accepted node 1 at action-arclength `0.25`, causal coordinate 61, the two
adjacent blocks `[0,0.25]` and `[0.25,0.5]`, their Hermite midpoint identities,
and their complete frozen causal transport.  All action
contractions through order five and all bordered solves were evaluated with
384-bit Arb balls.  The two transported contributions were added before the
norm was taken.  This proves

\[
  Z_2 \geq 3.376470260273630\times10^6.
\]

Dropping the nonnegative `Z1 r` term can only make the self-map inequality
easier.  Nevertheless the necessary quadratic already has

\[
  1-4Y_{\rm lower}Z_{2,\rm lower}
  \leq -7.316611462997230 <0,
\]

so `Y_lower + Z2_lower r^2 - r` is strictly positive for every real `r`.
There is therefore no admissible positive radius for this center and this
frozen global proof architecture.

## Physical localization

The exact selected-eigenvalue cover places the canonical earliest stop in
the certified action-arclength bracket

\[
 [92.30037143976939,92.30513924040065].
\]

The witness at `0.25` is therefore strictly `PRE_ENVELOPMENT`, with signed
witness-minus-hit separation in

\[
 [-92.05513924040065,-92.05037143976939].
\]

The already-defined binary64 proper-time pullback (diagnostic, not interval
authority) places the witness at `1.0405369000633607e-8` and the stop bracket
at approximately
`[1.476952666565266e-4,1.4769526964842944e-4]`.  Thus every parent corridor
from the accepted reset start through the certified first hit contains this
witness.  The obstruction cannot be discarded as post-formation dynamics.

The exact Gate-7 theorem is not over-scoped: it asks for a finite parent
history from the certified reset relation through the earliest stop and no
post-hit segment.  Post-hit child persistence is separately owned by BHSM's
complete-child/persistence certificates and is not transferred by this
parent-history `Z2`.

## Amplification owner

For the first adjacent block the rigorous norm chain is

```text
raw exact rate D2                         1.54501268025558e5
complete Hermite-Simpson residual D2      1.28679611444448e4
after test frame                          1.28816554823449e4
after frozen preconditioner               1.51828458153451e4
after complete causal transport           1.75722763630061e6
```

The second block behaves similarly.  Before global causal transport, the
local preconditioned coefficient has a positive radii discriminant and small
root `1.1550931266155543e-6`, inside the frozen admissible interval ending at
`1.4763242717870264e-6`.  Causal transport is therefore the decisive stage
that destroys the radii inequality.

The sharper channel split explains why.  The raw Hermite-Simpson descriptor
output is only `5.938214949951746e-4`; the frozen descriptor test scale
amplifies it by `1e6`, the preconditioner by at least `10.8927`, and causal
transport by at least `322.306`.  The two terminal descriptor-channel
contributions have norm above `4.0019e6`, while the terminal field-only
contribution is below `6.2614e5`; their signed recombination gives the
`3.3765e6` witness.  The input direction itself has zero independent
descriptor component.  Hence field curvature generates a small descriptor
output that the frozen proof scaling and transport amplify.

At the raw local-rate level the configuration-output contribution is below
`14.653`, the reduced Euler--Dirac field response is
`1.54501267330803e5`, and the descriptor-rate output is below
`6.827e-3`.  Lapse, shift, radius, anisotropy, and constraint terms are mixed
inside the signed action-owned D3/D4/D5 bordered response; this identity does
not define an invariant additive split among them.  None of these numbers is
physical spacetime curvature.

This adjudicates the authorized owner as
`PROOF_COORDINATE_CURVATURE_AMPLIFICATION`.  It obstructs the current frozen
same-center contraction theorem, but is not a nonexistence theorem for a
Gate-7 root and does not authorize another center, trajectory, branch, cone,
coordinate change, or numerical campaign.  Gate 7 and full BHSM remain open.

The reproducible sequence is:

```text
python scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py --stage endpoint
python scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py --stage midpoint
python scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py --compose-linear
python scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py --compose-z1
python scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py --curvature-obstruction
```
