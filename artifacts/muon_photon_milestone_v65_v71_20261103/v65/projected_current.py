"""v65: apply owned photon directions to the local classical current operator.

Only the frozen initializer coefficients are numerical. No physical current,
electric momentum, event history, native contraction or occupation is selected.
"""
from pathlib import Path
from hashlib import sha256
import argparse,importlib.util,json
import numpy as np
from prepare_evidence import npz,save

HERE=Path(__file__).resolve().parent
EPS=np.zeros((3,3,3));EPS[0,1,2]=EPS[1,2,0]=EPS[2,0,1]=1;EPS[0,2,1]=EPS[2,1,0]=EPS[1,0,2]=-1


def bracket(a,b):
    out=np.zeros(np.broadcast_shapes(a.shape,b.shape));out[...,:3]=np.cross(a[...,:3],b[...,:3])/np.sqrt(2)
    return out


def operators(theta,omega,E,stabilizer,stabilizer_gradient):
    """Unit-S3 coefficient application; density/radial multipliers stay external."""
    A=theta[6:18].reshape(3,4)
    s=np.sqrt(16/3)*stabilizer
    ds=np.zeros((4,22));ds[:,18:]=np.sqrt(16/3)*stabilizer_gradient
    curl=2*omega+np.einsum('ijk,jhl,klb->ihb',EPS,E,omega)
    div=np.einsum('ihl,ilb->hb',E,omega)
    Dq=bracket(A,s)
    neutral=np.einsum('c,ihb->ichb',s,curl)
    charged=np.einsum('ijk,jc,khb->ichb',EPS,Dq,omega)
    V=neutral+charged
    G=np.einsum('c,hb->chb',s,div)+np.einsum('ic,ihb->chb',Dq,omega)
    dV=np.zeros((22,)+V.shape);dG=np.zeros((22,)+G.shape)
    for a in range(22):
        dA=np.zeros((3,4))
        if 6<=a<18:dA.reshape(-1)[a-6]=1
        dDq=bracket(dA,s)+bracket(A,ds[:,a])
        dV[a]=np.einsum('c,ihb->ichb',ds[:,a],curl)+np.einsum('ijk,jc,khb->ichb',EPS,dDq,omega)
        dG[a]=np.einsum('c,hb->chb',ds[:,a],div)+np.einsum('ic,ihb->chb',dDq,omega)
    flat=lambda v:v.reshape(-1,8)
    K=flat(V).T@flat(V);Kn=flat(neutral).T@flat(neutral);Kc=flat(charged).T@flat(charged)
    dK=np.array([flat(v).T@flat(V)+flat(V).T@flat(v) for v in dV])
    return dict(source_s=s,source_s_gradient22=ds,curl_omega=curl,ordinary_divergence=div,
        D_source_s=Dq,magnetic_curvature=V,neutral_curvature=neutral,charged_curvature=charged,
        covariant_angular_divergence=G,magnetic_curvature_gradient22=dV,
        covariant_angular_divergence_gradient22=dG,magnetic_Gram8=K,
        neutral_Gram8=Kn,charged_Gram8=Kc,magnetic_Gram_gradient22=dK)


def owner_check(b,op):
    """Independent original Maxwell first variation on every source/harmonic.

Absent temporal/radial jets are NaN, not assigned physical zero. Only the
magnetic component, proved independent of these operands, is consumed.
"""
    p=HERE/'evidence/owned_curvature.py';spec=importlib.util.spec_from_file_location('owned_curvature_v65',p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    n=20*8
    field=np.empty((n,5,4));field[:,0]=b['theta22'][2:6];field[:,1]=np.nan;field[:,2:]=b['theta22'][6:18].reshape(3,4)
    direction=np.zeros_like(field)
    source=np.einsum('c,ihb->ihbc',op['source_s'],b['omega'])
    direction[:,2:]=source.transpose(1,2,0,3).reshape(n,3,4)
    ed=np.zeros((n,3,5,4))
    derivative=np.einsum('jhl,klb,c->jhbkc',b['E'],b['omega'],op['source_s']).reshape(3,20,8,3,4)
    ed[:,:,2:]=derivative.transpose(1,2,0,3,4).reshape(n,3,3,4)
    missing=np.full_like(field,np.nan)
    _,_,_,B=m._direction_polynomials(field,direction,missing,missing,ed)
    actual=B[0].reshape(20,8,3,4).transpose(2,3,0,1)
    assert np.isfinite(actual).all()
    return float(np.max(abs(actual-op['magnetic_curvature'])))


def calculate():
    p=HERE/'evidence/inputs.npz';provenance=json.loads((HERE/'evidence/provenance.json').read_text())
    assert sha256(p.read_bytes()).hexdigest()==provenance['inputs_sha256']
    with np.load(p,allow_pickle=False) as a:b={k:a[k].copy() for k in a.files}
    op=operators(b['theta22'],b['omega'],b['E'],b['stabilizer_value'],b['stabilizer_gradient'])
    s=op['source_s'];B=b['orbit_value'];Bg=b['orbit_gradient'];ds=op['source_s_gradient22'][:,18:]
    checks={
        'source_Gram_unit_Tr16':float(np.max(abs(np.einsum('ihA,ihB->AB',b['omega'],b['omega'])-np.eye(8)))),
        'coexact_divergence':float(np.max(abs(op['ordinary_divergence']))),
        'source_norm_16_over_3':float(abs(s@s-16/3)),
        'neutral_charged_orthogonality':float(np.max(abs(np.einsum('c,ichb->ihb',s,op['charged_curvature'])))),
        'Gram_split':float(np.max(abs(op['magnetic_Gram8']-op['neutral_Gram8']-op['charged_Gram8']))),
        'neutral_curvature_48I':float(np.max(abs(op['neutral_Gram8']-48*np.eye(8)))),
        'projected_angular_Gauss_zero':float(np.max(abs(np.einsum('c,chb->hb',s,op['covariant_angular_divergence'])))),
        'classical_Higgs_photon_current':float(np.max(abs(B@s))),
        'classical_Higgs_total_H_contact':float(np.max(abs(np.einsum('ach,c->ah',Bg,s)+B@ds))),
        'owned_original_magnetic_variation':owner_check(b,op),
    }
    # Independent central finite differences of the four normalized Higgs directions
    # are not needed: their archived analytic jets already have a receipt. Check
    # new coefficient chain rules by the polynomial gauge sector, exactly linear.
    for axis in (6,11,16):
        delta=np.zeros(22);delta[axis]=1/8
        plus=operators(b['theta22']+delta,b['omega'],b['E'],b['stabilizer_value'],b['stabilizer_gradient'])
        minus=operators(b['theta22']-delta,b['omega'],b['E'],b['stabilizer_value'],b['stabilizer_gradient'])
        checks[f'new_gauge_Gram_derivative_{axis}']=float(np.max(abs((plus['magnetic_Gram8']-minus['magnetic_Gram8'])/(1/4)-op['magnetic_Gram_gradient22'][axis])))
    # A photon insertion commutes with itself: no missing F.delta2F seagull
    # in this fixed-H, fixed-geometry neutral source direction.
    checks['neutral_second_curvature_zero']=float(np.max(abs(bracket(s,s))))
    checks['neutral_charged_contact_one_insertion_zero']=float(np.max(abs(np.einsum('c,ic->i',s,bracket(b['theta22'][6:18].reshape(3,4),s)))))
    op['magnetic_Gram_gradient189']=np.einsum('aij,ak->kij',op['magnetic_Gram_gradient22'],b['theta_full_gradient189'])
    op['covariant_divergence_gradient189']=np.einsum('achb,ak->kchb',op['covariant_angular_divergence_gradient22'],b['theta_full_gradient189'])
    assert max(checks.values())<2e-11,checks
    result=dict(schema='bhsm.muon-projected-photon-current.v65',classification='EVALUATED_CLASSICAL_PHOTON_CURRENT_COEFFICIENT_BLOCK_ON_SAVED_INITIALIZER',
        checks=checks,max_consistency_defect=max(checks.values()),source_count=8,angular_coordinate_count=400,
        scalar_harmonics=20,new_quadrature=False,new_resolution=False,
        magnetic_Gram_eigenvalues=np.linalg.eigvalsh(op['magnetic_Gram8']).tolist(),
        charged_Gram_eigenvalues=np.linalg.eigvalsh(op['charged_Gram8']).tolist(),
        covariant_angular_divergence_norm=float(np.linalg.norm(op['covariant_angular_divergence'])),
        covariant_angular_divergence_singular_values=np.linalg.svd(op['covariant_angular_divergence'].reshape(80,8),compute_uv=False).tolist(),
        D_source_s_norm=float(np.linalg.norm(op['D_source_s'])),
        source_Higgs_norm_squared=float(b['theta22'][18:]@b['theta22'][18:]),
        magnetic_Hessian_density_factor='-MAXWELL_TO_CAP*d(rho), with the owned radial source factors and same material measure; not inserted here',
        derivative_scope='22 local fields, then original saved 22x189 pullback; total physical response still requires actual source jets',
        physical_guard=2e-10,admitted_temporal_strength=2**-9,physical_state_admitted=False,
        complete_projected_current_evaluated=False,physical_reconnection_demonstrated=False,
        a_mu=None,g_mu=None,total_physical_uncertainty=None,
        earliest_remaining_equation='Covariant radial Gauss return with inherited normal flux and complete bulk current; match its conormal to boundary Higgs/native/released rows on the same partial graph.',
        boundary_Higgs_not_used_to_cancel_bulk=True,no_electric_momentum_selected=True,no_extra_occupations=True,
        prior_v64_remote_commit='1ef75378916644c34229da5c24148b85d9fba868')
    return op,result


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('Preserve prior runs')
    op,r=calculate();a.out.mkdir();npz(a.out/'projected_current.npz',op);save(a.out/'result.json',r)
    print(json.dumps({k:r[k] for k in ('max_consistency_defect','magnetic_Gram_eigenvalues','covariant_angular_divergence_norm','complete_projected_current_evaluated')}))

if __name__=='__main__':main()
