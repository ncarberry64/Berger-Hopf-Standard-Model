# Magnetic quantum insertions and birth-composed native mean

The common-background scalar mixed Green application now evaluates the
magnetic numerator contact, both derivatives of the squared fermion
factor, and the scalar propagator insertion. It retains all eighteen
lepton components and all three fixed-Y families. Independently, the
true-birth source-driven mean has been propagated through both arms with
its canonical momentum contact included once. These are evaluated
applications in the continuing magnetic-moment calculation. Their finite
reference-domain scope and unperformed physical matching are stated
below; this report does not assign them a completed anomaly.

The preserved starting revision is
`d80d77273102b7728e4d6f967dd652f80b79ad3b` on PR #465. The current physical
cutoff owner remains `BHSM-AE4-BRANCH-BIRTH-CUTOFF-2026-10-08`: one common
parent-to-muon birth surface, child-plus evaluation with no temporal
offset, the physical section's inertia normalization, and `c=i/r`.
Numerical probes below do not select that section or replace this rule.

## Actual scalar and fermion applications

The intrinsic real Higgs Jacobi form is evaluated on the actual retained
gauge/Higgs coefficient fields. It includes the temporal covariant term,
spatial covariant derivatives, the negative part of the Higgs potential,
the material temporal connection and the original action weights. It is
not an identification of the intrinsic Higgs with the Einstein--Cartan HS
auxiliary. The scalar action Gram has its real `2 Re` factor and the cap
normalization once. The canonical lepton coefficient has unit current
Gram: `chi_hat=R4^(3/2) psi/(2 pi^2)`.

For the native fermion factor `A`, the left factor Green is

\[
 G_F=P_F^{-1}A^\dagger,\qquad
 \delta G_F=-P_F^{-1}(\delta P_F)P_F^{-1}A^\dagger
             +P_F^{-1}\delta A^\dagger,
\]

with `delta P_F=A^dagger delta A+delta A^dagger A` on the fixed represented
core. The two terms in `delta P_F` are retained individually. Reordering
this nonnormal factor Green as `A^dagger P_F^-1` would change the action
application. The scalar insertion is `-G_H delta P_H G_H`. Both open
vertex placements are evaluated. The fixed-Y bare mixed vertex has a
derived zero first derivative with respect to gauge/Higgs fields at
fixed coframe: the original Yukawa action is linear in real Higgs
coordinates. This zero does not remove pairing, coframe, domain, cutoff
or external-state motion.

The starting virtual scalar component is the retained real eighty
dimensional `n=1,3` space. The actual first magnetic source is exactly
`n=1` in the stored coefficient representation. Its complete even images
are `n=0,2,4`, scalar dimension 140 and full lepton dimension 630. These
images are included before the insertions are contracted. Image closure
for this starting component is not completeness of the entire internal
loop over every angular shell or temporal mode. In particular,
`integral b^2 bprime=0` in the one-tent projection is not an operator
identity removing its differential temporal complement.

At the shared explicit probe `c=1e-11`, the full18 forward operator norms
are `2.236012593424986e-19` incoming and `2.2612021975810674e-20`
outgoing. The middle-minus-light norms are `8.06938971747994e-22` and
`8.160294721039472e-23`; the reverse placements agree in norm at the
reported binary resolution. Incoming full18 component norms are about
`2.23601259375e-19` for the numerator contact, `1.35171636e-29` and
`4.36491276e-29` for the two squared-factor placements, and
`2.11803494e-29` for the scalar propagator insertion. All are nonzero.
Four/six-term series refinement changes no exported binary digit. The
middle-family outward stored-spectrum numerator-tail contraction bound
is `3.263091791193638e-53` incoming and `1.5831316576597748e-55`
outgoing. These small series bounds do not bound the unrepresented loop
complement or convert these operator norms into anomaly errors.

## One common proper-time cutoff and controlled scalar arithmetic

All reached Green factors share the total cutoff, rather than each
receiving an independent lower limit. For positive spectra,

\[
 L_n(p_1,\ldots,p_n;c)=
 \int_{u_i\ge0,\,\sum_i u_i\ge c}
       e^{-\sum_i p_i u_i}\,du_1\cdots du_n.
\]

If `g_c(p)=exp(-cp)/p`, then `L2=-g_c[p,q]` and
`L3=g_c[p,q,r]`. The source numerator contact consumes `L2`; the
fermion and scalar propagator insertions consume `L3`. The coincident
three-factor value is

\[
 e^{-cp}\left(\frac{c^2}{2p}+\frac{c}{p^2}+\frac1{p^3}\right).
\]

Direct binary divided differences would lose these values for the
nearly equal temporal-dominated spectra. The implementation instead
expands about `m=max p_i`, with `rho_i=(m-p_i)/m`, `z=cm` and complete
homogeneous polynomials `h_j(rho)`:

\[
 L_n=\frac{e^{-z}}{m^n}
 \sum_{j\ge0}h_j(\rho)
 \sum_{l=0}^{n+j-1}\frac{z^l}{l!}.
\]

Every summand is nonnegative. Let `p_min=min p_i`, `D=max p_i-p_min`,
and retain terms `j=0,...,k-1`. The exponential Taylor remainder on
the simplex gives the outward bound

\[
 0\le\mathrm{tail}\le
 {n+k-1\choose n-1}\frac{D^k}{p_{\min}^{n+k}}
 e^{-c p_{\min}}
 \sum_{l=0}^{n+k-1}\frac{(c p_{\min})^l}{l!}.
\]

The implementation evaluates this bound in Arb. It also evaluates the
positive `-partial_c L_n` boundary kernel, retaining the negative sign
when cutoff motion is applied. An unknown physical cutoff jet is not
assigned zero. A Frobenius norm majorant of the exact stored coefficients,
`sqrt(N*(max Re^2+max Im^2))`, and outward Arb products/Gram division
carry the series bound into the actual contractions. Eigensystem,
original field/operator formation and binary contraction errors are
outside this exact-stored-spectrum series bound. Series refinement is
reported separately and is not a physical anomaly enclosure.

## True-birth mean and the original action rows

Literal cubic action contacts are evaluated at the actual sourced E1
endpoint fields, including the fixed-action energy term and separate
source-motion work. The canonical mean momentum is
`p_mean=H_v eta_mean+g_v`; the direct `g_v` contact is included once.
The two retained central gauge relations are evaluated explicitly:

\[
 \theta\cdot(\mathrm{Gauss}_P-\mathrm{Gauss}_C)
 +\theta_r\cdot[ p_{A_r} ]
 -(G_Y H_P)\cdot[ p_H ]
 +(G_Y^T p_{H,C})\cdot[ H ]=0.
\]

Differentiation retains the off-shell coefficient contact against the
base residual. A named 218-row quotient of the original 220 rows is
solved, with all original rows and null directions retained. No floating
singular vector chooses a constraint to delete. Its exact-stored Arb
certificate bounds every original-row residual by
`1.3713e-27`; the exported binary residual norm is about `3.12e-15`.
The quotient condition is about `37579.75`; the untreated 220-row
floating inverse had condition about `3.83e16`. Source compatibility is
about `4.575e-28`.

The actual source-driven mean is then propagated in both arms. The
incoming reverse-coordinate action is `L(x,-v)` with reversed canonical
momentum `p_reverse=-p_future`; raw fields and rates are exported on the
future physical clock. The raw268 midpoint mean norms are
`10.95894137284226` incoming and `0.13927136426536227` outgoing. Exact
stored algebraic application residual bounds are `1.363e-31` and
`6.331e-34`. These arithmetic bounds exclude paired-source formation
and continuum errors. The represented fixed-reference birth restriction
and minimum coefficient-weight particular solution do not select the
physical E0 mean or moving formation section.

The propagated mean is applied to the actual same-background raw268
native target and combined with the previously evaluated magnetic square
contact and both ordered insertions. The complex-fermion `+1/2` is
inserted once. At the common `q=1` probe,
`c=1.0329133712274834e-11`, the graded form traces are
`-8.322517712426465e-20` incoming and `1.1008727173095823e-20` outgoing.
The exact-stored mean-contraction radii are at most `1.81e-35` and
`2.26e-36`; target quadrature16/32 differences are `2.32e-35` and
`2.49e-36`. The radii exclude the target and paired-source formation,
directional Dg and continuum errors. This replaces the initially held
per-arm mean on this represented birth restriction; the earlier values
and scope are preserved.

The resulting actual form is inserted into the original signed magnetic
Maxwell/Higgs source action, on its three physical source coordinates:

\[
 (A_0+R)U=1,\qquad
 \delta U=-A_0^{-1}RU=U-A_0^{-1}.
\]

At the same common `q=1` probe, the boundary-return norms are
`1.0353643865913604e-27` incoming and `1.2673835244396767e-9` outgoing.
The inverse residual bounds are `4.4186154042178936e-39` and
`1.687547944949555e-30`. The outgoing bare form retains its negative
eigenvalues; it is not sign-flipped or promoted to a positive quantum
covariance. The interval return preserves the mean entry intervals and
stored direct imaginary rounding. The source space has three axes;
five padded representation coordinates are absent. The upstream
encloser's outward-rounded zero pads are retained in its immutable
archive and the consumer applies the actual three-dimensional inclusion
before padding the old coefficient representation. No physical
nonzero entry is discarded.

The reached fixed-fields/fixed-mean cutoff partial is also evaluated.
At `q=1`, its graded mean trace is `4.02839941838e-9` incoming and
`-1.91650057097e-9` outgoing. Thus cutoff independence of this component
cannot be assumed. This partial is not a test of cancellation in the
complete overlap-subtracted Pauli amplitude and does not set physical
cutoff or mean-motion jets to zero.

## Evaluated overlap, signed moment and shared inputs

The continuum local VP overlap already evaluated on the same external
muon shell is

\[
 \Delta a_\mu^{\rm VP}=(\alpha/\pi)^2
     [A_{\rm VP}(1)-A_{\rm VP}(m_\mu/m_e)].
\]

Its normalized signed soft Pauli projection and local spin-sector LSZ
application are retained. It is already within the frozen local QED
ledger. The native comparison must match current, domain and external
shell before subtracting this overlap once; a finite `Tr P` moment or
Green identity is not substituted for this continuum amplitude.

For a negative muon with spin projection `+hbar/2`, this graph's moment
component is

\[
 \Delta\mu_z=-\frac{e\hbar}{2m_\mu}\Delta a_\mu^{\rm VP}.
\]

The nonmagnetic calibration gives
`m_mu=2 h R_infinity r/(c_light alpha^2)`. Thus the SI component is
`-e c_light alpha^2 Delta a/(8 pi R_infinity r)` and its shared charge
dependence is `alpha^4`. An independent mass uncertainty is not appended
to this shared-input expression. With the pinned selected central inputs,
the outward local component interval is
`[2.610135811989493e-31, 2.610135811989495e-31] J/T`. On the specified
primary plus/minus one-standard-uncertainty box it is
`[2.6101343061435867e-31, 2.6101373178373668e-31] J/T`.
The extrema are evaluated with the correct shared-input corners and the
mass-ratio monotonicity proof. No joint coverage probability is assigned
to that box. An independent SI/GeV unit application gives
`2.610135811989494e-31 J/T`, inside the central interval. This component
is not added again and is not a final native magnetic moment.

## Physical consumer and unfinished application

The physical open-leg target remains the same-background graded quantum
action derivative, with field Green, two vertices, internal fermion
Green, square contacts, pairing/domain/source/cutoff motion and relative
completion on its owned domain. The applications above are its reached
operands. The starting scalar component and its exact source images do
not include the entire quantum field complement. The intrinsic scalar
loop is not the EC-HS block. The classical retarded response and the
integrated source-boundary inverse are not quantum covariances.

After the quantum/current/domain and external-shell matching, the
disjoint native Pauli remainder belongs in the existing ledger once.
The preserved calibrated `a_subtotal=0.0011659186179552334` and
`g_subtotal=2.0023318372359107` remain subtotals. A complete numerical
native remainder and the remaining matched finite weak terms have not
yet been bounded. Their absence is not a zero, so no final `a_mu`,
`g_mu` or total uncertainty is asserted here. This is unfinished internal
action production; no independent covariance or new action-definition
gap is established by the absence of a finished packet.

## Verification and scope

The verification records process commands, outputs, exit codes, hashes,
source pins, deterministic replays and the five repository publication
audits. The first signed-moment run failed on a nonexistent primary-input
key; the correct inherited key is `R_infinity`. The failed log is
preserved and the successful runs are byte-identical. The independent
angular derivative test for the scalar source originally used the wrong
index contraction; its corrected independent check passes without a
change to the production derivative. These failures are distinguished
from physical error bounds.

The initial chronological-return runs exited at the exact-zero padding
guard because outward interval export gave exact zero pads subnormal
radii. The corrected consumer uses the proved three-axis source
inclusion, preserving all original intervals. Successful runs 3/4 are
byte-identical. Their failure logs remain in the verification.

| Classification | Scope |
| --- | --- |
| DERIVED | Ordered nonnormal Green derivative, both squared-factor placements and scalar insertion, common-total-cutoff kernels and rigorous stored-spectrum series tails, named Ward-row relations, canonical mean source once, shared-input SI moment normalization. |
| EVALUATED | Actual scalar positive/source images and all-family mixed magnetic insertions; true-E1 cubic contacts and original-row-compatible birth mean; two-arm propagated mean and its actual native target contact/cutoff partial; signed interval photon boundary return; signed continuum-overlap SI component and its primary box. |
| CONTROL_ONLY | Finite reference cells, explicit common cutoff probe, assigned nu-squared4/gamma-null trial realization, stored-array arithmetic certificates and any matched free-symbol diagnostic. |
| UNEVALUATED | Complete same-background graded quantum open-leg action with its field/temporal/stratum complement and physical pole/domain matching, owned formation/cutoff if consumed, disjoint native soft Pauli remainder, remaining matched finite weak terms and complete observable uncertainty. |
| OWNER_DEFINITION_GAP | None established. |
