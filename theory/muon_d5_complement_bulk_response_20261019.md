# Same-branch D5 complement response and event ports

Continuation of `e02747f2`. This checkpoint advances from the saved E1
boundary forcing to a finite **bulk field-response family**. It does not
claim the complete outer/event boundary problem has been solved. The
incoming conditional preparation, calibration and physical2e-10 guard
are unchanged.

## Reuse and the actual domain

The previous sigma-normal flow, collar Green work, full-carrier source
derivative and joined causal solvers were reviewed before construction.
The old complex child normal/collar arrays have different fields, clock,
branch, source, radial basis and incomplete outer domain. They cannot be
substituted for current arrays. Their algorithms and original equation
checkers are reused. `REUSE_COMPARISON_v1.json` records exact identities
and the historical nonpasses; no ancestor solve or precision study is
replayed.

The current gauge chart has three regular radial functions and a wall
lift, unlike the old two regular functions, affine reference complement
and wall. Both have80 coordinates. That size equality is not a map.
The new application uses the current regular-order-three material maps.

The original full384 carrier contains all three families and both
particle/conjugate Spin4 times SM16 branches. Its coefficient action is
the signed unsquared Lorentz D5. The existing combined-f contact is used
before evaluation:

\[
 \eta_f=-i\cot f\,[\Gamma^0 f_0+\epsilon\Gamma^4 f_4].
\]

This avoids inventing a global unit-grad-sigma chart. It does not remove
eta by a nonunitary similarity or change the polar form domain. Angular
constant truncation is explicit; no full angular or physical spectrum
is inferred. Higgs remains the once-owned interacting seam, not a bulk
mass appended to D5.
The supplied background has the retained SU2/U1 channels. The evaluated
lepton particular images are SU3 singlets, on which a strong-gauge
insertion vanishes by representation. Additional strong backgrounds on
the colored homogeneous coordinates are not evaluated or set to zero.

The application is on the known incoming history. On the child, the
unverified inherited mechanical connection image remains a correction;
own-plus-independent fields cannot silently become the full child
connection. More fundamentally, a fixed-wall-label normal ray from the
child birth corner does not lie in the future child domain. Evaluating
the original sigma-normal coordinate field at E1 gives

\[
 (n^t,n^\rho)_{p}=(0.059196716339331754,1.0668028975535322),
 \quad
 (n^t,n^\rho)_{c}=(0.1687758438749448,1.0616590663951266).
\]

The inward ray has opposite signs and immediately enters t<0 from the
child-lo t=0 face. Extending a child polynomial there would invent a
pre-birth child. The joint event-corner problem, with its actual
transmission, must supply that incidence. A finite incoming response can
nevertheless provide an actual nonzero operand on the event Cauchy
face. It is not promoted into a sewn child solution.
Writing X(q,s) for inward flow, the actual local birth curve satisfies
`q_birth'(0)=0.1687758438749448` and
`q_birth''(0)=-3.9939675780234976` on the child. The differentiated
original level equation is checked; the valid future normal domain is
`q>=q_birth(s)`, rather than the rectangular domain q,s>=0.

## Interior extension and retained freedom

Let Ehat(t) be the saved moving-frame trace numerator and U_eta(t) the
opposite-collar map on **this single history**. A computational interior
extension is chosen in the same fixed material frame:

\[
 \mathcal E_+(t,\rho)g=\zeta(\rho)\widehat E(t)a_R(t),\qquad
 \mathcal E_-(t,\rho)g=\zeta(\rho)U_\eta(t)\widehat E(t)a_R(t),
 \quad a_R=D_Rg,
\]

where `D_R=u_R,+ P_L+u_R,- P_R`. The explicit compact C2 quintic cutoff equals1
near the wall and0 before the inner computational face; it extends by
zero toward the pole. It is a regular chart choice for lifting the
boundary value, not a physical normal profile or boundary selector.
All cutoff radial derivatives, moving frame/time derivatives and
nodal derivatives of a_R are retained in `-D5(mathcal_E g)`.

Changing an admissible extension by Z with zero selected boundary trace
must change chi to chi-Zg and preserve the reconstructed field. This
extension-independence check does not require choosing a physical mode.
The boundary matrix I-EB is used only at the boundary, never as a bulk
projector.

Use the previously evaluated physical normalization cancellation:

\[
 F_{LR}=\widehat N_{LR}\widehat E,\quad
 F_{RL}=\widehat N_{RL}\widehat E,\qquad
 N E g=F_{LR}a_{LR}+F_{RL}a_{RL},
\quad a_{LR}=g/u_{L,+},\ a_{RL}=g/u_{L,-}.
\]

Right normal factors have already canceled in this forcing. They are
not divided out again. The three coefficient functions a_R,a_LR,a_RL
are related through the SAME physical g and normal profiles. Treating
them as independent input slots computes a linear operator family; it
does not fit them or declare them independent physical preparations.

The boundary complement is parameterized completely:

\[
 x=\widehat E a_R+Qh,\qquad
 z=U_\eta(\widehat E a_R+Qh+F_{LR}a_{LR}+F_{RL}a_{RL}),
\]

where range(Q)=ker(Bhat), of dimension366 at every time node. Thus
chi_plus=Qh and chi_minus=Qh+NEg in the common eta chart. All homogeneous
h and its source derivatives are retained. Zero h labels only the
particular coefficient of this affine family. It is not an adopted
outer/initial condition. The second selected-trace equation is checked
independently even though isotropy makes it redundant.

The physical localization fields still obey

\[
 (\partial_s+\tfrac12\partial_s\log J-
 \partial_s\log\sin f)u_{R,L}=0,
\qquad \int_{\text{actual full normal domain}}J|u_{R,L}|^2ds=1
\]

on the real branch, with independently continued analytic left data.
Neither full integral is replaced by a material-radial strip norm or by
the historical partial collar integral. Their values and event/outer
profile incidence remain held equations. Fermionic u, fermionic chi
and mechanical formation deformation psi are distinct objects.

## Executed finite bulk problem

The six actual incoming time nodes are retained. Their Lagrange time
derivative acts on full field coefficients; no fixed frequency or zero
tangential derivative is substituted. For each eta orientation and
particle/conjugate block the full Lorentz equation becomes

\[
 R(\rho)\partial_\rho\Psi+
 [T(\rho)D_t+A(\rho)]\Psi=0,
\qquad G=-R^{-1}(TD_t+A).
\]

The fundamental solution H and its independent analytic inverse are
evaluated on the bounded material collar strip. Repeated family blocks
are applied exactly, not divided out as a physical multiplicity. The
boundary affine family is propagated before subtracting the interior
extension:

\[
 \Psi=H\Psi_{\rm wall},\qquad
 \chi=\Psi-\mathcal E g.
\]

Consequently both D5chi=-D5(mathcal_E g) and the reconstructed D5Psi
are tested. An independent derivative of the returned radial field is
required alongside algebraic defining-row checks. Temporal collocation,
angular truncation, off-node continuation, strip truncation and unknown
physical outer incidence remain separate errors, not bounded by finite
linear algebra residuals.

The new source application retains the coefficient and boundary-state
contacts, in the supplied one-sided raw-time direction at fixed
material/time nodes:

\[
 H_j'=G H_j+G_jH,\qquad
 \Psi_j=H_j\Psi_{\rm wall}+H(\Psi_{\rm wall})_j,
\]

\[
 D_5\chi_j=-D_{5,j}(\mathcal E g+\chi)
             -D_5(\mathcal E_jg+\mathcal Eg_j).
\]

Input-amplitude and homogeneous-data derivatives remain explicit slots.
This one evaluated direction is not the complete physical derivative.
No old52 inverse or changed-background pass is transferred.

## Consumption in original event and Jacobi rows

The computed incoming field at t=0 throughout the strip is supplied to
the ORIGINAL temporal event relation

\[
 \Gamma_{0,c}(\rho)-U_R(\rho)\Gamma_{0,p}(\rho)=0,
\]

and its Jacobi contact

\[
 \delta\Gamma_{0,c}-(\delta U_R)\Gamma_{0,p}
                         -U_R\delta\Gamma_{0,p}=0.
\]

Here Gamma0,p and its new field response are actual evaluated bulk
operands. U_R, its derivative, child Cauchy data, inherited phase and
normal profile ratios are not assigned identity or zero values. An
unsquared Dirac Green flux is distinguished from the originating square
conormal in Dom(D5^2); no eta normal is identified with a native
temporal conormal.

The independent analytic-left finite response supplies signed wall and
inner Green terms and the complete evaluated weak vertex/state
variation. Neither Hilbert-daggering a continued source nor canceling
bulk state terms before the original equations hold is allowed. Held
inner/time/event ports remain in the returned relation. They are not
absorbed as a force chosen to cancel the classical residual.
The existing constant angular coefficient is Y0=1 in unit Haar measure.
The physical S3 volume factor2*pi^2 is included exactly once in the weak
density and currents, including their source derivatives. The point-fibre
trace/seam maps are unchanged; their common angular factor cancels in the
domain equation. The computational left basis is not a normalized
physical left state or its outer annihilator.

This event constraint is part of the joint constrained formation
problem. The mechanical prescription remains the first regular simple
oriented zero of the full constrained formation operator followed by
its nonlinear branch. No eigenline, scalar birth quotient or norm
chooses that mode here. The full coupled KKT, physical retarded outer
domain and normalized normal profiles remain necessary before physical
admission.

## Accounting and checkpoint scope

The width of the explicit computational strip is1.1875863735508981e-7;
it is not a physical exterior, cutoff root or normal-mode support scale.
Each chiral particular has inner bulk coefficient norm about0.03826078.
The actual incoming t=0 trace consumed by the event equation has norm
about0.03559047 for each LR/RL channel, with source norm0.05108809.
All366 homogeneous coordinates at each of the six time nodes remain.

The numerical nonpasses are part of the result. On the complete
fundamental, the original D5 polynomial residual reaches1.7563e-9 at
collocation nodes and6.2327 off-node; its source reaches7.4506e-9 and
131.2383 respectively. On the propagated seed/forcing fields the
corresponding maxima reach1.3970e-9/6.2777 and9.3133e-9/132.1343.
Complement-plus-extension source reconstruction reaches5.9605e-8.
Independent analytic inverse defects reach8.7834e-8, with source defect
2.4640e-6. None is replaced by the small stage-solve residual.

The actual raw time-polynomial/jet mismatch is1.9932e-9. The wall-frame
time-product mismatch is0.038111. The variable-coefficient temporal
product-aliasing norm is about14281.7, with source norm105339.4 in the
declared matrix norm. These are explicit finite-chart diagnostics, not
continuum enclosures or rescaled physical error budgets. No refinement
of the completed E1 kernels or old native heat is performed to conceal
these new bulk/domain limitations.

The newly assembled collar constraints and source rows are checked
separately from these bulk errors. Normal-profile integrals, physical
outer/time faces, the child full D5 equation, event transmission and
mechanical formation residuals remain unassigned quantities, not passed
zero residuals. Cancellation of weak vertex and response coefficients
in the finite collocation problem is not physical load closure.

The whole local Maxwell/Higgs term is not subtracted again. The existing
Higgs seam is not duplicated in the bulk or added as another force.
Complementary native, phase, matched-state, physical-unit and cutoff
obligations remain explicit. The native clock/density contact is reused;
for T=dV its unknown Vdot and commutator remain in the event incidence.
The stationary comparison return is not inserted as a physical corner.

The prior known subtotal, area obstruction and historical gauge,
membrane, continuum/time nonpasses are preserved. No physical cutoff
root, simple-root test, implicit cutoff derivative, coupled correction,
Maxwell/all226 pass, magnetic readout or uncertainty is inferred.

`NEXT_OPERAND`: match the returned incoming bulk Cauchy/Green family to
the actual event/child and retarded outer equations, determine the
retained homogeneous data jointly with the normal profiles and
mechanical formation KKT, and consume the complete state/vertex/domain
derivative. The new finite bulk fields and source responses are saved
for reuse; they must not be restarted as a new forcing-only problem.
