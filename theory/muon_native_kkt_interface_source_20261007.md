# Direct owner KKT interface source and downstream continuation

Starting HEAD: `da155f24a2663d1570d9d78acc9771197fc16670`.
Branch: `codex/muon-parent-maxwell-density-review`, PR #465.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.

This milestone implements direct scalar-action differentiation of the single
interface-source KKT column and follows an explicit finite control through
Pauli projection. It does **not** evaluate a physical BHSM `h_psi`, `z_psi`,
cutoff, native heat, or muon magnetic moment. The bounded producer audit finds
historical callable actions/KKT residuals, but no examined callable that binds
the selected current AE4 support-loss displacement, stationary base,
multiplier coordinates, domain and action dual. Every missing physical
operand and signed sector remains `UNEVALUATED` in the packet. This is not an
exhaustive absence theorem or a physical nonidentifiability claim.

## Source differentiation in the action dual

For the prescribed normal displacement `dX/ds|_0=xi_psi`, the only boundary
kinematic coordinates remain the existing three traces, two canonical
momenta and two dynamic fluxes. The existing producer retains

\[
b_\psi=\begin{bmatrix}
T u_\psi+(D_\psi T)q\\
D_\psi P\\
D_\psi F-D_\psi G-D^2P[X,u_\psi]-DP[D_\psi X]
\end{bmatrix}.
\]

The new module consumes a **complete supplied scalar weak action**, one
source coordinate, signed sectors and uneliminated constraints. It never
accepts cached `F_p` or `g_n` as a physical source and selects no launch,
descriptor, SVD vector or right inverse as `xi_psi`. Provenance strings and
coordinate metadata are required, but do not themselves prove ownership.
Its numerical backend is an exact rational finite real/explicitly realified
action chart, followed by an Arb replay. A complex physical weak form requires
its own justified realification and dual pairing; it is not silently narrowed
to the real Euclidean chart.

With `L=S_bulk^owner+lambda^dagger R`, differentiation holds both `eta` and
`lambda` fixed:

\[
h_\psi=\partial_s\binom{L_\eta}{R}
=\binom{S_{\eta s}^{\rm owner}+R_{\eta s}^\dagger\lambda}{R_s}.
\]

The implementation independently differentiates this full residual and
checks the displayed decomposition. It differentiates only the consumed
source direction. No generic second source/constraint tensor is formed.
The response `lambda_s` is not in this partial derivative.

The KKT matrix is derived from the same scalar Lagrangian:

\[
H_{\rm KKT}=\begin{bmatrix}
L_{\eta\eta}&R_\eta^\dagger\\R_\eta&0
\end{bmatrix},\qquad
H_{\rm KKT}\delta_\psi=-h_\psi,\qquad
\delta_\psi=(\delta\eta_\psi,\delta\lambda_\psi).
\]

It rejects a nonstationary supplied base. It retains `lambda R_etaeta`,
`R_s`, `lambda R_eta,s` and `lambda R_ss` when those terms occur. Constraint
rows are independent of their multipliers; multiplier terms are inserted
only through `lambda^dagger R`. Signed sectors cannot be omitted or repeated,
and a declared zero requires explicit action provenance. Zeros in the finite
fixture mean absent sectors **by definition of that control**, not physical
zeros. All nine physical sector groups remain unevaluated separately.

The exact and Arb solvers apply only one source column, without an inverse.
Both retain the multiplier response and replay the full owned residual.
The reduced curvature is

\[
z_\psi=L_{ss}+h_\psi^\dagger\delta_\psi.
\]

An independent second derivative of the full action along
`(eta0+epsilon delta_eta,lambda0+epsilon delta_lambda,s=epsilon)` equals this
Schur expression. No positive-definiteness requirement is imposed on the
indefinite KKT matrix. Positivity needed for the physical mode-frequency
cutoff belongs to the reduced allowed tangent and total `r,i` contractions.

An arbitrary invertible residual row map `C` gives the same solution of
`C H delta=-C h`. The impedance still contracts the **owner** covector `h`
with that solution. The non-diagonal finite row-mixing control shows both
response invariance and the changed, incorrect naive `(C h)^dagger delta`
contraction. No consumed physical row-dual map is presumed or needed for
the direct owner path.

## Controls and immediate downstream use

The primary finite action has two fields, one nonlinear source-dependent
constraint and the nonzero stationary multiplier `lambda0=3/2`. Its source
produces nonzero `R_eta,s`, `R_s` and `R_ss`. The existing seven-port producer
uses all shape, conormal and momentum-rate operands. The moving-port check
also retains `(DB)lambda+B delta_lambda` with a nonzero first term.
No historical producer or physical branch solver runs.

A second independent finite test action gives
`h=(13,7,4)`, `delta=(-13/5,-7/5,4)` and `z=-23/5`; its full quadratic action
agrees exactly. This negative *control* curvature specifically verifies
that the KKT routine does not impose blanket positivity.

The primary finite family has explicit `v,J` action dependence while its
stationary base remains exactly fixed by definition. One symbolic KKT column
therefore supplies its actual `z,z_v,z_J,z_vJ` jets. Separately prescribed
finite surface/inertia sectors give the total contractions

\[
r=\langle\psi,\gamma J_\Sigma\psi\rangle+z_\psi,
\qquad i=\langle\psi,I\psi\rangle,\qquad c=i/r.
\]

The new downstream composition consumes the existing total-branch quotient
and lower-limit machinery, including

\[
\frac12\big[(\log i)_{vJ}-(\log r)_{vJ}\big].
\]

It continues through fixed plus moving-length AE4 heat, relative zeta/eta,
the retained local subtraction, `R_ind`, one completed photon-response solve,
paired electron/muon heat and the existing Pauli tensor projection. Missing
derivatives are not inferred from `z` itself. Each provider must share the
declared action/domain/source/branch identity, and unknown downstream stages
retain their missing-input lists. The strong ledger term stays a subset of
native heat and is not summed a second time.

The complete downstream **control** uses expressly prescribed one-dimensional
heat and photon actions and two finite family heat cotangents. Its scalar
`R_ind` is a full photon form only within that defined one-dimensional
control; a physical mixed scalar cannot reconstruct the missing native
photon operator. The API continues supplied directional providers and does
not generate their physical actions or domains. A finite difference of the
integrated E1 control independently checks its moving-cutoff mixed heat.
Every control report leaves physical `a_mu`, `g_mu` and promotion null/false.

## Execution, records and remaining operand

The targeted and adjacent muon suite passes 100 tests, including 56 new tests.
The final two fresh replays (`run_3`, `run_4`) have byte-identical `control.json`, `result.json` and
`input_hashes.json`. The packet records the starting revision, owner/source
identity, seven-port column, stationary base and multipliers, all consumed
KKT/source blocks, response, owned residual, reduced curvature,
direct-vs-Schur equality, row controls and the continued finite chain.
`owner_audit.json` inventories eighteen inspected producer groups.

The initial 73-test regression and `run_1`/`run_2` controls are preserved.
Independent review then reproduced silent interval midpoint conversion,
nonfinite provider acceptance and an incomplete-Pauli `KeyError` in the new
downstream input guards. Those cases were corrected, independently rechecked
and covered by 27 additional tests before the final regression/replays.

Arb error scope is rounding of the supplied exact finite entries only.
Downstream arithmetic uses binary64 without an enclosure; interval inputs
are rejected instead of reduced to midpoints. These are not physical,
continuum, domain, history, heat-tail or signed-transfer error estimates.

Status, forbidden-claim, frozen-integrity and precision audits pass.
Public readiness retains one inherited hygiene failure: the already tracked
`artifacts/muon_first_order_complement_20261006/run_2/first_order_compact_reduction.npz`
is 11,125,650 bytes, above the audit's 10 MiB threshold without its reviewed
retention entry. The audit failure is recorded, and that historical artifact
is preserved.

The next physical computation still requires the same-owner moving-interface
weak-action pullback on the selected `xi_psi`, its support-loss stationary
base and multipliers, and the complete directional source/Hessian blocks.
The callable historical local/N3 KKT systems have different fixed-boundary,
event or heat owners; they are not substituted for this current AE4 owner.
When those operands exist, the implemented path immediately consumes them
and then requires the matching surface/inertia branch jets and native
heat/completion/response inputs. It does not stop intentionally at `h` or `z`.

Reproduction, always into a fresh directory:

```powershell
python scripts/replay_muon_native_kkt_interface_source.py --output <fresh-directory>
python -m pytest --noconftest -q tests/test_muon_native_kkt_interface_source.py tests/test_muon_native_kkt_downstream.py
```

No full Gate7 campaign, 73-launch recomputation, `jmath`, common-A, optional
seam, local-QED change or primitive photon refinement is performed.
