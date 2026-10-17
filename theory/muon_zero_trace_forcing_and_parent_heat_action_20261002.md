# Same-source forcing: lifting, output adjoint and first heat action

Continuation of PR465 at `3c6be0cc0e09e73abe01588479db5c88d704016a`,
scientific reference `524ed90689bd5923c249bba2e699abf627e703cd`.
The publication branch is `codex/muon-parent-maxwell-density-review`.
The adopted effective common-A connection is resolved at the preceding
report's scope. Its arrays, four checks, full weak cross, neutral-left and
higher-angular outputs are unchanged. No precursor package, new Gram or
Clebsch selection is required here.

**Outcome:** the requested numerical induced zero-trace/source contraction
was not reached. This step establishes the nonsymmetric lifting correction
and a contracted output-adjoint route, and identifies the precise missing
heat action. The replay is a source/array inspection and exact algebra
control; it executes zero native operator contractions. It must not be
described as an evaluated f_Z, causal return, anomaly or numerical bound.

## Actual consumer and zero-trace space

`ae4_c2_stratified_event_flux_assembly.solve_retarded_event_kkt` consumes
`parent_block`, `parent_child_coupling`, `child_retarded_block`,
`response_operator`, `source`, and `response_target`. It does not produce
parent basis functions, a material trace operator B5, photon source
profiles, a zero-trace frame or an output adjoint. Its finite theorem
implementation forms an inverse and uses adjoint reverse coupling; it
is not executed as a native source solver here. It is insufficient to
force a general dissipative parent relation into a symmetric graph.

The existing `muon_source_weak_extension.weak_extension_contract` supplies
the weak problem on the owned Gauss/BRST complex, with

\[
\mathcal V_0=\{v\in\mathcal V_{\rm owned}^{R}:B_5v=0\}.
\]

Here B5 is the inherited M5/M4 material trace, not either artificial-time
trace. The past temporal face retains the C2 step1222 prefix relation; the
future has its canonical stop. Reset and material trace variations remain
in the inherited first-order form domain. No new endpoint condition is
selected. A compact interior test is mathematically in this kernel when
it belongs to the same owned complex, but no such numerical test direction
or gauge partner is supplied by that KKT consumer. We do not fabricate one
and count it as the solver's retained physical direction.

The saved independent16 columns are child spinor functions. The eight
photon labels are source coordinates, not the dimension of V0. The parent
temporal-face trace includes radial functions and the constraint complex.
Neither frame is substituted for that space. The primary
`heat_zeta_mixed_boundary_launch` also contains a general implicit adjoint,
but its saved seven boundary and 73 geometry-launch directions do not
identify parent photon zero-trace variations.

## Construct forcing before the physical extension

Use an inherited-admissible computational lifting a_L of the SAME boundary
source. This chooses a representation of an imposed trace, not a new
physical continuation. Let K^R denote the full causal weak action from
trial coefficients to test duals, and Z_trial, Z_test represent its owned
zero-trace spaces. With the same coordinates on the two spaces, write

\[
K_{ZZ}=Z^\dagger K^RZ,\quad f_Z=Z^\dagger f,
\quad K_{\gamma Z}=L_{\rm test}^\dagger K^R Z,
\quad f_\gamma=L_{\rm test}^\dagger f.
\]

The unreduced source forcing includes q5_AE4(v,a_L) and any independently
owned affine source row. For distinct trial/test spaces replace Zdagger
by Z_testdagger and Z by Z_trial. No symmetry of K^R is used. Solve

\[
K_{ZZ}z=f_Z,\qquad
a_{\rm eff}=a_L-Zz,\qquad
j=f_\gamma-K_{\gamma Z}z.
\]

For a lifting change a_L'=a_L+Zr, linearity of the same action gives

\[
f_Z'=f_Z+K_{ZZ}r,\quad
f_\gamma'=f_\gamma+K_{\gamma Z}r,\quad z'=z+r,\quad j'=j.
\]

Thus a completed physical extension is not a prerequisite for constructing
the linearized forcing. It is its correction, rather than a preferred
auxiliary radial profile, that determines the extension. This identity
requires the same source and full form; dropping an induced part breaks
the required equality for that part.

Changing only the test lifting L_test'=L_test+ZT gives

\[
j'-j=T^\dagger(f_Z-K_{ZZ}z).
\]

Hence the return is independent of both liftings on the solved relation.
Differentiating these identities requires lifting, basis, pairing, trace,
source and domain jets; none is silently assigned zero.

For a singular chart, compatibility is f_Z in ran K_ZZ. The set of returns
is j0-K_gammaZ ker K_ZZ. It is single-valued exactly when
K_gammaZ ker K_ZZ=0. Otherwise retain the affine Calderon relation. This
adds no regularizer, positivity hypothesis or freely chosen boundary law.
It does not claim continuum closed-range or uniqueness estimates that
have not been established by the physical operator.

## A sufficient contracted output, without a full forcing vector

For an owned output covector p, a numerical adjoint would solve

\[
K_{ZZ}^\dagger w_p=K_{\gamma Z}^\dagger p,\qquad
p^\dagger j=p^\dagger f_\gamma-w_p^\dagger f_Z.
\]

The exact error identity is

\[
(p^\dagger f_\gamma-w_p^\dagger f_Z)-p^\dagger j
=-(K_{ZZ}^\dagger w_p-K_{\gamma Z}^\dagger p)^\dagger z
 -w_p^\dagger(f_Z-K_{ZZ}z).
\]

This identifies the required contractions, not numerical adjoint values.
It allows a matrix-free action/solve and only the consumed source rows;
no explicit inverse or complete parent matrix output is required. The
adjoint is a mathematical dual calculation, not an advanced physical
child-to-parent propagator. The same retarded physical domain is retained.

## First missing induced action

The retained owner is the complete stratified finite-E1 functional with
relative zeta/eta completion. On its co-based quotient write

\[
A=M^{-1}K,\qquad Q(A)=\frac12A^{-1}e^{-\ell_*^2 A},
\]

\[
A_X=M^{-1}(K_X-M_XA),\qquad
A_{ZA}=M^{-1}(K_{ZA}-M_{ZA}A-M_ZA_A-M_AA_Z).
\]

For fixed native length, the Dirac graded contribution contains

\[
c^{D}_{ZA}=-\operatorname{Tr}
\{DQ[A_A]A_Z+Q A_{ZA}\}.
\]

The first absent coefficient is already the contact trace
**c_D,ZA_contact = -Tr(Q A_ZA)**, namely the owned heat-cotangent action
on the source-connected parent image. Its paired derivative is also
unevaluated. The source insertions are supplied in the child/cut arrays;
the action of Q from the parent same-domain pencil on those required
images is not. Neither an unweighted source contact nor the small charged
cross gives this heat-weighted trace.

Only the required contracted entries of Q and DQ, or equivalent
same-domain shifted-resolvent actions with controlled tails, need be
computed. A complete precursor wavefunction, vertex or kernel is not a
prerequisite. A parent restriction must preserve interfaces and the
connected complement:

\[
\Pi_5Q(A_{\rm strat})\iota_5
\ne Q(\Pi_5A_{\rm strat}\iota_5)\quad\hbox{in general}.
\]

Thus an isolated finite child or parent block cannot replace this action.
The source/cross-stratum contact jets must come from the same D_strat.

A smaller exclusion follows for an explicitly material-trace-only term:
if Gamma4 depends on the parent connection solely through the fixed B5A5,
then its unreduced mixed row is

\[
\delta_Z\delta_A\Gamma_4[B_5A_5]
=\Gamma_4''[B_5v_Z,B_5a_L]=0.
\]

Thus that pure child/local term supplies no direct zero-trace forcing.
Its boundary traction remains in f_gamma. This observation applies to the
trace-only term, not to the global heat block with parent/interface
dependence, or to a moving trace/pairing/completion. In particular the full
saved weak source cross must still be retained before native propagation;
its small charged compression is never used to discard it. A conditional
Higgs row is reused only in its owning boundary or coupled-operator slot,
not automatically added to every parent zero-trace row.

Producer: the common-A Dirac weak pencil and source jets on the owned
stratified domain, restricted only after its interface/complement action.
Consumer: q5_AE4(v_Z,a_L,A), or its required output-adjoint contraction,
before K_ZZ^R z_A=f_Z,A and the corrected source return. This is an
uncomputed consequence of the adopted prescription, not an unresolved
common-A coupling or a demand for an entirely new history.

The existing `aether_common_source_frechet_response_v15_99.
frechet_second_response` takes supplied operator and source matrices.
`ae4_current_c2_hs_frechet_hessian.generalized_e1_coordinate_jet` takes
supplied K,M,vertex,contact under fixed M. Neither generates a parent
photon pencil or loads one. The actual primary `HeatPencil.mixed_direction`
retains both moving-mass terms using solves; it is the appropriate existing
arithmetic route if its owned inputs/contracted equivalents become available.
No evaluator was invoked with a convenient finite substitute.

Native length variation, relative zeta/eta, gauge/BRST, contact, pairing,
domain and completion jets required by the actual functional remain
unevaluated. No ell=1 or zero jet is inserted. The positive spectral heat
pencil is distinct from the Lorentz causal gauge weak operator K^R.

## Preserved sources, matching and execution

The source coordinate remains b, beta=T_b b and A_Q=sqrt(2) beta, with
independent Q=T3+Y. The existing full weak source action, neutral-left and
higher-angular outputs, carrier/coframe transport and pointwise weight
remain intact. No shape variation, repeated action-index factor, source
support change or physical-state choice is made.

The saved primitive mechanical and conditional Higgs rows are components
of the same AE4 functional. Their matching subtraction must accompany
the induced calculation before accumulation; a full heat Hessian is not
added on top of its already included local expansion. Strong-within-native
is a subset, never an extra addend. No old row was reevaluated.

The new replay checks 16 source/data hashes, inventories the actual arrays,
and extracts the scoped producer equations by AST without importing their
scientific producers. Four exact symbolic residual identities were checked
for arbitrary nonsymmetric blocks and symbolic dimensions. Run1 is kept;
run2 corrects the initial isolated-parent notation to the full stratified
heat action with interfaces. It repeats only this inexpensive changed
derivation replay. Neither run evaluates a physical operator contraction.
The original four child tests and all earlier production calculations
were not rerun. The current primary heat routines are archived byte-for-byte
as inspected source, with their original locations and hashes.

Reproduction, using an unused output directory:

```powershell
python scripts/replay_muon_zero_trace_forcing.py --output C:\Users\carbe\Downloads\BHSM_muon_forcing_derivation_replay_new
```

The standalone script and its manifest are in
`C:\Users\carbe\Downloads\BHSM_muon_zero_trace_forcing_3c6be0cc_20261002`.
It replays exact algebra/provenance only. The result records target_reached
as false and f_Z,A, z_A, j_ext,A as null. No synthetic finite matrix is
treated as a physical operand. No new tests are claimed for old code;
the executed symbolic controls verify this changed derivation.

Frozen QED/Higgs/weak local values and the original calibration-only
standard uncertainty are retained verbatim in result.json. The selected
local interval is already combined. All six physical native ledger entries
remain null, physical signed-transfer direction count is zero, and
physical a_mu and g_mu remain unevaluated. Exact algebra is conditional
on its stated domain and solvability hypotheses; there is no new native
numerical or theoretical uncertainty enclosure.
