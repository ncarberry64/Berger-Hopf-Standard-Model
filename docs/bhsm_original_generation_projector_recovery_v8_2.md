# BHSM v8.2 original generation projector recovery

## Steering correction

V8.2 recovers the original BHSM generation architecture before considering
any new cap-fermion action. The smooth hyperspherical background retains its
role as common geometry, measure, scale, and interface response. The finite
boundary-mode architecture carries the family labels:

\[
N_{\rm family}=1\ {\rm base}+2\ {\rm excitations}=3.
\]

No domain-wall cap-fermion action is committed, the field ledger is not
replaced, and the original mode architecture is not removed.

> BHSM is formulated as a deterministic geometric boundary theory in which particle and quantum-field descriptions are intended to emerge from classical nonlinear modes, topology, and interface response. Standard QFT is used as an effective observable correspondence, not assumed to be the fundamental microscopic ontology. Accordingly, the present campaign first tests the original finite BHSM boundary-mode generation architecture before introducing additional quantum-field primitives.

The causal order used here is geometry and topology, then the classical
boundary-value problem, then discrete resonances and modes, and only then
effective particle and QFT descriptions. Differential operators, spectral
projectors, and self-adjoint domains are admissible when they arise from the
classical geometric action or its Hessian; resemblance to a microscopic QFT
operator is not an action source.

## Provenance and mode assignments

The repository supplies the charged-sector ledger in `src/constants.py` and
implements its operational selection in `src/mode_selection.py`:

| Sector | Base/heavy | Excitation 1 | Excitation 2 |
| --- | --- | --- | --- |
| charged lepton | \((0,0)\) | \((5,2)\) | \((9,3)\) |
| up | \((0,0)\) | \((6,0)\) | \((10,1)\) |
| down | \((0,0)\) | \((6,3)\) | \((8,2)\) |

With \(q=k-2j\), their nonzero \((q,j)\) labels are respectively
\[
(1,2),(3,3);\qquad (6,0),(8,1);\qquad (0,3),(4,2).
\]

The symbolic boundary scaffolds are
\[
\Omega_\ell=-q+2j=3,\qquad
\Omega_u=q-2j=6,\qquad
\Omega_d=q+4j=12.
\]
`src/boundary_derivation.py` explicitly classifies these rules as
`ACTION_LINKED`, not `ACTION_DERIVED`: their targets contain an already
supplied `family_index=3`.

The finite-sector theorem calls the ladder `reference mode + two excitation
slots` and classifies it as a strongly supported candidate whose rank-three
closure remains to be derived. The v6.2 triality theorem constructs exact
cyclotomic projectors
\[
P_a=\frac{1+\omega^{-a}T+\omega^{-2a}T^2}{3},\qquad a=0,1,2,
\]
and conditionally identifies those three abstract slots with the Berger
ladder through the exact \(C_3\) Fourier transform. This rejects multiplying
triality and Berger triplications into nine. It does not turn the selected
mode triples into an action-derived kernel.

The v7.0/v7.1 master-action ledgers settle the authoritative type:
triality projectors are representation-derived conditional on their carrier;
sector projectors are finite inputs; generation/mode projectors are
conditional retained spectral subspaces. The stored mode ledger is a finite
independent projector input fixed before comparison.

## Strongest boundary-selection operator

On the formal Berger basis \(\{|k,j\rangle:k\ge0,\,
0\le j\le\lfloor k/2\rfloor\}\), the strongest existing diagonal boundary
operator is
\[
\mathcal B_f|k,j\rangle
=\left[(\Omega_f(k,j)-t_f)^2+
\chi_{\rm parity\ violation}(k,j)\right]|k,j\rangle,
\]
with targets \(t_f=(3,6,12)\) and the stored sector parity rules. The base
\(|0,0\rangle\) is separately declared as the protected reference slot; it
does not solve the nonzero excitation equation.

For each stored orthonormal triple
\(\{u_{f,0},u_{f,1},u_{f,2}\}\), the exact finite projector is
\[
P_f^{(3)}=\sum_{n=0}^2
|u_{f,n}\rangle\langle u_{f,n}|,
\qquad {\rm rank}\,P_f^{(3)}=3.
\]

This proves that the original projector can be reconstructed. Its honest
classification is

`INDEPENDENT_FINITE_GENERATION_MODULE_INPUT`.

Accordingly, v8.2 emits

`BHSM_ORIGINAL_THREE_SLOT_GENERATION_PROJECTOR_RECOVERED`

and

`BHSM_THREE_GENERATION_BOUNDARY_MODULE_TYPED_AS_FINITE_STRUCTURE_INPUT`.

It does not emit the action-derived rank-three verdict.

## Exact root count and higher modes

Substitution of \(q=k-2j\) gives the complete nonzero root sets.

For charged leptons,
\[
k=4j-3,\qquad j=2,3,4,\ldots,
\]
so the roots are
\[
(5,2),(9,3),(13,4),(17,5),\ldots .
\]

For the up sector,
\[
k=4j+6,\qquad j=0,1,2,\ldots,
\]
so the roots are
\[
(6,0),(10,1),(14,2),(18,3),\ldots .
\]

For the down sector,
\[
k=12-2j,\qquad j=0,1,2,3,
\]
giving four nonzero roots. In increasing \(a=1\) Berger proxy action they
are
\[
(6,3),(8,2),(10,1),(12,0).
\]

The corresponding first proxy action values are
\[
\begin{array}{c|rrrr}
\ell&35&99&195&323\\
u&48&120&224&360\\
d&48&80&120&168
\end{array}.
\]

The implementation returns the first two nonzero roots through the default
argument `n_modes=2`. That number is the finite three-slot input; it is not
the result of the boundary equation. The cutoff `k_max` is a computational
scan boundary, not a physical spectral cut. The higher labels obey the same
regular Berger-label condition and stored parity rule. No chirality,
anomaly, seam-matching, self-adjoint-domain, finite-action, or physical-gap
theorem excludes them.

Thus:

- boundary root count does not derive \(1+2\);
- the finite algebra provides exact abstract \(C_3\) projectors but only a
  conditional identification with the physical mode triples;
- the supplied projector has rank three as a typed input;
- the variational domain does not remove the displayed higher roots;
- the proxy action ordering does not supply an action-selected isolated
  two-excitation cluster.

## Action-domain and interface response

The intrinsic \(M_4\) fermion action is well defined on a supplied
maximal-isotropic/self-adjoint Dirac domain. The mode projectors are declared
spectral-domain preserving. This is a formal finite-input compatibility
statement, not a common operator theorem: the authoritative fermion bundle
contains the supplied family factor, while the \((k,j)\) modes remain a
Berger scalar proxy ledger.

The one-of-two up-sector virtual-door rule is a later candidate dressing. It
does not select the three generation slots or exclude higher roots.

The full Brown--York tensor and first shape response are available, but a
mode-dependent family response would require
\[
R_{f,ij}=\int_{M_4}\pi_{\rm env}^{ab}
\left\langle u_{f,i},
\frac{\delta\mathcal A}{\delta h^{ab}}u_{f,j}
\right\rangle d\mu_h .
\]
The mode stress inside this expression is undefined because the scalar proxy
modes are not an action factor of the localized fermion bundle. Replacing it
by a universal scalar times \(I_3\) would repeat the invalid v8.0 route.
Inserting the historical overlap law would also violate the required
action-response test.

Therefore all three response matrices, their ranks and singular values, the
charged-sector mass ratios, and \(V_{\rm CKM}\) remain undefined. A diagonal
response is not assumed, and off-diagonal incidence is not invented.

## Freeze, comparison, and completion

The deterministic artifact freezes the original doctrine, historical mode
assignments, boundary operator, rank-three finite input, exact higher-root
sets, action-domain boundary, absent mode response, absent ratios, absent
CKM result, and falsification condition before comparison. Historical overlap
ratios, the virtual-door dressing, and the historical CKM screen are recorded
only as unrelated comparison-era objects and do not select or retune the
projector.

The family count is three within the finite typed BHSM module, not a
parameter-free action prediction. No fourth-family exclusion and no distinct
action-derived falsifiable observable follow. RB-15 remains
`BLOCKED_EXACT_OBJECT_PROVED`; RB-16 remains downstream, and the release gate
does not close.

The domain-wall route remains a paused, non-authoritative fallback. The next
exact object is an action/domain theorem selecting exactly the stored base
and two excitation modes while excluding all displayed higher roots.

Layer G is the deterministic geometric-core problem. In this campaign its
finite projector is recovered, but its higher-mode exclusion and
mode-specific interface response remain blocked. Layer Q is the later map
from geometric dynamics to effective quantum states, probabilities,
spin-statistics, scattering, decay, and radiative observables. Its status is

`OPEN_EMERGENT_QUANTUM_CORRESPONDENCE`.

That open correspondence does not by itself invalidate the classical
projector campaign, but it prevents a claim that BHSM has already
demonstrated a full replacement for quantum theory. The v7.2 Standard Model
observable map is retained as `GEOMETRIC_TO_QFT_CORRESPONDENCE`; its gauge
and Yukawa parameters are `EFFECTIVE_QFT_PARAMETER`, `G_F` is
`EMPIRICAL_CALIBRATION`, and the legacy overlap/CKM rules remain
`HISTORICAL_SCREEN`.

The singular v8.2 verdict is

`BHSM_ORIGINAL_GENERATION_PROJECTOR_BLOCKED_BY_UNEXCLUDED_HIGHER_MODES`.
