# v14.79 source provenance

Repository: `ncarberry64/Berger-Hopf-Standard-Model`

Recovered from PR #223:

- `src/bhsm/interface/completion/eta_minimally_gauged_p2_p8_action_v14_29.py`
  - retained candidate density `-w[kappa1 X/2 + X^4/8]`
  - fixed `p8` coefficient `1/8`
  - no new coefficient
  - common-domain reduction remains open

- `src/bhsm/interface/completion/full_hopf_preimage_effective_action_v14_30.py`
  - round full-preimage fiber-integrated measure factor
    `16 pi^2 a_fiber^3 cos(rho)^3`
  - constant-background Hessian is p2 only; `X^4` starts at eighth fluctuation order
  - nonlinear p8 reduction is `NOT_DERIVED`
  - nonlinear normalization requires profile tensors / infinite Clebsch-Gordan tower
  - degree-one full-preimage stationary background and self-adjoint domain remain absent

- `src/bhsm/interface/master_action/view2_master_action_promotion_v14_29.py`
  - `authoritative_action = None`
  - v14.29 View-2 action remains a conditional completion candidate
  - M8-to-collar eta/SU3 common-domain reduction remains open

The fine-structure scaling directive in v14.79 is a new architectural directive
from the current BHSM program.  It is not represented as a pre-existing
repository derivation.
