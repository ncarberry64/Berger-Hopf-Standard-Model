# Operation Muon: isolate the Higgs-amplitude force projection

This incremental checkpoint starts from `883523bf77c212804f5f2a74c23ce613b00a9fd5`. It makes a new finite source-projection reduction on the same formed incoming-hi candidate. It does not compute an exterior solution, a physical magnetic moment, or a physical uncertainty. The original `2e-10` guard and every earlier artifact remain unchanged.

## New result

The previously remaining force covector of norm `2.32264984565e-8` is, to a finite numerical remainder, determined by one gauge-invariant Higgs-amplitude force projection in addition to the five existing readouts. Define

```
A u = f,
R u = (B1, B2, B3, Jcomp, Wsheet),
nH = H0 / |H0|,
chi_H = nH.T f_H.
```

`Jcomp` is the normalized axial companion `-sqrt(5) J3`; `Wsheet` is the original central axial Higgs action row, proportional to `delta(|H|² J3)` with its owned measure. `f` is the net right-hand-side load in the original 16-coordinate held-temporal equation. `f_H` comprises its four real Higgs components. **Amplitude here means the internal Higgs norm direction, not a spatial normal derivative.** All coefficients below use the archived coordinate/time normalization.

The independent adjoint solve gives

```
gap = c.T (R u) + kappa chi_H + epsilon.T f,
c = (2.4040e-15, -2.2113e-15, 0.4623857062370151,
     0.7718212718757994, -3.5858503398143644e-6),
kappa = -7.21199006824777e-7,
norm(epsilon) = 3.61603589901269e-13.
```

This is an evaluated finite identity with a retained numerical remainder, not an exact continuum cancellation. The rows have normalized rank 6 and condition number 76.31, stable across relative rank thresholds `1e-8` through `1e-14`. Without the Higgs-amplitude-force row, the residual remains `2.32265e-8`; adding zero wall-temporal reaction does not remove it. Adding all four scalar-force rows makes it about `6.12e-14`, but those scalar loads have not been shown to vanish physically.

A local constraint witness varies `chi_H` by one coordinate unit while preserving all five readouts and zero temporal wall reaction. Its gap shift is `-7.21199007000785e-7`; the original 84-row interior/Gauss residual is `6.15e-13`, temporal reaction residual `3.69e-16`, and readout/force-constraint residual `9.98e-13`. This proves that these **local finite identities** do not determine `chi_H`. The witness is not a physical incident field, a solution of the full exterior, or evidence that the complete physical problem is nonunique. Its minimum-norm construction is used only to exhibit local freedom.

The witness is a linearized direction; its unit normalization is not a finite physical perturbation or a new state assignment.

## Symmetry and numerical tests

For every compact Higgs gauge generator `T_a`, the real-coordinate action has `T_a.T = -T_a`, hence `nH.T T_a H0 = 0`. A radial-amplitude reaction is gauge invariant. Consequently, the linearized Ward identity

```
G_A.T delta f_A + G_H.T delta f_H + delta G.T f0 = 0
```

does not select its value. Moving-generator/base-force contacts are retained in this statement; no zero base force is assumed. The action and exterior equations may fix it, but gauge symmetry alone cannot.

Focused executable checks in `verify_projection.py`:

- Independently diagonalize the same six-dimensional Hamiltonian and track the saved two modes by overlap. The gap-covector change is `9.50e-13`; the `2.32265e-8` residual persists. No new mode or occupation is selected.
- Rebuild the original 84-coordinate Maxwell/Higgs action with 96-point radial quadrature, compared against the hash-verified saved 384-point matrix. The interior quotient rank remains 60, `max|delta K84|=1.28e-11`, `max|delta A16|=3.77e-12`, and the change in `kappa` is `4.93e-16`. This tests integration refinement on the same four radial profiles, not radial-basis or exterior-domain convergence.
- Apply a passive Spin/SU(2) frame rotation to the action, right fields, independent covectors and finite spin operator. Coefficient change is `5.26e-16`; residual-covariance error is `3.07e-16`. This is representation covariance, not a full native moving-domain Ward proof.
- Convert the action, gap and weighted sheet covector together to proper wall time using lapse `1.108427234091954`. Coefficient error is `1.85e-15`; witness-gap error is `6.78e-16`.

The numeric source arrays, actual witness and remaining covector are saved in `RESULT.json`. No eigenvalue width is interpreted as spin splitting or moment.

## Common trial space, force sign and exterior limit

Let `T` select all 20 shared gauge/Higgs wall traces from the original 84-coordinate interior fields. The interior action `K84` already contains the intrinsic Higgs sheet Hessian. If the physical exterior were instantiated, it would first enter as `K84 + T.T Lambda_R T`, with its incident and distributed loads pulled back by the same `T`, before eliminating shared variables or holding the four temporal traces. Separately condensed two-port returns cannot be added without a complement-compatibility proof. This sprint does not insert a synthetic `Lambda_R`.

Using outward **action** conormals, write

```
p_ext = Lambda_R (w - w_inc) - t_inc,
K_int w + p_ext + j_other = 0,
f = -p_ext - j_other
  = Lambda_R w_inc + t_inc - j_other - Lambda_R w.
```

The reported sensitivity is to this net RHS `f`. A sensitivity stated instead for the outward exterior conormal has the opposite sign. `j_other` denotes only separately owned loads; the intrinsic Higgs term already included in `K84` must not be added to it again.

The owned central radial action has density `C_M/2 [e(b_t-s b_rho)^2-r b_rho^2-4 d b^2]`. For the lower exterior face, its action conormal is `C_M(s pi+r b_rho)`, with `pi=e(b_t-s b_rho)`. This is not a Euclidean outward derivative. The source-selected future rule is `omega -> omega+i0` and outgoing/retarded support. These establish conventions, not a numerical zero-frequency return on this candidate. There is no justified outgoing-root or exterior-refinement numerical result to report here.

## Precise remaining physical operand

Conditional on the five readouts, the new leading missing scalar is

```
chi_H = nH0.T delta_B f_H
      = -nH0.T delta_B(p_ext,H + j_other,H)
```

on the same formed-background, held-incident, native/relative domain. Here `nH0` is fixed at the base point. A total derivative of the projected base force additionally contains `(delta_B nH).T f_H0`; it cannot be discarded or counted twice. The complete physical force includes mixed gauge/Higgs return, source incidence and moving-domain contacts. Even an incident source with no directly prescribed scalar component need not have zero *returned* Higgs reaction. The intrinsic `Wsheet` readout is already accounted for and does not determine `chi_H` by itself.

The focused source reconciliation found an existing common interface law, an induced-action owner and a retarded domain selection, but no instantiated incoming-hi `Lambda_R`/mixed Higgs reaction, calibrated `w_inc,t_inc`, or corresponding common-domain current incidence. The earlier exterior-face producer explicitly stores `radial_jet=None`, `complete_temporal_momentum=None`, and `exterior_affine_return=None`. The intrinsic Higgs action has time/angular derivatives on M4; it does not supply an exterior radial Higgs equation by relabeling. The native/relative action must furnish its actual mixed amplitude reaction.

Canonical photon normalization and physical spin/pole residues remain separate. The neutral connection Hessian identifies the Higgs-null electromagnetic direction but explicitly leaves a common temporal/spatial Maxwell residue unresolved. The finite tracked spin pair remains a candidate. A numerical `chi_H` would advance this finite matching problem, but by itself would not establish physical `a_mu` or `g_mu`.

The optional receiving-cut regression was not run: no verified smooth native exterior collar with the same formed background, incident preparation and affine load was recovered. The archived half-line is expressly artificial; the known radial reconstruction is an interior trial on `0 <= rho <= pi/2`. Extending either by hand would not test the requested physical cut invariance. No formation-history reconstruction or broad search was launched.

The owned intrinsic Higgs action explicitly states that its Grassmann-body `J_H=0` does not delete the independent quantum/native load. It therefore cannot justify setting the returned amplitude reaction to zero. Its physical intrinsic angular measure requires an explicit cap normalization; this calculation preserves the archived reduced action normalization and calibrated potential unchanged, without promoting either to a physical residue.

## Reproduce

From the repository root, using an inspected global package directory under the selected interpreter's prefix:

```
python -I -S artifacts/operation_muon_residual_projection_20261120/verify_projection.py --site-packages /inspected/python/Lib/site-packages --output /fresh/result.json
```

The script verifies all 57 input manifest hashes, runs with one numerical thread, blocks network and subprocesses, checks import origins, and writes only the requested output. The original evidence is read-only. Two runs must produce byte-identical JSON. The action reassembly is a single small 84-coordinate calculation per run, with no nonlinear solve or exterior campaign. Source hashes and replay receipts accompany this checkpoint.
