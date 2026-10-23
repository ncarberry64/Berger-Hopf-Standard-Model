# Non-cut muon-source temporal weak elements

Starting revision: `58e5941b38faae24e67be87aa55537aadeec656e`.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.
The adopted common-A coupling, daughter eta, radial inclusion, source,
cut forms and frozen locals are inherited. No earlier production was replayed.

## New evaluated objects

The new packet `artifacts/muon_prefix_time_element_20261004` contains:

| Region | Temporal density model | Proper duration, nominal | Original-source weak contraction |
|---|---|---:|---:|
| accepted physical prefix STEP1222 before the artificial cut | degree4 | 4.812244687273648e-31 | 1.5928499679389998e-29 |
| cut0 to retained future node1, action arc0..2 | degree1 | 5.768080623161497e-7 | 1.907643448553739e-5 |
| retained future nodes1..2, action arc2..4 | degree1 | 1.5797256218711772e-6 | 5.221547643364169e-5 |

These are local Dirac weak-form contractions in the retained action's
normalization, not magnetic anomalies, probabilities or error estimates.
The connected partial K/M arrays have shape144x144; joining total-field
trace constraints have shape48x144. The original unprojected source obeys
these constraints with binary64 residual zero. A source load and form
cotangent are saved. No exterior inverse, solution, stationary residual,
stationary conormal, native heat action or physical Pauli extraction was run.

## First non-cut actions and clock

The prefix uses the inherited accepted descriptor segment STEP1222, from
sigma=1.77358179301789798e-20 to1.77392720485438779e-20, branch24.
Its original-center line/response Taylor records, selected branch reference,
fixed-s field, first acceleration and whole-step Lohner certificate are
consumed. The numerical representative is the saved quadratic predictor;
it is not an exact dense physical trajectory. The physical descriptor-fiber
trajectory and Taylor errors are retained in each point receipt. The
original whole-step chart controls the interior points; the endpoint tube
is not extrapolated. No new eigensolve, Jacobian or98-direction campaign
is used.

The conversion is performed before enclosing the first action:

    Y_tau = W_Y^-1(b_psi Psi_w + sigma V_w)/(N_b sigma),
    q_tau = v/N_b,
    m_tau = Y_tau[74:98].

The shared Delta cancels. The twelve lapse rows are m_tau[:12]. The clock
is d_tau/d_sigma=N_b sigma/Delta, with Delta=c b_psi+sigma R. Its
whole-cell enclosure is widened for explicit sigma dependence, not
replaced by a constant endpoint rate. The integrated proper duration has
the inherited-model enclosure

    2.8743598113835007e-31 <= duration <= 1.4641876289633338e-30.

This encloses the clock integral in that descriptor-cell model; it does
not enclose the nonlinear quadratic weak form over the entire trajectory
tube. Five distinct Gauss points, two additional comparison points and
the original-center face are evaluated. The first lapse rate varies
between7.698733239146561e12 and7.700091914497817e12 at the five integration
points; a0 varies with norm9.82071786603948e9.

The future points are actual nodes1 and2 of the retained high-order C2
history, with their same-action first rates. The live workspace supplied
the backreaction clock records; Git was not treated as the complete
scientific record. Their actual inputs and provenance are retained in
`future_run_1` and `future_run_2`.

The high-order history supplies f_arc=G/||G||. Its point clock satisfies

    c=W_q v,
    alpha=(c.f_arc,q)/(c.c),
    rho_arc=N_b alpha=N_b sigma/||G||,
    Y_tau=W_Y^-1 f_arc/rho_arc.

Thus the same Delta and field normalization cancel upstream. No tiny
descriptor is recovered from sorted raw eigenvalues. The retained
mode-response report establishes branch24 continuation and positive
selected-line gaps at both points. Numerical q_tau=v/N_b discrepancies
are below3e-16. The first lapse rates are155.40834109428215 and
-9.680096343727488; the a0 difference has norm1190.8070047885526.
These future center records have no interval-certified history authority.

The future anchor differs from the stored cut predictor by action norm
6.0689642906101e-18, from multiplication/division by the action weights
in the high-order producer. Both historical arrays are preserved. This
few-ulp identity tolerance is not a trajectory certificate. Direct
radius-action covectors verify the point H values to6e-16; no spline
radius derivative or affine-logR slope is substituted.

## Moving field and weak temporal integral

Use the same W/p spatial frame and its moving complement. The source
continues as p=T_b(tau) hat(rho) Xi/r with the original hat and angular
coefficients, and T_b proportional to R_b^-1/2. The same daughter profile
rho/2 and full-cap affine normalization supply W. At each new state,
I_tau is formed from its actual q_tau; it is not the old right-cell
time-interpolation derivative. Pointwise direct Fourier lapse rates are
kept distinct from nodal spatial interpolation.

The adopted D5 action, including shift, spin and common-A terms, gives

    D5(E c)=F0 c+F1 c_tau,  E=(W,p),
    F0=(D5 W,D5 p), F1=(i Gamma0 W/nu,i Gamma0 p/nu).

F0 includes E_tau. Its lower-order coefficient is

    a0=[-I_tau/(2I)-L_nu/2+3H/2+C_tau/(2C)
        -z C_rho/(2C)-z_rho/2+z nu_rho/(2nu)
        -(z/2)cot(rho/2)]/nu.

The retained volume pairing is2pi^2 nu C r^3 d_rho; the temporal Cauchy
pairing is2pi^2 C r^3 d_rho. They are saved separately. The full n1/n3
source outputs, including neutral-left and higher angular/carrier rows,
enter the spatial moment contractions. There is no heat of an isolated
source image. The finite W/p trial space is not asserted to close under
resolvent or heat propagation.

Define A=<F0,F0>, B=<F0,F1>, C=<F1,F1>, M=<E,E>. For element coordinate
x and positive clock tau_x, the pulled weak densities are

    Atilde=tau_x A, Btilde=B, Ctilde=C/tau_x, Mtilde=tau_x M.

Use hierarchical trials phi0=1 and phi1=scale(x-1/2), where scale is an
action-derived computational basis factor, not a physical coefficient.
The source, dual forms and endpoint trace maps are transformed together.
No diagonal regularizer or arbitrary inverse is used. The weak integral is

    K_ij=int[phi_i phi_j Atilde + phi_i phi'_j Btilde
          +phi'_i phi_j Btilde^dagger+phi'_i phi'_j Ctilde] dx,
    M_ij=int phi_i phi_j Mtilde dx.

Prefix degree4 density interpolants produce degree6 weak integrands;
five-point Gauss integrates this declared polynomial model. Future and
connecting degree1 density interpolants are integrated by exact Legendre
moments. This is a completed model integral, not a claim that point
sampling certifies the physical history integral. In particular, the
bridge retains both endpoint densities and clocks, without extending the
cut jet constantly. Its cut A/B/C/M blocks are reused, not recalculated.

The saved prefix endpoint trial conormals are separately sampled point
actions. They need not equal the interior-node interpolant's conormal
B_model(x)^dagger X at x=0,1. Neither is a stationary exterior return.
Future degree1 endpoint densities do reproduce their model endpoint
conormals. The joining trace constraints use fields and Cauchy pairings,
not an assertion equating these different trial conormals.

The original source is applied in unprojected coordinates `(0,p,0_time)`
before time-jet application. Large W/complement contributions are not
subtracted to recover its small contraction. The coupled implementation
keeps element hierarchical coordinates and trace constraints, avoiding
an inverse of the approximately1e-31 prefix basis scale. The domain
continues to own the original reset, material and canonical-stop graphs;
no boundary law is imposed at either artificial element face.

## Error and execution scope

The prefix degree2/degree4 comparison gives K absolute difference
3.980770841815331e-18, relative2.982569124207796e-14, and source-contraction
difference1.7376100957627712e-43. This is not a certified temporal
interpolation remainder. Future/bridge interpolation remainders remain
unevaluated. Saved Hermite history defects are recorded as history
diagnostics, not propagated coefficient/operator bounds. Spatial
quadrature remains the inherited8-point-per-cell rule; no old cut
quadrature refinement was repeated. Matrix roundoff, continuum, full
domain and full stratified uncertainty are not certified.

The first prefix run persisted its arrays and point receipts, then a
receipt-only reparse of a wide Arb display string lost its positive lower
bound. Receipt runs2 and3 consume outward interval endpoints without
replaying any field or time element. Run3 additionally saves the point
pairings. The current replay has this delivery fix. `executed_source`
preserves the exact initial calculation and later execution revisions.
The first future attempt stopped before coefficient actions on exact
anchor-byte equality; its retained inputs were reused after identifying
the few-ulp weighted-coordinate roundtrip.

Ten unique targeted readonly checks pass: five prefix checks and five
future/assembly checks. No old guard, cut checks, covariance witness,
endpoint extraction, local calibration or whole test suite was replayed.

## Next contracted operator action

The next continuation operand is the inherited tail weak/conormal action
on the total W/p source-reached trace at future node2/action_arc4. For the
trace injection i2 and its geometric dual, the needed response is

    i2^sharp Gamma1^owner u_s,
    Gamma0 u_s=i2 g,
    q_tail,0^owner(v,u_s)+s <v,u_s>_tail=0 for owned zero-trace v.

It must retain the connected output and material/reset/canonical-stop
matching; a full DtN graph need not be constructed. Later same-action
point/clock records exist. The remaining tail weak action, interface,
constraint and completion blocks have not been assembled in this
packet. This is an uncomputed operator/domain action, not an unselected
new physical boundary condition. A partial element inverse is not its
replacement. The spectral shift/heat length remains owned by the native
prescription; no value was inserted.

The frozen local terms and calibration convention are unchanged. All
physical native Pauli ledger entries and physical a_mu/g_mu remain null.
This intermediate numerical milestone advances the muon realization; it
does not yet extract a reusable generic child engine or a muon anomaly.
