# AE3.1 current-C2 gauge--spinor--ghost Calderon trace skeleton

The owned AE2 reset defines a unitary transmission graph. For any reset lift
`U`, the orthogonal projector onto `graph(U)` is

```text
P_graph = (1/2) [[I,U_dagger],[U,I]].
```

It is Hermitian, idempotent, half rank, and fixes every admissible trace
`(x,Ux)`. Applying this construction to the coexact gauge, matched
constraint/ghost, and spinor-times-family sectors assembles the complete
current reset-transmission trace skeleton without a new boundary parameter.

This projector is not the missing physical outer Calderon projector. The
distinction is now exact:

- the reset graph glues event and child traces and variations;
- reciprocal gauge transmission doubles both residues and retains
  `Z_t/Z_s=0.590609601652908`;
- unitary spinor transport preserves the continuum of admissible Hadamard
  covariances and selects no positive-frequency splitting;
- it therefore supplies no finite state-dependent scalar determinant.

The one missing outer operator is typed as

```text
C_phys,current-C2(omega,k;z_event)
```

on the direct sum of coexact gauge Cauchy data, temporal/longitudinal
constraint data, Faddeev--Popov ghost data, and the self-dual spinor CAR trace
with its family factor. It must be self-adjoint on the complete Green pairing,
BRST compatible, reset compatible, and family preserving.

Its required outputs are simultaneously:

1. noncommon gauge DtN derivatives satisfying
   `delta_Z_t-delta_Z_s=0.409390398347092`;
2. one action-selected spinor Cauchy covariance/polarization;
3. the finite `Z_fin[C,mu]` and `H0_fin[C,mu]` entering the scalar determinant.

The N=3 chain closes the gravity/eta scalar boundary block but explicitly
leaves this gauge--spinor--ghost projector open. Archived Wentzell matrices
cannot be substituted because their current event-specific gauge curvature
and complete Calderon provenance remain absent.

Promoted:

- the exact multi-sector reset graph projectors;
- the direct-sum gauge--ghost--spinor trace skeleton;
- proof that transmission is not physical outer selection;
- one shared typed owner for three downstream dependencies.

Not promoted:

- the physical outer Calderon projector itself;
- a selected fermion state, Maxwell residue, finite scalar Hessian, photon, or
  muon magnetic moment.

`FULL_BHSM_COMPLETE = FALSE`.
