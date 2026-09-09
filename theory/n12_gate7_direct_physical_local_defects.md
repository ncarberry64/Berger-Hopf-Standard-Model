# Physical-point local blocks for the frozen Newton map

Direct ambient endpoint and physical-midpoint Jacobians enter the exact HS
chain rule before reduction to the unchanged stored trial and test frames.
For ambient residual derivatives `Dr0, Dr1`, fixed trial frames `E0, E1`,
test frame `T`, and stored frozen ambient left block `L` and reduced right
block `R`, define

```
C  = R^-1 T L E0
DL = R^-1 T (L - Dr0) E0
DR = I - R^-1 T Dr1 E1.
```

These are the local coefficients in the derivative of the frozen Newton
map, with the same signs as the existing finite-history composition:

```
v_(i+1) = -C_i v_i + DL_i u_i + DR_i u_(i+1).
```

The initial endpoint is fixed. Its input block `DL_0` is exactly zero and
`v_0=0`; the stored propagation block `C_0` remains recorded. No exact
orthonormality of either frame is assumed. All products and right-block
solves run in Arb at 512 bits. The unchanged binary64 frames and blocks are
treated as exact algebraic operands, not as a proved intrinsic quotient.

The consumer requires independently reproduced DF for both endpoints and
the actual physical midpoint of each selected interval. Exact derivative
and value manifests, raw-byte source bindings, and the legacy normalized
foundation bindings must agree. The result retains both hash conventions.
It exports rational Arb balls for `C`, `DL`, and `DR`. A second invocation
with `--recompute` performs the assembly again and requires identical JSON
and NPZ bytes. Mismatches retain both candidates.

After the paired selected DF campaign has completed, run:

```
python scripts/certify_n12_gate7_direct_physical_local_defects.py --midpoints 13
python scripts/certify_n12_gate7_direct_physical_local_defects.py --midpoints 13 --recompute
```

`--all-midpoints` requires all 370 intervals' derivative inputs. Complete
local blocks are still distinct from a bound on the full causal operator.
Physical branch continuation, state-dependent frame derivatives, quotient
identification, and neighborhood control remain separate obligations. This
consumer does not certify the full physical `Z1`, contraction, or Gate 7.
