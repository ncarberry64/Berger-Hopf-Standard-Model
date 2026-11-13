"""Actual finite-core Y² heat value and cotangent with outward arithmetic.

The analytic divided differences have exact equal-pole limits.  A separate
semigroup perturbation bound connects the reference diagonal calculation
to the stored generalized FE pencil. Field/FE-entry production and
continuum errors remain separate. Frozen target/tail producers are reused
read-only.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from flint import arb, acb, acb_mat, ctx

from .muon_native_even_y_remainder_certificate import (
    ROOT, INPUT, PINNED, _acb_matrix, _adjoint, _frobenius_upper,
    _operator_norm_upper, _record, _upper_float, certify_generalized_even_pencil,
    even_y_tail_bounds,
)


def cutoff_divided_differences(poles, cutoff):
    """Exact-stored positive poles; Arb g,g[1],g[2], with Hermite limits."""
    lam = np.asarray(poles, float)
    if lam.ndim != 1 or not lam.size or not np.all(np.isfinite(lam)) or np.min(lam) <= 0:
        raise ValueError('finite positive retained poles required')
    if not np.isfinite(cutoff) or cutoff <= 0:
        raise ValueError('positive finite cutoff required')
    c = arb(float(cutoff))

    @lru_cache(None)
    def g_at(x):
        a = arb(x)
        return -(-c*a).exp()/a

    @lru_cache(None)
    def first_at(x, y):
        if x > y: return first_at(y, x)
        a = arb(x)
        if x == y:
            return (-c*a).exp()*(c/a+1/a**2)
        return (g_at(y)-g_at(x))/(arb(y)-a)

    @lru_cache(None)
    def second_at(x, y, z):
        if not x <= y <= z: return second_at(*sorted((x,y,z)))
        a = arb(x)
        if x == z:
            return -(-c*a).exp()*(c*c/a+2*c/a**2+2/a**3)/2
        return (first_at(y,z)-first_at(x,y))/(arb(z)-a)

    g = [g_at(float(x)) for x in lam]
    first = [[first_at(float(x),float(y)) for y in lam] for x in lam]
    return g, first, lambda i,j,k: second_at(float(lam[i]),float(lam[j]),float(lam[k]))


def _Hermitian_stored(value):
    a = _acb_matrix(np.asarray(value,complex))
    return (a+_adjoint(a))/2


def reference_coefficient_and_cotangent_matrices(poles, C_stored, B_stored, cutoff):
    """Outward reference G and the actual matrix cotangent coefficients."""
    lam = np.asarray(poles,float); n = len(lam)
    if np.shape(C_stored)!=(n,n) or np.shape(B_stored)!=(n,n):
        raise ValueError('Taylor matrices must share the retained pole dimension')
    if not np.all(np.isfinite(C_stored)) or not np.all(np.isfinite(B_stored)):
        raise ValueError('finite stored Taylor matrices required')
    C = _Hermitian_stored(C_stored); B = _Hermitian_stored(B_stored)
    g, first, second = cutoff_divided_differences(lam,cutoff)
    D = acb_mat(n,n); Z = acb_mat(n,n); G = acb(0)
    for i in range(n):
        G += g[i]*B[i,i]
        for j in range(n):
            D[i,j] = first[i][j]*C[i,j]
            G += first[i][j]*C[i,j]*C[j,i]/2
            z = first[i][j]*B[i,j]
            for k in range(n):
                if not C[i,k].is_zero() and not C[k,j].is_zero():
                    z += second(i,k,j)*C[i,k]*C[k,j]
            Z[i,j] = z
    # Exact Hermitian expressions may have interval radii, never discarded.
    Z = (Z+_adjoint(Z))/2; D = (D+_adjoint(D))/2
    Lambda = acb_mat(np.diag(lam).tolist()); gg=acb_mat(n,n)
    for i in range(n): gg[i,i]=g[i]
    counter = (Lambda*Z+Z*Lambda+B*gg+gg*B+C*D+D*C)/2
    return dict(coefficient=G.real, imaginary_coefficient=G.imag,
        g_diagonal=gg, D=D, Z=Z, Gram_counter=counter, C=C, B=B)


def _load_retained(root):
    base=Path(root)/INPUT
    for name,digest in PINNED.items():
        if sha256((base/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('pinned target input changed: '+name)
    receipt=json.loads((base/'paired_target_coefficients.json').read_text())
    for row in receipt['source_records']+receipt['consumed_input_records']:
        raw=(Path(root)/row['path']).read_bytes()
        if len(raw)!=row['bytes'] or sha256(raw).hexdigest()!=row['sha256']:
            raise ValueError('retained source identity changed: '+row['path'])
    # The primitive application uses these concrete background/field owners.
    # Bind their earlier receipt hashes rather than silently taking changed
    # reconstruction functions while keeping the old coefficient archive.
    response=json.loads((Path(root)/'artifacts/muon_parent_maxwell_corrected_retarded_20261010/run_3/result.json').read_text())
    for name,digest in response['input_hashes'].items():
        if sha256((Path(root)/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('retained primitive/background owner changed: '+name)
    with np.load(base/'paired_target_coefficients.npz',allow_pickle=False) as archive:
        arrays={k:archive[k] for k in archive.files}
    for name,row in receipt['array_records'].items():
        a=np.ascontiguousarray(arrays[name])
        if list(a.shape)!=row['shape'] or str(a.dtype)!=row['dtype'] or sha256(a.tobytes()).hexdigest()!=row['raw_sha256']:
            raise ValueError('retained array identity changed: '+name)
    return receipt,arrays


def _retained_primitive_samples(root, a):
    """Reconstruct the same reached primitive jets, with saved reference V."""
    from .muon_native_coupled_source_heat import retained_corrected_scalar_photon_response
    from .muon_native_product_factor_graph import (
        _source_core_samples, finite_common_family_intrinsic_operator,
        lepton_unit_trace_gauge_representation,
    )
    from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from .muon_parent_gauge_geometry_correction import finite_common_iterate_at_time
    from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from .muon_parent_retarded_hypercharge import WALL,regular_radial_basis
    from .muon_parent_maxwell_full_weak import FIELD_ORDER,M
    from .muon_native_mean_core_heat_target import _unit_lepton_mass6,_stored_frobenius_upper
    response=retained_corrected_scalar_photon_response(root);rep=response['representation']
    nodes=np.linspace(-.001,0,17)
    samples=_source_core_samples(response['coefficients'],rep,response['reference'],nodes,np.ones((17,8)),4)
    fiber=np.array([0,1,6,7,12,13]);frame=lepton_current_hilbert_representation()
    alpha=frame['alpha'][:,fiber][:,:,fiber]
    gen=lepton_unit_trace_gauge_representation()['generators'][:,fiber][:,:,fiber]
    mechanical=sum(-1j*alpha[j]@gen[k]*M[j,k] for j in range(3) for k in range(4))
    radial,_=regular_radial_basis(np.array([WALL]),rep['radial_order']);ov=np.zeros((60,4,6,6),complex)
    for j,label in enumerate(rep['gauge_labels']):
        field=FIELD_ORDER.index(label['field']);value=radial[0,label['radial']]*gen[label['internal']]
        if field==0:ov[j,0]=value
        elif field>=2:ov[j,field-1]=value
    mass_basis=np.array([_unit_lepton_mass6(H) for H in ([1,0],[0,1],[1j,0],[0,1j])])
    ev=np.zeros((102,90),complex);ev[6:-6]=a['computed_generalized_eigenvectors']
    result=[];C=np.zeros((90,90),complex);B=C.copy()
    for s in samples:
        i,x,h=s['cell'],s['x'],s['h'];t=nodes[i]+x*h
        data=finite_common_iterate_at_time(t,response['coefficients'],rep,response['reference'],rho=np.array([WALL]))
        geo=intrinsic_m4_weight_jet(12,data['q'],data['qdot'],data['m'],source_value=data['normal'],source_rate=data['normal_rate'])
        H=finite_common_family_intrinsic_operator(t,response['coefficients'],rep,response['reference'])['H']
        W=s['W'].copy();W[:12,12:]=0;W[12:,:12]=0;W=W[np.ix_(fiber,fiber)]
        omega=s['Omega_t'][np.ix_(fiber,fiber)];N,R=s['N'],s['R']
        u=(1-x)*ev[6*i:6*(i+1)]+x*ev[6*(i+1):6*(i+2)]
        du=(ev[6*(i+1):6*(i+2)]-ev[6*i:6*(i+1)])/h
        temporal=du+omega@u;Au=temporal/N+W@u;Mu=_unit_lepton_mass6(H)@u
        dN=geo['induced_lapse'].gradient;dR=geo['R4'].gradient;dl=geo['mechanical_connection_lambda'].gradient
        da=np.zeros((228,6,90),complex);dm=da.copy()
        da[:100]=-dN[:,None,None]*temporal[None]/N**2-dR[:,None,None]*(W@u)[None]/R+dl[:,None,None]*((mechanical/R)@u)[None]
        da[100:160]=np.einsum('jkl,li->jki',ov[:,0],u)/N
        for j in range(3):da[100:160]+=np.einsum('jkl,li->jki',-1j*np.einsum('kl,jlm->jkm',alpha[j],ov[:,j+1])/R,u)
        dm[220:224]=np.einsum('bkl,li->bki',mass_basis,u)
        measure=np.zeros(228);measure[:100]=dN/N
        row=len(result)
        for key,value in (('u_Frobenius_upper',u),('Au_Frobenius_upper',Au),('Mu_Frobenius_upper',Mu)):
            if _stored_frobenius_upper(value)!=a[key][row]:
                raise ValueError('stored primitive reconstruction norm identity failed: '+key)
        for key,value in (('deltaA_Frobenius_upper',da),('deltaMu_Frobenius_upper',dm)):
            if not np.array_equal(_stored_frobenius_upper(value,axis=(1,2)),a[key][row]):
                raise ValueError('stored derivative reconstruction norm identity failed: '+key)
        measure_upper=np.zeros(228);measure_upper[:100]=np.nextafter(abs(dN/N)/(1-np.finfo(float).eps),np.inf)
        if not np.array_equal(measure_upper,a['abs_deltaN_over_N'][row]) or s['weight']!=a['sample_weight'][row]:
            raise ValueError('stored primitive measure identity failed')
        C+=s['weight']*(Au.conj().T@Mu+Mu.conj().T@Au);B+=s['weight']*(Mu.conj().T@Mu)
        result.append(dict(u=u,Au=Au,Mu=Mu,deltaA=da,deltaMu=dm,measure=measure,weight=s['weight'],time=t))
    if not np.array_equal(np.array([v['time'] for v in result]),a['coefficient_time_samples']):
        raise ValueError('reconstructed primitive sample times disagree with retained target')
    if not np.array_equal(C,a['normalized_P1']) or not np.array_equal(B,a['normalized_P2']):
        raise ValueError('stored Taylor coefficient reconstruction was not bit-identical')
    return result


def _inner_real(a,b):
    return sum((a[i,j].conjugate()*b[i,j] for i in range(a.nrows()) for j in range(a.ncols())),acb(0)).real


def _endpoint_float(x,upper):
    point=x.upper() if upper else x.lower()
    return float(np.nextafter(float(point),np.inf if upper else -np.inf)) if not x.is_zero() else 0.


def _reference_directional_target(sample,readout):
    Au=_acb_matrix(sample['Au']);Mu=_acb_matrix(sample['Mu']);u=_acb_matrix(sample['u'])
    Ar=Au*readout['Z']+Mu*readout['D'];Mr=Mu*readout['g_diagonal']+Au*readout['D']
    measure=_inner_real(Au,Ar)+_inner_real(Mu,Mr)-_inner_real(u,u*readout['Gram_counter'])
    result=[]
    for da,dm,ratio in zip(sample['deltaA'],sample['deltaMu'],sample['measure']):
        if np.count_nonzero(da)==0 and np.count_nonzero(dm)==0 and ratio==0:
            result.append(arb(0));continue
        value=2*_inner_real(Ar,_acb_matrix(da))+2*_inner_real(Mr,_acb_matrix(dm))+arb(float(ratio))*measure
        result.append(arb(float(sample['weight']))*value)
    return result


def _mismatch_bounds(a,receipt,constants,readout,radius):
    V=_acb_matrix(a['computed_generalized_eigenvectors']);n=len(a['normalized_P0_eigenvalues'])
    G=_adjoint(V)*_acb_matrix(a['actual_FE_Gram'])*V
    eps=_frobenius_upper(G-acb_mat(np.eye(n).tolist()));r=arb(radius)
    defects=[]
    for K,proxy in zip((a['actual_FE_K0'],a['actual_FE_K1'],a['actual_FE_K2']),
        (acb_mat(np.diag(a['normalized_P0_eigenvalues']).tolist()),readout['C'],readout['B'])):
        defects.append(_frobenius_upper(_adjoint(V)*_acb_matrix(K)*V-proxy))
    cn,_=_operator_norm_upper(readout['C'],(a['normalized_P1']+a['normalized_P1'].conj().T)/2)
    bn,_=_operator_norm_upper(readout['B'],(a['normalized_P2']+a['normalized_P2'].conj().T)/2)
    norm=arb(float(np.max(a['normalized_P0_eigenvalues'])))+r*cn+r*r*bn
    E=(defects[0]+r*defects[1]+r*r*defects[2]+eps*norm)/(1-eps)
    half=constants['gap_lower']/2;c=arb(float(receipt['parameter']))
    if not arb(float(np.min(a['normalized_P0_eigenvalues'])))-r*cn-r*r*bn >= half:
        raise ValueError('reference polynomial does not share the certified half-gap circle')
    q0=(-c*half).exp()/half;q1=(-c*half).exp()*(c/half+1/half**2)
    delta=arb(receipt['fixed_Y_middle'])**2-arb(receipt['fixed_Y_light'])**2
    value=n*q0*E/(r*r)*delta
    derivative=np.zeros_like(a['deltaA_Frobenius_upper'])
    for i in range(len(derivative)):
        un,an,mn,w=(arb(float(a[name][i])) for name in ('u_Frobenius_upper','Au_Frobenius_upper','Mu_Frobenius_upper','sample_weight'))
        for j in range(derivative.shape[1]):
            da,dm,measure=(arb(float(a[name][i,j])) for name in ('deltaA_Frobenius_upper','deltaMu_Frobenius_upper','abs_deltaN_over_N'))
            dK=w*(2*an*da+2*r*(mn*da+an*dm)+2*r*r*mn*dm+measure*(an+r*mn)**2)
            dG=w*measure*un**2;prox=dK+dG*norm
            difference=eps/(1-eps)*(dK+dG*(norm+E))+dG*E
            derivative[i,j]=_upper_float(n*(q0*difference+q1*E*prox)/(r*r)*delta)
    return value,derivative,dict(reference_Gram_defect=_record(eps),
        stiffness_Taylor_coefficient_defects=[_record(v) for v in defects],
        circle_operator_difference_upper=_record(E),reference_circle_norm_upper=_record(norm),
        paired_Y2_value_FE_reference_difference_upper=_record(value),
        derivative_difference_includes_Gram_normalization=True,
        bound_method='Duhamel/semigroup difference on the shared half-gap circle, then Cauchy Y2 coefficient bound')


def retained_target_certificate(*,repository=ROOT,precision_bits=192):
    """Evaluate the actual reached raw228 target without numerical g quadrature."""
    if type(precision_bits) is not int or precision_bits<128:
        raise ValueError('at least128 explicit bits required for target divided differences')
    receipt,a=_load_retained(repository);old=ctx.prec
    try:
        ctx.prec=precision_bits
        constants,pencil=certify_generalized_even_pencil(a['actual_FE_K0'],a['actual_FE_K1'],a['actual_FE_K2'],a['actual_FE_Gram'],
            a['computed_generalized_eigenvectors'],a['normalized_P0_eigenvalues'],a['actual_FE_LR_sign_grading'],precision_bits=precision_bits)
        tail=even_y_tail_bounds(constants,receipt['parameter'],receipt['fixed_Y_middle'],receipt['fixed_Y_light'],precision_bits=precision_bits)
        readout=reference_coefficient_and_cotangent_matrices(a['normalized_P0_eigenvalues'],a['normalized_P1'],a['normalized_P2'],receipt['parameter'])
        diff=arb(receipt['fixed_Y_middle'])**2-arb(receipt['fixed_Y_light'])**2
        value=diff*readout['coefficient']
        value_error,target_error,mismatch=_mismatch_bounds(a,receipt,constants,readout,tail['circle_radius_exact_binary64'])
        samples=_retained_primitive_samples(repository,a);lower=np.zeros((64,228));upper=lower.copy()
        reference_radius=0.
        for i,s in enumerate(samples):
            row=_reference_directional_target(s,readout)
            for j,v in enumerate(row):
                y=diff*v
                lower[i,j]=_endpoint_float(y,False);upper[i,j]=_endpoint_float(y,True)
                reference_radius=max(reference_radius,_upper_float((y-y.mid()).abs_upper()))
        arrays=dict(reference_paired_Y2_target_lower=lower,reference_paired_Y2_target_upper=upper,
            actual_FE_Y2_target_reference_difference_upper=target_error,
            coefficient_time_samples=a['coefficient_time_samples'],response_time_samples=a['response_time_samples'])
        packet=dict(classification='OUTWARD_FINITE_FE_PAIRED_Y2_HEAT_VALUE_AND_REACHED_RAW228_COTANGENT',
            consumed_target_path=INPUT,consumed_target_hashes=PINNED,precision_bits=precision_bits,
            pencil_certificate=pencil,FE_reference_mismatch=mismatch,
            reference_Y2_coefficient_arb=str(readout['coefficient']),
            reference_paired_Y2_value_arb=str(value),
            actual_FE_paired_Y2_value_lower=_endpoint_float(value-value_error,False),
            actual_FE_paired_Y2_value_upper=_endpoint_float(value+value_error,True),
            actual_FE_paired_value_through_higher_even_tail_lower=_endpoint_float(value-value_error-arb(tail['value_tail_upper']['arb']),False),
            actual_FE_paired_value_through_higher_even_tail_upper=_endpoint_float(value+value_error+arb(tail['value_tail_upper']['arb']),True),
            analytic_removable_pole_limits=True,numerical_divided_difference_quadrature_used=False,
            primitive_norm_measure_and_Taylor_coefficient_reconstruction_bit_identical=True,
            reference_directional_Arb_radius_upper=reference_radius,
            raw228_order='geometry100,gauge_value60,gauge_rate60,Hreal4,Hrate4',
            derivative_Gram_measure_count=1,derivative_same_LR_grading_required=True,
            derivative_scope='finite jet defined by reconstructed stored primitives; base exact stored FE pencil; field/jet production rounding excluded',
            coefficient_scope=receipt['coefficient_scope'],
            omitted_error_sources=['production of field/FE/geometry derivative entries','continuum/quadrature convergence','descriptor phase error unless separately paired'],
            complete_native_or_Pauli_evaluated=False,physical_background_or_cutoff_selected=False)
        return packet,arrays
    finally:ctx.prec=old
