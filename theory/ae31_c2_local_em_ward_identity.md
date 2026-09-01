# AE3.1 current-C2 local electromagnetic Ward identity

The already-derived neutral connection Hessian supplies the structural
current `J_Q proportional to J3+JY`.  On the charged-lepton Dirac field, the
lower component of `L_L` has

```text
T3=-1/2,  Y_BH=-1/2,  Q_em=-1.
```

The all-left-handed representation ledger contains `e_c` with `Q_em=+1`;
charge conjugation therefore gives the physical right-handed component
`e_R` with `Q_em=-1`.  The three-family physical Dirac charge operator is

```text
Q_l=-I4_spinor tensor I3_family.
```

It commutes with the existing family-noncentral mass endomorphism.  For the
local current-`C2` inverse tree operator

```text
S_l^(-1)(p)=slash(p)-M_l,
Gamma_Q^mu=Q_l gamma^mu,
```

the exact Ward--Takahashi identity follows:

```text
q_mu Gamma_Q^mu
  = Q_l S_l^(-1)(p+q)-S_l^(-1)(p) Q_l.
```

The machine witness verifies the Clifford algebra, the mass-charge
commutator, and this identity simultaneously for the three retained family
projectors.  No observed lepton mass, gauge coupling, or photon residue is
used.

The on-shell vertex decomposes as

```text
Gamma^mu=F1(q^2) gamma^mu
         + i sigma^(mu nu) q_nu F2(q^2)/(2m).
```

Antisymmetry gives `q_mu sigma^(mu nu) q_nu=0`.  Therefore the Ward identity
constrains the longitudinal/Dirac part but cannot determine the Pauli form
factor.  The minimal local tree vertex has `F2=0`; this is not the quantum
muon anomaly.

This closes a structural piece of the muon chain while preserving the real
blocker.  A physical `F2(0)` still requires the canonically normalized photon
pole, an action-selected fermion two-point function, and the renormalized
state-dependent three-point vertex.

- `CURRENT_C2_LOCAL_STRUCTURAL_QEM_VERTEX_DERIVED = TRUE`
- `CURRENT_C2_LOCAL_TREE_WARD_TAKAHASHI_IDENTITY_DERIVED = TRUE`
- `CURRENT_C2_PAULI_FORM_FACTOR_TRANSVERSALITY_DERIVED = TRUE`
- `CURRENT_C2_MINIMAL_TREE_F2_ZERO_DERIVED = TRUE`
- `CURRENT_C2_PHYSICAL_PHOTON_POLE_DERIVED = FALSE`
- `CURRENT_C2_RENORMALIZED_MUON_VERTEX_DERIVED = FALSE`
- `MUON_MAGNETIC_MOMENT_DERIVED = FALSE`
