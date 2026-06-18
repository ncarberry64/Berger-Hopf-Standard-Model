# Boundary Interface Mixing Kernel

Status: `BOUNDARY_INTERFACE_MIXING_KERNEL_STRUCTURAL_CANDIDATE`

Candidate interface kernel:

```text
I_ff'[i,j] =
    gcd(N_f,N_f') / sqrt(N_f*N_f')
    * exp[-tau_mix*D_ij^2 - tau_mix*beta_eff*D_ij^4]
    * exp[i * integral_Gamma(A_f - A_f')]
    * R_ij
```

Definitions:

```text
N_f = |Omega_f_star|
x_i = (q_i/N_f, j_i/N_f)
G_B = diag((1+epsilon)^(-2), 1)
D_ij^2 = (x_i - x_j)^T G_B (x_i - x_j)
A_f = O_q^f A_q + O_j^f A_j
```

Cover-overlap checks:

```text
C_ud = gcd(6,12)/sqrt(6*12) = 1/sqrt(2)
C_lnu = gcd(3,3)/sqrt(3*3) = 1
```

Physical unitary interface:

```text
V_ff' = I_ff' * (I_ff'^dagger I_ff')^(-1/2)
V_CKM = U_u^dagger V_ud U_d
U_PMNS = U_l^dagger V_lnu U_nu
```

This is a structural candidate. It does not update frozen CKM or PMNS output.
