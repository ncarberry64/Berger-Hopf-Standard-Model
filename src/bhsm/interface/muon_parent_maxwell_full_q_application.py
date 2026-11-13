"""Apply the full Maxwell Hessian to the retained eight angular photon lifts.

The actual E1+ metric/connection two-jets are used.  Only the geometry-
independent angular coefficients are read from the older source receipt.
The 400-coordinate odd angular space closes the reference linearization;
neither the eight-source compression nor a nonlinear truncation is assumed
closed.  These are Lorentz weak-action applications, not heat or Pauli values.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import numpy as np
from numpy.polynomial.legendre import leggauss

from .muon_birth_candidate_geometry_action import ROOT, RESET_RECEIPT, STATE_SOURCE
from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_matched_mechanical_source import epsilon
from .muon_moving_geometric_action import retained_state
from .muon_parent_maxwell_full_weak import FIELD_ORDER, M
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_retarded_hypercharge import WALL

SOURCE = 'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz'
SOURCE_SHA256 = '146435df28178967c321c0aa7e89a1511395d196f96b8715532aa98e3e312c2b'
FACTOR_NAMES = ('k',) + tuple(f'{name}_h{p}' for name in ('e','neg_e_beta','e_beta2_minus_r','neg_d') for p in range(3)) + ('electric_contact','radial_contact','magnetic_contact')
DERIVATIVE_ORDER = ('value','coordinate_time_derivative','reference_radial_derivative')


def retained_full_q_angular_space(repository=ROOT):
    """Reconstruct the saved complete n1+n3 source in the owned real frame."""
    repository = Path(repository)
    path = repository/SOURCE
    if sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError('retained full-Q angular source hash disagrees with the audited source')
    scalar = scalar_s3_discretization(3)
    odd = np.array([i for i,l in enumerate(scalar['real_basis_labels']) if l[0] in (1,3)])
    coefficients = np.zeros((8,5,4,scalar['scalar_count']), complex)
    with np.load(path, allow_pickle=False) as packet:
        for n in (1,3):
            ids = [i for i,l in enumerate(scalar['scalar_labels']) if l[0] == n]
            value = packet[f'transformed_n{n}']
            if value.shape != (8,3,4,n+1,n+1) or not np.isfinite(value).all():
                raise ValueError('complete retained eight real full-Q angular lifts required')
            coefficients[:,2:,:,ids] = value.reshape(8,3,4,-1)
        saved_gram = packet['transported_source_Gram'].copy()
    real = np.einsum('ji,Afcj->Afci', scalar['real_basis_coefficient_transform'].conj(), coefficients)
    if np.max(abs(real.imag)) > 1e-12 or np.max(abs(real[:,:,:,[i for i in range(30) if i not in odd]])) > 1e-12:
        raise ValueError('source violates the owned real n1+n3 representation')
    Q = real[:,:,:,odd].real.reshape(8,400).T
    gram = Q.T@Q
    # The old receipt exports Gram/Tr16Q^2, whereas transformed_n1/n3
    # contain raw primitive Q components.  Preserve both conventions.
    if np.max(abs((3/16)*gram-saved_gram)) > 2e-12 or np.max(abs(gram-(16/3)*np.eye(8))) > 2e-12:
        raise ValueError('retained primitive source Gram does not equal Tr16(Q^2)=16/3')
    E = scalar['real_angular_derivative_matrices'][:,odd][:,:,odd]
    return dict(source_coefficients=Q, source_gram=gram,
        derivative_matrices=E, harmonic_labels=[scalar['real_basis_labels'][i] for i in odd],
        saved_normalized_source_gram=saved_gram.real,
        basis_values=scalar['real_basis_values'][:,odd],
        basis_derivative_values=scalar['real_basis_derivative_values'][:,:,odd],
        Haar_weights=scalar['haar_weights'], source_sha256=SOURCE_SHA256,
        angular_coordinate_count=400, scalar_harmonic_count=20,
        field_order=FIELD_ORDER, coefficient_axes=('one_form','unit_Tr16_internal','real_scalar_harmonic'),
        source_coordinate='retained primitive beta photon angular directions; no old T_b or geometry imported',
        nonlinear_truncation_invariant=False, physical_source_profile_selected=False)


def full_q_reference_operators(angular):
    """Literal right-coframe derivative and curvature maps on all400 columns."""
    E = np.asarray(angular['derivative_matrices'], float)
    if E.shape != (3,20,20) or not np.isfinite(E).all() or np.max(abs(E+E.transpose(0,2,1))) > 2e-12:
        raise ValueError('owned real antisymmetric right-coframe derivative maps required')
    eps = epsilon()
    ad = np.zeros((3,4,4)); ad[:,:3,:3] = 2*eps.transpose(0,2,1)
    G0 = np.vstack([np.kron(np.eye(4), x) for x in E])
    G1 = np.vstack([np.kron(x, np.eye(20)) for x in ad])
    S = np.zeros((240,400)); S[:,160:] = np.eye(240)
    At = np.zeros((80,400)); At[:,:80] = np.eye(80)
    Ar = np.zeros((80,400)); Ar[:,80:160] = np.eye(80)
    C0 = 2*np.eye(240); C1 = np.zeros((240,240)); B = np.zeros_like(C1)
    for i,j,k in np.argwhere(eps):
        C0[i*80:(i+1)*80,k*80:(k+1)*80] += eps[i,j,k]*G0[j*80:(j+1)*80]
        C1[i*80:(i+1)*80,k*80:(k+1)*80] += eps[i,j,k]*G1[j*80:(j+1)*80]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for b in range(3):
                    for c in range(3):
                        B[j*80+b*20:j*80+(b+1)*20,k*80+c*20:k*80+(c+1)*20] += eps[i,j,k]*eps[i,b,c]*np.eye(20)
    Ct = np.zeros((400,400)); Cr = np.zeros_like(Ct)
    for i in range(3):
        for a in range(3):
            for b in range(3):
                block = 2*eps[i,a,b]*np.eye(20)
                Ct[a*20:(a+1)*20,(2+i)*80+b*20:(2+i)*80+(b+1)*20] += block
                Cr[80+a*20:80+(a+1)*20,(2+i)*80+b*20:(2+i)*80+(b+1)*20] += block
    Ct += Ct.T; Cr += Cr.T
    return dict(G0=G0,G1=G1,spatial_selector=S,temporal_selector=At,radial_selector=Ar,
        curl0=C0,curl1=C1,magnetic_contact=S.T@B@S,
        temporal_curvature_contact=Ct,radial_curvature_contact=Cr)


def hessian_response_polynomials(operators, directions):
    """Exact finite operator application, factored by actual geometric scalars.

    Returns P[factor,left_jet,right_jet,full400,input_direction].  Its sum
    with the geometry factors is the complete Hessian action, including
    At/Ar and nonlinear curvature contacts.  No inverse/compression occurs.
    """
    Q = np.asarray(directions)
    if not np.isrealobj(Q) or Q.ndim != 2 or Q.shape[0] != 400 or not np.isfinite(Q).all():
        raise ValueError('finite real full400 direction columns required')
    S,At,Ar = (operators[k] for k in ('spatial_selector','temporal_selector','radial_selector'))
    X = {(1,0):Ar,(2,0):-At}
    Ft = {(0,0):-operators['G0']@At,(0,1):-operators['G1']@At,(1,0):S}
    Fr = {(0,0):-operators['G0']@Ar,(0,1):-operators['G1']@Ar,(2,0):S}
    B = {(0,0):operators['curl0']@S,(0,1):operators['curl1']@S}
    out = np.zeros((len(FACTOR_NAMES),3,3,400,Q.shape[1]))
    def add(left,right,name):
        for (i,p),L in left.items():
            for (j,q),R in right.items():
                key = name if name == 'k' else name+'_h'+str(p+q)
                out[FACTOR_NAMES.index(key),i,j] += L.T@(R@Q)
    add(X,X,'k'); add(Ft,Ft,'e'); add(Ft,Fr,'neg_e_beta'); add(Fr,Ft,'neg_e_beta')
    add(Fr,Fr,'e_beta2_minus_r'); add(B,B,'neg_d')
    for factor,key in (('electric_contact','temporal_curvature_contact'),
                       ('radial_contact','radial_curvature_contact'),
                       ('magnetic_contact','magnetic_contact')):
        out[FACTOR_NAMES.index(factor),0,0] += operators[key]@Q
    return out


def geometric_response_factors(row):
    """Same-coordinate100 two-jets; induced lambda motion counted once."""
    e,r,d,k,beta,lam,lt,lr = (row[n] for n in ('electric','radial','angular','electric_radial','shift','connection_lambda','lambda_tau','lambda_rho'))
    h=lam-1; normal=lt-beta*lr
    result = [k]
    for f in (e,-e*beta,e*beta*beta-r,-d):
        result.extend((f,f*h,f*h*h))
    result.extend((e*normal,-(e*beta*normal+r*lr),-4*d*lam*h))
    return result


def apply_full_q_hessian(row, polynomials):
    factors = geometric_response_factors(row)
    return np.einsum('f,fijca->ijca', np.array([x.value for x in factors]), polynomials)


def full_q_offshell_ward(angular,operators,row,*,eta_time_rate=1.,eta_radial_rate=-.7):
    """All8 sources against80 gauge parameters, retaining the Euler contact.

    Gauge parameters use the same odd harmonics.  Their first/second jets
    are a mathematical Ward test, not a physical field or driving profile.
    The contact product has even harmonics; its exact constant component
    couples to the nonstationary mechanical reference Euler row.
    """
    alpha,b = float(eta_time_rate),float(eta_radial_rate)
    if not np.isfinite([alpha,b]).all():
        raise ValueError('finite Ward parameter jets required')
    lam,lt,lr,beta,e,r,d = (row[n].value for n in ('connection_lambda','lambda_tau','lambda_rho','shift','electric','radial','angular'))
    D=operators['G0']+(lam-1)*operators['G1']
    gauge=np.zeros((3,400,80))
    gauge[0,:80]=alpha*np.eye(80); gauge[0,80:160]=b*np.eye(80); gauge[0,160:]=D
    gauge[1,:80]=alpha*alpha*np.eye(80); gauge[1,80:160]=alpha*b*np.eye(80)
    gauge[1,160:]=alpha*D+lt*operators['G1']
    gauge[2,:80]=alpha*b*np.eye(80); gauge[2,80:160]=b*b*np.eye(80)
    gauge[2,160:]=b*D+lr*operators['G1']
    Q=angular['source_coefficients']
    applied=apply_full_q_hessian(row,hessian_response_polynomials(operators,Q))[:,0]
    hessian=np.einsum('ica,icb->ab',applied,gauge)
    eps=epsilon(); qi=Q[160:].T.reshape(8,3,4,20)
    mean=np.zeros((8,80,3,4))
    for c in range(3):
        for x in range(3):
            for y in range(3):
                mean[:,y*20:(y+1)*20,:,c] += eps[x,y,c]*qi[:,:,x,:].transpose(0,2,1)/np.sqrt(2)
    curlmean=2*mean.copy()
    for i,j,k in np.argwhere(eps):
        curlmean[:,:,i,:3] += eps[i,j,k]*(lam-1)*np.cross(M[j,:3],mean[:,:,k,:3])/np.sqrt(2)
    n=lt-beta*lr
    contact=(e*n*(alpha-beta*b)-r*lr*b)*np.einsum('ic,abic->ab',M,mean)
    contact-=d*np.einsum('ic,abic->ab',2*lam*(lam-1)*M,curlmean)
    residual=hessian+contact
    return dict(hessian=hessian,Euler_contact=contact,residual=residual,
        maximum_residual=float(np.max(abs(residual))),
        identity='S_double_prime[Q,D_A eta]+S_prime[[Q,eta]]=0',
        gauge_parameter_count=80,source_count=8,Gauss_columns_included=True,
        reference_stationarity_assumed=False,even_contact_harmonics_retained=True,
        parameter_scope='CONTROL_ONLY gauge Ward tangent jets; no source or primal chosen')


def retained_full_q_application(repository=ROOT,*,points=96):
    """Evaluate the uncompressed angular Hessian source image at actualE1+."""
    repository=Path(repository)
    angular=retained_full_q_angular_space(repository); operators=full_q_reference_operators(angular)
    Q=angular['source_coefficients']; polynomials=hessian_response_polynomials(operators,Q)
    x,w=leggauss(points); rho=(x+1)*WALL/2; w=w*WALL/2
    q,v,m=retained_state(repository)
    c=geometric_connection_coefficient_jets(12,q,v,m,rho,clock='coordinate_time')
    factors=[geometric_response_factors(row) for row in c['rows']]
    values=np.array([[z.value for z in row] for row in factors])
    application=np.einsum('rf,fijca->rijca',values,polynomials)
    corners=np.einsum('ca,rijcb->rijab',Q,application)
    projected=np.einsum('ca,rijab->rijcb',Q,corners)*(3/16)
    remainder=application-projected
    gauss=application[:,:,:,:160]
    # The coefficients and their100 two-jets keep the full angular mixed
    # application factored; no lossy8-source reduction is substituted.
    ward=[full_q_offshell_ward(angular,operators,c['rows'][i]) for i in (0,points//2,points-1)]
    levels=np.array([x[0] for x in angular['harmonic_labels']])
    # Closure follows from constant internal matrices and E_i preservingn.
    derivative_cross=max(float(np.max(abs(D[np.ix_(levels==1,levels==3)]))) for D in angular['derivative_matrices'])
    return dict(angular=angular,operators=operators,polynomials=polynomials,
        rho=rho,quadrature=w,coefficient_jets=c,factor_jets=factors,
        actual_geometry=dict(q=q,velocity=v,lapse_shift=m),
        application=application,source_corners=corners,uncompressed_remainder=remainder,
        Gauss_source_image=gauss,ward=ward,
        eight_source_closure_absolute=float(np.max(np.linalg.norm(remainder,axis=3))),
        full400_cross_shell_derivative_max=derivative_cross,
        computational_radial_integral=np.einsum('r,rijab->ijab',w,corners),
        physical_radial_source_profile=None,physical_retarded_solution=None,
        physical_current_Pauli_form=None,stationary_E1_claim=False)


def materialize(output,repository=ROOT):
    """Two independent calls are required for the publication replay pair."""
    output=Path(output); repository=Path(repository)
    if output.exists():
        raise FileExistsError('preserve prior evidence; use a new output directory')
    result=retained_full_q_application(repository); angular=result['angular']
    arrays={name:result[name] for name in ('rho','quadrature','polynomials','application','source_corners','Gauss_source_image','computational_radial_integral')}
    arrays.update(result['actual_geometry'])
    arrays.update(source_coefficients=angular['source_coefficients'],source_gram=angular['source_gram'],
        angular_derivative_matrices=angular['derivative_matrices'])
    arrays['factor_values']=np.array([[x.value for x in row] for row in result['factor_jets']])
    arrays['factor_geometric_jacobian']=np.array([[x.gradient for x in row] for row in result['factor_jets']])
    arrays['factor_normal_hessian_columns']=np.array([[x.hessian[:,-2:] for x in row] for row in result['factor_jets']])
    arrays['ward_hessian']=np.array([x['hessian'] for x in result['ward']])
    arrays['ward_Euler_contact']=np.array([x['Euler_contact'] for x in result['ward']])
    arrays['ward_residual']=np.array([x['residual'] for x in result['ward']])
    output.mkdir(parents=True)
    with ZipFile(output/'application.npz','w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name,value in sorted(arrays.items()):
            stream=BytesIO(); np.lib.format.write_array(stream,np.asarray(value),allow_pickle=False)
            member=ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0)); member.external_attr=0o600<<16; member.compress_type=ZIP_DEFLATED
            archive.writestr(member,stream.getvalue(),compresslevel=9)
    refs=[SOURCE,STATE_SOURCE,RESET_RECEIPT,
        'src/bhsm/interface/muon_parent_maxwell_full_q_application.py',
        'src/bhsm/interface/muon_parent_maxwell_full_weak.py',
        'src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',
        'src/bhsm/interface/muon_intrinsic_scalar_discretization.py',
        'src/bhsm/interface/muon_matched_mechanical_source.py']
    receipt=dict(scope='EVALUATED_ACTUAL_E1_PLUS_FULL_FIVE_COMPONENT_MAXWELL_HESSIAN_ON_RETAINED_FULL_Q_ANGULAR_SOURCES',
        input_hashes={p:sha256((repository/p).read_bytes()).hexdigest() for p in refs},
        numerical_application_sha256=sha256((output/'application.npz').read_bytes()).hexdigest(),
        field_order=FIELD_ORDER,derivative_order=DERIVATIVE_ORDER,factor_names=FACTOR_NAMES,
        coefficient_axes=angular['coefficient_axes'],harmonic_labels=angular['harmonic_labels'],
        scalar_harmonic_count=20,full_real_angular_coordinate_count=400,
        source_count=8,source_Gram=angular['source_gram'].tolist(),
        primitive_source_normalization='raw unit-Tr16 Q directions; Gram16/3 retained, not divided into geometry weights',
        source_coordinate=angular['source_coordinate'],geometry_coordinate_count=100,
        reference='actual retained E1+ outgoing_C2 mechanical A_i=sqrt8 H_i(lambda-1), At=Ar=0; induced first jets retained',
        imported_old_geometric_profile_arrays=False,imported_old_T_b=False,
        radial_quadrature_count=96,angular_rule='current unit-Haar real Wigner n<=3 rule, exact through degree12; only oddn1+n3 coefficients consumed',
        full400_reference_linearization_closure=True,
        closure_proof='E_i preservesn; internalconstant AdMi, coframeepsilon and all curvature contacts preserve each scalar harmonic shell. All5 oneforms and4 internals retained.',
        cross_shell_derivative_max=result['full400_cross_shell_derivative_max'],
        eight_source_span_invariant=bool(result['eight_source_closure_absolute']<1e-10),
        eight_source_closure_absolute=result['eight_source_closure_absolute'],
        eight_source_compression_used_for_solve=False,
        full400_source_image_norm=float(np.linalg.norm(result['application'])),
        Gauss_source_image_norm=float(np.linalg.norm(result['Gauss_source_image'])),
        offshell_Ward_maximum_residual=max(x['maximum_residual'] for x in result['ward']),
        offshell_Ward_Euler_contact_maximum=float(max(np.max(abs(x['Euler_contact'])) for x in result['ward'])),
        offshell_Ward_identity=result['ward'][0]['identity'],offshell_Ward_includes_At_Ar_and_even_Euler_contact=True,
        Gauss_columns_eliminated=False,curvature_contacts_retained=True,
        source_image_factorization='application[r,i,j,c,A]=sum_f factor_values[r,f]*polynomials[f,i,j,c,A]; geometry100 first/normal secondjets use same factors',
        computational_radial_integral_scope='constant-profile radial pairing diagnostic; not selected source extension or physical trace',
        nonlinear_truncation_invariant=False,nonlinear_product_completion='not inferred: n1+n3 products can populateevenhigher harmonics',
        added_independent_scalar='S_Maxwell(Abar+a)-S_Maxwell(Abar); reference curvature already in R8',
        relative_attachment_factor_to_normalized_cap=None,
        physical_radial_source_profile=None,physical_retarded_solution=None,physical_current_Pauli_form=None,
        stationary_E1_claim=False,complete_native_action=False,heat_evaluation=False,
        error_scope='binary64 finite same-action operator application; no continuum tail, coupled stationary solve or native Pauli enclosure')
    (output/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return receipt


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); print(json.dumps(materialize(args.output),sort_keys=True))
