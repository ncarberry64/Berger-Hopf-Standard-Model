# Adopted cutoff: total branch jets consumed into AE4 heat

Starting revision: `20849fe1f8fae375c011b9eea1b70c400ebe6a1c`.
Adopted-owner scientific commit: `34034e79b821f55e55ebf9109a84c026f100478d`.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.
Branch: `codex/muon-parent-maxwell-density-review`, PR #465.

The October 7 adoption resolves the cutoff **definition**. The implemented
owner is `BHSM-AE4-MODE-FREQUENCY-CUTOFF-2026-10-07`: at AE4 support loss,
`R=gamma J_Sigma+H_impedance`, `E_impedance=sqrt(r/i)`, and `c=ell_star^2=i/r`.
Initial formation is not support loss by default. The previous owner-gap
report remains historical evidence; no arbitrary energy function is needed.

The new mathematical result is the complete form/embedding two-jet and its
exact composition into the existing AE4 moving-lower-limit term. No physical
mode, r/i contraction, support-loss event or native heat trace is supplied by
the arithmetic controls. This continuation inspected retained local history
records without rerunning their producers.

## Full contraction, without a resistance-eigenline assumption

Let K denote an action form pulled back to a common domain, including its
geometric pairing. Let p denote the transported selected line in that same
representation. Derivatives below are total derivatives on the selected
surface. For `n=p^dagger K p`,

\[
 n_x=p_x^\dagger Kp+p^\dagger K_xp+p^\dagger Kp_x,
\]

and

\[
\begin{aligned}
 n_{xy}={}&p_{xy}^\dagger Kp+p_x^\dagger K_yp+p_x^\dagger Kp_y\\
 &+p_y^\dagger K_xp+p^\dagger K_{xy}p+p^\dagger K_xp_y\\
 &+p_y^\dagger Kp_x+p^\dagger K_yp_x+p^\dagger Kp_{xy}.
\end{aligned}
\]

This is applied separately to the total restoring form and kinetic-inertia
form. Their pairing, source, interface and domain derivatives belong inside
K's jets; embedding and event motion belong inside the total p/K jets. A
second event correction would double count them. Neither the frequency
eigenproblem `R p=omega^2 I p` nor `I=identity` is assumed. The second embedding
terms do not generally vanish.
An arbitrary common normalization cancels from i/r only when its complete
derivatives are retained. For complex current J, extend the real-coordinate
Hessian using its existing weights; do not conjugate those weights.

The implementation is a contraction helper, not a physical operator producer.
It does not infer a mode or a domain from supplied finite matrices.

## Exact heat consumption

Write x=v, y=J and

\[
 T(c)=\operatorname{STr}e^{-cP},\quad
 H_P(c)=\operatorname{STr}(Pe^{-cP}),\quad
 H_x(c)=\operatorname{STr}(e^{-cP}P_x),\quad
 H_y(c)=\operatorname{STr}(e^{-cP}P_y).
\]

Substituting the adopted total quotient jets into the **existing**
`muon_native_induced_polarization.lower_limit_mixed` gives

\[
\begin{aligned}
 L_{xy}={}&-\frac{r i_x-i r_x}{2r^2}H_y(c)
           -\frac{r i_y-i r_y}{2r^2}H_x(c)\\
 &+\frac12\left(\frac{i_{xy}}i-\frac{i_xi_y}{i^2}
                  -\frac{r_{xy}}r+\frac{r_xr_y}{r^2}\right)T(c)\\
 &-\frac{(r i_x-i r_x)(r i_y-i r_y)}{2i r^3}H_P(c),
 \qquad c=i/r.
\end{aligned}
\]

In particular the T coefficient simplifies to
`[(log i)_xy-(log r)_xy]/2`. SymPy verifies exact equality to the retained
four-term lower-limit expression. This is an explicit symbolic consumption,
not a numerical native heat contribution. The four heat cotangents retain
the same grading, zero-mode/BRST quotient, domain and connected complement.
They cannot be replaced by heat of the primitive photon/probe block.

The fixed-length contact/pair term, moving Gram, source pullback, interface,
relative-zeta/eta and completion actions remain required. Unknown entries
remain unevaluated. Strong interactions are included through the same bulk
environment/native functional where required; no separate strong addend or
zero value is introduced. Only already-owned local terms may be subtracted
once in the unchanged b/beta/A_Q frame. No old primitive diagnostic is
subtracted wholesale.

## Recovered history and the first action that stops physical assembly

The read-only primary checkout is at the scientific reference on
`codex/n12-current-finite-stop-witness`. Its current mode-response and
backreaction handoffs refer to the same retained 48-node center. Their exact
hashes, shapes, conventions and producer identities are in the new packet.

The mode arrays contain a `(48,98,98)` graph Jacobian and `(48,98,73)`
constraint tangents. Their producer chooses SVD gain vectors of state
transport. The graph producer does use a local action Hessian and a
reference-matched reduced eigenline, but the stored graph Jacobian is the
derivative of the normalized cancelled evolution field. Its inputs do not
include an interface embedding X, a normal-displacement mode or an allowed
bulk zero-trace test. It is not the mechanical impedance action.

The geometry-incidence producer returns state covectors `D_y log R4` and
`D_y log N`. A covector is not a displacement-to-field injection. The saved
backreaction endpoint imposes `signed_descriptor=0` and
`proper_time_density=0`. Its outgoing normal is a descriptor-gradient state
direction, not an outward-support/Noether-flux evaluation. These records do
not establish that the canonical stop is AE4 support loss. No new branch is
chosen from their spectra or singular values.

With the same mode and positive inertia, energy equality needs only

\[
 F(\tau,b)=\langle\psi_\tau,
       (\gamma_\tau J_\Sigma+H_{\rm impedance}-H_{\rm event,drive})
       \psi_\tau\rangle=0.
\]

The independent outward-support-cessation condition remains part of the
event; a balance law or descriptor zero does not evaluate it. No event
locator is executed on an invented residual.

The next constructive action is the **source-restricted mixed bulk/interface
forcing**, not an unspecified scalar energy law:

\[
 f_\psi(\eta)=D_\Phi D_X S_{\rm bulk}^{\rm owner}[\eta,\xi_\psi]
             \in\mathcal V_0^*.
\]

Here xi_psi is the normal-interface direction, and V0 is the allowed
constraint-reduced bulk variation space with zero interface trace. The
sign convention above gives the stationary equation

\[
 H_{\eta\eta}\,\delta\Phi_\psi=-f_\psi,
 \quad Q_{\rm bulk}^{\rm owner}((\eta,0),(\delta\Phi_\psi,\xi_\psi))=0.
\]

Where this stationary-response realization and its same-action interface
matching are established, its contracted bulk impedance is

\[
 z_\psi=Q_{\rm bulk}^{\rm owner}
       ((\delta\Phi_\psi,\xi_\psi),(\delta\Phi_\psi,\xi_\psi)).
\]

This requires only the connected forcing/response, not a full inverse or
impedance spectrum. If a graph chart fails, retain the inherited full
trace/traction relation without a regularizer. The v15.69 fixed-trace gauge
functional exhibits stationary bulk reduction; it does **not** alone prove
the all-sector mechanical matching. No symmetry of a causal response is
imposed by the displayed contracted notation.

The examined state-Jacobian and geometry-incidence producers supply neither
this mixed action covector nor a same-action normal-displacement injection
that would contract their Hessians into it. Existing photon b-source
Clifford insertions vary the connection, not X. Accepted parent-spinor and
primitive photon component solves cannot be relabeled as this response.
Assembly therefore stops **before the response right-hand side is formed**;
no physical complementary solve, support-loss search or heat application
was executed. This is a gap in the examined action realization, not a proof
that the adopted definition is inconsistent or that no other retained
scientific record could provide the action. No additional constitutive
postulate is installed.

## Execution and error scope

Ten new owner checks and two affected legacy contract checks passed. The old
historical materializer and all frozen muon production/check campaigns were
not run. Six additional new contraction/heat-composition checks passed.

One two-dimensional supplied arithmetic control includes explicit form
motion, a nonstationary line, second embedding jets and a prescribed moving
surface. Exact symbolic differentiation and decreasing two-parameter finite
differences check the quotient. Common normalization motion is checked in
the same convention. Its numbers and subtraction residuals are arithmetic
consistency evidence, not physical cutoff values or uncertainty estimates.
No validated finite-difference remainder or continuum error is claimed.

The new replay ran once and wrote
`artifacts/muon_native_support_loss_cutoff_20261007/run_1/`. It records the
input hashes, actual history identities, source/form control actions, exact
composed heat term, event equation, first unprovided action, ownership ledger
and checkpoint. Physical r/i/length/native/Pauli values are explicitly null.
The frozen local interval already includes its local terms; none is added
again and its calibration-only uncertainty is not a total bound.

Reproduction uses a fresh directory and the read-only retained history:

```powershell
C:\Python314\python.exe scripts/replay_muon_native_support_loss_cutoff.py --output <fresh-directory>
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_native_support_loss_cutoff.py
```

The standalone Downloads launcher requires the retained repository/history;
it is not a physical muon-number program. Source snapshots and raw/canonical
hashes preserve executed identities. The first owner push encountered two
GitHub internal-server errors; an ordinary retry with HTTP/1.1 succeeded and
the owner head was verified. No reset, force push, cleaning or cache overwrite
was used.
