# Boundary Projector To State Bridge

```text
P_C eigenvalue 0 -> single_channel_boundary
P_C eigenvalue 1 -> three_channel_active

P_ell eigenvalue 1 -> leptonic_closure
P_ell eigenvalue 0 -> hadronic_closure

S_sigma eigenvalue +1 -> upper orientation
S_sigma eigenvalue -1 -> lower orientation

P_w eigenvalue 1 -> interface active
P_w eigenvalue 0 -> interface inactive
```

Physical registry:

```text
nu_L: C=0, ell=1, sigma=+1, w=1
e_L:  C=0, ell=1, sigma=-1, w=1
u_L:  C=1, ell=0, sigma=+1, w=1
d_L:  C=1, ell=0, sigma=-1, w=1
nu_R optional: C=0, ell=1, sigma=+1, w=0
e_R:  C=0, ell=1, sigma=-1, w=0
u_R:  C=1, ell=0, sigma=+1, w=0
d_R:  C=1, ell=0, sigma=-1, w=0
```

## Related Finite Algebra Gate

- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)
