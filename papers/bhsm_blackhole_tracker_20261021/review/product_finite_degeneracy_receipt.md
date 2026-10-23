# Exact finite harmonic / compact degeneracy control

**C9 operator identity and inflated-state rejection pass.** This is a formal operator test with deliberately nonadmitted coefficients, not a physical scalar-state injection or sensitivity calculation. Only `LensEngine.potential` evaluates these large coefficients. Public `predict` is tested separately and rejects the state under the physical admission rules.

For zero monopole flux, a transverse boundary coefficient a produces the exact harmonic phase `q(r)=K*a/r²`, where `K=-beta_hat*N2*r0_pc³/(3*mref_pc*rE_pc²)`. The coefficient is computed independently from the supplied geometry, SI mass length, orthonormal N2=sqrt(15/(16*pi)), and the pinned action background beta_hat. An ordinary compact quadrupole with coefficient K*a has the same potential, gradient and Hessian. The axial zero-flux projection vanishes.

Three finite two-component states and three finite compensating changes of compact/boundary coefficients reproduce the same operator. Maximum absolute potential/gradient/Hessian difference is 2.22e-16, within the frozen rtol=atol=5e-12. The four combined compact/boundary operator columns have singular values about 136.05, 135.98, 4.32e-14 and 2.93e-14, hence rank two at the fixed relative 1e-10 cutoff. Two separate pairs of amplitudes cannot be identified by their shared operator. This is a finite model identity, stronger than a first-order null of a particular mass estimator.

The inflated state is rejected by the public forward interface: `prediction outside admitted r1_boundary_conditional domain: worldtube_weak_metric, state_within_sufficient_cap, small_spatial_background_gradient`. Physical claims continue to use the admitted amplitude cap.

The nonlinear product currently does not expose a joint unconstrained compact-plus-boundary fit, so this control does not claim calibration of four separate amplitude intervals. It verifies the finite cause ambiguity, the expected rank loss, and the public admission boundary. A future joint fit must preserve the two nulls or name any prior that removes them.

Complete mappings, coefficients, source hashes and numerical results are recorded in `product_finite_degeneracy_receipt.json`; replay with `python product/tests/check_finite_harmonic_degeneracy.py`.
