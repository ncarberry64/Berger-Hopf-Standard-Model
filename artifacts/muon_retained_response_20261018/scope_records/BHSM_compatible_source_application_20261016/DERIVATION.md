# Compatible even source and direct lepton wall-current derivative

Norman Carberry / BHSM continuation — 16 October 2026

**Repository anchor:** PR #465, `00f9d781feb96914f5a1226cba70d12ae252837b`.

## Executed result and strict boundary

This continuation constructs the new even-harmonic source multiplication tensors
in the repository's normalized Wigner convention, applies them to the retained
full18 lepton representation, constructs the direct intrinsic lepton wall load
in the original 800-row ordering, and evaluates its first and mixed derivatives.
Independent finite-Fock scalar-action evaluations check those derivatives.

A specific error is demonstrated if the earlier 24-point, degree-five angular
rule is reused for a newly reached degree-six source matrix element. Exact
harmonic multiplication removes that error in this finite source construction.
This is not an assertion that the old rule was wrong for its originally
certified lower-degree Maxwell applications.

The completed Maxwell/geometry arrays were not recomputed, refined, changed, or
numerically composed with a newly solved collider history. Their ordering and
source conventions were reused in the new interface. The exact finite source
operators below are NOT the complete physical collider source, inherited
reference, full moving interface/native source, outgoing derivative or magnetic
moment. Physical packets were not manufactured from the reference Gaussian.
No coupled correction or fresh Maxwell/all-226 after-state was produced.

## 1. Source-defined conventions

The current source files establish:

* Original EM test rows have order `(radial4, field5, internal4, harmonic10)`;
  the field order is material `(At, Ar, A1, A2, A3)`. The even real scalar
  harmonics have degrees n=0,2. A separate 800 rows test connection rates [S1].
* The lepton fiber has 18 components in the order
  `L_L[weak,family,spin2], e_R[family,spin2]`. Canonical spinors are
  `chi=R4^(3/2) psi`; their represented spatial pairing is the canonical Haar
  pairing, not a point Gram [S2].
* The unit-Tr16 anti-Hermitian gauge matrices are G_c. The scalar-space
  multiplication convention is normalized conjugate Wigner D, and the existing
  `_gaunt` function supplies its product coefficients [S3,S4].
* The source audit fixes an exact one-electron/one-positron unpolarized pair
  density, not a quasifree replacement. It supplies actual packet-current
  consumers but no instantiated normalized physical packet in the adopted
  collider preparation [S5,S6].
* The old trace-enriched radial coordinate frame contains two interior functions,
  a source-complement function with its wall value removed, and the independent
  wall lift. Consequently its exact material-wall value is (0,0,0,1) [S7].

Nothing here changes their physical coefficients. Source action normalization
must be supplied once in the actual measure/field maps. In particular the bulk
Maxwell conversion factor cannot simply be appended to the canonical lepton
current. Common unit and action-level matching remain required before adding
numerical loads from independently normalized sectors.

## 2. Construct the even source on the lepton harmonic space

Let phi_(n,m,k)=sqrt(n+1) conjugate(D^(n/2)_(m,k)). For gauge harmonic g and
input harmonic s,

    phi_g phi_s = sum_t C(t;g,s) phi_t,

where the source-owned coefficient is

    C(t;g,s) = sqrt((n_s+1)(n_g+1)/(n_t+1))
               CG(n_s/2,m_s/2;n_g/2,m_g/2 | n_t/2,m_t/2)
               CG(n_s/2,k_s/2;n_g/2,k_g/2 | n_t/2,k_t/2).

The established complex-to-real matrix converts the gauge index to the SAME ten
real n=0,2 labels used by the new EM rows. Spinor coefficients retain the complex
Wigner basis. For the retained input n=0,1 this constructs

    T[h,t,s], shape (10,30,5).

There are 118 nonzero entries above representation roundoff. Output n<=3 is
retained. In particular n=2 acting on n=1 reaches n=1,3. No compression back to
the five input harmonics is made. General `even_multiplication(nin)` retains
output n<=nin+2; it does not assert convergence of a physical Gaussian packet
at any chosen finite nin.

The full18 action vertices tensor with this angular multiplication. Thus one
source matrix acts from 90 to 540 coefficient components, with an explicit
`scalar harmonic major, full18 fiber minor` ordering. Existing code with another
ordering needs a verified permutation, not a dimension-only identification.

### Direct source and the return channels

The actual four right-frame EM wavefunctions are expanded in the same ten real
harmonics; their reconstruction is verified. The first two are degree-zero in
this frame and the last two have degree-two components. In the source-defined
hypercharge coordinate, the latter two have nonzero n=3 output. Dropping that
output also removes the nonzero matrix V_tail^dagger V_tail in the finite
identity-weighted two-insertion diagnostic.

That diagnostic is not a heat contraction or an uncertainty. A physical
propagator, current normalization and native domain still have to be applied.
It establishes which intermediate channels must not be silently deleted.

## 3. A demonstrated, source-specific quadrature failure

The old 24-cell angular rule is exact through polynomial degree five. A new
matrix element can have degree 3+2+1=6:

    <phi_(3,1,1), Y_(2,2,2,imag) phi_(1,-1,-1)>.

Put z1=a and x=|a|^2. The integrand is

    -2 i sqrt(3) (3x-2) (x^2-a^4).

The exact Haar integral is

    -i sqrt(3)/6.

On the 16 hypercube points of the 24-cell rule it equals i sqrt(3)/2; on the
remaining eight axis points it vanishes. The 24-point average is therefore

    +i sqrt(3)/3,

an exact difference of

    i sqrt(3)/2.

This is a concrete aliasing error, not a tolerance problem or an error in an
old coefficient. Both degree-six (98 points) and degree-eight (243 points)
Haar product rules agree with exact CG multiplication for the entire 10x30x5
tensor at about 1e-15. The exact CG map, rather than another radial precision
sprint, is used for this finite source application.

These polynomial certificates do not extend to arbitrary nonpolynomial physical
packets, nonhomogeneous backgrounds or native products without their own degree
or convergence analysis.

## 4. Direct current incidence into the original 800 rows

Write the full18 packet field on the intrinsic wall as

    Psi = U_s a_s + V_s b_s^dagger,
    F_R = (U_1,U_2,V_1,V_2).

Let F_L be its physical left dual on a real chart and its independently
continued analytic left leaf on a complex source chart. The exact finite pair
algebra yields

    M_ij = <eta_i^dagger eta_j - C_ref,ij>
         = diag(1/2,1/2,-1/2,-1/2).

C_ref=diag(0,0,1,1) is the existing finite excitation-subtraction convention.
It is NOT a selection of the continuum primordial sea. The full ordered second
bilinear tensor is retained in the artifacts; products are not factorized into
this first moment.

In the retained material trace convention the direct gauge action vertices are

    Gamma_t,c = +i G_c,
    Gamma_r,c = 0,
    Gamma_a,c = +(i N/R4) alpha_a G_c,  a=1,2,3.

The Hamiltonian temporal derivative has the opposite -iG_c/N sign. The action's
-N cancels the lapse and supplies +iG_c. Introducing another 1/N or N in the
At source would be wrong. The spatial 1/R4 and the action lapse remain once.
The zero Ar vertex is the direct intrinsic material pullback statement; it is
NOT zero radial Maxwell flux, zero radial field, or zero exterior response.

For material-wall radial trace beta_b, real angular test Y_h, and the actual
source measure w, the direct lepton action covector is

    j_(b,f,c,h) = sum_p w_p beta_(p,b) Y_(p,h)
                 sum_ij (F_L Gamma_(p,f,c) F_R)_ij M_ij.

This is the compatible new source incidence. It needs no old odd-band eight-source
return. For beta=(0,0,0,1), only 160 of the 800 value rows can receive this direct
load: wall radial index, four temporal/spatial components, four generators and
ten harmonics. The direct gauge-rate load is zero because this matter vertex
contains A but not its time derivative. Other interface/native terms are NOT
set to zero by this sparsity statement.

For additional radial frames, evaluate their actual wall traces. Do not copy the
old four entries without verifying that frame's definitions.

### Parity does not remove the physical current

The old odd single-field source is orthogonal to the new even test space on
the stated homogeneous reference. A matter current is a bilinear. Odd times odd
is even and can have nonzero projections onto n=0,2. The executable calculation
verifies both facts independently. It therefore does not infer a zero collider
current from the old source's orthogonality.

## 5. Complete derivative of this finite direct-source functional

Every operand above carries explicit (value,h,k,hk) data. No unspecified jet is
filled with zero. The first derivative is the product rule on all factors:

    w, beta, Y, F_L, Gamma, F_R, M.

For example its vertex term is

    w beta Y sum_ij (F_L Gamma_h F_R)_ij M_ij,

and there are distinct measure, trace/test, left/right packet and state terms.
The mixed derivative includes all ordered placements of h and k, including
the genuine mixed derivative of each one factor.

The source mean is held fixed for the specified unpolarized pair in the control,
but the code requires an explicit four-slot jet even for that fact. The Higgs
axis Q_H(H) in the sixteen-column EM inclusion is differentiated through its
normalized projector HH^dagger/(H^dagger H); its left analytic leaf is supplied
independently. No differentiation of a complex source parameter by conjugation
is permitted.

For the actual new inclusion S (800x16),

    j_seed = S^T j,
    (j_seed)_h = S_h^T j + S^T j_h,
    (j_seed)_hk = S_hk^T j + S_h^T j_k + S_k^T j_h + S^T j_hk.

This is distinct from changing the separately fixed adjoint in a contraction.
The old sixteen released amplitudes remain independent; no phase lock or
normal-load fitting is introduced.

### Cauchy normalization must move with the packets

For complete normalized sections the identity is

    sum_p w_C,p F_L,p F_R,p = I4.

Its first/mixed variations are checked separately. A moving Cauchy pairing does
not permit keeping normalized packet coefficients frozen unless their actual
construction makes that legitimate. The tests use explicitly constructed unitary
coefficient paths and matching measure renormalization; they do not QR-normalize
or mix physical particle/antiparticle states in the collider solution.

### Independent numerical check and its scope

The check generator constructs finite normalized full18 sections. They are not
physical electron spectral packets or the adopted collider state. It varies both
packet leaves, Cauchy normalization, source measure/clock, radial wall incidence,
angular test frame, lapse, radius and Higgs-aligned inclusion.

An independent implementation recomputes the finite Fock scalar action directly
with 16-dimensional creation/annihilation matrices, then forms all 800 weak rows.
It uses no derivative routine from the jet application. Four-point central first
differences and their two-direction tensor product check the first and mixed
source derivatives across 816 outputs (800 original rows plus 16 seed rows).

First-derivative errors at step .002 are about 3.98e-14 and 2.23e-14. The mixed
error at step .004 is about 3.93e-12. At the smaller mixed step .001, roundoff
raises the error to about 4.21e-11; this is preserved rather than described as
monotone convergence. Every reported final check is below its 2e-10 CONTROL
threshold. None is a physical outgoing derivative certificate.

Omitting the wall-trace derivative gives a nonzero error about .00278045 in the
constructed control. This is an omission-detection regression, not proof of the
cause of the historical 1.05–6.21% matching discrepancy.

## 6. How this joins the retained response without rerunning it

The code returns an original 800-row action covector and a separate direct
connection-rate contribution. Its projection uses the same 800x16 source layout
as the completed Maxwell block. In the actual repository, consume the existing
Maxwell/geometry arrays unchanged and ADD only the correctly normalized,
verified common-action source contributions. Do not re-add an interaction
already present in those arrays.

The full derivative requires total packet, trace, normalization, collision,
interface and native source jets along the SAME solved physical branch. Held-H,
held-source or held-geometry derivatives are not substitutes. Once supplied,
the direct-source routine includes the full chain rule in its declared chart.
A different coframe or general material incidence requires the corresponding
source vertex/trace map, not a silent substitution of the simple R4 formula.

Native and inherited absolute currents have not been evaluated here. They must
not be omitted just because the finite excitation difference can be computed
without choosing a complementary covariance after physical sections are given.

Only the genuine common source and its full outgoing-domain derivative may enter
one coupled correction. Fresh Maxwell/all-226 residuals then belong to that
updated collider-preparation state, not to the old provisional histories.

## 7. Verification, remaining inputs and publication

Fifteen scoped check groups pass in two byte-identical final executions. Eleven
result/tensor files match byte for byte between `replay_A` and `replay_B`.
The complete physical flags remain false, and a_mu/g_mu remain null.

The physical operands not supplied by this continuation are normalized collider
packet sections and their solved jets, actual collision incidence, full moving
interface/native source derivatives, a reference-state construction or adequate
observable-level bound, and the compatible retarded solution. The binding at
the pinned repository revision also records these distinctions [S6]. No further
experimental beam choices are requested.

No GitHub write or Windows-worktree change was made. The implementation and
compact tensors are supplied for reviewed integration. The local scientific
control computations in this package were actually executed.

## Source references (all at the pinned revision)

[S1] `src/bhsm/interface/electromagnetic_carrier_original_maxwell.py`, blob
`ed357682d038bfe1e8000873dce089746060c708`.

[S2] `src/bhsm/interface/muon_native_dirac_hamiltonian.py`, blob
`7afd78d8ee94a9e0ceafbbd947270349c0820489`.

[S3] `src/bhsm/interface/muon_intrinsic_scalar_discretization.py`, blob
`47868a252ca79325f71d1c7c6608dd54788d2fa5`.

[S4] `src/bhsm/interface/muon_local_source_jet.py`, blob
`c0a70665c021cedfe64db68d32a28d835858783e`.

[S5] `audits/bhsm_collider_incoming_field_current.py` (connector read).

[S6] `docs/muon_collider_preparation_binding_20261016.md` (connector read).

[S7] `src/bhsm/interface/muon_birth_trace_enriched_action.py`, blob
`98b133d88d5b15e1f5858e60ec4a4cf6ce743746`, and
`src/bhsm/interface/muon_parent_retarded_hypercharge.py`, blob
`a9dfca45aa654066ed84b9b72cbe8e6489b027b0`.

[S8] `src/bhsm/interface/muon_native_product_factor_graph.py`, blob
`2ebd62dbf8afedacb7a1c6130f1a9b916f501f16`.

[S9] `src/bhsm/interface/muon_primal_electromagnetic_source.py` and
`src/bhsm/interface/electromagnetic_carrier_mode_reduction.py` (connector reads).

These source-derived finite representation formulas are reimplemented in the
standalone test package. They were not byte-for-byte imports of a local repository
checkout. A local integration must compare the supplied matrices/labels with the
live original owner functions before admitting them on a physical path.
