# AE3 family/mode harmonic-energy pullback audit

This unit tests the proposed bridge without fitting electron, muon, tau, or
any quark mass. It reuses the frozen BHSM manifestation labels and the
action-normalized v15.54 Berger spectrum.

## The pullback exists

Let `I` map a current C2 family slot to its stored Berger label. On the round
reset fiber,

\[
 \lambda_{k,j}
 =\frac{k(k+2)-q^2}{R_F^2}+\frac{q^2}{R_F^2}
 =\frac{k(k+2)}{R_F^2},\qquad q=k-2j.
\]

Pulling this spectral observable back gives

\[
 K_{\rm family}
 =I^\dagger(-\Delta_{\rm Berger})I
 =\sum_f\lambda_fP_f.
\]

The three dimensionless spectra are

| sector | frozen roles `(heavy,middle,light)` | `R_F^2 lambda` |
|---|---|---|
| charged lepton | `(0,0),(5,2),(9,3)` | `0,35,99` |
| up | `(0,0),(6,0),(10,1)` | `0,48,120` |
| down | `(0,0),(6,3),(8,2)` | `0,48,80` |

Therefore the pullback is genuinely family-noncentral. This is the important
positive result: the missing noncentral observable need not originate as an
arbitrary matrix in family space.

## The positive-energy killer test

The current C2 fibers all lie over the same action-owned reset geometry and
carry the same `R_F`; no family-dependent radius is present. Any positive
static gradient energy proportional to `lambda`, and any positive frequency
monotone in `sqrt(lambda)`, orders these slots as

\[
 E_{(0,0)}<E_{\rm middle}<E_{\rm light}.
\]

The frozen BHSM roles require the opposite mass ordering,
`heavy > middle > light`. Moreover the proposed ratios relative to the heavy
slot are undefined for a displacement from the scalar zero mode because
`Delta E_heavy=0`. No finite choice of a family-dependent radius can lift a
strict `lambda=0` gradient displacement.

Thus the narrow rule

\[
 m_f=F(\lambda_f,R_F)
\]

with `F` positive and monotone in the current scalar harmonic energy is
falsified as the rest-mass map for the frozen roles. This conclusion uses no
measured mass.

## What remains open

The spectral stiffness is not yet a physical fermion mass. The current action
does not supply a normalized current-C2 manifestation isometry into a field
energy domain, a spinor/Dirac lift of these scalar labels, an evaluated
composite-minus-parent energy displacement or simple fermion pole, a
family-dependent localization scale, or a numerical absolute unit.

A signed binding energy, a nonmonotone parent-relative energy, or another
action-selected localization mechanism is not disproved. It must be derived
from the action and must explain why the zero-harmonic slot is the heaviest;
the historical exponential overlap screen cannot be inserted as that answer.

Accordingly, PR #282 remains correct that no physical family-noncentral mass
operator has been derived, but its search space is sharpened: the harmonic
pullback supplies a noncentral spectral seed, while the missing bridge is the
action energy/pole functional and its manifestation map, not an arbitrary
three-by-three family matrix.
