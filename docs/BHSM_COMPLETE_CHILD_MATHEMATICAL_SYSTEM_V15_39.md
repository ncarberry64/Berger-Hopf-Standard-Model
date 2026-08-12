# BHSM v15.39 — the complete-child mathematical system

BHSM is the following variational construction.

## 1. The object

Let

\[
 M_8=\mathbb R_t\times[0,\pi/2]_\chi\times S^3_u\times S^3_v
\]

with

\[
 ds^2=-N^2dt^2+C^2(d\chi+\beta^\chi dt)^2
 +A^2d\Omega_{3,u}^2+B^2d\Omega_{3,v}^2,
\]

\[
 \eta=(\cos f\,u,\sin f\,v).
\]

The pole data are

\[
 B(0)=0,\quad B'(0)=C(0),\quad A'(0)=0,
\]

\[
 A(\pi/2)=0,\quad A'(\pi/2)=-C(\pi/2),\quad B'(\pi/2)=0,
\]

and

\[
 f(0)=0,\qquad f(\pi/2)=\pi/2.
\]

The material response is the normalized reciprocal join trace

\[
 W_J[f]=\sin^2f\cos^2f,
 \qquad Z_J[f]=\int_0^{\pi/2}W_J[f]d\chi,
\]

\[
 \boxed{\sigma'=W_J[f]/Z_J[f],\qquad \sigma(0)=-1/2.}
\]

Thus \(\sigma(\pi/2)=+1/2\). The material surface is the unique regular
level set \(\sigma=0\). Its scale is

\[
 \boxed{x=\log(B/A)\big|_{\sigma=0}.}
\]

The particle is the complete persistent solution

\[
 \Phi_*=(G,\eta,\sigma,\text{interface},\text{FR sector},\ldots)_*,
\]

not any one of these components.

## 2. The functional

Define

\[
 X_\eta=-\frac{(D_tf)^2}{N^2}+\frac{f'^2}{C^2}
 +\frac{3\cos^2f}{A^2}+\frac{3\sin^2f}{B^2},
\]

\[
 F(X)=\frac{\kappa_1}{2}X+\frac18X^4.
\]

The regular join action is the ADM reduction of

\[
 \int_{M_8}\sqrt{-G}\left[
 \frac{\kappa_1}{2}R-\frac{\kappa_0}{2}
 -(1-4\sigma^2)F(X_\eta)
 \right].
\]

The coefficient follows from the retained quadratic carrier
\(1+g\sigma^2\): seam normalization and vanishing at both material-response
vacua select

\[
 \boxed{g=-4.}
\]

The response law is imposed by

\[
 S_{\rm response}=\int\lambda_\sigma
 \left(\sigma'-\frac{W_J[f]}{Z_J[f]}\right)d\chi.
\]

The multiplier \(\lambda_\sigma\) is nonpropagating and introduces no
physical field or continuous coefficient. The independent inverse-Euler
\(\sigma\) action is not also retained: that would impose the response twice
and preserve an unselected \(Z_\sigma\). The v15.31 oriented interaction is
preserved as a leading local response candidate for the unfinished operator
basis/provenance calculation; it is not independently added to the final join
law here.

The skin-supported Hopf inertia is

\[
 I_H[\Phi]
 =\int_{S^7}\sqrt h\,(\kappa_1+X_\eta^3)
 (1-4\sigma^2)|K_H|^2.
\]

On the odd-FR domain

\[
 \Psi(\theta+2\pi)=-\Psi(\theta),
\]

the compact zero-current ground state is

\[
 \Psi_0=\pi^{-1/2}\cos(\theta/2),
 \qquad \langle J\rangle=0,
 \qquad \langle J^2\rangle=\frac14.
\]

It contributes

\[
 \boxed{E_{\rm FR}[\Phi]=\frac{1}{8I_H[\Phi]}.}
\]

Thus the stationary child functional is

\[
 \boxed{H_{\rm child}[\Phi]=H_{\rm regular}[\Phi]+E_{\rm FR}[\Phi].}
\]

There is no free pressure, wall tension, spring, or empirical Standard Model
datum in this functional.

## 3. The equations

BHSM solves one system:

\[
 \delta_N S=0,
 \qquad \delta_{\beta}S=0,
\]

\[
 \delta_C S=0,
 \qquad \delta_A S=0,
 \qquad \delta_B S=0,
\]

\[
 \delta_f(S+S_{\rm response}-E_{\rm FR}dt)=0,
\]

\[
 \delta_{\lambda_\sigma}S=0,
 \qquad \delta_\sigma(S+S_{\rm response}-E_{\rm FR}dt)=0.
\]

These are respectively the Hamiltonian constraint, momentum constraint,
three spatial Einstein equations, the eta equation with its nonlocal
normalized-response reaction, the response constraint, and its adjoint
material equation. They are solved on the smooth two-pole domain and
quotiented by time and radial diffeomorphisms.

The solution map is

\[
 \Phi_*(x)=(N,\beta,C,A,B,f;\sigma=C_J[f]-1/2,\lambda_\sigma)_*(x).
\]

The physical child energy is

\[
 H_{\rm child}^{\rm on-shell}(x)=H_{\rm child}[\Phi_*(x)].
\]

The particle conditions are

\[
 \boxed{x<0,\qquad
 \frac{dH_{\rm child}^{\rm on-shell}}{dx}=0,
 \qquad
 \frac{d^2H_{\rm child}^{\rm on-shell}}{dx^2}>0.}
\]

Persistence is then the stationary zero-current FR ray or, when the complete
solution is relative-periodic, unit-modulus physical Floquet multipliers after
gauge directions are removed.

## 4. The constructed branch

Formation is

\[
 a_c^6=\frac{343}{5\kappa_1},
\]

\[
 f_q=\chi+q\sin\chi+\frac{19}{108}q^2\sin\chi\cos\chi+O(q^3),
\]

\[
 \frac{a^6}{a_c^6}=1+\frac{23}{45}q^2+O(q^4),
 \qquad
 \mathcal C_\eta=1+\frac{49}{8}q^2+O(q^4).
\]

Its join response is

\[
 a=\frac{343}{1728}\zeta q^2+O(q^3),
\]

with the canonical \((s,p_s)\) pair and the established nonzero invariant
formation-to-shape transfer.

The unconstrained material subsystem has the physical \(-14.202\) seam mode.
It is not tangent to the complete response-constrained child because
\(\delta f=0\) implies \(\delta\sigma=0\). The controlled fixed-profile
calculation found

\[
 x_*\simeq-4.78752,
 \qquad k_x\simeq3.1005>0.
\]

These two numbers are conditional material-coordinate controls, not the
physical child scale or Hessian. The round geometry cannot satisfy the Hamiltonian constraint after positive
skin/FR energy is added. The v15.38 nonconstant conformal solution is the
first constraint-solved enclosed-spacetime response on this branch.

The response-constrained nonround York solve now supplies a pointwise
constraint-solved moving slice with transverse-traceless shape momentum

\[
 K=0,\qquad D_jK^{ij}=0,\qquad K_{ij}K^{ij}>0,
\]

with zero momentum current, nonconstant conformal geometry, and normalized FR
expectation. Its orientation-odd Lorentzian exponent is \(1.32507>0\). The
nonlinear child branch reaches

\[
x=-0.00207504,\qquad d[\Phi]=0.00121243>0,
\]

so the material and geometric parent surfaces separate. Continuing reaches
the eta Legendre reconstruction firewall. The global degree, orientation, FR
parity, incidence order, and separate parent/child boundary identities have
been carried through the metric-free cut.

The negative-response cap is reconstructed after the cut as
\(\mathcal C_c\simeq B^4\times S^3\), without importing metric data from the
singular side.  The coefficient-selected radius and the minimum-norm real
ADM Cauchy data are

\[
 R_*=\left(\frac{343}{5}\right)^{1/6}=2.0232708255,\qquad
 H_*=-0.1383575369,\qquad
 \omega_*=5.1036401\times10^{-5}.
\]

They obey \(I\omega_*=1/2\), close the Hamiltonian constraint to
\(9.1\times10^{-14}\), and keep
\(\min(1+X_\eta^3)=6>0\).  The self-similar constraint function has
\(\min\mathcal G=0.0035658083>0\) and no turning point, so the one-scale
sector is not periodic.  The active calculation is now the nonround cap
shape-response-boundary-traction flow and its physical Floquet monodromy.

The nine-mode Lorentzian cap embeds the reconstructed CMC-plus-TT data and
selects \(\dot x<0\).  Its unit-lapse diagnostic reaches \(x=-0.4530\)
without turning, but that chart carries only the integrated Hamiltonian
equation.  Jointly projecting the two lapse-shape, two radial-shift, and
constant-lapse equations gives

\[
 \max|\mathcal C_A|=6.6\times10^{-11},\qquad
 \max|\mathcal C_A|_{\rm independent}=2.891\times10^{-4},\qquad
 \dot x=-0.98421.
\]

On the monotone-map gauge \(f=\chi\), the two eta-coordinate modes are removed
and the differentiated Euler--Dirac matrix is an \(11\times11\) full-rank
block. The constrained projection gives

\[
 \max|\mathcal C_A|=4.4\times10^{-11},\qquad
 \max|\mathcal C_A|_{\rm independent}=5.04\times10^{-4},
 \qquad \dot x=-0.97887.
\]

The constrained flow has no turning point. It encounters a multiplier-chart
fold near \(t=0.2655\), then reaches a second eta Legendre firewall at the
next Runge--Kutta stage after the last regular state

\[
 t=0.3095,\qquad x=-0.312613,\qquad \dot x=-6.19876,
\]

\[
 \min N=0.37335,\qquad \min(1+X_\eta^3)=2.12563.
\]

The order-one full-velocity projection used at the fold does not prove global
branch continuity, so this is a controlled finite-chart event and not a
foundational no-go theorem.

The post-cut topology itself fixes the next enlargement. Simultaneous right
\(Sp(1)\) multiplication on \(S^3_u\times S^3_v\) is free and gives

\[
 M_5=\mathbb R_t\times B^4,\qquad
 M_4=\mathbb R_t\times(S^3_u\times S^3_v)/Sp(1)_{\rm diag}
     =\mathbb R_t\times S^3.
\]

With \(S=A^2+B^2\), the parent metric completes as

\[
 A^2|\theta_u|^2+B^2|\theta_v|^2
 =S|\omega|^2+\frac{A^2B^2}{S}|\theta_u-\theta_v|^2,
\]

\[
 \omega=\frac{A^2\theta_u+B^2\theta_v}{S},\qquad
 R_4=\frac{AB}{\sqrt S},\qquad
 K_F=\frac{\kappa_1}{2}\operatorname{Vol}(S^3_{\sqrt S})S.
\]

This connection curvature is already in the parent Einstein scalar and is
not added again. The active persistence calculation is the non-double-counted
gauge/ghost/Weyl determinant on this derived \(M_4\), followed by its
renormalized stress in the Dirac child equations.

The free conformal part is now exact. Three rank-16 families, twelve physical
gauge vectors, and four real scalar-doublet components give

\[
 E^{(0)}_{\rm SM}=\frac{59}{30R_4}
 =\frac{59}{15L_F}\cosh x,
 \qquad \partial_x^2E^{(0)}_{\rm SM}>0.
\]

After this term is inserted with the proper boundary lapse, all five reduced
constraints close and the attached Euler--Dirac matrix remains full rank.
Nevertheless the orbit has no turn and reaches a new eta Legendre event near
\(t=0.103\), after

\[
 x=-0.0818350,\qquad \dot x=-1.37356.
\]

Thus the free conformal coefficient is retained but not retuned. It is the
exact backreaction of the selected electroweak-symmetric conformal vacuum.

The Legendre surface also closes the event semantics. Since the event carries
only the discrete invariant tuple \(\mathcal I_*\) and erases continuous
metric/canonical data, while constrained reconstruction returns the selected
state \(z_*\), the hybrid map is

\[
 \mathcal P=\mathcal R\circ\mathcal E\circ\Phi_{T_*},
 \qquad \mathcal P(z_*)=z_*.
\]

On a fixed discrete event component, \(D\mathcal R=0\). Therefore the
finite-chart physical monodromy is zero on its 12-dimensional continuous
Poincare tangent, while the odd FR ray returns projectively with multiplier
one. On the full Sobolev phase space \(H^s\), \(s>11/2\), the reset is the
constant map on the selected event basin, so its continuous spectrum is
\(\{0\}\), its fixed set is \(\{z_*\}\), and the odd FR ray returns
projectively. This is state-level unique actualization on that basin.

The global chiral bundle on each open segment is now

\[
 G_{SM}=\frac{SU(3)\times Sp(1)\times U(1)_Y}{\mathbb Z_6},
\]

with three triality copies of the rank-16 family

\[
 (3,2)_{1/6}\oplus(1,2)_{-1/2}\oplus
 (\bar3,1)_{-2/3}\oplus(\bar3,1)_{1/3}\oplus
 (1,1)_1\oplus(1,1)_0.
\]

The geometric (Y_{BH}) operator removes the otherwise anomaly-free (B-L)
mixing continuum. All local anomalies vanish, the global (Sp(1)) anomaly is
absent, and the bundle returns to the same isomorphism class at actualization.
The global bundle and its anomaly-free chiral incidence are therefore fixed
on the hybrid cycle.

The round reconstructed diagonal fiber also fixes the stored Berger scalar
excitation seeds:

\[
 \lambda_{k,j}=\frac{k(k+2)-q^2}{L_2^2}+\frac{q^2}{L_1^2},
 \qquad q=k-2j,
\]

and \(R_F^2\lambda_k=k(k+2)\) at reset. The actual diagonal fiber is round,
with exact internal spinor spectrum

\[
 \lambda_{\ell,\pm}=\pm\frac{\ell+3/2}{R_F},
 \qquad d_\ell=(\ell+1)(\ell+2).
\]

These are internal Kaluza--Klein energies, not four-dimensional chiral
masses. The normalized wall mode and the four matched family ledgers give

\[
 \int ds\,J|u_0|^2=1,
 \qquad \Omega_u=\Omega_d=\Omega_e=\Omega_\nu=I_3,
 \qquad M_f(H)=H Y_f.
\]

The intrinsic matrices \(Y_f\) are foundational \(M_4\) Wilson operators in
the adopted fermion action; neither overlap nor the round Dirac spectrum
determines their entries. On the selected conformal reset,

\[
 H_*=0,
 \qquad M_{u,*}=M_{d,*}=M_{e,*}=M_{\nu,*}=0_3.
\]

All twelve gauge fields are likewise massless. Hence physical CKM and PMNS
matrices are unobservable on this exactly degenerate background: their left
diagonalizers are arbitrary. The identity obtained in the triality basis is
the canonical event-to-event basis transport, not a physical mixing
prediction.

The event quotient has now been promoted to the full Sobolev phase space.
For (s>11/2), let (mathcal X^s_{m phys}) be the complete constrained
field space modulo gauge and diffeomorphisms. On the selected degree-one,
negative-child, odd-FR event basin,

\[
 \mathcal P_s(z)=z_*,\qquad
 \operatorname{Fix}(\mathcal P_s)=\{z_*\},\qquad
 D\mathcal P_s=0.
\]

The continuous hybrid spectrum is therefore ({0}) in every (H^s) norm;
the FR ray returns projectively. This is unique actualization on the selected
hybrid event component. The regular child interior survives as the
reconstruction cobordism carrier, not as transported metric or momentum data.

The action-owned diagonal quotient supplies the five-dimensional weak
coefficient (K_F^{(5)}). The single rank-16 carrier trace fixes the
four-dimensional gauge ray

\[
 K_Y:K_2:K_3=\frac53:1:1,
 \qquad \sin^2\theta_W=\frac38.
\]

The absolute dimensionless (M_4) coefficient (Z_{\rm gauge}) still
requires the normalized (M_5\to M_4) mode/localization pushforward; the
dimensionful (K_F^{(5)}) is not relabelled as (1/g_2^2).

On the closed spatial (S^3), the global color Gauss generators annihilate
physical states. Thus color-open quarks are local sections, while the minimal
physical enclosures are the singlets in

\[
 3\otimes\bar3=1\oplus8,
 \qquad
 3\otimes3\otimes3=1\oplus8\oplus8\oplus10.
\]

The massless neutrino operator is (i\partial_t-D_{S^3}\otimes I_3). Its
frequencies obey

\[
 \omega_n=\frac{n+3/2}{R_4},
 \qquad e^{-i\omega_n(2\pi R_4)}=-1.
\]

Hence the selected neutrino is an exactly null projective propagation cycle,
with (Delta m^2=(0,0)) and no observable PMNS matrix on this background.
Finally,

\[
 \ell_\kappa=\kappa_1^{-1/6},
 \qquad R_F=\left(\frac{343}{5}\right)^{1/6}\ell_\kappa,
 \qquad R_4=R_F/2,
\]

so all derived lengths and energies are fixed multiples of the single action
scale. No numerical external-unit value of (kappa_1) is inserted.

The remaining interacting normalization is not a smooth dimensional
reduction of the bulk Einstein term. On the round quotient base,

\[
 ds_5^2=-dt^2+R_F^2d\chi^2+r(\chi)^2d\Omega_3^2,
 \qquad r(\chi)=R_F\sin\chi\cos\chi,
\]

a tangential mode \(A_\mu=u(\chi)a_\mu\) gives electric and magnetic weights

\[
 I_E=\int R_Fr\,u^2d\chi,
 \qquad I_B=\int \frac{R_F}{r}u^2d\chi.
\]

Four-dimensional Lorentz invariance requires \(I_E=R_4^2I_B\). For every
regular profile in the complete test family
\(u_p=\sin^p(2\chi)\),

\[
 \frac{I_E}{R_4^2I_B}=\frac{2p}{2p+1}<1.
\]

Equality is only the distributional boundary limit \(p\to\infty\). Thus a
local Lorentz-invariant gauge action requires an intrinsic boundary/Wentzell
term, whose absolute coefficient is not fixed by the bulk Einstein term.

The active parent bosonic tangent bundle contains metric and response
singlets, the Path-B color \(3\oplus\bar3\) weak singlet, and the weak adjoint
connection. It contains no \((1,2)_{1/2}\) scalar. A principal-fiber
coordinate is gauge redundancy, not an associated Higgs section. Therefore
the doublet \(H\) used in the Standard Model attachment is foundational
intrinsic \(M_4\) data. Its selected reset value is \(H_*=0\); that value does
not make the field parent-derived.

The actual operator selects the matching scale

\[
 \mu_*=R_4^{-1}=2R_F^{-1},
\]

and its heat trace reproduces the gauge coefficient ray, but it cannot create
an absent bifundamental zero-order Dirac block. Zeta regularization fixes the
nonlocal determinant and logarithmic anomaly, not the finite local gauge,
Higgs, and Yukawa counterterms. Moreover, with

\[
 b_i=(41/6,-19/6,-7),
 \qquad \frac{d}{d\log\mu}\frac1{g_i^2}=-\frac{b_i}{8\pi^2},
\]

the one-loop flow is not tangent to the ray \((5/3,1,1)\); its only common
perturbative fixed point is Gaussian.

After canonical field normalization, the intrinsic interacting action has
real coefficient-space dimension

\[
 1+2+4(18)=75.
\]

Even imposing family centrality \(Y_f=y_fI_3\) leaves

\[
 1+2+4(2)=11
\]

real directions. At \(A_*=H_*=\Psi_*=0\), the Jacobian of the background
equations with respect to all eleven directions is the zero matrix. Hence a
continuum of inequivalent actions has the same selected reset, event tuple,
and anomaly ledger while possessing different Hessians and scattering.
State-level unique actualization is therefore not theory-level uniqueness.

The missing mathematical datum is precisely the single-valued coefficient
functor

\[
 \boxed{\mathcal M_{\rm micro}:\mathcal I_*\longmapsto
 (g_*,m_H^2,\lambda_H,Y_u,Y_d,Y_e,Y_\nu),}
\]

compatible with gauge symmetry, diffeomorphisms, event gluing, the global spin
bundle, boundary renormalization, and the finite Dirac block. No such functor
is present in the current parent-child action. This rank statement directs
the continuation to the microscopic law rather than to further evolution of
the already selected zero background.

The owned triality symmetry by itself gives the weaker equation
\([P,Y_f]=0\), whose complete solution is

\[
 Y_f=a_fI_3+b_fP+c_fP^2.
\]

It therefore leaves (27) real action directions, not (11). The
family-central count is a deliberately stronger kill screen, not a consequence
of (C_3). Event naturality cannot finish the selection: because event arrows
act trivially on gauge-invariant Wilson data, it only makes
\(\mathcal M_{\rm micro}\) constant on the connected event orbit. Every
constant remains natural, so the natural-assignment fiber is still
eleven-dimensional even under the stronger kill screen.

The smallest adequate extension is one universal scalar law
\(\mathscr L_{\rm micro}(\mathcal I,c)\), with the Wilson data as variational
outputs satisfying

\[
 d_c\mathscr L_{\rm micro}=0,
 \qquad \operatorname{Hess}_c\mathscr L_{\rm micro}>0.
\]

This is one new law, not eleven new constants. Its formula must be derived
without an arbitrary coefficient-space center; otherwise the constants have
merely been hidden in the definition of the law.

There is, however, a derived alternative to treating (H) as elementary.
The chiral fermion bundle contains the exact color-singlet scalar channels

\[
 \Pi_1(\bar Q_Lu_R),\ \bar L_L\nu_R\in(1,2)_{1/2},
 \qquad
 \Pi_1(\bar Q_Ld_R),\ \bar L_Le_R\in(1,2)_{-1/2}.
\]

Thus an elementary parent doublet remains absent, while the composite-doublet
representation is owned by already-derived fields. A nonzero order parameter
must solve the actual-child gap equation

\[
 \Delta=K_{LR}(R_4^{-1})\Delta,
 \qquad \lambda_{\max}(K_{LR})=1
\]

at threshold; it is not inferred from the zero classical fermion background.

The geometric weak part of this kernel is now exact. Under
\(\rho=2\chi\), the spatial (M_5) cap is an (S^4) hemisphere of radius
\(R_4). For a static coexact (S^3) vector harmonic with eigenvalue (m^2),

\[
 u_m(\rho)=\tan^m(\rho/2),
 \qquad \partial_nu_m|_{\partial}=m/R_4,
\]

so

\[
 \mathcal N_T=(\Delta_1^{\rm coexact})^{1/2}.
\]

This is the action-owned nonlocal order-one weak boundary operator. It is not
the missing local order-two Maxwell term. Moreover (T_R^a=0) for every
right-handed weak singlet, hence its left-right Higgs-channel factor is exactly
zero. The nonzero gap kernel must therefore be derived from color,
hypercharge, or a direct finite-Dirac interaction.

The single rank-16 carrier trace extends this exact nonlocal operator to the
full faithful gauge group without a new factor-dependent coefficient:

\[
 S_{\rm DtN}^{SM}=\frac{K_F^{(5)}}2\int\sqrt h\left[
 \frac53A_Y\mathcal N_TA_Y+A_2\mathcal N_TA_2+A_3\mathcal N_TA_3
 \right].
\]

Therefore the inverse current kernels lie on

\[
 G_Y:G_2:G_3=\frac35:1:1.
\]

The color-singlet left-right projections, before the common Fierz factor two,
are

\[
 C_u=\frac75,\qquad C_d=\frac{13}{10},\qquad
 C_e=\frac3{10},\qquad C_\nu=0.
\]

Thus the gauge kernel selects the ordering (u>d>e>\nu) and the up channel is
the first gap candidate. It is still proportional to (I_3) in family space.
The remaining dynamical factor is now a single definite operator:
the regulated left-right two-fermion susceptibility
\(\chi_{LR}\) on the actual odd-FR Weyl domain of
\(\mathbb R\times S^3\).

For one left-right Weyl pair this susceptibility is now exact:

\[
 \chi_{LR}=\frac1{2\pi^2R_4^2}
 \sum_{n\geq0}\frac{(n+1)(n+2)}{n+3/2}.
\]

Writing (q=\mu R_4), its meromorphic form and Laurent expansion are

\[
 S(s;q)=q^{2s}\left[\zeta_H(2s-1,3/2)
 -\frac14\zeta_H(2s+1,3/2)\right],
\]

\[
 S(s;q)=-\frac1{8s}+\frac1{24}-\frac{\gamma_E}{4}
 -\frac{\log2}{2}-\frac{\log q}{4}+O(s).
\]

The positive cutoff sum is

\[
 S_N=\frac{(N+1)(N+3)}2-rac14
 [\psi(N+5/2)-\psi(3/2)].
\]

The pole is exactly the local (H^\dagger H) operator. Consequently the
nonlocal spectral dependence is determined, while its finite local quadratic
subtraction remains an output required from the Aether reset law. A zeta
minimal-subtraction finite part is a convention and is not used as a physical
gap eigenvalue.

The static gauge pushforward also includes the Gauss/Coulomb sector. For a
scalar harmonic of level \(\ell\geq1\), the exact electric DtN eigenvalue is

\[
 \nu_\ell=\frac{\ell(\ell+2)}{(\ell+1)R_4},
\]

or

\[
 \mathcal N_0=\Omega-R_4^{-2}\Omega^{-1},
 \qquad \Omega=\sqrt{-\Delta_0+R_4^{-2}}.
\]

The \(\ell=0\) mode is the global Gauss mode. Thus the v15.66 carrier result
is the transverse part, while v15.68 supplies the electric part required by
the left-right binding problem.

Most importantly, absolute gauge normalization and nonzero Yukawa structure
are now one closure gate. Define one boundary functional

\[
 \Gamma_\partial[a,\psi]=-log\int_{B\Phi=(a,\psi)}e^{-S_5[\Phi]}D\Phi.
\]

Its tree Schur reduction contains both

\[
 \frac{K_F^{(5)}}2\langle a,\mathcal N_{\rm DtN}a\rangle
 \quad\hbox{and}\quad
 -\frac1{2K_F^{(5)}}\langle J,G_{\rm DtN}J\rangle.
\]

The absolute local gauge residue is a two-point derivative of this same
\(\Gamma_\partial\); the composite zero mode, Higgs residue, and Yukawa
matrices are its four-point eigenvector and three-point residues. One parent
regulator and subtraction must be applied before all source derivatives.
Independent gauge normalization, an independent intrinsic Yukawa matrix, or
separate finite subtraction scales are excluded.

The common geometric heat regulator at
\(t=(\ell_\kappa/R_4)^2\) is a valid one-law test but is subcritical at the
regular reset: even the conservative up-channel norm bound is only
\(4.28294\times10^{-5}\).  This failure is not repaired by a separate Yukawa
term or a gauge rescaling.

The selected child action supplies a stronger, genuinely non-Gaussian event
coefficient.  Its localized principal-fiber kinetic weight is

\[
 W_{\rm event}=\Lambda(\sigma)L_\eta,
 \qquad \Lambda=1-4\sigma^2,
 \qquad L_\eta=1+X_\eta^3.
\]

Placing this weight once in the common rank-16 parent block gives, on a
regular branch slice with \(L=\min L_\eta>0\),

\[
 K_A(L)=L K_{A,0}+\Pi_{AA},
 \qquad B_u(L)=L^{-1}B_{u,0}.
\]

Here

\[
 B_{u,0}=2\frac75\,\chi_{LR}^{1/2}G_{{\rm DtN},0}\chi_{LR}^{1/2}
\]

is positive, compact under the one parent regulator, and nonzero.  If
\(\lambda_{u,0}=\lambda_{\max}(B_{u,0})\), the first crossing is therefore

\[
 \boxed{L_*=\lambda_{u,0}},
 \qquad \lambda_{\max}(B_u(L_*))=1,
 \qquad 0<L_*\leq9.01334422666\times10^{-5}.
\]

The spatially uniform replacement used in that formula is only a controlled
softening model.  On the actual cap \(L_\eta=L_\eta(\rho)\), and its first
minimum lies on an interior cohomogeneity-one shell.  The exact common object
is therefore the weighted Dirichlet problem

\[
 \langle a,\mathcal N[W_t]a\rangle
 =\min_{BA=a}\int_{M_5}W_t|d_AA|^2,
 \qquad W_t=(1-4\sigma_t^2)(1+X_{\eta,t}^3).
\]

It obeys the rigorous joint monotonicity law

\[
 W_1\leq W_2\Longrightarrow
 \mathcal N[W_1]\leq\mathcal N[W_2],
 \qquad \mathcal G[W_1]\geq\mathcal G[W_2].
\]

Thus the event lowers gauge stiffness and strengthens LR binding through the
same operator.  The first actual crossing

\[
 t_*:=\inf\{t:\lambda_{\max}(B_u[W_t])=1\}
\]

is, by definition, also the slice at which the absolute gauge and composite
Yukawa residues are evaluated from the same \(\Gamma_\partial\).  It cannot
be replaced by two independent normalization conditions, and it is not
inferred from \(\min L_\eta\) without evaluating the full weighted operator.

That actual nonround evaluation has now been performed on four controlled
Lorentzian child slices.  The lowest transverse and electric stiffnesses move
from approximately

\[
 (3091.98,2302.72)\quad\hbox{to}\quad(2588.00,1919.47),
\]

so the same-operator LR bound strengthens monotonically.  It reaches only
\(1.93\times10^{-5}\), however.  Even the frozen zero-shell limit retains a
finite exterior-annulus stiffness. Gauge exchange alone therefore does not
generate the condensate on this branch.

The adopted Dirac sector already contains a spin connection.  The minimal
Hermitian first-order completion of that foundational action and the parent
Einstein term has no new continuous coefficient. Writing
\(\omega=\omega^\circ+C\) and eliminating algebraic contorsion gives the
standard axial interaction and its scalar LR Fierz projection,

\[
 \Gamma_{EC}=-\frac12\langle J_S,\mathcal M_C[W]^{-1}J_S\rangle,
 \qquad
 G_{EC}(t)=\frac{3}{4K_G^{(5)}}
 \int ds\,J\frac{|u_0(s)|^4}{W_t(s)}.
\]

For an interior quadratic event shell,

\[
 W_\epsilon(s)=\Lambda_e[\epsilon+c_e(s-s_e)^2+\cdots],
\]

the exact eta-bound zero mode is nonzero at \(s_e\), and hence

\[
 G_{EC}(\epsilon)=\frac{A_{EC}}{\sqrt\epsilon}+O(1).
\]

The last controlled shell gives

\[
 A_{EC}=0.00231394,
 \qquad
 \epsilon_{*,u}^{\rm leading}=3.08435\times10^{-10}.
\]

Thus the coefficient-free Cartan block forces a finite pre-event composite
crossing.  This number is the frozen-shell leading value; the next system is
the coupled Hubbard--Stratonovich gap plus child KKT problem whose stress
shifts the event layer.  The gauge residue and nonzero composite Yukawa
residue remain evaluations of the same \(\Gamma_\partial\) on that coupled
solution.

That nonlinear gap equation has now been solved with the same heat regulator.
Writing \(x=mR_4\), it is

\[
 1=G_u(\epsilon)\,\chi(x),\qquad
 \chi(x)=\frac{1}{2\pi^2R_4^2}
 \sum_{n\ge0}\frac{(n+1)(n+2)e^{-t(n+3/2)^2}}
 {\sqrt{(n+3/2)^2+x^2}}.
\]

There is one positive solution for every \(\epsilon<\epsilon_{*,u}\).  For
example, \(x=0.50599\) at \(0.9\epsilon_*\) and \(x=1.52272\) at
\(0.5\epsilon_*\).  Its composite residue

\[
 Z_H=-\frac{\partial\chi}{\partial m^2}>0,
 \qquad Y=Z_H^{-1/2}
\]

is nonzero and is derived from the same regulated susceptibility; it is not a
second operator inserted after the gauge calculation.

The minimized gap potential satisfies

\[
 V_*<0,
 \qquad
 \frac{dV_*}{d\epsilon}
 =-\frac{x_*^2}{2\widehat g^2}
 \frac{d\widehat g}{d\epsilon}>0,
\]

so the condensate stress drives the same Legendre event.  As
\(\epsilon\downarrow0\), \(m\sim\epsilon^{-1/2}\) and
\(Y\sim\epsilon^{-3/4}\), while the gauge DtN residue remains finite.  If the
constrained KKT pencil gives \(\epsilon\sim(T_*-t)^p\), the mass and Yukawa
cycle insertions are finite precisely for \(p<2\) and \(p<4/3\), respectively.
The exponent is to be computed from that pencil; no configuration-space
kinetic law is silently assigned to the phase-space Legendre eigenvalue.

The physical pushforward is therefore one period of one functional,

\[
 \Gamma_{\rm cyc}=\Gamma_{\rm reset}
 +\int_0^{T_*}dt\,\Gamma_\partial[W_t].
\]

Absolute gauge normalization is \(T_*^{-1}\delta^2\Gamma_{\rm cyc}/\delta
F_i^2\).  The composite kinetic residue and LR vertex are the corresponding
second and third derivatives of this same \(\Gamma_{\rm cyc}\), and their
canonically normalized ratio is \(Y_f^{\rm cyc}\).  The fermion mass is the
logarithm of the same-period fermionic monodromy.  These are not two remaining
normalization problems.

The refined constrained trajectory changes which event variable is physical.
At (t=0.10602), the pointwise eta coefficient is

\[
 \min L_\eta=0.78065,
 \qquad \frac{d}{dt}\min L_\eta\simeq 2.8210\times10^3>0.
\]

It is moving away from zero.  The singular object is instead the
smallest-magnitude eigenvalue of the full eleven-dimensional Euler--Dirac
velocity/multiplier matrix,

\[
 \lambda_s=-3.51435\times10^{-3},
 \qquad \dot\lambda_s=2.04221\times10^2.
\]

Its linearized zero is (t_*\simeq0.1060372), where transported
(min L_\eta\simeq0.829).  The soft eigenvector is metric-shape dominated,
with largest component (e_s^{\dot w_1}=-0.89260). Consequently the
(L_\eta\downarrow0) Cartan shell calculation, its
(epsilon_*=3.08435\times10^{-10}) crossing, and its nonlinear gap branch
are conditional off-orbit results.  The algebraic Clifford coefficient
(c_{EC}=3/4) remains valid, but that extrapolated shell cannot be used as the
physical normalization slice.

The actual common reduction must use

\[
 \delta=-\lambda_s\downarrow0,
 \qquad
 \mathcal D_{KKT}=-\delta P_s+\mathcal D_\perp.
\]

If (J_s=e_s^T\delta\Gamma_5/\delta(\dot q,m)), eliminating the same soft
block gives

\[
 \Gamma_{\rm soft}=-\frac1{2\delta}\langle J_s,J_s\rangle.
\]

The next joint calculation is the fermionic spin-stress projection of this
term into the scalar LR channel and the gauge DtN evaluated on this same
(delta)-controlled layer.  Both residues then remain derivatives of one
(Gamma_{\rm cyc}); the correction changes the physical event variable, not
the one-pushforward requirement.

In the fixed constraint-solved Galerkin chart that projection is now explicit.
The soft mode induces

\[
 \delta_s\log N_*=-0.0922212,
 \qquad \delta_sH_4=-0.0220053.
\]

Because the wall-normal fermion overlap is exactly one, the lowest normalized
(S^3) Dirac mode has the nonzero source

\[
 g_{s,0}=-(\delta_s\log N_*)\frac{3}{2R_4}
          +\frac32\delta_sH_4
        =0.103733.
\]

The temporal left/right density product has a nonzero scalar Fierz component.
The first actual-orbit crossing therefore solves

\[
 1=B_u^{\rm gauge}
 +\chi_{LR}\frac{g_{s,0}^2}{2\delta_*},
 \qquad \delta_* =4.08349\times10^{-5}.
\]

It occurs at (t=0.106037009), with (min L_\eta=0.82526>0).  Transporting
the same child state to that slice and solving both nonround radial equations
gives

\[
 N_T=2594.57,
 \qquad N_E=1924.32,
 \qquad G_{LR}^{\rm soft}=131.756.
\]

These are the gauge and nonzero LR residues of one physical
(M_5\to M_4) localization calculation in the fixed Galerkin chart.  Their
full-period values still require the Sobolev lift and backreacted hybrid
cycle; no independent gauge or Yukawa normalization is introduced in that
lift.

The rank-one inversion in that paragraph is superseded by the invariant
calculation.  A Hessian eigenvalue and the source of a Euclidean-normalized
eigenvector depend on Galerkin coordinates; the physical response is

\[
 \mathcal K_{LR}^{(N)}=rac12J_{LR}^{T}\mathcal D_{KKT,N}^{-1}J_{LR}.
\]

Exact second variations now include the lapse, shift, ADM form, eta
nonlinearity, reciprocal FR inertia, and boundary Casimir term.  At every
radial order all (2N) lapse/shift constraints and the Hamiltonian constraint
are solved before inversion.  The matched lowest (S^3) Dirac states are
Killing spinors with homogeneous scalar stress, so their source has exactly
zero projection on nontrivial angular harmonics.  This reclassifies the
coordinate-dependent v15.80 value of (delta_*); its weighted DtN calculation
remains a valid fixed-chart diagnostic, not the physical gap crossing.

The same calculation also resolves the phrase “nonzero Yukawa sector.”  A
Yukawa vertex is not a condensate and is not a fermion mass.  The regular
Einstein--Cartan term is unweighted by (W) and gives a nonzero LR kernel.
Its exact Hubbard--Stratonovich representation is

\[
 e^{G_f\int O_f^\dagger O_f}
 \propto\int\mathcal D H_f\,
 e^{-\int(|H_f|^2/G_f-H_fO_f^\dagger-H_f^\dagger O_f)}.
\]

Thus the unnormalized LR--(H_f) vertex is one.  The same regulated fermion
determinant gives

\[
 Z_H(0)=0.00168735,
 \qquad Y_f=Z_H(0)^{-1/2}=24.3443
\]

per normalized paired mode in all four LR channels.  The branch remains
subcritical, so (H_*=m_*=0), but (Y_f\ne0).  On the identical controlled
(t=0.10602) slice the nonround pushforward gives

\[
 N_T=2588.002,
 \qquad N_E=1919.466.
\]

Therefore one physical (M_5\to M_4) boundary functional generates both the
absolute gauge normalization and the nonzero Yukawa sector.  No gap crossing
or second normalization condition is required for that statement.

The same functional has now been pushed through one controlled hybrid period.
Writing

\[
 \Gamma_{\rm cyc}=\int_0^{T_*}dt\,\Gamma_\partial[\Phi_*(t)]
 +\Gamma_{\rm reset},
\]

the reset map has zero probe derivative on the selected Aether event
component, so it introduces no extra kinetic normalization. PCHIP quadrature
of the constraint-solved cycle samples gives

\[
 \overline N_T=3166.083808,
 \qquad \overline N_E=2345.290877,
\]
\[
 Z_H^{\rm cyc}=0.001757141,
 \qquad Y_f^{\rm cyc}=(Z_H^{\rm cyc})^{-1/2}=23.855948.
\]

These four numbers are derivatives of this one \(\Gamma_{\rm cyc}\), not
independently fitted coefficients. Monotonicity supplies the controlled
envelopes

\[
 2588.002\leq N_T\leq3327.187,
 \quad 1919.466\leq N_E\leq2452.703,
 \quad 23.3404\leq Y_f\leq24.3443.
\]

On the symmetric orbit \(H_*(t)=0\), hence
\(M_f(t)=Y_f(t)H_*(t)=0\) and the mass part of the fermionic monodromy is the
identity. Thus the one-cycle calculation simultaneously yields positive
absolute gauge residues and a nonzero canonical Yukawa vertex, while its
Floquet mass remains zero. “Nonzero Yukawa,” “condensate,” and “nonzero
mass” are three distinct mathematical statements.

The family part of this residue is also fixed by the same localization. Let
\(P_a\) denote the three orthogonal triality eigenbundles. The parent operator
has no triality-changing block,

\[
 P_aD_5P_b=0\qquad(a\ne b),
\]

so every derivative of \(\Gamma_{\rm cyc}\) is diagonal in family space. The
cycle return is \(C_3\)-equivariant. Therefore

\[
 \operatorname{Diagonal}(3,\mathbb C)\cap\mathbb C[C_3]
 =\mathbb C I_3,
 \qquad Y_f^{\rm cyc}=23.855948 I_3.
\]

Abstract \(C_3\) symmetry alone permits a general circulant matrix, but such
off-diagonal terms require a triality-changing intertwiner that the localized
action does not contain. Family centrality is thus derived for this branch;
family hierarchy is absent rather than awaiting an independent Yukawa input.

Finally, the same cycle determines whether that vertex condenses. In the up
channel, which has the largest gauge attraction,

\[
 G_u(t)=2\frac75\left(N_T(t)^{-1}+N_E(t)^{-1}\right)+G_{EC}(t).
\]

On all controlled cycle slices,

\[
 6.6753\times10^{-5}\leq G_u(t)\chi(0;t)
 \leq7.0359\times10^{-5}<1,
 \qquad \overline{G_u\chi}=6.72468\times10^{-5}.
\]

Because \(\partial\chi/\partial(m^2)<0\), the nonzero gap equation cannot be
satisfied. Thus \(H_*=0\) and \(M_f^{\rm Floquet}=0\) are consequences of the
same pushforward that gives \(Y_f^{\rm cyc}\ne0\); they are not caused by a
missing Yukawa coefficient.

The same cycle also fixes its own matching scale. With
\(\ell_\kappa=\kappa_1^{-1/6}\), define

\[
 \log\mu_{\rm cyc}^{-1}
 =T_*^{-1}\int_0^{T_*}\log R_4(t)\,dt.
\]

Then

\[
 R_{\rm cyc}=1.02082779\ell_\kappa,
 \qquad \mu_{\rm cyc}=0.97959715\ell_\kappa^{-1}.
\]

The carrier trace extends both the transverse and electric DtN components on
the exact inverse-coupling ray \(K_Y:K_2:K_3=5/3:1:1\). They are components
of one nonlocal boundary form factor, not separately adjustable Maxwell
coefficients. Renormalization transports the common matched operator,

\[
 K_i(\mu)=K_i(\mu_{\rm cyc})
 -\frac{b_i}{8\pi^2}\log\frac{\mu}{\mu_{\rm cyc}},
\]

and supplies no new matching constant. An external number in GeV requires a
numerical value for the single dimensionful action datum \(\kappa_1\); that is
not a missing dimensionless gauge or Yukawa normalization.

The preceding v15.86--v15.90 averages use coordinate time and the frozen
spatial DtN operator. They are retained as diagnostics, but v15.91 supersedes
them as physical cycle normalizations. The physical functional uses boundary
proper time,

\[
 d\tau=N_b(t)dt,
 \qquad
 \Gamma_{\rm cyc}=\int_0^{T_*}d\tau\,\Gamma_{\rm proper}(t)
 +\Gamma_{\rm reset}.
\]

Restoring the constraint-solved ADM lapse in zero-shift gauge gives

\[
 I_B=\int d\chi\,\mathcal KWN\frac{C}{r},
 \qquad
 I_E=\int d\chi\,\mathcal KW\frac{Cr}{N},
\]

and

\[
 K_B=\frac{R_bI_B}{N_b},
 \qquad K_E=\frac{N_bI_E}{R_b}.
\]

Using this same proper-time measure for the gauge derivatives, composite
determinant, and matching scale gives

\[
 \overline K_B=813.476975,
 \qquad \overline K_E=2717.004292,
\]

\[
 Z_H^{\rm proper}=0.00176673551,
 \qquad Y_f^{\rm proper}=23.7910840I_3,
\]

\[
 \mu_{\rm proper}=0.97837264\ell_\kappa^{-1}.
\]

Thus gauge and Yukawa remain outputs of one physical pushforward. The same
calculation also gives a definite gauge-cone test,

\[
 \frac{\overline K_E}{\overline K_B}=3.33998918,
 \qquad
 \frac{c_{\rm gauge}}{c_{\rm metric}}
 =\sqrt{\frac{\overline K_B}{\overline K_E}}=0.54717654.
\]

The local Lorentzian Maxwell identity is therefore not yet established. The
next operator is not an independent gauge normalization: it is the full
shift-covariant frequency-dependent Schur complement of this same
\(\Gamma_{\rm cyc}\), including event/reset gluing. The v15.88 gap average is
likewise retained as a frozen-static subcritical diagnostic until that proper
operator is inserted.

The ADM-corrected lowest finite modes are

\[
 \overline N_T(\lambda_T=4)=2405.175268,
 \qquad
 \overline N_0(\lambda_0=3)=3795.978189.
\]

Substitution into the same proper Einstein--Cartan plus gauge gap kernel gives

\[
 6.5317\times10^{-5}\leq G_u(t)\chi(0;t)
 \leq6.7856\times10^{-5},
 \qquad
 \overline{G_u\chi}^{\rm proper}=6.55642\times10^{-5}.
\]

Hence the no-condensate result survives the ADM correction:
\(H_*=M_f^{\rm Floquet}=0\) while \(Y_f^{\rm proper}\ne0\).

Nor can the event reset supply an unrecorded quadratic correction. On the
selected Sobolev event component reconstruction is constant, so

\[
 D\widehat{\mathcal R}_s=D^2\widehat{\mathcal R}_s=0,
\]

and the Hessian chain rule gives

\[
 D^2(F\circ\widehat{\mathcal R}_s)=0.
\]

The normalized wall fermion independently gives the proper spatial principal
residue \(0.657256738\) relative to its unit temporal residue. The currently
derived propagation cones are therefore

\[
 c_{\rm metric}=1,
 \qquad c_\psi=0.657256738,
 \qquad c_A=0.547176542.
\]

They are pairwise distinct. This is a definite Lorentz-breaking symmetric
phase, not a normalization ambiguity. A common coordinate change preserves
the ratios, while independent gauge or fermion rescaling violates the one
pushforward construction.

Classical constraint backreaction cannot alter this conclusion at quadratic
order.  Let \(x\) denote all geometry, lapse, shift, material, and constraint
variables and \(m=(A,\Psi,H)\).  At the selected symmetric background
\(A_*=\Psi_*=H_*=0\), gauge invariance, fermion bilinearity, and the even
Hubbard--Stratonovich action imply

\[
 D_xD_A\Gamma=D_xD_\Psi\Gamma=D_xD_H\Gamma=0.
\]

Consequently the constrained Hessian and its matter Schur complement are

\[
 H^{(2)}=\begin{pmatrix}H_{xx}&0\\0&H_{mm}\end{pmatrix},\qquad
 H_{\rm eff}=H_{mm}-H_{mx}H_{xx}^{-1}H_{xm}=H_{mm}.
\]

The first classical backreaction terms have field degree four.  A common
Lorentz-invariant boundary term adds the same \(\Delta K\) to \(K_E\) and
\(K_B\), and therefore also preserves \(K_E-K_B\).

On the sparse v15.91 quadrature, the remaining correction could not
consistently be treated as a small one-loop normalization.  It gave

\[
 \delta K_E-\delta K_B=-(K_E-K_B),\qquad
 K_E-K_B=1903.527318.
\]

The triangle inequality then gives

\[
 \max(|\delta K_E|,|\delta K_B|)\geq951.763659
 =1.169995\,K_B.
\]

Thus a controlled one-loop expansion about the unshifted saddle cannot do
the required work.  Even assigning opposite maximal Standard Model one-loop
rates to the two coefficients would require more than \(10735\) logarithmic
scale units.  The next mathematical object is therefore the single regulated
quantum functional

\[
 \Gamma_q[\Phi;A,H]
 =\Gamma_{\rm cl}[\Phi;A,H]
 +\frac12\operatorname{STr}\log_{R_{\rm parent}}P[\Phi;A,H],
\]

whose quantum Euler--event saddle must be solved before recomputing
\(K_E,K_B,Z_\psi,Z_H\), and \(Y\).  In particular, no separate gauge
counterterm is introduced: the nonzero Yukawa operator must be pushed forward
again from that same quantum saddle.

This quantum functional now has a finite proper-cycle Galerkin realization.
On \(L^2(S^1_\tau\times S^3_{R_4(\tau)})\), set

\[
 P_{\rm cyc}=P_{A\oplus gh}\oplus P_{48W}\oplus P_{4HS},
 \qquad
 \Gamma_1^R=-\frac12\operatorname{STr}E_1(\ell_\kappa^2P_{\rm cyc}).
\]

The event is glued periodically by the derived Standard Model bundle
isomorphism, and longitudinal gauge and complex ghost modes cancel in the
BRST quotient.  At 24 proper-time nodes, the regulated free spectral seed is

\[
 \Gamma_1^R=1.27293717,
 \qquad
 \frac{d\Gamma_1^R}{d\log R_4}=8.37066013.
\]

The analytic Fréchet trace derivative agrees with a centered numerical
derivative to relative residual \(5.7\times10^{-10}\).  These numbers are the
free operator seed and geometry force, not the completed quantum saddle.  The
background-covariant source matrices still have to be inserted before taking
the common \(D_A^2\Gamma_q\), \(D_{H^\dagger}D_H\Gamma_q\), and
\(D_{\bar\Psi}D_\Psi D_H\Gamma_q\) derivatives.

The classical cycle has now also been densified.  The Euler--Dirac flow was
constraint-projected at \(\Delta t=5\times10^{-4}\) and every tenth state was
passed directly through the same ADM gauge and HS localization formulas.  The
uniform continuation reaches \(t=0.105\), where its next step encounters the
Legendre singularity; the independently refined constraint-solved
\(t=0.10602\) last-regular state closes the event-side quadrature.  Including
the event limit gives 24 direct rows and

\[
 K_B^{\rm dense}=809.858537,\qquad
 K_E^{\rm dense}=2514.195062,
\]

\[
 Z_{H,\rm pair}^{\rm dense}=0.00176756762,\qquad
 Y_{\rm pair}^{\rm basis}=23.7854834,
\]

\[
 \mu_{\rm dense}=0.97828731\,\ell_\kappa^{-1}.
\]

These jointly supersede the sparse v15.91 numerical averages.  In particular,

\[
 \frac{K_E^{\rm dense}}{K_B^{\rm dense}}=3.10448670,\qquad
 c_A^{\rm dense}=0.567551267.
\]

The dense quantum gate is correspondingly

\[
 K_E-K_B=1704.336525,\qquad
 \max(|\delta K_E|,|\delta K_B|)
 \ge 852.168262=1.052243\,K_B.
\]

Even the optimistic opposite-maximal one-loop running construction needs
\(9612.07\) logarithmic scale units.  The old sparse \(10735\) figure is
therefore superseded, while the theorem it tested survives: the necessary
correction remains larger than the full smaller classical coefficient and
must come from the one unsplit quantum event saddle.

The last number above is a nonzero normalized-pair HS basis vertex, not yet a
physical single-Higgs Yukawa matrix.  The explicit rank-16 trace resolves the
field normalization.  Family centrality gives pairing multiplicities

\[
 D=\operatorname{diag}(9,9,3,3)
\]

for the up, down, charged-lepton, and neutrino channel coordinates.  If a
candidate physical direction is \(H_f=c_fh\), then

\[
 Z_H(c)=Z_{\rm pair}\,c^\dagger Dc,\qquad
 Y_f(c)=\frac{c_f}{\sqrt{Z_{\rm pair}\,c^\dagger Dc}}.
\]

Thus the unit HS vertex remains nonzero, but the physical \(Y_f\) requires the
eigenvector \(c\) of the complete four-channel HS Hessian.  Assuming
\(c=(1,1,1,1)\), or canonically normalizing each channel independently, would
be an extra Higgs-alignment choice and is not made.

The source differentiation is also now executable without a commuting-vertex
approximation.  For (f(P)=-\tfrac12E_1(\ell_\kappa^2P)), the common response
engine evaluates

\[
 D_aD_b\operatorname{STr}f(P)
 =\sum_{ij}f'[\lambda_i,\lambda_j](P_a)_{ij}(P_b)_{ji}
 +\sum_i f'(\lambda_i)(P_{ab})_{ii}.
\]

The second term retains the gauge-covariant seagull vertex.  A noncommuting
matrix witness agrees with a centered two-source derivative.  The electric,
magnetic, HS, Yukawa, and geometry-force vertices are all declared on the
same (P_{\rm cyc}[\Phi;A,H,\Psi]) before any sector is extracted.  The next
step is therefore concrete matrix assembly in the radial-times-(S^3)
harmonic basis on each dense state, followed by one quantum Euler--event
solve.

There is one further accounting identity.  The v15.51 orbit already contains
the Standard Model zeta vacuum functional, so adding the heat determinant to
that attached action would count the same species twice.  The correct quantum
functional is the replacement

\[
 \Gamma_Q=\Gamma_{\rm attached}^{\zeta}
 -\Gamma_{\rm SM}^{\zeta}[\Phi;0,0,0]
 +\Gamma_{\rm SM}^{\rm heat}[\Phi;A,H,\Psi].
\]

Consequently the dense v15.97 orbit is a collocation seed, not the final
quantum orbit.  With 24 cycle nodes, nine geometry coordinates and four
lapse/shift multipliers per node, plus the period and phase multiplier, the
replacement action gives a square (24(9+4)+2=314) dimensional global KKT
system.  The determinant couples the cycle nodes and cannot be inserted as an
independent local acceleration.  This same replacement, saddle, and regulator
must precede both absolute gauge normalization and the nonzero Yukawa
extraction.

## 5. Standard Model attachment

Once \(\Phi_*\) is persistent, the physical four-dimensional action is

\[
 \Gamma_{M4}^{\rm phys}=\Phi_*^*\Gamma_{\rm stratified}.
\]

The gauge, Dirac/Weyl, color, family, mixing, neutrino, mass, and scale
operators are defined on this actual child. For a specified nonzero Higgs
background and specified intrinsic Yukawa operators, mixing would be

\[
 V_{\rm BHSM}
 =W_u^\dagger\operatorname{Pol}
 \left(G_u^{-1/2}K_{ud}G_d^{-1/2}\right)W_d.
\]

The construction ends when

\[
 \left|\mathrm{Sol}(\mathfrak C_{\rm BHSM})/
 (\mathrm{Gauge}\times\mathrm{Diff})\right|=1
\]

and every attached operator is derived and normalized.

`FULL_BHSM_COMPLETE = FALSE` because the interacting source Hessian and
coupled quantum event saddle and its four-channel HS Hessian remain to be
completed, and the
derived metric, fermion, and gauge cones are not equal. The event/reset and
classical constraint-backreaction quadratic contributions are exactly zero,
and controlled perturbative repair is too small. The family-central nonzero
HS basis vertices and both proper local gauge coefficients are already
generated together by one \(M_5\to M_4\) cycle functional; physical Yukawa
canonicalization awaits the same functional's HS eigenvector. The active calculation is the
common gauge--ghost--spinor--HS superdeterminant and quantum saddle inside that
same functional; it is not an independent normalization choice and not a
stopping condition.
