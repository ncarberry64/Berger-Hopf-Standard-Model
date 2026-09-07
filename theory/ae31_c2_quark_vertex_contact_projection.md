# AE3.1 current-C2 quark vertex/contact projection theorem

The retained product-Dirac source jet is a unit commuting reduced probe.  Its
exact dependence on the source-generator eigenvalue is

```text
V(q) = q V(1),
Q(q) = q^2 Q(1).
```

This follows directly from `delta W=q p`: the first derivative is linear and
the contact derivative quadratic in `q`.

The authoritative 1,222-segment descriptor contains the two keys families
`chirality_plus` and `chirality_minus`.  It has no up/down sector axis.  The
attached family factor is `I3`, and the unit probe is not a dynamical field
coordinate.  Chirality therefore cannot be relabelled as quark-sector
incidence.

Existing orthogonal sector projectors can define block support.  For

```text
G_H = q_u P_u + q_d P_d,
```

projection gives

```text
V_u=q_u V(1),  V_d=q_d V(1),
Q_uu=q_u^2 Q(1), Q_dd=q_d^2 Q(1), Q_ud=0.
```

But every finite pair `(q_u,q_d)` obeys the same projector algebra.  Two
explicit pairs give different up/down residue ratios while preserving
orthogonality and completeness.  The projectors select where the blocks act;
they do not select their coefficients.  Gauge closure similarly permits the
`H` and `H_tilde` contractions without deriving their absolute residues.

The exact missing object is a current-C2 representation-valued incidence map

```text
rho_qH : (H,H_tilde) -> End(Q_L direct_sum u_R direct_sum d_R)
```

whose first and second variations supply `V_u,V_d,Q_fg` with fixed trace,
domain, and field normalization.  The unit probe cannot be declared to have
both physical sector coefficients, and independent or mass-fitted values are
forbidden.

Promoted:

- exact unit-probe scaling;
- structural up/down block projection using existing projectors.

Not promoted:

- up/down incidence in the current descriptor;
- action-derived vertex/contact coefficients;
- a quark-channel direction, quark poles, or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
