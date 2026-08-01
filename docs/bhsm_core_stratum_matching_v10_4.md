# BHSM v10.4 core-stratum matching

The complete domain is stratified as
`M_complete=M_regular union Sigma_core union M_core`. Only `M_regular` carries
the present nondegenerate inverse-metric action.

Variation separates two admissible ensembles:

- Terminal Dirichlet: `upsilon|Sigma_core=0`, `delta upsilon=0`, with fixed
  induced metric. This is well posed on the regular side but licenses no
  absorption, emission, or transfer claim.
- Flux matching: allow `delta upsilon` at the stratum and require
  `[Pi_upsilon]_Sigma=0`, where the regular contribution is
  `sqrt(|h|) n_A Z nabla^A upsilon` and the other contribution is the
  variation of `S_Sigma_core+S_core`.

The metric relation similarly equates the regular P1/GHY canonical momentum
to the metric variation of the stratum and core actions. On-shell tangential
stress, gauge-current, and topological-current balance have their standard
distributional forms. Their numerical fluxes are undefined because the core
action, core symplectic form, and core currents are not supplied.

The only identified support symplectic contribution is
`delta pi_upsilon wedge delta upsilon` on the regular side. No fundamental
dissipation or information destruction is introduced.

Conditional status:
`BHSM_REGULAR_TO_CORE_SUPPORT_BOUNDARY_CONDITIONS_DERIVED_CONDITIONALLY`.
