# BHSM v6.10.0 action-selected junction functional

Primary result:
`BHSM_MINIMAL_WELL_POSED_ACTION_HAS_NO_JUNCTION_MIXING_TERM`.

Secondary results:

- `BHSM_CURRENT_ACTION_SELECTS_NO_SELF_ADJOINT_JUNCTION_DOMAIN`;
- `BHSM_C3_HERMITIAN_COMMUTANT_IS_CIRCULANT`;
- `BHSM_JUNCTION_K_PROP_REJECTED_FOR_CURRENT_ACTION`;
- `BHSM_JUNCTION_BENDING_REQUIRES_ONE_BOSONIC_CORNER_INVARIANT`.

The result is structural Case 7. The required well-posed action contains no
light-heavy junction term. Symmetry permits optional junction operators, but
their coefficients, Clifford grades, and boundary traces are not derived.
Those optional extensions must not be reported as consequences of the current
action.

## Variational geometry

The retained geometric package is P1 plus its GHY completion. P1 contains the
volume and scalar-curvature terms. Once the scalar-curvature term is chosen,
the Dirichlet metric variation requires

\[
 S_{\rm GHY}=\kappa_1\int_{\partial M}\epsilon_n K\,d\mu_h .
\]

Its coefficient is fixed by the bulk coefficient \(\kappa_1\). It is a
smooth-boundary completion, not a physical surface tension.

The declared geometry has one oriented \(S^7\) boundary with a
Gaussian-normal collar. B1 is a provisional intrinsic boundary action and
condition, not a second boundary face derived from P1. The moving cap endpoint
produces transversality and shape-response terms, but it does not by itself
create two intersecting boundary pieces. No normal pair, relative joint angle,
or codimension-two corner is declared. Therefore the P1 variational problem
does not presently require a Hayward joint term.

If a genuine two-face corner were later derived, its P1 joint coefficient
would be locked to \(\kappa_1\). Adding such a term now would silently add the
missing corner geometry. A junction-volume density

\[
 S_{J,\mathrm{bos}}^{(0)}
   =\tau_J\int_{\Sigma_J}\sqrt{|\gamma|}
\]

is symmetry permitted, but \(\tau_J\) is an independent physical junction
energy and is not fixed by GHY well-posedness.

## Junction trace space

The endpoint trace locus is denoted \(\Sigma_J\), with induced metric
\(\gamma_{ab}=X_J^*h_{ab}\) and measure
\(d\mu_J=\sqrt{|\gamma|}\,d^{\dim\Sigma_J}y\). The trace map is

\[
 T_J:\operatorname{Dom}(C_{\rm BHSM})
   \longrightarrow H^{1/2}(\Sigma_J,E|_{\Sigma_J}).
\]

The reduced v6.7 Green form is

\[
 \omega(u,v)=\langle u,J_n v\rangle_J,\qquad
 J_n=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
\]

Normal reversal changes the signs of \(\Gamma_n\) and \(J_n\). The v6.7
numerics export a bulk-normalized zero mode, quarter-cap junction
probability, and first gap. They do not export the point trace or normal
derivative of the zero mode, nor a normalized first-heavy eigenvector and its
trace. Thus an optional trace overlap cannot yet be evaluated.

Bulk orthogonality is not substituted for a boundary trace. For a local
operator \(M_J\), the correct matrix element is

\[
 j_{01}=(T_Jf_0)^\dagger M_J(T_Jf_1).
\]

## Exact triality commutant

The repository declares the cyclic generator

\[
 C=\begin{pmatrix}
 0&0&1\\
 1&0&0\\
 0&1&0
 \end{pmatrix},\qquad C^3=I.
\]

It does not declare the transpositions needed for full \(S_3\). Solving
\([J,C]=0\) together with \(J=J^\dagger\) gives the three-real-dimensional
circulant algebra

\[
 J=aI+bC+b^*C^2
  =aI+x(C+C^2)+iy(C-C^2),
\]

where \(a,x,y\in\mathbb R\) and \(b=x+iy\). In the exact C3 Fourier basis the
eigenvalues are

\[
 \lambda_0=a+2x,\qquad
 \lambda_1=a-x-\sqrt3\,y,\qquad
 \lambda_2=a-x+\sqrt3\,y.
\]

They are generically three distinct singlets of the abelian C3 action. Thus
nonuniversal neutral structure is symmetry permitted. It is not required,
and none of \(a,x,y\) is fixed by the action. The v6.9 scalar ansatz is the
special subalgebra \(x=y=0\), not the complete commutant.

## Junction invariant classification

The complete lowest Clifford-order local matter basis built only from
declared rank-two structures is represented by

\[
 I,\quad \Gamma_n,\quad \sigma_J\Gamma_\star,\quad
 K=i\Gamma_n\Gamma_\star,
\]

tensored with a Hermitian C3 commutant element. Charge and color operators
act trivially or covariantly in the neutral block; no sector-dependent Yukawa
matrix is added. The \(\Gamma_n\) density is orientation odd. The
\(\sigma_J\Gamma_\star\) product is classified with the stored wall/carrier
Z2 transformation. All four junction bilinears are absent from the adopted
action, optional, and coefficient dependent.

Tangential derivative terms are not retained because the current action does
not supply a junction tangential operator or its integration-by-parts
domain. Normal jump terms require a declared second trace side. The bosonic
lowest-order optional basis begins with junction volume, followed by
curvature/shape terms such as \(K^2\) and
\(\operatorname{Tr}(S^2)\). None is duplicated with the smooth-boundary GHY
completion.

## First variation and domain

The Green identity fixes the admissible self-adjoint domains as
maximal-isotropic graph spaces

\[
 \psi_-=U\psi_+,\qquad U\in U(1)
\]

in the reduced two-component normal problem. Every unitary graph cancels
flux and is self-adjoint at this reduced level. The current action has
\(S_{J,F}=0\), so it supplies no projector, bag angle, APS cut, or graph
unitary. The v6.7 \(U(1)\) family remains.

For comparison only, if an extra real boundary generator \(\alpha_J\) and a
polarization are declared by

\[
 (1+i\alpha_J)\psi_-=(1-i\alpha_J)\psi_+,
\]

then the corresponding Cayley chart is

\[
 U(\alpha_J)=\frac{1-i\alpha_J}{1+i\alpha_J}.
\]

This sign follows from the displayed graph equation. Under normal reversal
\(\alpha_J\mapsto-\alpha_J\) and \(U\mapsto U^{-1}\). This is a conditional
chart, not an action-derived selection. Charge and triality covariance would
further require the generator to commute with \(Q_{\rm em}\), \(Y_{\rm BH}\),
and C3. The auxiliary index-one result is compatible with the previous
diagnostic member but cannot choose \(U\).

## Light-heavy projection

For the current action,

\[
 M_J=0,\qquad j_{01}=0,\qquad V_{LH}=V_{HL}=0.
\]

The zero follows from operator absence, not from replacing the trace pairing
with the bulk overlap. An optional operator could factor as

\[
 V_{LH}=j_{01}\bigl[aI+x(C+C^2)+iy(C-C^2)\bigr],
\]

but both its action coefficient and the required point traces are missing.
The first-heavy truncation remains the v6.9 three-copy \(f_1\) block.

## Additive versus mass-like response

Using the declared collar grading

\[
 K=i\Gamma_n\Gamma_\star=-\sigma_z
\]

as a two-chirality algebra audit, set \(H_0=pK\). This is not a new physical
bulk Dirac parent law. The operators \(I\) and \(K\) commute with \(H_0\) and
therefore give same-sector additive or kinetic-sign responses. They do not
justify \(K_{\rm prop}\).

The operators \(\Gamma_n\) and \(\Gamma_\star\) anticommute with \(H_0\).
Conditionally, a derived opposite-sector matrix \(M_{\rm eff}\) would give

\[
 H_{\rm eff}^2=p^2+M_{\rm eff}M_{\rm eff}^\dagger,\qquad
 E_i=p+\frac{\mu_i}{2p}+O(p^{-3}).
\]

Only in that conditional case could
\(K_{\rm prop}=M_{\rm eff}M_{\rm eff}^\dagger\) be defined. The current
action provides no such matrix. Its junction energy shift, relative phase,
and \(K_{\rm prop}\) all vanish.

## Sheet bending

The classical background has \(\Psi_{\rm background}=0\). A quadratic
fermion junction term would therefore make no tree-level classical
contribution to the bending Hessian. No determinant or loop contribution is
inserted.

For a normal displacement \(\delta X=\xi_\perp n\),

\[
 \delta d\mu_J=K_J\xi_\perp d\mu_J,\qquad
 \delta K=-\Delta_{\Sigma_J}\xi_\perp
 -[\operatorname{Tr}(S^2)+\operatorname{Ric}(n,n)]\xi_\perp .
\]

The physical Hessian must be formed only after removing gauge kernels:

\[
 H_{\rm phys}=H_{PP}-H_{PC}H_{CC}^{-1}H_{CP}.
\]

The stored action supplies no junction density whose second variation closes
this expression. It also supplies neither \(k_b\), \(B_+\), nor \(B_-\).
Consequently no lower-sheet tachyon, ghost, or survival result is certified,
and no upper-sheet stability claim follows.

The minimal optional bosonic term capable of beginning this calculation is
the junction-volume invariant with coefficient \(\tau_J\). Deriving
\(\tau_J\) from a localized bosonic source, or deriving a genuine corner and
its coefficient-locked angle term, is the next action-level construction.
The constraint-reduced embedding response must then still be evaluated.

## Closure matrix

The current dependency graph is

\[
\begin{aligned}
S_J=0 &\longrightarrow U\ {\rm unselected},\\
S_{J,F}=0 &\longrightarrow M_J=0
 \longrightarrow V_{LH}=0
 \longrightarrow K_{\rm prop}\ {\rm rejected},\\
S_{J,\rm bos}=0 &\longrightarrow
 B_+,B_-\ {\rm unresolved}.
\end{aligned}
\]

The optional fermionic coefficients and \(\tau_J\) belong to distinct action
sectors and are not one closure parameter. Therefore one junction action
package does not presently close domain, neutral propagation, and sheet
bending.

The v6.8 theorem
\(y_\sigma^{(4)}(\beta)=y_\sigma^{(4)}(0)=\lambda_{\rm geom}\) is unchanged.
The v6.9 zero light-heavy block, missing bending invariant, and auxiliary
index-one certification are preserved. No measured inputs, fitted matrices,
sector-dependent couplings, physical bulk Dirac parent law, frozen prediction
change, or official prediction-logic change is introduced.

