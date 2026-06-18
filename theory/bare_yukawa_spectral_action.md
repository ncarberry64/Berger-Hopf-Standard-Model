# Bare Yukawa Spectral Action Candidate

Status:

```text
BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE
FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE
```

Candidate mass engine:

```text
m_f,i / m_f,0 = exp[-S_bare(q_i,j_i)] * Z_response(q_i,j_i)
```

Candidate bare action:

```text
lambda_hat(q,j) = (1+epsilon)^(-2) * q^2 + j^2

S_bare(q,j) =
    tau_0 * [lambda_hat(q,j) + beta_eff * lambda_hat(q,j)^2]
    - xi * q^2/(q^2+j^2)
```

Convention:

```text
q^2/(q^2+j^2) = 0 for (q,j)=(0,0)
S_bare(0,0)=0 by heavy/reference normalization
```

Interpretation:

1. second-order internal harmonic cost;
2. fourth-order topographic stiffness cost;
3. Berger-axis focusing bonus.

Open constants:

```text
epsilon, tau_0, beta_eff, xi
```

These constants remain candidate geometric-closure targets. They must not be
fitted per sector in this sprint.
