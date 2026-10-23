"""New fourth AE4 E1 variation on the recorded current-C2 form prefix.

The actual saved K/M and source-owned V/Q are evaluated through fourth order.
Multiprecision tridiagonal Weyl solves avoid the ill-conditioned dense-float
low-eigenvalue subtraction. No descriptor/history/source solve is replayed.
The reduced HS result is not an intrinsic canonical Higgs quartic.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
import argparse
import json
import os
import sys
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'


def evaluate(repository,output):
    import numpy as np
    import mpmath as mp
    from scipy.linalg import eigh
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve every earlier evaluation.')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.ae3_c2_action_puzzle import reduced_product_dirac_hs_source_jet,assemble_tridiagonal
    from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    descriptor_rel='artifacts/flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz'
    descriptor_md_rel=descriptor_rel.replace('.npz','.json')
    old_rel='artifacts/action_extension/BHSM_AE4_CURRENT_C2_HS_FRECHET_HESSIAN.json'
    previous=json.loads((root/old_rel).read_bytes())
    n=128
    source={}
    with np.load(root/descriptor_rel,allow_pickle=False) as archive:
        durations=archive['segment_proper_duration_proof_center'][:n].copy()
        for chirality in ('plus','minus'):
            key='product_Dirac_lambda1_5_chirality_'+chirality
            kd=archive[key+'__K_diagonal'][:n].copy();ko=archive[key+'__K_off_diagonal'][:n-1].copy()
            md=archive[key+'__M_diagonal'][:n].copy();mo=archive[key+'__M_off_diagonal'][:n-1].copy()
            W=archive[key+'__element_coefficient'][:n].copy()
            jet=reduced_product_dirac_hs_source_jet(proper_durations=durations,base_W=W,source_profile=np.ones(n))
            source[chirality]=dict(kd=kd,ko=ko,md=md,mo=mo,
                vd=jet['vertex_diagonal'],vo=jet['vertex_off_diagonal'],
                qd=jet['contact_diagonal'],qo=jet['contact_off_diagonal'],W=W,
                ell=previous['channels'][key]['spectral_length'])
    y=np.asarray(charged_lepton_yukawa_operator()['family_operator'],float)
    trY4=float(np.trace(y@y@y@y))

    def exact_weights():
        # Exact rational nine-point fourth derivative: moments 0..8.
        pts=list(range(-4,5));a=[[Fraction(k**j) for k in pts]+[Fraction(24 if j==4 else 0)] for j in range(9)]
        for i in range(9):
            pivot=next(k for k in range(i,9) if a[k][i]);a[i],a[pivot]=a[pivot],a[i]
            scale=a[i][i];a[i]=[v/scale for v in a[i]]
            for j in range(9):
                if j!=i:
                    scale=a[j][i];a[j]=[v-scale*w for v,w in zip(a[j],a[i])]
        return [row[-1] for row in a]
    fdweights=exact_weights()

    def calculate(data,dps,with_fd):
        with mp.workdps(dps):
            m=lambda x:mp.mpf(float(x))
            ell=m(data['ell']);ell2=ell*ell
            mass=[m(x) for x in data['md']]
            norm=[mp.sqrt(mass[i]*mass[i+1]) for i in range(n-1)]
            K=[ell2*m(x)/mass[i] for i,x in enumerate(data['kd'])]
            Ko=[ell2*m(x)/norm[i] for i,x in enumerate(data['ko'])]
            M=[mp.mpf(1)]*n;Mo=[m(x)/norm[i] for i,x in enumerate(data['mo'])]
            B=[ell*m(x)/mass[i] for i,x in enumerate(data['vd'])]
            Bo=[ell*m(x)/norm[i] for i,x in enumerate(data['vo'])]
            C=[m(x)/mass[i] for i,x in enumerate(data['qd'])]
            Co=[m(x)/norm[i] for i,x in enumerate(data['qo'])]
            def mv(d,o,x):
                return [d[i]*x[i]+(o[i-1]*x[i-1] if i else 0)+(o[i]*x[i+1] if i<n-1 else 0) for i in range(n)]
            def factors(d,o):
                piv=[d[1]];lower=[]
                for j in range(1,n-1):
                    lower.append(o[j]/piv[-1]);piv.append(d[j+1]-o[j]*lower[-1])
                return piv,lower
            def solve(factor,b):
                piv,lo=factor;yy=[b[0]]
                for j in range(1,n-1):yy.append(b[j]-lo[j-1]*yy[-1])
                xx=[yy[j]/piv[j] for j in range(n-1)]
                for j in range(n-3,-1,-1):xx[j]-=lo[j]*xx[j+1]
                return xx
            def pencil(u):
                return ([K[i]+u*B[i]+u*u*C[i]/2 for i in range(n)],
                        [Ko[i]+u*Bo[i]+u*u*Co[i]/2 for i in range(n-1)])
            def inertia(value,u=mp.mpf(0)):
                d,o=pencil(u);p=d[0]-value;negative=int(p<0)
                for i in range(1,n):
                    if p==0:p=-mp.power(10,-dps+10)
                    off=o[i-1]-value*Mo[i-1]
                    p=d[i]-value-off*off/p;negative+=int(p<0)
                return negative
            def mode(value,u):
                d,o=pencil(u);d=[d[i]-value for i in range(n)];o=[o[i]-value*Mo[i] for i in range(n-1)]
                fac=factors(d,o);x=[mp.mpf(1)]+solve(fac,[-o[0]]+[mp.mpf(0)]*(n-2))
                residual=d[0]+o[0]*x[1]
                mx=mv(M,Mo,x);slope=-mp.fdot(x,mx)
                return d,o,fac,x,mx,residual,slope
            def roots(u):
                d,o=pencil(u)
                af=assemble_tridiagonal(np.array([float(v) for v in d]),np.array([float(v) for v in o]))
                mf=assemble_tridiagonal(np.ones(n),np.array([float(v) for v in Mo]))
                starts=eigh(af,mf,eigvals_only=True,subset_by_value=(0.,100.),driver='gvx')
                if len(starts)!=5 or inertia(mp.mpf(100),u)!=5:
                    raise ArithmeticError('Actual outer trace low-mode count changed.')
                rr=[]
                for index,initial in enumerate(starts):
                    value=m(initial)
                    for it in range(14):
                        *_,residual,slope=mode(value,u)
                        update=residual/slope
                        value-=update
                        if abs(update)<mp.power(10,-dps+20):break
                    else:raise ArithmeticError('Multiprecision Weyl root failed to converge.')
                    eps=mp.power(10,-dps+30)
                    if inertia(value-eps,u)!=index or inertia(value+eps,u)!=index+1:
                        raise ArithmeticError('Weyl root failed the indexed Sturm check.')
                    rr.append(value)
                return rr
            base_roots=roots(mp.mpf(0))
            def eigen_coefficients(value,bb,bo,cc,co):
                d,o,fac,x0,mx0,*_=mode(value,mp.mpf(0))
                z=solve(fac,mx0[1:]);den=o[0]*z[0]-mx0[0]
                vectors=[x0];ec=[];equation_errors=[]
                for k in range(1,5):
                    rhs=[-v for v in mv(bb,bo,vectors[k-1])]
                    if k>=2:
                        part=mv(cc,co,vectors[k-2]);rhs=[a-b/2 for a,b in zip(rhs,part)]
                    for j in range(1,k):
                        part=mv(M,Mo,vectors[k-j]);rhs=[a+ec[j-1]*b for a,b in zip(rhs,part)]
                    yy=solve(fac,rhs[1:]);ek=(rhs[0]-o[0]*yy[0])/den
                    xx=[mp.mpf(0)]+[a+b*ek for a,b in zip(yy,z)]
                    lhs=mv(d,o,xx)
                    equation_errors.append(max(abs(a-b-ek*c) for a,b,c in zip(lhs,rhs,mx0)))
                    ec.append(ek);vectors.append(xx)
                return ec,max(equation_errors)
            zero=[mp.mpf(0)]*n;zeroo=[mp.mpf(0)]*(n-1)
            def contract(bb,bo,cc,co):
                components=[mp.mpf(0)]*4;maxres=mp.mpf(0);coeffs=[]
                for lam in base_roots:
                    e,err=eigen_coefficients(lam,bb,bo,cc,co);maxres=max(maxres,err);coeffs.append(e)
                    a,b,c,d=e;exp=mp.exp(-lam)
                    r=exp/lam;rp=-exp*(1/lam+1/lam**2)
                    rpp=exp*(1/lam+2/lam**2+2/lam**3)
                    rppp=-exp*(1/lam+3/lam**2+6/lam**3+6/lam**4)
                    terms=[r*a,2*r*b+rp*a*a,6*r*c+6*rp*a*b+rpp*a**3,
                        24*r*d+rp*(24*a*c+12*b*b)+12*rpp*a*a*b+rppp*a**4]
                    components=[old-v/2 for old,v in zip(components,terms)]
                return components,coeffs,maxres
            total,coeffs,maxres=contract(B,Bo,C,Co)
            v4,_,_=contract(B,Bo,zero,zeroo)
            q2,_,_=contract(zero,zeroo,C,Co)
            mixed=total[3]-v4[3]-q2[3]
            rowmax=lambda d,o:max(abs(d[i])+(abs(o[i-1]) if i else 0)+(abs(o[i]) if i<n-1 else 0) for i in range(n))
            masslower=1-rowmax([mp.mpf(0)]*n,Mo)
            bbound=rowmax(B,Bo)/masslower;cbound=rowmax(C,Co)/masslower
            rho=mp.mpf('.025');delta=rho*bbound+rho*rho*cbound/2
            cut=mp.mpf(100)
            if masslower<=0 or inertia(cut-2*delta)!=5 or inertia(cut+2*delta)!=5:
                raise ArithmeticError('Outer trace analytic-cluster separation failed.')
            tail_action=(n-5)*mp.exp(-(cut-delta))/(2*(cut-delta))
            tail_quartic=24*tail_action/rho**4
            intrinsic_h=6*(-1)*m(trY4)*sum(-mp.exp(-v)*(1/v+1/v**2) for v in base_roots)
            action0=sum(mp.e1(v) for v in base_roots)/2
            fd=[]
            if with_fd:
                cache={}
                for h in (mp.mpf(1)/160,mp.mpf(1)/320):
                    values=[]
                    for k in range(-4,5):
                        u=h*k;key=mp.nstr(u,30)
                        if key not in cache:cache[key]=sum(mp.e1(v) for v in roots(u))/2
                        values.append(cache[key])
                    weights=[mp.mpf(w.numerator)/w.denominator for w in fdweights]
                    result=mp.fdot(weights,values)/h**4
                    fd.append(dict(step=mp.nstr(h,20),literal_E1_fourth=mp.nstr(result,70),
                        absolute_error=mp.nstr(abs(result-total[3]),20),
                        relative_error=mp.nstr(abs((result-total[3])/total[3]),20),
                        omitted_outer_eigenline_action_bound=mp.nstr(tail_action,20)))
            fmt=lambda value:mp.nstr(value,70)
            return dict(dps=dps,held_ell=fmt(ell),
                base_low_eigenvalues_dimensionless=[fmt(v) for v in base_roots],
                dimensionless_E1_action=fmt(action0),
                reduced_HS_dimensionless_u_derivatives=[fmt(v) for v in total],
                reduced_HS_original_H_derivatives=[fmt(v*ell**(i+1)) for i,v in enumerate(total)],
                fourth_parts_dimensionless=dict(four_vertex=fmt(v4[3]),two_contact=fmt(q2[3]),mixed=fmt(mixed)),
                simple_eigenline_Taylor_coefficients=[[fmt(v) for v in e] for e in coeffs],
                bordered_equation_max_absolute_residual=fmt(maxres),
                outer_trace_tail_fourth_Cauchy_bound=fmt(tail_quartic),
                mass_Gershgorin_lower_bound=fmt(masslower),
                source_operator_norm_upper_bounds=[fmt(bbound),fmt(cbound)],
                separate_contact_only_intrinsic_probe=dict(
                    neutral_component_h_fourth_dimensionless=fmt(intrinsic_h),
                    neutral_component_h_fourth_original_units=fmt(intrinsic_h*ell**4),
                    canonical_real_phi_fourth_original_units=fmt(intrinsic_h*ell**4/4),
                    Tr_family_Y4=trY4,
                    operator_embedding='Conditional held zero-gauge anti-Hermitian equal-chiral kinetic operator and constant neutral h: V=0,Q=2M tensor Y_l^2. Separate from reduced commuting HS probe.',
                    physical_embedding_selected=False,physical_lambda_H=None,
                    finite_Higgs_wavefunction_Z=None),literal_E1_fd_checks=fd)

    results={};arrays=dict(proper_durations=durations,frozen_family_Y=y)
    for chirality,data in source.items():
        for k,v in data.items():arrays[chirality+'_'+k]=np.asarray(v)
        low=calculate(data,80,False)
        high=calculate(data,105,True)
        with mp.workdps(80):
            rel=abs((mp.mpf(low['reduced_HS_dimensionless_u_derivatives'][3])-mp.mpf(high['reduced_HS_dimensionless_u_derivatives'][3]))/mp.mpf(high['reduced_HS_dimensionless_u_derivatives'][3]))
            reference=mp.mpf(previous['channels']['product_Dirac_lambda1_5_chirality_'+chirality]['HS_curvature'])
            current=mp.mpf(high['reduced_HS_original_H_derivatives'][1])
            old_error=abs((reference-current)/current)
        results[chirality]=dict(precision80=low,precision105=high,
            fourth_relative_precision_change=mp.nstr(rel,20),
            previous_dense_binary64_HS_curvature_relative_discrepancy=mp.nstr(old_error,20))
        print(json.dumps(dict(chirality=chirality,quartic=high['reduced_HS_original_H_derivatives'][3],
            conditioned_quartic=high['reduced_HS_dimensionless_u_derivatives'][3],
            precision_change=mp.nstr(rel,12),FD=high['literal_E1_fd_checks']),sort_keys=True),flush=True)
    sources=[
        'src/bhsm/interface/ae3_c2_action_puzzle.py',
        'src/bhsm/interface/ae4_current_c2_hs_frechet_hessian.py',
        'scripts/materialize_ae4_current_c2_hs_frechet_hessian.py',
        'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
        'src/bhsm/interface/ae31_c2_lepton_composite_mixing_structure.py',
        'src/bhsm/interface/ae31_c2_full_scalar_derivative_pole.py',
        'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
    ]
    pins={p:sha256((root/p).read_bytes()).hexdigest() for p in [descriptor_rel,descriptor_md_rel,old_rel,*sources]}
    result=dict(classification='NEW_NONCOMMUTING_FOURTH_E1_VARIATION_ON_ACTUAL_CURRENT_C2_128_FORM_PREFIX',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_hashes=pins,
        channels=results,dimension=128,
        exact_fourth_formula='Gamma4=(w/2){3Tr(Dr[Q]Q)+6Tr(D2r[V,V]Q)+Tr(D3r[V,V,V]V)}, r(x)=exp(-ell^2*x)/x',
        method='Simple generalized eigenline Taylor recurrence through fourth order using multiprecision tridiagonal Weyl/bordered solves; every solve retains all128 form modes; outer E1 trace low-cluster truncation controlled separately.',
        parameter_scaling='u=held_ell*H, Gamma_H4=held_ell^4*Gamma_u4',
        supertrace_weight=-1,physical_channel_multiplicities_added=False,
        actual_reduced_source_kind='UNIT_COMMUTING_REDUCED_LR_HS_PROBE, fixed M and fixed domain, not dynamical intrinsic Higgs coordinate',
        background='Current-C2 descriptor proof centers; not an exact physical coupled history.',
        far_boundary='128-node Galerkin Dirichlet truncation, not physical outgoing endpoint',
        held_length_role='Original saved conditioned witness, not physical branch ell_star',
        tensor_or_contact_only_intrinsic_probe_is_full_physical_Higgs_coefficient=False,
        intrinsic_bare_potential_or_all_scalar_mixing_included=False,
        physical_Higgs_Z=None,physical_lambda_H=None,physical_nu_squared=None,
        relative_zeta_eta_log_completion_included=False,
        moving_mass_length_domain_jets_included=False,
        MP_and_analytic_tail_bounds_are_outward_interval_certificate=False,
        literal_FD_scope='Derivative of actual fixed128 E1 pencil; no physical Maxwell/outgoing/muon derivative gate.',
        completed_source_D5_profile_integrations_replayed=False,
        physical_muon_moment=None,coupled_matching_corrections_applied=0)
    out.mkdir(parents=True)
    _compressed_npz(out/'actual_128_K_M_V_Q_operands.npz',arrays)
    result['array_archive_sha256']=sha256((out/'actual_128_K_M_V_Q_operands.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();evaluate(a.repository,a.output)
