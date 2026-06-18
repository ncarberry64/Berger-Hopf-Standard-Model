# Derived Finite-Width Overlap Moment Expansion

The finite-width scaffold expands the active and singlet internal modes around `y0` and contracts them with universal profile moments.

```text
Psi_A_i(y)=Psi_A_i(y0)+xi^a partial_a Psi_A_i(y0)+1/2 xi^a xi^b partial_a partial_b Psi_A_i(y0)+...
Psi_S_i(y)=Psi_S_i(y0)+xi^a partial_a Psi_S_i(y0)+1/2 xi^a xi^b partial_a partial_b Psi_S_i(y0)+...
```

Moment tensors:

```text
M0=integral Phi(y) dV_gamma
M_ab=integral xi_a xi_b Phi(y) dV_gamma
M_abcd=integral xi_a xi_b xi_c xi_d Phi(y) dV_gamma
```

Finite-width expansion:

```text
I_ij=M0 a_i^* b_j + M_ab (partial_a a_i^*)(partial_b b_j) + higher finite-width moments
```

Status: `FINITE_WIDTH_OVERLAP_MOMENT_SCAFFOLD_DERIVED_CONDITIONAL`.
