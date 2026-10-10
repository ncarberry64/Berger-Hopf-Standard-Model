# C2 face placement and continuation of the saved local source

Continue PR465 at `36a4ea6fcfc005a75bf385cf55d4b00e6f171705`;
scientific reference `524ed90689bd5923c249bba2e699abf627e703cd`.
This packet preserves the earlier 16-column frame, constant coefficient map,
transported forms, n2 contact, principal/flux arrays and frozen local ledger.
It does not evaluate an exterior response, parent weak solution, native E1
contraction, shifted resolvent or physical anomalous moment.

## Actual temporal faces

The earlier description of both cached faces as artificial cuts is corrected.
`recon_n12_c2_global_canonical_stop.py` starts from the certified C2
`BHSM_N12_C2_LOHNER_STEP_1222.npz::endpoint_predictor_center` and resets its
local arclength to zero. The high-order-center producer starts from the same
1222 frontier. The saved 48-node geometry/source interval is therefore:

* **Past:** an artificial cut at the C2 step1222 frontier, downstream of the
  inherited E1 reset. An existing C2 prefix precedes it; no pre-E0 arm is added.
* **Future:** the saved numerical representative of the actual canonical
  first stop/domain exit. It is not an artificial cut requiring an invented
  future tail. This center identification is not a new whole-history interval
  first-hit certification.
* **Material boundary:** rho=pi/2 is spatial and separate from these faces.

The frontier-to-stop proper duration is 0.00014753362308861907 in the retained
action coordinates. The weighted difference between the prefix endpoint
predictor and cached initial center is 6.0689642906101e-18, compared with the
saved endpoint tube radius 1.0183219028996276e-10. This is a center-provenance
comparison; it is not a new trajectory solve. The initial logR values agree
at binary64 precision. The saved terminal descriptor is zero. The raw local
backreaction arrays were inspected and their states, proper times, logR and
log lapse exactly match the downloaded parent inputs; their producer was not
rerun.

The local current center differs from the Git reference cache: SHA-256
`6d966cb6c731dc545d520522f897b82250e0a7817c0447f262363d6d22858635`
versus reference
`086c41068b9f3a6c0e5f8040b661202e067d017c909a381010e45ff352498d00`.
Their later states differ by at most3.959810044307233e-6 in raw coordinates
and their terminal arclengths by4.490726638550768e-6. They are not asserted
scientifically interchangeable. This calculation consumed only the initial
state and terminal descriptor; those are exactly equal. A compact two-face
snapshot of the newer local cache is now the replay input, with its full
producer identity recorded separately. The initial evaluated manifest and
reference are preserved, and no unchanged source calculation is repeated.

At the past cut, core-outward orientation is -d_tau and prefix-outward is
+d_tau. Thus lambda_core=-lambda_prefix. At the future physical stop, the
core-outward orientation is +d_tau and the owned endpoint-domain prescription
applies. There is no fabricated exterior-outward future load. Temporal
momentum Pi_tau remains distinct from radial/material traction Pi_rho.
The canonical-stop Friedrichs statement concerns its retained nonnegative
form; it does not authorize flipping the Lorentz radial sign or prescribing
a positive Maxwell minimum.

## Nonzero continued local source, without choosing a forcing history

The differentiation coordinate remains b. The already supplied pointwise
coordinate rule is

\[
 \beta=T_b b,\quad A_Q=\sqrt2\beta,\quad
 T_b=(2\pi^2R_4)^{-1/2},\qquad f_R=T_b/R_4.
\]

In particular the local functional derivative is

\[
 \delta a_4(\tau)/\delta b_A(s)=T_b(\tau)Y_AQ\,\delta(\tau-s),
 \qquad \Xi_A^{(4)}(\tau)=f_R(\tau)\Xi_{A,\rm unit}^{(4)}.
\]

It is evaluated on the retained center and endpoint of upstream segment1222,
using the original radius/velocity producer and saved complete Xi arrays.
No new radius normalization, electromagnetic fit, profile, source support,
constant physical beta field, or boundary condition is selected. These are
continued **local source-kernel coefficients**, not a fully evaluated
exterior forcing solution or j_ext. The geometry plus/minus profiles are not
used as photon profiles. The test source keeps its saved n0+n1 input and n2
output; it is not a physical muon state or a repeated-action tail theorem.

At the frontier, the evaluated values are

\[
 T_b=0.22565333970481702,\quad f_R=0.22680626023337117,
 \quad T_b'=-0.010016545014069036,
 \quad f_R'=-0.030203166300202398.
\]

The upstream complete local Xi array has Frobenius norm2.868897479689303.
This is an insertion-array norm in its saved normalization, not a magnetic
moment, vertex residue, physical uncertainty or exterior response.

## A concrete endpoint-H issue

The saved backreaction reconstruction explicitly creates beta=zeros and
assigns only beta[1:-1]. Consequently its saved endpoint H=0 is a placeholder
of that reconstruction, not an evaluated physical radius rate at this cut.
The existing local velocity formula gives

\[
 H_f=0.08877816767234145\in
 [0.08877816713689007,0.08877816820779219],
\]

inside the reused step1222 certified domain interval. The old arrays are
unchanged. The different first affine-logR profile slope is
0.09356155097592357; the parent-H and affine-logR reconstruction errors are
not identified or certified by this packet.

For a unit b-coordinate direction at the material/past corner, the known
terms of the retained temporal equation are

\[
 \Pi_\tau=-e\zeta\,b_\rho-eH_f/2,
 \quad -eH_f/2=-58.64153078485478\quad(\text{per }\kappa_1).
\]

The coefficient of the still unknown radial jet is
2.434197193029561e-13 at that corner; it is not discarded as zero. At fixed
saved e, propagating the reused H interval gives the known-term interval
[-58.64153113854141,-58.64153043116772]. This is not a full parent error
enclosure: the electric coefficient, geometry, frame and extension errors
are not all enclosed here. The complete temporal momentum and affine
exterior return remain null. Core-outward traction multiplies the complete
Pi_tau by -1 at this face; the known piece cannot stand in for the whole
traction on the temporal trace space.

## Attempted angular application and its missing frame conversion

The retained rank16 matrices give the new exact carrier identity

\[
 \operatorname{Tr}_{16}([\jmath_a,Q]^\dagger[\jmath_b,Q])
     =\operatorname{diag}(8,8,0)_{ab}.
\]

Here jmath=-2iT and Q=T3+Y, with the old index8 and Tr16 Q^2=16/3 reused.
This identity alone does not determine a complete mixed Hessian, exterior
response or Pauli coefficient.

One small numerical application was attempted in the local section
(u,v)=(w,1), assuming the saved angular/body coframe and constant carrier Q
were already the mechanical coframe. Under that **unproved matching**,

\[
 *d_\omega(-iQ T_bY_A)=T_b\{(\mathrm{curl}\,Y_A)(-iQ)
               +\lambda\epsilon_{cab}Y_{A,b}[\jmath_a,-iQ]\},
 \quad\lambda=A^2/(A^2+B^2).
\]

The full charge-output contraction is orthogonal to Q in its connection
piece. Its conditional QQ contact matrix has exact spectrum
(3/2 four times,5/2 four times), with zero Q cross term. Thus the conditional
QQ angular matrix has spectrum9+(3/2)lambda^2 and9+(5/2)lambda^2.
The observed frontier values9.38499683438244 and9.64166139063741 are preserved
as **conditional frame diagnostics only**. They were not inserted into the
parent weak problem. The metric ratio r_radial(C_rho/r_orbit)^2 and the full
pointwise W were retained; no extra2/3 vertex or contact fraction is added.
Normalized Wigner coefficients use the saved Haar pairing, not an extra1/2
factor for unnormalized D functions.

Peer review found the missing conversion before publication:
`angular_derham_blocks` supplies curl=2I+S.P. With curl=*d this is the right
Maurer coframe, while the mechanical predecessor uses theta_L=w^-1dw.
Then

\[
 \theta_R=\operatorname{Ad}_w\theta_L,\qquad
 \Omega_a^{\rm saved}=\lambda\sum_d
             (\operatorname{Ad}_{w}^{-1})_{da}\jmath_d.
\]

A carrier gauge transformation h=w^-1 instead gives
omega'=(lambda-1)theta_R **and** Q'=Ad_w Q. Keeping Q fixed during that
conversion changes the source. A left-coframe interpretation with
curl=-*d would instead require the corresponding commutator-Hodge sign.
The inspected producer chain does not instantiate the actual identification.
The conditional calculation cannot decide it. This is a source/coframe
matching issue, not a new charge-index normalization or a reason to
recalculate the old photon modes.

## First unresolved operand and consumer

The first concrete missing map is the retained mechanical connection and
same source expressed in the **existing saved coframe/carrier**:

\[
 \Omega_{\rm saved}=U\rho(F_B^*\omega)U^{-1}-dU\,U^{-1},\qquad
 S_{\rm saved}=U(-iQ)U^{-1}.
\]

Input: the retained A,B and quotient mechanical omega, its actual attachment
F_B, and the saved angular/body and rank16 source frames. Output: the
matrix-valued Omega_saved,a(tau,rho,w) and same-source S_saved, or just their
contracted Gaunt actions on the eight supplied one-forms. The relevant
producers are `diagonal_quotient_contract`, `angular_derham_blocks`, the
saved source coefficients and rank16 attachment. Their normalization is
available; their coframe/carrier pullback is not instantiated by the scoped
producer chain. This is an uncomputed geometric/source matching consequence,
not an independently unselected external forcing law, cap, vacuum or metric.
No exhaustive absence theorem about other chats or caches is asserted.

The consumer is d_Omega of the continued photon source, followed by the
complete mixed zero-trace gauge/BRST equations of the causal prefix solve.
In particular, retain the mixed primitive curvature contact

\[
 \langle d_\Omega v,W d_\Omega a_Q\rangle+
 \langle F_\Omega,W(v\wedge a_Q+a_Q\wedge v)\rangle,
\]

and the same-owner AE4 induced terms. A nonzero first-order curvature image
does not prove a nonzero full mixed row: the contact and other rows can
cancel. No complete complement response, full Calderon graph or DtN chart
is forced from the conditional compression. The frozen scalar curl2
frequency assembler cannot supply the weighted curl3 prefix evolution.

Consequently the intended nonzero exterior response and consumption in a
parent weak solve were **not reached**. No response cut-composition check was
performed; a source identity/center agreement is not that check. No
regularizer, reflected cap, independent temporal endpoint condition or
positive minimum was introduced. The attempted angular derivation and its
precise failed matching step are preserved for resumption.

## Evidence and physical-result boundary

The standalone directory is
`C:\Users\carbe\Downloads\BHSM_muon_exterior_source_524ed906_20261002`.
run_1 preserves the original numerical attempt; final_reference reuses its
arrays with corrected claim scope, without a second numerical calculation.
Nine actual input identities and thirteen producer identities are recorded.
The primary branch/HEAD and tracked working changes are preserved; unrelated
work and caches were not changed. The publication branch starts at36a4ea6.

Repository reproduction, to a fresh directory:

```text
python scripts/replay_muon_exterior_face_source.py --output <new-directory>
python -m pytest tests/test_muon_exterior_face_source.py -q
```

Standalone: `python replay.py --output <new-directory>`. It consumes the
hash-addressed repository inputs listed in input_refs.json. It reproduces
local source kinematics and **conditional** angular controls, not a native
anomaly. The new calculation ran once. Three targeted controls passed
(2.55s); after the frame-scope correction the changed controls passed again
(2.13s). After reconciliation with the newer local history, an additional
consumed-face identity check was added: four targeted checks passed in2.14s.
No old replay, normalization, angular n2 contact, covariance witness,
history solve, expensive native calculation or broad audit was rerun.
Old publication audit evidence is retained, not claimed freshly executed.

All six native ledger entries, exterior response, parent extension, native
E1/shifted applications and physical transfer-direction evaluations remain
null/zero-count as appropriate. Strong_within_native remains a subset,
not a separate addend. Numerical, state/domain, spectral-tail and unresolved
theory uncertainty remain distinct and unevaluated where no bound exists.

Frozen conditional locals remain a_QED=0.00116550200495813, calibration-only
standard uncertainty1.79e-13 (alpha_inverse137.035999084, standard
uncertainty2.1e-8, other original inputs held fixed),
0<delta_a_h<3.500331e-9, and
0.0011655039493<a_selected_local<0.0011655109506, already combined.
Calibration-only uncertainty is not a rigorous total bound. Physical
a_mu=F2(0) and g_mu=2(1+a_mu) are not yet evaluated. No dimensionful magnetic
moment, experimental target or fitted comparison enters this packet.
