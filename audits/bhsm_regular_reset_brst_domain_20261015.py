"""Independent algebraic controls of the regular-reset FP adjoint domain.

No retained physical F/U or exterior is chosen.  Nonconstant unitary maps,
moving nonunit measures, independent antighosts and nonzero temporal/gauge
coefficients are source-level theorem controls, labeled as such in output.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
from scipy.linalg import expm

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'src'))
from bhsm.interface.gauge_connection_reset_bundle_lift_adjudication import induced_connection_transport
from bhsm.interface import muon_regular_reset_brst_domain as domain


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();mp.mp.dps=70
    records=[]
    for seed in (16101,16179):
        rng=np.random.default_rng(seed)
        def anti():
            a=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2))
            return (a-a.conj().T)/7
        K,L=anti(),anti();U0=expm(anti())
        U=np.stack((U0,K@U0,L@U0,K@L@U0))[:,None]
        J0=1.7 if seed==16101 else .43
        alpha,beta,kappa=.23,-.19,.11
        J=np.array((J0,J0*alpha,J0*beta,J0*(alpha*beta+kappa)))[:,None]
        fieldjets=[rng.normal(size=(4,1,2,2))+1j*rng.normal(size=(4,1,2,2)) for _ in range(8)]
        names=('ghost_parent_jet','ghost_child_pulled_jet',
            'ghost_parent_outward_conormal_jet','ghost_child_pulled_outward_conormal_jet',
            'antighost_parent_jet','antighost_child_pulled_jet',
            'antighost_parent_outward_conormal_jet','antighost_child_pulled_outward_conormal_jet')
        operands=dict(zip(names,fieldjets))
        out=domain.regular_reset_fp_domain_jets(bundle_jet=U,boundary_density_ratio_jet=J,**operands)
        keys=('ghost_trace_rows','ghost_outward_conormal_rows',
            'independent_antighost_trace_rows','independent_antighost_outward_conormal_rows')
        numerical=np.concatenate([out[key].reshape(4,-1) for key in keys],axis=1)
        mm=lambda a:mp.matrix([[mp.mpc(str(z.real),str(z.imag)) for z in row] for row in a])
        Km,Lm,Um=map(mm,(K,L,U0))
        fj=[[mm(a[i,0]) for i in range(4)] for a in fieldjets]
        def literal(x,y):
            u=mp.expm(x*Km)*mp.expm(y*Lm)*Um
            ud=u.H;j=mp.mpf(str(J0))*mp.exp(mp.mpf(str(alpha))*x+mp.mpf(str(beta))*y+mp.mpf(str(kappa))*x*y)
            gp,gc,pp,pc,bp,bc,pbp,pbc=[a[0]+x*a[1]+y*a[2]+x*y*a[3] for a in fj]
            vals=(gc-u*gp*ud,pp+j*ud*pc*u,bc-u*bp*ud,pbp+j*ud*pbc*u)
            return mp.matrix([z for a in vals for z in a])
        h=mp.mpf('1e-15');zero=mp.mpf(0)
        exact=[literal(zero,zero), (literal(h,zero)-literal(-h,zero))/(2*h),
            (literal(zero,h)-literal(zero,-h))/(2*h),
            (literal(h,h)-literal(h,-h)-literal(-h,h)+literal(-h,-h))/(4*h*h)]
        reference=np.array([[complex(z) for z in a] for a in exact])
        jeterror=float(np.max(abs(numerical-reference)))
        primal=lambda a:domain._mul(domain._mul(U,a),domain._dagger(U))
        adjoint=lambda a:domain._scale(domain._mul(domain._mul(domain._dagger(U),a),U),J)
        matched=operands.copy()
        matched['ghost_child_pulled_jet']=primal(matched['ghost_parent_jet'])
        matched['ghost_parent_outward_conormal_jet']=-adjoint(matched['ghost_child_pulled_outward_conormal_jet'])
        matched['antighost_child_pulled_jet']=primal(matched['antighost_parent_jet'])
        matched['antighost_parent_outward_conormal_jet']=-adjoint(matched['antighost_child_pulled_outward_conormal_jet'])
        yes=domain.regular_reset_fp_domain_jets(bundle_jet=U,boundary_density_ratio_jet=J,**matched)
        # A guessed dual-density rule on the antighost FIELD is distinguishable.
        wrong=matched.copy();wrong['antighost_child_pulled_jet']=matched['antighost_child_pulled_jet']/J0
        bad=domain.regular_reset_fp_domain_jets(bundle_jet=U,boundary_density_ratio_jet=J,**wrong)
        Ap=np.stack([anti() for _ in range(4)])
        dU=np.stack([anti()@U0 for _ in range(4)])
        M=np.array([[1.2,.1,0,.02],[.04,.93,.07,0],[0,.03,1.14,-.04],[.06,0,.03,.86]])
        Ac=induced_connection_transport(Ap,M,U0,dU)
        Acpulled=np.einsum('mi,mab->iab',M,Ac)
        c=anti();dc=np.stack([anti() for _ in range(4)])
        brst=domain.regular_reset_internal_brst_intertwiner(bundle=U0[None],
            bundle_spatial_derivatives=dU[None],parent_connection=Ap[None],
            child_connection_pulled=Acpulled[None],parent_ghost=c[None],
            parent_ghost_spatial_derivatives=dc[None])
        fail=False
        broken=U.copy();broken[3,0]+=np.eye(2)*.01
        try:
            domain.regular_reset_fp_domain_jets(bundle_jet=broken,boundary_density_ratio_jet=J,**matched)
        except ValueError:
            fail=True
        record=dict(seed=seed,classification='ALGEBRAIC_SOURCE_LEVEL_DOMAIN_CONTROL_NOT_PHYSICAL_HISTORY',
            independent_mp70_total_pullback_jet_error=jeterror,
            arbitrary_trace_cross_green_factorization_error=float(np.max(abs(out['cross_green_identity_defect']))),
            matched_domain_all_jet_rows=float(max(np.max(abs(yes[k])) for k in keys)),
            matched_domain_cross_green_all_jets=float(np.max(abs(yes['cross_green_form']))),
            wrong_antighost_field_density_rule_detected=float(np.max(abs(bad['independent_antighost_trace_rows'][0]))),
            density_ratio=J0,noncommuting_bundle_generators_norm=float(np.linalg.norm(K@L-L@K)),
            independent_antighost_vs_ghost_norm=float(np.linalg.norm(fieldjets[4][0]-fieldjets[0][0])),
            internal_brst_four_axis_intertwining_error=float(np.max(abs(brst['internal_brst_intertwining_rows']))),
            existing_affine_owner_incidence_error=float(np.max(abs(brst['affine_connection_incidence_rows']))),
            nonzero_temporal_parent_connection_norm=float(np.linalg.norm(Ap[0])),
            nonzero_temporal_child_connection_norm=float(np.linalg.norm(Ac[0])),
            nonzero_temporal_bundle_derivative_norm=float(np.linalg.norm(dU[0])),
            incompatible_mixed_unitarity_jet_rejected=fail)
        if jeterror>1e-12 or record['arbitrary_trace_cross_green_factorization_error']>1e-11:
            raise AssertionError(record)
        if record['matched_domain_cross_green_all_jets']>1e-11 or record['internal_brst_four_axis_intertwining_error']>1e-12 or not fail:
            raise AssertionError(record)
        records.append(record)
    result=dict(classification='REGULAR_RESET_FP_ADJOINT_DOMAIN_CONSTRUCTED_WITH_SUPPLIED_TOTAL_FIRST_AND_MIXED_JETS',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        module_sha256=sha256(Path(domain.__file__).read_bytes()).hexdigest(),
        affine_owner_sha256=sha256((REPO/'src/bhsm/interface/gauge_connection_reset_bundle_lift_adjudication.py').read_bytes()).hexdigest(),
        records=records,physical_incidence_packet_consumed=False,
        physical_outgoing_domain_evaluated=False,full_derivative_at_2e_minus_10_passed=False,
        coupled_corrections=0,spin_normalization_evaluated=False,muon_magnetic_moment=None,
        scope='No F/U, measure, exterior or quantum state selected. Four-axis nonzero temporal algebraic controls are not a full spacetime background or physical derivative.')
    args.out.mkdir(parents=True,exist_ok=False)
    (args.out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
