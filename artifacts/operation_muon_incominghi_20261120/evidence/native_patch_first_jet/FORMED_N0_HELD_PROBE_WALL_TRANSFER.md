# Formed n0 spin-gap transfer in the existing native wall chart

New calculation on one saved incoming-hi background. Combines its original n0 K84 action, its 84×20 Dirichlet lift and D20 conormal, and its actual n0 spin-pair/current/Higgs vertices. No new history, previous outgoing arm, canonical-stop response, or generic flat fixture attached.

Temporal wall trace is held. Let w be the free 16 spatial-connection and scalar wall coefficients. A=D20[4:,4:] is nonsingular (minimum singular value .009478881, maximum 4.108405). The coordinate-time spin gap E_up−E_down has linear covector g on w: N_wall/R4 multiplying the action-owned spatial current difference and N_wall multiplying the fixed-Y Higgs mass-vertex difference. This is a same-hi algebraic eigenpair comparison, not pole normalization. No source factor e or additional Haar normalization was inserted.

For unit axial trace q in the central hypercharge basis, or in the unit Higgs-aligned charge basis, solve full complement relaxation holding only qᵀw. With chi=qᵀA^-1q, tau=gᵀA^-1q, the induced gap per unit axial trace is tau/chi. This is verified against direct perturbed 6×6 eigensolves tracking the actual spin pair, not a reclassification by eigenvalue ordering.

| Axis-3 port | chi | Gap derivative / unit trace | Gap derivative / unit RHS traction | Direct trace only |
|---|---:|---:|---:|---:|
| Central hypercharge | .2425877974679 | 1.260378864249 | .3057525326532 | 1.260378937521 |
| Higgs-aligned EM | .2458520471552 | 1.001322859098 | .2461772747725 | .9964170052518 |

Interior original-equation residual below 7.3e−14. Complement reaction below 7e−16. Centered finite-difference eigensolve at amplitude1e−6 agrees with analytical coefficients within2.1e−9. Thus both axial coordinates are visible to this finite present-state spin-gap readout. The fact that their geometric carrier overlap is substantial does not make the readouts interchangeable. This is not the earlier parity-null finite n1 magnetic probe. A unit n0 covariant wall connection is not a normalized physical incident B.

Exact usable matching contract: if an exterior really is supported only on q and incurs outward action response Lambda and same-chart incident RHS j, then
  (A+Lambda q qᵀ)w=j q,
  delta gap=tau j/(1+Lambda chi).
This follows either by solving or projecting the paired action force. A held incident field requires the affine drive j derived from both incident trace and incident conormal; it is not “fixed wall trace” and is not a homogeneous force condition. For an exterior that couples additional shared wall variables, use the full jointly solved wall action; the rank-one formula does not apply.

The nonzero tau removes one potential internal ambiguity: an independently matched axial load would not be invisible to the saved spin pair. The finite calculation does not supply the two needed physical quantities Lambda and j per applied field, the actual induced temporal trace, scattering state normalization, or the physical n0/soft-photon matching. No g or new physical width, uncertainty, or regime identification.

Reproduce: OPENBLAS_NUM_THREADS=1 python native_patch_first_jet/formed_n0_wall_spin_transfer.py. JSON reports analytical/eigensolve checks; NPZ saves A and g for exact future joint contraction.
