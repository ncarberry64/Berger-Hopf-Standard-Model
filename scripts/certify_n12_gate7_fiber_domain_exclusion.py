"""Necessary-row feasibility of the fiber-constrained interval-13 solve.

Use the certified uniform covector in a signed mean-value support calculation.
If even the fiber row excludes zero, no augmented center can exist in this
frozen affine endpoint domain. No Newton iteration or scientific producer.
"""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx, fmpq

from checkpoint_n12_gate7_66d_tangent_binding import ROOT, BASE, FIXED, PHYSICAL, amat, digest, encoded
from audit_n12_gate7_history_jet_prerequisites import EVIDENCE, interval

COVECTOR = ROOT / BASE / 'gate7_fiber_covector_20260927'
FIBER = ROOT / BASE / 'gate7_descriptor_fiber_owner_20260926/report.json'
DOMAIN = EVIDENCE / BASE / '.affine_action_hessian_pilot_work/endpoint_013'
EIGEN = EVIDENCE / BASE / '.affine_eigenpair_pilot_work/endpoint_013'
RADII = EVIDENCE / BASE / 'BHSM_N12_GATE7_PHYSICAL_INCIDENCE_CAUSAL_ENVELOPE.json'


def restore(z, name):
    c, r = z[name+'_mid_q'], z[name+'_rad_q']
    return np.array([arb(str(a))+arb(0,arb(str(b))) for a,b in
                     zip(c.flat,r.flat,strict=True)],dtype=object).reshape(c.shape)


def signed_support(g, state_direction, descriptor_direction, state_frame,
                   descriptor_scale, r_long, r_trans):
    """Compose g*dY-ds first; support interval x Euclidean ball afterward."""
    if g.nrows()!=1 or g.ncols()!=state_frame.nrows() or state_direction.ncols()!=1:
        raise ValueError('one covector and compatible state columns required')
    longitudinal=(g*state_direction)[0,0]-descriptor_direction
    transverse=g*state_frame
    row=transverse.entries()+[-descriptor_scale]
    norm=sum((abs(v).upper()**2 for v in row),arb(0)).sqrt().upper()
    long_bound=(abs(longitudinal).upper()*r_long).upper()
    trans_bound=(norm*r_trans).upper()
    return longitudinal,row,long_bound,trans_bound,(long_bound+trans_bound).upper()


def calculate():
    ctx.prec=512;sources={}
    def bind(p,expected=None):
        actual=digest(p)
        if expected is not None and actual!=expected:raise ValueError('source changed: '+str(p))
        key=p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p.resolve())
        sources[key]=actual
    def read(p):
        bind(p);return json.loads(p.read_bytes())
    cov=read(COVECTOR/'report.json');fiber=read(FIBER)
    bind(COVECTOR/'arrays.npz',cov['arrays_SHA256'])
    receipt=read(COVECTOR/'reproduction.json')
    for name,entry in receipt['files'].items():
        bind(COVECTOR/name,entry['SHA256'])
        if not entry['byte_identical']:raise ValueError('independent covector replay required')
    domain=read(DOMAIN/'record.json');dom_receipt=read(DOMAIN/'reproduction.json')
    bind(DOMAIN/'record.json',dom_receipt['record_SHA256'])
    bind(DOMAIN/'matrix.npz',domain['data_SHA256'])
    eig=read(EIGEN/'record.json')
    # The covector is certified using this exact eigenpair packet/domain.
    bind(EIGEN/'record.json',cov['source_SHA256'][str((EIGEN/'record.json').resolve())])
    bind(EIGEN/'eigenpair.npz',cov['source_SHA256'][str((EIGEN/'eigenpair.npz').resolve())])
    for p in (ROOT/FIXED,ROOT/PHYSICAL):
        bind(p,cov['source_SHA256'][str(p.resolve())])
        bind(p,eig['binding']['files'][p.relative_to(ROOT).as_posix()])
    bind(RADII,eig['binding']['files'][RADII.relative_to(EVIDENCE).as_posix()])
    radii=json.loads(RADII.read_bytes())['stored_polynomial_adjudication']['witness']['radius']
    rL,rT=map(arb,(domain['radius_longitudinal_rational'],domain['radius_transverse_rational']))
    if any(a.fmpq()!=arb(float(b)).fmpq() for a,b in zip((rL,rT),radii,strict=True)):
        raise ValueError('trial radii differ')
    if not (dom_receipt['independent_recomputation'] and dom_receipt['byte_identical']
            and eig['report']['validation_passed'] and eig['report']['uniform_action_eigenpair_enclosed']):
        raise ValueError('paired certified domain/eigenline required')
    with np.load(ROOT/FIXED) as z:weights=z['state_weights']
    with np.load(ROOT/PHYSICAL) as z:B=amat(z['endpoint_physical_tangent_action'][13])
    with np.load(COVECTOR/'arrays.npz') as z:g=arb_mat(1,98,list(restore(z,'affine_tube_gradient_action').flat))
    with np.load(DOMAIN/'matrix.npz') as z:u=restore(z,'raw_longitudinal_direction')
    with np.load(EIGEN/'eigenpair.npz') as z:
        dirs=restore(z,'affine_directions')
        # Frozen action maps define both the eigenline and covector domains.
        # Verify the serialized state generators agree exactly as balls.
        def same(a,b):return a.contains(b) and b.contains(a)
        if not all(same(a,b) for a,b in zip(u[:98],dirs[:,0],strict=True)):
            raise ValueError('longitudinal domain mismatch')
        for i in range(98):
            for j in range(74):
                wanted=B[i,j].fmpq()/arb(float(weights[i])).fmpq() if j<73 else fmpq(0)
                if not dirs[i,j+1].lower().fmpq()<=wanted<=dirs[i,j+1].upper().fmpq():
                    raise ValueError('transverse frame mismatch')
    weighted_u=arb_mat(98,1,[u[i]*arb(float(weights[i])) for i in range(98)])
    ell,row,sL,sT,support=signed_support(g,weighted_u,u[98],B,arb(1e-7),rL,rT)
    residual=fiber['node13']['residual_physical']
    # Keep certified rational endpoints; avoid widening through binary64.
    lower=(arb(residual['lower_exact'])-support).lower()
    upper=(arb(residual['upper_exact'])+support).upper()
    if not upper<0:raise ValueError('fiber exclusion not proved; proceed to center solver instead')
    for name in ('src/bhsm/interface/affine_longitudinal_hessian.py',
                 'src/bhsm/interface/direct_physical_neighborhood.py',
                 'scripts/certify_n12_gate7_affine_action_hessian_pilot.py',
                 'scripts/certify_n12_gate7_affine_eigenpair_pilot.py'):
        bind(EVIDENCE/name,eig['binding']['files'][name])
    for p in (Path(__file__).resolve(),ROOT/'scripts/checkpoint_n12_gate7_66d_tangent_binding.py',
              ROOT/'scripts/audit_n12_gate7_history_jet_prerequisites.py'):bind(p)
    report=dict(
        status='FROZEN_ENDPOINT13_DOMAIN_RECLASSIFIED_FIBER_ZERO_EXCLUDED',
        base_commit='752fff23b4809572b292c5a25deb1f8675ef32c1',source_SHA256=sources,
        interval=13,endpoint=13,
        domain='z13+E13(e13*l+t), |l|<=rL, ||t||2<=rT; the saved full 74-coordinate transverse ball is a superset of the axis-orthogonal ball.',
        radius_longitudinal_exact=str(rL.fmpq()),radius_transverse_exact=str(rT.fmpq()),
        radius_longitudinal_diagnostic=float(rL),radius_transverse_diagnostic=float(rT),
        coordinate_convention='weighted 98-state plus physical descriptor; E13=diag(B13,1e-7); raw state directions multiplied by W_state once.',
        necessary_owner_row='R_fiber(Y13,s13)=lambda_event(Y13)-s13',
        augmented_residual_implication='Every zero of the SAME HS+constraint+boundary+implicit-owner+fiber residual in this domain must make R_fiber zero. Its exclusion suffices regardless of the other residual rows.',
        mean_value_formula='R(z+du)-R(z)=integral_0^1 [g(Y(tau))*du_state-du_s] dtau. The frozen affine domain is convex and the selected line is uniformly certified there.',
        signed_longitudinal_row=interval(ell),
        longitudinal_support_upper_exact=str(sL.fmpq()),longitudinal_support_upper_diagnostic=float(sL),
        transverse_Euclidean_support_upper_exact=str(sT.fmpq()),transverse_support_upper_diagnostic=float(sT),
        total_support_upper_exact=str(support.fmpq()),total_support_upper_diagnostic=float(support),
        center_fiber_residual=residual,
        full_domain_fiber_residual=dict(lower_exact=str(lower.fmpq()),upper_exact=str(upper.fmpq()),
            lower_diagnostic=float(lower),upper_diagnostic=float(upper),contains_zero=False),
        separation_from_zero_lower_exact=str((-upper).fmpq()),
        separation_from_zero_lower_diagnostic=float(-upper),
        defect_to_support_ratio_diagnostic=float(abs(arb(residual['upper_exact']))/support),
        ratio_scope='Ratio inside the certified calculation only; not a claimed necessary enlargement factor outside the domain where g is certified.',
        corrected_center=None,block_corrections=None,full_augmented_center_residual=None,
        corrected_center_Jacobian=None,corrected_center_rank=None,corrected_center_sigma_min=None,
        corrected_center_condition=None,corrected_center_inverse_defects=None,
        authoritative_66D_tangent=None,pairwise_comparisons_with_new_tangent=None,
        tangent_reclassification='NONE: no admissible corrected center in this domain, so no new tangent C exists for comparison here.',
        exact_failed_object='A fiber-consistent endpoint-13 base point inside the frozen signed affine endpoint domain.',
        next_single_owner='An action-owned fiber-consistent endpoint-13 domain/center certificate with its constraint and boundary parameterization; validate its relation to the frozen history before any local Jacobian or downstream rebinding.',
        scope='Exclusion only for this frozen affine domain and selected branch; no global nonexistence, physical instability, or contradiction to an augmented off-fiber local contraction is asserted.',
        center_solver_run=False,center_projected_after_solve=False,domain_enlarged=False,
        normal_directions_silently_added=False,independent_descriptor_input_added=False,
        scientific_producers_run=False,old_center_certificate_promoted=False,
        tolerances_changed=False,Layer_C_rebound=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    arrays={}
    for key,values in [('signed_longitudinal_row',[ell]),('signed_transverse_row',row)]:
        arrays[key+'_mid_q']=np.array([str(v.mid().fmpq()) for v in values])
        arrays[key+'_rad_q']=np.array([str(v.rad().upper().fmpq()) for v in values])
    return report,arrays


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report,arrays=calculate();args.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue());report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['status']);print(report['full_domain_fiber_residual'])


if __name__=='__main__':main()
