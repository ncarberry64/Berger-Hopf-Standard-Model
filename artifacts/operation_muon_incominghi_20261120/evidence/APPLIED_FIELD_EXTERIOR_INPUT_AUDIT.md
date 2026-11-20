# Applied field and exterior source audit

Checked three additional source constructions on the retained repository branch:

1. muon_birth_external_trace_chart: constructs canonical half-density and energy-origin reset, with independent inverse-transpose dual. It explicitly keeps lapse out of spinor amplitude and does not select exterior band/mass. The scalar kinetic seam scaling computed earlier is a scalar phase-space chart, not this spinor half-density; they must not be interchanged.
2. muon_birth_incoming_parent_trace_response: supplies complete signed carrier shell bookkeeping and normalized trace pairings, but leaves physical P_F, amplitudes and all-level physical support unbound. It cannot turn the finite magnetic probes into normalized physical photon/lepton legs.
3. muon_exterior_face_source: explicitly leaves the exterior radial derivative, complete temporal momentum, and exterior affine return unevaluated. Its face source has pi_tau=-e*zeta*b_rho-e*H/2 for the specified unit b corner, with b_rho unknown. The material radial conormal is not the temporal momentum; substituting one for the other would change matching.

These are inspected source boundaries, not a claim that no future construction can supply the missing data.

## Preserve an applied field instead of allowing cancellation

Let w_inc and t_inc denote the same-domain physical incident trace and oriented traction. Write scattered trace w_sc=w-w_inc. If the action-owned exterior response is Lambda, a consistent sign convention can define the external force as
 f_ext=Lambda(w-w_inc)-t_inc.
Then the existing local wall equation becomes
 (K+Lambda)w=Lambda w_inc+t_inc-Pz-Qb.

The incident trace, its conormal, and Lambda must be computed together; setting f_ext=0 does not represent a held applied field. The formula is a matching identity, not a chosen Robin coefficient. It also shows why supplying only a nominal magnetic amplitude is insufficient to determine the exterior drive.

The already computed six adjoints give the source response once the six projections X^T f_ext are supplied. They do not determine these projections. The remaining uncomputed radial/trace data in the inspected exterior source affect precisely the force needed here. The source-compatible near-null bypass is preserved; no full inverse is demanded.

## Result of this pass

No additional numerical exterior force can be derived from these inspected contracts without supplying an exterior solution or boundary selection absent from them. I have not guessed b_rho, replaced a conormal by a time derivative, inserted an arbitrary impedance, or interpreted a free-wall cancellation as physical F2=0. The available raw268 and derivative arrays remain valid local assets; physical Pauli extraction is not numerically determined by them.

Sources:
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/codex/muon-parent-maxwell-density-review/src/bhsm/interface/muon_birth_external_trace_chart.py
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/codex/muon-parent-maxwell-density-review/src/bhsm/interface/muon_birth_incoming_parent_trace_response.py
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/codex/muon-parent-maxwell-density-review/src/bhsm/interface/muon_exterior_face_source.py
