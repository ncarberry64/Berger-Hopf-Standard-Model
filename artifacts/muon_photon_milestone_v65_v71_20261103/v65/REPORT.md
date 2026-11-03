> Recovery, 2026-11-03: interpreter coverage was explicitly confirmed. Isolated replay reproduces both saved outputs byte for byte, and seven focused tests pass. Final archive promotion additionally requires the bundled replay recorded in the checkpoint receipt. Historical recovery evidence remains preserved.

# v65: an evaluated photon-current component and its Gauss obligation

The original eight photon test directions have been recovered and applied to
the saved action coefficients. The charged connection contributes a nonzero
magnetic-current Hessian and a nonzero covariant angular divergence. Direct
classical Higgs and neutral-source contacts cancel in their proved scope.
This constructs a concrete part of the projected-current operator. It does
not yet supply the complete current, event trace or reconnection history.

The previous v64 milestone was pushed with explicit approval and verified at
[commit 1ef75378916644c34229da5c24148b85d9fba868](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/commit/1ef75378916644c34229da5c24148b85d9fba868).
This v65 checkpoint is local; the v64 push approval is not extended to it.

## Recovered source and actual calculation

The eight retained lifts were absent from the sparse working files but present
in the current worktree's base Git object, commit
`4a650a61a6e0e4cd3674650c399b435c106d66c3`. Their original NPZ hash is
`146435df28178967c321c0aa7e89a1511395d196f96b8715532aa98e3e312c2b`.
It was recovered read-only into this artifact. No Downloads Git-log access,
new packet, new quadrature or old campaign was used.

The owned real coefficient transform and derivative matrices retain the
original 20 scalar harmonics, 400 gauge coordinates and eight source columns.
Only the existing coefficient matrices are constructed; no angular grid is
generated. The retained scalar one-form profiles omega have Haar Gram I8.
Their Higgs-aligned internal direction is

    s_H = sqrt(16/3) q(H),   s_H.s_H=16/3,
    delta A_i = s_H omega_i.

The radius/lapse/gauge/Higgs values and their 22-by-189 pullback come from the
same v20 saved initializer used by v25-v64. In particular the spatial A_i
already includes `M_i (lambda-1)` once, as `field_pullback` specifies. The
mechanical contribution is not added again in the curvature variation.
These coefficients are not a newly admitted physical field or an external
LSZ photon. The physical common Cauchy/event background remains unconstructed.

## Exact projected current on a regular patch

Let P^(mu nu) be the original antisymmetric curvature momentum density,
defined so that the Maxwell first variation is
`delta S_M=(1/2) integral <P^(mu nu),delta F_mu nu>` in the chosen material
coordinates. P includes the original Lorentz signs, metric/Jacobian and
normalization. For a fixed-background neutral source `delta A_mu=s alpha_mu`,

    delta F_mu nu = s (d alpha)_mu nu
                    +(D_mu s) alpha_nu-(D_nu s) alpha_mu,

    delta S_M = integral [<s,P^(mu nu)> partial_mu alpha_nu
                           +<D_mu s,P^(mu nu)> alpha_nu].

Thus the bulk projected row and its natural boundary conormal are

    J_gamma^nu = -partial_mu <s,P^(mu nu)>+<D_mu s,P^(mu nu)>
               = -<s,D_mu P^(mu nu)>,
    boundary work = integral_boundary n_mu <s,P^(mu nu)> alpha_nu.

This is an action-derived application, with no extra charge or Haar factor.
It distinguishes the projection derivative from the covariant current. In a
total source response, vary s, P, D, the measure, normal and source/readout;
the induced changes are not the same as a direct fixed-background insertion.
For a moving boundary or retained/released edge, its transport and conormal
terms remain. A sharp indicator is not used to split arbitrary weak flux.

The same-domain classical Higgs current is `j_H=B(H)^T p_H` on the intrinsic
boundary only. Since `B(H) s_H=0`, its direct photon projection vanishes for
arbitrary p_H, and

    delta(B s_H) = (delta B)s_H+B(delta s_H)=0.

This includes source-axis motion. It does not eliminate ordered Higgs/native
correlations in rho_rest, and does not turn boundary Higgs momentum into an
interior charge source. The actual projected boundary compatibility still is

    s_H^T [b_Gamma Pi+rho_Gamma,rest]=0,

with inherited/released flux and all matched terms retained.

On a regular Higgs-frame patch, the charged-connection contact from v64 has
zero variation under a **direct** neutral insertion: invariant pairing gives
`<s,[A,s]>=0`. Likewise `[s alpha,s beta]=0`, so the second curvature contact
vanishes for two fixed-H neutral insertions. Charged-field, Higgs-frame and
moving-domain responses induced by the physical photon remain present.
Neither result proves complete matched-source cancellation.

## New numerical component

In the retained right coframe, with the full saved angular-constant A_i,

    curl omega_i = 2 omega_i+epsilon_ijk E_j omega_k,
    V_i = delta B_i = s_H curl omega_i
                         +epsilon_ijk [A_j,s_H] omega_k.

The second term is orthogonal to s_H. The original Maxwell curvature
variation independently reproduces every coefficient of V. Absent temporal
and radial jets are marked NaN in that check; only the magnetic component,
which does not consume those operands, is used. They are not supplied as zero.

The full magnetic-curvature Gram `K_AB=<V_A,V_B>_Haar` splits as follows:

| Component | Eigenvalues, each with multiplicity four |
| --- | --- |
| Neutral curvature Gram | 48, 48 |
| Charged-connection contribution | 2.05669022238486, 3.42781703730810 |
| Sum K | **50.0566902223848, 51.4278170373081** |

These are local coefficient values, not energies, physical masses or a_mu.
In the original magnetic action the corresponding direct Hessian density is
`-MAXWELL_TO_CAP d(rho) K`, including the owned radial source factors and
material integration. No radial interpolation, energy integral, inverse,
retarded history or Euclidean positivity inference has been performed.

The first derivatives in all 22 local fields and their saved 189-coordinate
pullback are saved. Their eventual contraction with a **physical** total
source jet also needs its actual background/domain variation. A partial
envelope and nonconstant H/A can mix higher harmonics; these eight columns
are not asserted to close a physical truncation.

## The constraint that remains visible

The recovered omega obeys ordinary coexactness, `sum_i E_i omega_i=0`.
Its covariant angular divergence on this initializer is nevertheless

    G_A = sum_i [A_i,s_H] omega_i,A,
    s_H^T G_A=0.

The evaluated 80-by-8 map has norm **3.311950259195615** and singular values
`1.43411653026693` (four) and `0.827987564798904` (four). Hence none of these
eight source directions is annihilated by this covariant angular map.
The electromagnetic projection of this particular load vanishes; its charged
components do not. This is a concrete constraint operand, not proof of
inconsistency or a count of physical states.

If these angular profiles enter canonical electric momentum, the actual
density/radial coefficients and the full linearized interior Gauss equation
must also be applied. In material density variables its normal return has
the form

    (partial_rho+ad A_rho) delta Pi^rho
      = -D_i delta Pi^i-[delta A_m,Pi^m]-delta rho_bulk,

with the original inherited entering flux, coordinate/measure pullback and
event/edge terms. The bracket term includes the radial component as well.
The boundary conormal produced by this equation then enters the intrinsic
Higgs/native/interface row. It cannot be cancelled by placing boundary Higgs
momentum into the interior. No electric momentum or bulk native current has
been chosen to complete it.

For a regular same-domain connection, adjoint radial parallel transport is
an isometry in the unit-Tr16 internal pairing. Thus this first-order return
can be applied or bounded without a dense inverse, retaining its entering
term and the integral of the complete forcing. That identity does not assign
the missing entering flux or remove any current. The saved radial connection
samples are small but nonzero; they are not set to zero or treated as a
certified continuum bound.

## Outcome and next calculation

The new result identifies and evaluates a compulsory charged part of the
photon-current operator. It also identifies an exact direct-insertion
cancellation. Both help assemble the electromagnetic trace/current system
needed by the reconnection test, without assuming reconnection or choosing a
new child state. The nonzero angular Gauss load is an explicit reason to
construct its radial/entering response before treating a bare photon lift as
a constrained event perturbation.

The smallest next construction is the **source-projected radial Gauss return
for these eight load columns**, including the known material coefficient
maps and the symbolic complete bulk-current/entering terms, followed by the
same-domain boundary conormal test. Existing v43/v44 arrays contain 49 radial
evaluation points and the original profiles, so no new resolution is needed
to evaluate a coefficient component. A naive source-column representation
would hold 49x4x20x8=31,360 real values (about 245 KiB); field/source derivative
storage can be streamed. This is a scope estimate, not a launched solve or
error enclosure. A physical application additionally needs the actual
common event trace and complete matched current; initializer interpolation
cannot supply them. A broader nonlinear/history solve remains unlaunched.

Actual connectivity change, released energy, newly formed child modes,
physical elastic F2 and total uncertainty remain open. The adopted 500 MeV,
100 fm, +/-1000 fm unpolarized preparation, independent left data, symbolic
inherited moments, nine matched placements and single overlap subtraction
are unchanged. No native source is set to zero. The t=2^-9 admitted temporal
baseline remains distinct from the later conditional wall diagnostic and
from a physical state. The 2e-10 physical guard is unchanged.

## Reproduction

```text
C:\Python314\python.exe -I -S isolated_muon_runner_20261103.py produce --artifact . --out fresh_run --receipt fresh_run_invocation.json
C:\Python314\python.exe -I -S isolated_muon_runner_20261103.py tests --artifact . --out fresh_tests.xml --receipt fresh_tests_invocation.json
```

The checkpoint contains the exact recovered source, frozen owned
coefficient/curvature functions, initializer jets, provenance, producer,
tests, results and receipts. Fifteen consistency checks have maximum defect
4.98e-14; this is method consistency, not physical uncertainty. Only changed
operators are tested. The bundled runner is for the explicitly inspected Dads
Python314 installation and package roots. It disables site initialization,
.pth processing, custom PYTHONPATH, pytest plugin autoload and repository
conftest loading. Package origins and subsequent imports are bounded to those
roots and the explicitly owned artifact. It does not certify other environments,
custom startup sources or the host as a whole. Invocation receipts record the
actual paths and source hashes. No additional worker or broad audit is used.
