# Collider preparation bound to the current muon continuation

This binds the user's selected preparation to checkpoint
`5493924e97c8d23b9aaf9f54bd3c7657dad71b6c`. It records unresolved physical
operands; it does not report a terminal application, convergence result,
derivative admission, corrected state, or magnetic-moment prediction.
The checkpoint and subsequent local changes are preserved.

## Bound preparation

- Benchmark: `BHSM_NEW_COLLIDER_ELECTRON_POSITRON_TO_MUON_ANTIMUON_V1`.
- Process/readout: `e- + e+ -> mu- + mu+`, retaining all other action-coupled
  outgoing channels and radiation.
- Equal central beam energies, head-on centers, zero transverse impact
  parameter in the selected baseline. The local collision tetrad is an
  operand, not an assumed global flat exterior.
- Independent unpolarized incoming spins, `rho_spin = I4/4`.
- Exact pair Fock density
  `rho_pair = (1/4) sum_(s,t) |e-_s,e+_t><e-_s,e+_t|`, with exactly one
  electron and one positron. Preserve this density for ordered four-point
  contractions; its one-body covariance is not a replacement quasifree state.
- Electron/muon family slots remain the frozen light/middle slots, respectively.
  These labels do not select spatial Dirac pole modes.

The retained receipt is
`artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation/result.json`,
SHA256 `4eb26ad104914e6d78cd686157aecbad83e8bb376e642eb514430377d35fe369`.
Its adjacent `actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz`
has SHA256 `20db0b3b1a5cb09be1979b0fb24027bbb70f713d4001bd8c50e9807137a136d3`.
These are inherited data references, not new pair-kinematics controls.

The existing receipt explicitly leaves `E_beam` an external scan parameter;
no numerical energy or scan grid has been recovered. The following remain
unresolved preparation operands, including functions rather than just numbers:

1. Particle/antiparticle spectral coefficients and packet profiles, widths,
   separation, encounter timing, and observable coherence/phase data.
2. Their common collision geometry, tetrad, gauge/Higgs/metric Cauchy fields,
   positive-frequency embedding, complete Cauchy pairing, and constraints.
3. Homogeneous incoming exterior fields or their actual incoming
   characteristic data. No incoming vacuum or no-extra-radiation condition
   has been selected. Retarded response support is not a primal initial state.
4. The same-action collision incidence `Phi_coll` and its first/second
   derivatives, connecting the prepared incoming fields to the event/history.
5. Physical same-domain electron/muon poles, residues, and owned energy units.

The reaction label and retained interior enclosure supply none of these
missing full exterior data. No free-space packet, vacuum, zero exterior,
measured mass, or beam energy is inserted here.

## Actual application boundary

The existing physical source consumers in
`audits/bhsm_collider_incoming_field_current.py` are:

1. `construct_action_packet_sections`: consumes the common spatial basis and
   derivatives, `H`, `R4`, gauge connection, actual particle/antiparticle
   coefficients, and complete Cauchy quadrature.
2. `validate_action_packet_Cauchy_Gram`: checks the complete represented
   Cauchy Gram, not a pointwise normalization.
3. `apply_incoming_packet_current` and `original_material_Gauss_source`:
   consume those actual full18 two-spin sections and the retained exact pair
   density, with original vertices/density/tests/quadrature. Higgs, stress,
   angular, and interface sources must be bound on that same state as well.
4. The actual collision pullback and connected retarded `K_ZZ^R` application
   must then consume these same fields/loads and return the temporal-Green
   conormals on the common event/history domain.

The existing CLI's `--preparation` argument executes finite CAR/current
algebra. It does not call the physical packet constructors with a supplied
collision state. No such physical operand file was recovered in the active
collider artifacts or relevant local recovery/spectral/source folders.

The saved
`artifacts/muon_physical_retarded_terminal_attempt_20261013/run_1/result.json`
is explicit: `physical_terminal_return` and
`physical_source_domain_derivative` are null. Its smallest unexecuted operand
is the connected chronological weak Gauss/BRST `K_ZZ^R` solve on the actual
future/background/source and the same-pairing `K_EZ` return. The producer
records this missing application; it is not an executed physical solver.

`canonical_terminal_return_two_jet` in
`src/bhsm/interface/muon_full_canonical_terminal_return.py` consumes explicit
transfer, forcing, terminal matrix, and terminal source in every base/first/
mixed packet. A physical continuing exterior must supply these values and
jets. Its zero-terminal controls cannot fill the missing preparation or
physical outgoing relation. No physical terminal run was launched by this
binding.

## Boundary and regular-cap conventions

Use the current interaction-dependent law from
`src/bhsm/interface/muon_two_collar_weak_domain.py` on the original two traces:
`z = U_geo (I + J^-1 C T B) x`. Retain spin and complement rows.
At nonzero surface source, do not additionally impose the free law `z=U_geo x`.
The new local law is not yet a joined physical collider/terminal application.

The coefficient called `c` in the regular central-cap result is precisely
`c = q(0)`, the central U(1) radial Gauss-flux integration constant, with
`q = MAXWELL_TO_CAP * k * (ordinary_t A_rho^Y - ordinary_rho A_tau^Y)`.
It is not a heat coefficient or the Higgs surface matrix `T`.
The retained proof is
`artifacts/muon_baton_zoo_radial_convergence_20261014/actual_initial_central_flux_regular_body_and_saved_pointwise_audit_run_2/result.json`,
SHA256 `82a9518e7584c0af1f760314769d488a4a421fd7983351edfb8d4807860c0f5e`.

Within its proved regular fixed-cap domain, finite absolute electric form
excludes a nonzero constant flux. On a source-free solution, Gauss then gives
`c=0` and `q(rho)=0`. With distributed source, regularity can still give
`q(0)=0` while sourced Gauss gives `q(rho)=-integral_0^rho j`, generally
nonzero. On an off-shell trial, the Gauss equation itself need not hold.
Neither the cap result nor zero projected moments establishes a vanishing
body source, a zero exterior return, or radial convergence.

## Admission and magnetic readout

Keep the physical preparation, fields, ports, and outgoing condition fixed
while resolving the radial spaces. A changing finite germ or tiny cap/row
residual is not convergence of this prepared physical problem.

Independently evaluate fresh original-equation directional differences,
including terminal return, source binding, bulk operator, port conversion,
and domain motion separately. The complete outgoing derivative must pass the
unchanged `2e-10` guard before one coupled state correction. Only then
reevaluate original Maxwell and all 226 original matching rows. The source
derivative retains its existing fixed-adjoint convention.

Historical before-values are retained, not recomputed by this binding:
Maxwell `|R_Z[3,2]|=2.4777309846820184`; original matching maximum
`9.602842247524184e-7`, one-based row 226
`common_normal_temporal_dual[0]`. This binding computes no after-values and
applies no coupled state correction.

Production and probe are separate. Preserve the outgoing spin density matrix
and all action-coupled channel/overlap information through the formed-muon
readout; do not take the inclusive outgoing spin trace as a substitute.
The magnetic target is the formed-muon pole/residue-normalized soft Pauli
response in a weak measuring field, not a timelike production form factor
at `s=4 E_beam^2`.

For admitted same-domain pole modes, the existing unsquared consumer uses
`Z=L Gamma_E R` and the full spin matrices
`H_B^a=-Z^-1 L Gamma_Ba R` for all magnetic axes, retaining off-diagonals.
Actual charge/Ward and soft-vertex normalization, native completion,
overlap accounting, and their error bounds remain required. Preserve any
surviving preparation dependence explicitly; this binding does not identify
it with a universal magnetic anomaly.
