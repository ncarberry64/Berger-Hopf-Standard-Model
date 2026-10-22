# One-potential BHSM interpretation of the compact-lens tracker

The latest user clarification allows ordinary compact-lens fitting and asks
for its BHSM interpretation. The correct bridge is the exterior metric that
light sees. A BHSM-interpreted exterior can have an ordinary point-mass lens
potential; a departure from GR is not required. The same fitted potential
must be counted once. This statement does not identify the independent
microscopic, cosmological and compact-source scalar variables.

This is a targeted check of the recovered optical contracts, spherical
surface identities, supporting Hopf paper and fixed-environment records.
No archive inventory was repeated and no code was edited.

## 1. Exact optical dictionary within the implemented approximation

Use the local weak metric

\[
 ds^2=-(1+2\Phi)c^2dt^2+(1-2\Psi)d\boldsymbol r^2,
 \qquad W_{\rm full}=\Phi+\Psi.
\]

The local thin-lens phase and its angular potential are

\[
 \mathcal P[W](\boldsymbol b,t)=\int_{-\infty}^{\infty}
 W(\boldsymbol b,z,t)\,dz,
 \qquad
 \psi_\theta(\boldsymbol\theta,t)
 ={D_{ls}\over D_lD_s}
 \mathcal P[W](D_l(\boldsymbol\theta-\boldsymbol c),t).
\]

Here W is dimensionless, P has length units, and angular coordinates are
in radians. Then

\[
 \boldsymbol\beta=\boldsymbol\theta-\nabla_\theta\psi_\theta,
 \quad A=I-\nabla_\theta^2\psi_\theta,
 \quad t={1+z_l\over c}{D_lD_s\over D_{ls}}
 \left[\tfrac12|\theta-\beta|^2-\psi_\theta\right].
\]

For the code's reference mass length m_ref and
\(r_E^2=4m_{\rm ref}D_lD_{ls}/D_s\), this becomes exactly

\[
 \psi_x(\boldsymbol x,t)={\mathcal P[W](r_E\boldsymbol x,t)\over4m_{\rm ref}},
 \quad \boldsymbol y=\boldsymbol x-\nabla_x\psi_x,
 \quad t_M={4m_{\rm ref}\over c}(1+z_l).
\]

These are the potential, image Jacobian and Fermat normalization actually
used by `product/bhtracker/forward.py`. Distances, time/frame calibration,
geometric optics, the slow local evolution approximation and the admitted
primary branches are held the same in comparing interpretations.

**Optical equivalence theorem.** Suppose a BHSM exterior and a fitted
model have projected phases differing only by a spatial constant at each
epoch. Their primary images, magnification determinants, flux ratios and
same-epoch image-pair delays are identical. This follows directly from the
displayed equations: the constant has zero first/second derivative and
cancels from the Fermat difference. More generally, in normalized coordinates
\(\psi'_x=\psi_x+\boldsymbol d\cdot\boldsymbol x+C\) and
\(\boldsymbol y'=\boldsymbol y-\boldsymbol d\) give the same observables;
the changed Fermat expression differs by the image-independent quantity
\(-\boldsymbol d\cdot\boldsymbol y+|\boldsymbol d|^2/2-C\).
The product's independently free source coordinates permit this affine
source reparameterization at each row. No mass-sheet or arbitrary-potential
equivalence beyond the stated conditions is being asserted.

If \(\mathcal P W_{\rm BHSM}(q)=4m_{\rm ref}\psi_x(\vartheta(q))+C\),
the complete nonlinear observable map obeys

\[
 \mathcal O_{\rm BHSM}(q)=\mathcal O_{\rm fit}(\vartheta(q)),\qquad
 J_q=J_\vartheta D\vartheta,\qquad
 F_q=(D\vartheta)^T F_\vartheta D\vartheta.
\]

Thus the existing likelihood can estimate the exterior parameters of the
BHSM interpretation. A many-to-one source map yields a compatible set of
internal states, rather than a unique internal-state measurement. It is
unnecessary to add a separate BHSM force or require a nonzero GR residual.

## 2. What the fitted mass, center and motion mean

For an isolated static spherical Einstein-sector exterior,
\(\Phi=\Psi=-m/r\), \(m=GM/c^2\). Its formally cutoff-dependent phase is
\(\mathcal P W=4m\log b+C\), so the code's point mass is
\(\psi_x=(M/M_{\rm ref})\log|x|\). The same M can therefore denote the
BHSM exterior's monopole parameter when that exterior is represented by
this metric. More generally a fitted lensing mass is an operational Weyl
charge,

\[
 M_W=-{c^2\over2G}\lim_{r\to\mathrm{far}}rW_{\rm full}(r)
 ={c^2\over4G}\lim_{b\to\mathrm{far}}b\,\widehat\alpha(b),
\]

on a stated local isolated far zone. This is an ADM/Schwarzschild mass only
when the applicable metric/source assumptions establish that equality.

The recovered spherical boundary interpretation supplies a useful exact
dictionary under the static Schwarzschild, areal-radius, outward-normal
and flat-reference assumptions. With f=1-2m/r and r>2m,

\[
 H={2\sqrt f\over r},\quad
 \kappa_{\rm acc}={m\over r^2\sqrt f},\quad
 Q_\Sigma={c^2\over8\pi}\int H\kappa_{\rm acc}\,dA={GM\over r},
\]

\[
 E_{\rm BY}={c^4r\over G}(1-\sqrt f),\qquad
 M={rQ_\Sigma\over G}
 ={E_{\rm BY}\over c^2}-{GE_{\rm BY}^2\over2c^6r}.
\]

H and kappa_acc have inverse-length units, Q_Sigma velocity-squared units,
and E_BY energy units. The reported lens mass can be read in this boundary
representation through the last equation. The surface charge and its
Schwarzschild metric represent the same mass; adding both as separate
monopoles doubles it. Changing the enclosing radius changes E_BY but does
not create physical mass drift. The static construction is not extended
to the null horizon, rotation or accretion by substituting arbitrary M(t).
These identities are recovered/checked in
`provenance/blackhole_surface_recovery.md`; they are conditional uses of
the Einstein/GHY sector, not a new microscopic mass-selection law.
The displayed Q_Sigma uses positive proper acceleration. A source written
instead with K_uu must keep its normal convention: with the stated outward
normal, K_uu=-kappa_acc. This sign is not an additional optical charge.

The fitted center is the translation parameter of the total projected
monopole. In an isolated far-zone expansion
\(W=-2m/r+\boldsymbol D_W\cdot\boldsymbol n/r^2+\cdots\), a translated
monopole has \(\boldsymbol D_W=-2m\boldsymbol r_c\); thus
\(\boldsymbol r_c=-\boldsymbol D_W/(2m)\) in that coordinate convention.
The physical center r_c has length units; its transverse angular projection
is c=r_c,perp/D_l. The product estimates that angle and observer-time proper
motion, with known observer factors included once:

\[
 \boldsymbol c_i=\boldsymbol c_0+\boldsymbol\mu_{\rm obs}(t_i-t_0)
 +\boldsymbol\pi_i,
 \qquad
 \boldsymbol v_\perp=(1+z_l)D_l\boldsymbol\mu_{\rm obs}.
\]

This is a BHSM exterior center/trajectory interpretation. It does not
independently locate an internal seam or a horizon.

## 3. BHSM deformation coefficients and the single-counting rule

The recovered BHSM action-projection contract uses two physical scalar
metric directions and one normalized topographic profile:

\[
 A_g=\begin{pmatrix}a&b\\b&c\end{pmatrix},\quad B_{g\varphi}=\binom uv,
 \quad (\Phi,\Psi)^T=-A_g^{-1}B_{g\varphi}\,\varphi.
\]

Its convention is **half** the sum of the metric potentials:

\[
 \overline W_{\rm topo}={\Phi+\Psi\over2}=R_W\varphi,
 \qquad R_W={u(b-c)+v(b-a)\over2(ac-b^2)}.
\]

Consequently the input to the existing tracker operator is
\(\mathcal P W_{\rm full,topo}=\int2R_W\varphi\,dz\).
This factor of two is required; no new optical coupling is introduced.
The source demands action-owned, normalized a,b,c,u,v,c_phi on one physical
domain before claiming numerical source predictions. Their source-space
normalization is not supplied by a lens fit. Once an exterior potential
is specified, however, its optical evaluation and fitting require no
microscopic variable to be renamed as the R1 scalar.

Shear, convergence and compact quadrupoles are simply coordinates of that
same projected potential. A BHSM geometry that supplies a term already
represented by one of those coordinates is interpreted through its total
fitted coefficient, rather than added as another identical term. For example,
in the R1 zero-monopole-flux harmonic limit the normalized transverse term is

\[
 \delta\psi_x={k_H\over r^2}
 (a_+\cos2\phi+a_\times\sin2\phi),\qquad
 k_H=-{\widehat\beta N_2r_0^3\over3m_{\rm ref}r_E^2}.
\]

If c_ord is the ordinary compact-quadrupole coefficient, only
\(c_{\rm tot}=c_{\rm ord}+k_Ha\) enters the potential. The finite change
\((c_{\rm ord},a)\mapsto(c_{\rm ord}-k_H\delta a,a+\delta a)\)
leaves every nonlinear prediction identical. This is a representation
equivalence, not evidence against the BHSM interpretation. A distinct
screened radial profile can be tested as an additional shape within the
declared family, without treating every mathematically separate source
label as an independent observable.

The actual BHSM phase-current support gate is also transferable on its own
stated domain: for V=varphi*T*eta and j_mu=<D_mu eta,T eta>, a static
block-diagonal background with D0 eta=j0=dot(varphi)=0 has u=v=0 when
j_i=0 or grad_i varphi=0. It suppresses that action's linear metric source,
not every possible surface or metric channel. It supplies neither an R1
boundary amplitude nor a rule that a measured monopole must vanish.

## 4. Why the Hopf theorem does not determine the tracker boundary state

The supporting Hopf result acts on a degree-two spatial scalar on S3:
\(F_A(X)=X^TAX\), X in S3 subset R4, A in STF(4), dimension nine.
Stationary nodal behavior on a great circle requires A to annihilate its
real two-plane P. For an orthogonal complex structure J,

\[
 A_2={A-J^TAJ\over2},\qquad
 {\|A_2\|_F^2\over\|A\|_F^2}={1+\kappa^2\over2}\ge\tfrac12.
\]

This constrains charged power and fixed-radius Berger spectral response.
It is independent of amplitude. The tracker boundary scalar instead lives
on a physical S2 worldtube: Q in STF(3), dimension five, with l=2 harmonics.
Neither the physical domains nor their representation spaces are identical.
The microscopic eta target field in the M8 action is a third, distinct
operand. Equality of scalar coefficient dimensions would not identify them.

There is an exact check on the tempting Hopf-quotient shortcut. Write
z1=x1+i*x2, z2=x3+i*x4, and

\[
 n(z)=(2\Re(z_1\bar z_2),2\Im(z_1\bar z_2),|z_1|^2-|z_2|^2).
\]

On unit S3 this maps to unit S2 and is invariant under common phase.
For any Q in STF(3), n^TQn is a homogeneous **degree-four** harmonic in R4:
\(\Delta_{R^4}(n^TQn)=0\). Therefore its restriction belongs to the
neutral n=4, eigenvalue 24 space on unit S3, not the n=2, eigenvalue 8
space of the supporting theorem. Homogeneity, harmonicity and vanishing
Hopf-generator derivative were checked symbolically for all five independent
entries of Q, with exact residual zero. Analytically, each n_i is harmonic
and grad(n_i).grad(n_j)=4|X|^2 delta_ij, so the Laplacian of n^TQn equals
8|X|^2 tr(Q)=0. Conversely, an n=2 function descends
as a scalar through that quotient only when neutral, while every nonzero
stationary-nodal n=2 state has at least half charged power.

Thus no Hopf-charge inequality on the tracker a_plus,a_cross,a_axial follows
from that theorem. It cannot fix their amplitude, conormal source or flux,
and fitting an exterior mass does not infer a Hopf state. The auxiliary
free-scalar nodal-persistence theorem likewise requires its specified
Berger action and is not a derived compact-source evolution law.

## 5. Interpretation permitted by the recovered record

The reusable physical statement is:

`BHSM-interpreted exterior geometry -> one projected Weyl potential -> the
existing image/flux/delay likelihood -> exterior mass, center and motion.`

The recovered Einstein/GHY surface dictionary makes this concrete on the
stated spherical branch, including its ordinary-gravity limit. It is valid
to use that fit within the BHSM interpretation without requiring a deviation.
Additional microscopic state claims require their own action/source map;
their current freedom does not erase the measurable exterior parameters.

The fixed-environment N12 prescription reinforces correct bookkeeping:
delta e=0 leaves seven slaved interface rows (three traces, two momenta and
two dynamic fluxes), with a 7x73 moving-environment jet. It does not freeze
those rows or identify them with the five physical S2 scalar coefficients.
The normalized Schur identity is a transfer method once actual blocks,
domains and pairings are supplied. Its generic form alone is not a new
observable or an excuse to add the same gravitational contribution twice.

Targeted source operands: `Downloads/BHSM_optical_hessian_projection_contract.tex`,
`BHSM_optical_constitutive_reduction.tex`, `BHSM_optical_current_support_gate.tex`;
main BHSM `theory/n12_gate7_comoving_slaved_interface.md` and
`n12_gate7_environment_seam_pullback.md`; supporting paper
`review/hopf_nodal_bound.md`, `provenance/nodal_hopf_bound_review.md` and
`provenance/RECOVERY_MAP.md`. Detailed prior source hashes remain in
`provenance/micro_recovery.md` and `provenance/blackhole_surface_recovery.md`.

## 6. Audit of the implemented interpretation layer and manuscript

Inspected `product/bhtracker/interpretation.py`,
`product/tests/test_bhsm_interpretation.py`, its pinned fixture and source
manifest, and `manuscript/bhsm_interpretation.tex`. The new module is a
reporting/interpretation transformation; it does not alter the forward
potential, parameters, likelihood or fitted source positions. The manuscript
accurately states that ordinary fitting can be used within the declared BHSM
Einstein-sector interpretation. It does not require a deviation or use an
equivalence claim to identify a microscopic state.

The implemented stable boundary evaluation is correct. With
\(q=2GM/(c^2r)\), \(s=\sqrt{1-q}\), the code uses

\[
 \delta k_g={q\over r(1+s)},\qquad
 {E_{\rm BY}\over M_\odot c^2}={2M_{[M_\odot]}\over1+s}.
\]

These are the rationalized forms of the exact expressions, retaining small
curvature deficits without subtracting nearly equal floating-point numbers.
The energy inverse has the correct power c^6 and reconstructs the same
monopole at different enclosing radii. Its velocity-squared surface quantity
is converted from m^2/s^2 to km^2/s^2 by the required factor 10^6. The code
uses the same nominal solar GM, c and parsec as the lens engine.

At fixed r, direct differentiation gives

\[
 {d(E_{\rm BY}/c^2)\over dM}={1\over s},\qquad
 {d\delta k_g\over dM}={G\over c^2r^2s}.
\]

The code and manuscript use exactly these Jacobian pushforwards. They are
local uncertainty transformations conditional on a supplied radius, not
additional measurements, calibrated interval coverage, or a physical
precision forecast. In particular they become large near the static branch
boundary; a mass distribution that reaches r=2GM/c^2 cannot be represented
by that first-order Gaussian propagation. No claim of such a near-horizon
measurement is made here. The high precision numerical assertions test
algebra and software consistency only.

The R1 distinction is handled correctly: its reported mass is the adopted
action's metric/source parameter and includes a distinct scalar contribution
in the predicted total potential. The software returns
`NOT_ASSUMED_FOR_R1_METRIC` for the Schwarzschild boundary dictionary. As a
useful check, in the retained local unscreened overlap rV << r << L0 the R1
spherical metric has
\(M_W=(1+\epsilon_\infty)M\),
\(\epsilon_\infty=\chi\widehat\beta^2/(2C)\). In the transition region a
single point-exterior mass need not represent its full radial response.
Thus substituting the R1 source mass directly into a purported total-metric
Schwarzschild Brown--York energy would be unjustified; the implementation
does not do so. The ordinary dictionary is explicitly the spherical
equivalent of the fitted monopole, with the nonspherical/environmental
contribution excluded from that boundary-energy claim.

The new test file was run from the documented product directory:

```text
python -m pytest tests/test_bhsm_interpretation.py -q
10 passed in 0.96 s
```

The preserved-fit fixture was independently compared with the exact Git blob
at commit `16f796a8e3971357a3701b76ac73c4d05de950ff`, path
`papers/bhsm_blackhole_tracker_20261021/results/product_example.json`.
The source SHA256 is
`d90df6ce27d70fbceb89dfc5b36502ca24195952c070baf99cab2fe325912bd8`;
predictions, estimates and status in the fixture match that blob exactly.
The unchanged declared 2e-11 numerical comparison passes against this
pre-interpretation reference. It establishes preservation of that baseline
computation, not an astrophysical accuracy statement. The test also checks
input immutability, invalid static boundaries, fixed-radius derivatives,
R1 non-substitution, and suppression of a boundary measurement for rejected
or unresolved-mass fits. The packaged source hashes bind the interpretation
to the recovered BHSM records rather than only to a reporting label.

No substantive formula, mass-normalization or no-double-counting defect was
found in these reviewed files. No implementation or manuscript edits were
made during this audit.
