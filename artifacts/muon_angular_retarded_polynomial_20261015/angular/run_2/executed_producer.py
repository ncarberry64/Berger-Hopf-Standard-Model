"""Exact complete ONE-probe angular image on retained n0+n1 full18 inputs.

An n1 multiplication reaches n0+n1+n2 (252 by 90 full18 coefficients).
This rectangular source map is complete for that one application, but is
not a finite closed angular operator, retarded inverse, or physical muon.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import sympy as sy
from sympy.physics.wigner import clebsch_gordan


SOURCE = 'artifacts/muon_formed_weak_field_20261015/same_epoch_probe/run_2'
SOURCE_SHA = '25035d89b453023ae4fa97566b973c29e2899b24caeb4eac7236fdb7cbcacfdb'


def maxabs(a): return float(np.max(abs(a)))


def npz(path, arrays):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for k, v in sorted(arrays.items()):
            b = BytesIO(); np.lib.format.write_array(b, np.asarray(v), allow_pickle=False)
            info = zipfile.ZipInfo(k+'.npy', (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, b.getvalue())


def exact_transform(complex_labels, real_labels):
    lookup = {a:i for i,a in enumerate(complex_labels)}
    U = sy.zeros(len(complex_labels))
    for column, (n, m, k, part) in enumerate(real_labels):
        i = lookup[n,m,k]
        if part == 'self': U[i,column] = 1; continue
        j = lookup[n,-m,-k]; sign = sy.Integer(-1)**((m-k)//2)
        if part == 'real': U[i,column], U[j,column] = 1/sy.sqrt(2), sign/sy.sqrt(2)
        else: U[i,column], U[j,column] = -sy.I/sy.sqrt(2), sy.I*sign/sy.sqrt(2)
    return U


@lru_cache(None)
def cg(n1, n2, n, m1, m2, m):
    return clebsch_gordan(sy.Rational(n1,2), sy.Rational(n2,2), sy.Rational(n,2),
                         sy.Rational(m1,2), sy.Rational(m2,2), sy.Rational(m,2))


def exact_gaunt(out_labels, source_labels, input_labels, Uout, Usrc, Uin):
    """Exact real Peter--Weyl products from the actual sqrt(n+1) convention."""
    lookup = {a:i for i,a in enumerate(out_labels)}
    sparse = {}
    uo = [[(a,sy.conjugate(Uout[i,a])) for a in range(Uout.cols) if Uout[i,a] != 0] for i in range(Uout.rows)]
    us = [[(a,Usrc[i,a]) for a in range(Usrc.cols) if Usrc[i,a] != 0] for i in range(Usrc.rows)]
    ui = [[(a,Uin[i,a]) for a in range(Uin.cols) if Uin[i,a] != 0] for i in range(Uin.rows)]
    for j,(ns,ms,ks) in enumerate(source_labels):
        for k,(ni,mi,ki) in enumerate(input_labels):
            for no in range(abs(ns-ni), ns+ni+1, 2):
                target = (no,ms+mi,ks+ki)
                if target not in lookup: continue
                c = sy.sqrt(sy.Rational((ns+1)*(ni+1), no+1))*cg(ns,ni,no,ms,mi,ms+mi)*cg(ns,ni,no,ks,ki,ks+ki)
                if c == 0: continue
                for a,x in uo[lookup[target]]:
                    for b,y in us[j]:
                        for d,z in ui[k]: sparse[a,b,d] = sparse.get((a,b,d),sy.S.Zero)+c*x*y*z
    sparse = {key:sy.simplify(v) for key,v in sparse.items() if sy.simplify(v) != 0}
    if any(sy.im(v) != 0 for v in sparse.values()): raise ArithmeticError('real exact Gaunt coefficient has imaginary part')
    numeric = np.zeros((len(out_labels),len(source_labels),len(input_labels)))
    for key,v in sparse.items(): numeric[key] = float(v)
    return sparse,numeric


def exact_spin(n):
    j = sy.Rational(n,2); weights = [sy.Rational(n-2*k,2) for k in range(n+1)]
    plus = sy.zeros(n+1)
    for col in range(1,n+1):
        m = weights[col]; plus[col-1,col] = sy.sqrt((j-m)*(j+m+1))
    return [(plus+plus.T)/2,(plus-plus.T)/(2*sy.I),sy.diag(*weights)]


def exact_angular_operators(max_level, U):
    body, orbital = [], []
    for a in range(3):
        eb, ob = [], []
        for n in range(max_level+1):
            J = exact_spin(n)[a]; identity = sy.eye(n+1)
            eb.append(2*sy.I*sy.kronecker_product(J,identity))
            # Conjugation g -> u g u^-1 fixes g=I and rotates q in R3.
            ob.append(sy.kronecker_product(J,identity)-sy.kronecker_product(identity,sy.conjugate(J)))
        body.append(sy.simplify(U.conjugate().T*sy.diag(*eb)*U))
        orbital.append(sy.simplify(U.conjugate().T*sy.diag(*ob)*U))
    return body, orbital


def contract(gaunt, coefficients):
    return np.einsum('ohi,Ahst->Aosit',gaunt,coefficients).reshape(
        len(coefficients),gaunt.shape[0]*18,gaunt.shape[2]*18)


def run(repository, output):
    root, out = Path(repository).resolve(),Path(output).resolve()
    if out.exists(): raise FileExistsError('preserve independent angular evaluations')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_intrinsic_scalar_discretization import (
        scalar_section_labels,real_scalar_basis_labels,scalar_s3_discretization,
        scalar_basis_values,real_scalar_basis_transform)
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from bhsm.interface.muon_matched_mechanical_source import epsilon
    pins = {}
    def read(path):
        p = root/path; raw = p.read_bytes(); pins[path] = sha256(raw).hexdigest()
        if p.suffix == '.json': return json.loads(raw)
        if p.suffix == '.npz':
            with np.load(BytesIO(raw),allow_pickle=False) as a:return{k:a[k].copy()for k in a.files}
        return raw.decode('utf8')
    read('AGENTS.md')
    md = read(SOURCE+'/result.json')
    if pins[SOURCE+'/result.json'] != SOURCE_SHA: raise ValueError('saved source epoch changed')
    for module in ('muon_intrinsic_scalar_discretization','muon_native_dirac_hamiltonian','muon_matched_mechanical_source'):
        read('src/bhsm/interface/'+module+'.py')
    cl = scalar_section_labels(3); rl = real_scalar_basis_labels(3); U = exact_transform(cl,rl)
    if U.conjugate().T*U != sy.eye(30): raise ArithmeticError('exact real frame is not unitary')
    c1,r1 = scalar_section_labels(1),real_scalar_basis_labels(1)
    c2,r2 = scalar_section_labels(2),real_scalar_basis_labels(2)
    U1,U2 = U[:5,:5],U[:14,:14]
    exact, gall = exact_gaunt(cl, c1[1:], c2, U,U1[1:,1:],U2)
    G = gall[:14,:,:5]
    nextG = gall[14:,:,5:14]
    Eb, Lb = exact_angular_operators(3,U)
    E = np.array([np.array(a).astype(complex) for a in Eb])
    L = np.array([np.array(a).astype(complex) for a in Lb])
    if maxabs(E.imag) > 1e-14: raise ArithmeticError('body coefficient derivatives must be real')
    E = E.real
    # Exact Leibniz identities establish every reached coefficient, not just
    # a pointwise or dimension-only angular witness.
    Gexact = sy.zeros(14,20)
    for (o,h,i),v in exact.items():
        if o<14 and i<5:Gexact[o,h*5+i]=v
    exact_leibniz = []
    exact_rotation = []
    for a in range(3):
        body_rows = Eb[a][:14,:14]*Gexact-Gexact*(sy.kronecker_product(Eb[a][1:5,1:5],sy.eye(5))+sy.kronecker_product(sy.eye(4),Eb[a][:5,:5]))
        rotation_rows = Lb[a][:14,:14]*Gexact-Gexact*(sy.kronecker_product(Lb[a][1:5,1:5],sy.eye(5))+sy.kronecker_product(sy.eye(4),Lb[a][:5,:5]))
        exact_leibniz.append(all(sy.simplify(x)==0 for x in body_rows))
        exact_rotation.append(all(sy.simplify(x)==0 for x in rotation_rows))
    if not all(exact_leibniz+exact_rotation):raise ArithmeticError('exact source product derivative identity failed')
    quad = scalar_s3_discretization(3); Y=quad['real_basis_values']; w=quad['haar_weights']
    quadrature = np.einsum('po,ph,pi,p->ohi',Y[:,:14],Y[:,1:5],Y[:,:5],w)
    pointwise = np.einsum('po,ohi->phi',Y[:,:14],G)-Y[:,1:5,None]*Y[:,None,:5]
    gram = Y.T@(w[:,None]*Y)
    alpha = lepton_current_hilbert_representation()['alpha']
    S = np.array([-.5j*alpha[(a+1)%3]@alpha[(a+2)%3]for a in range(3)])
    eps = epsilon()
    Jout=np.array([np.kron(L[a,:14,:14],np.eye(18))+np.kron(np.eye(14),S[a])for a in range(3)])
    Jin=np.array([np.kron(L[a,:5,:5],np.eye(18))+np.kron(np.eye(5),S[a])for a in range(3)])
    pvalues = (scalar_basis_values(np.eye(2,dtype=complex)[None],3)@real_scalar_basis_transform(3))[0].real
    pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    qvalues=(.5j*np.einsum('aij,pji->pa',pauli,quad['su2_points'])).real
    qcoeff=Y[:,1:5].T@(w[:,None]*qvalues)
    body_q=np.einsum('h,ahk,kj->aj',pvalues[1:5],E[:,1:5,1:5],qcoeff)
    # Check that the selected isotropy generator is the physical coordinate
    # rotation around g=I. It leaves scalar w fixed and rotates q as a vector.
    q_rotation=np.einsum('ahk,kj->ahj',L[:,1:5,1:5],qcoeff)
    expected_rotation=1j*np.einsum('ajk,hk->ahj',eps,qcoeff)
    controls=dict(exact_Gaunt_nonzero_count=len(exact),
        exact_body_Leibniz_all_zero=all(exact_leibniz),exact_isotropy_Leibniz_all_zero=all(exact_rotation),
        Gaunt_quadrature_difference=maxabs(G-quadrature),pointwise_full_product_closure=maxabs(pointwise),
        real_Haar_Gram_rows=maxabs(gram-np.eye(30)),
        native_body_derivative_convention_rows=maxabs(E-quad['real_angular_derivative_matrices']),
        coordinate_isotropy_rotation_rows=maxabs(q_rotation-expected_rotation),
        spin_Casimir_rows=maxabs(sum(a@a for a in S)-.75*np.eye(18)),
        spin_su2_rows=max(maxabs(S[a]@S[b]-S[b]@S[a]-1j*sum(eps[a,b,c]*S[c]for c in range(3)))for a in range(3)for b in range(3)),
        orbital_su2_rows=max(maxabs(L[a]@L[b]-L[b]@L[a]-1j*sum(eps[a,b,c]*L[c]for c in range(3)))for a in range(3)for b in range(3)))
    if max(v for v in controls.values()if isinstance(v,float))>2e-10:raise ArithmeticError('angular/structural identity failed '+str(controls))
    out.mkdir(parents=True)
    core=dict(gaunt_out_n012_source_n1_input_n01=G,
        gaunt_n3_source_n1_input_n2=nextG,
        right_body_derivatives_out_n012=E[:,:14,:14],right_body_derivatives_input_n01=E[:,:5,:5],
        right_body_derivatives_source_n1=E[:,1:5,1:5],
        isotropy_orbital_generators_out_n012=L[:,:14,:14],isotropy_orbital_generators_input_n01=L[:,:5,:5],
        spin_generators_full18=S,total_spin_orbital_out_n012=Jout,total_spin_orbital_input_n01=Jin,
        real_basis_labels_out_n012=np.array(rl[:14],dtype=str),real_basis_labels_input_n01=np.array(rl[:5],dtype=str),
        real_basis_labels_source_n1=np.array(rl[1:5],dtype=str),point_harmonics=pvalues,
        coordinate_quaternion_coefficients=qcoeff,right_body_quaternion_jacobian=body_q)
    npz(out/'exact_angular_core.npz',core)
    records=[]; archives={'exact_angular_core.npz':sha256((out/'exact_angular_core.npz').read_bytes()).hexdigest()}
    for j in range(2):
        filename=f'stage_{j:04d}_actual_unit_magnetic_source_and_direct_insertion.npz'
        source=read(SOURCE+'/'+filename)
        if pins[SOURCE+'/'+filename]!=md['archives'][filename]:raise ValueError('saved source packet changed')
        HB=source['canonical_H_B_coefficients_per_unit_e']; HBt=source['canonical_H_B_coordinate_time_per_unit_e']
        R=source['wall_radius'].item(); Rt=source['R4_coordinate_time'].item()
        V=contract(G,HB); Vt=contract(G,HBt); nextV=contract(nextG,HB)
        dHB=np.einsum('ahk,Akij->aAhij',E[:,1:5,1:5],HB)
        dV=np.array([contract(G,a)for a in dHB])
        leibniz=np.array([np.kron(E[a,:14,:14],np.eye(18))@V-V@np.kron(E[a,:5,:5],np.eye(18))-dV[a]for a in range(3)])
        total=np.array([Jout[a]@V-V@Jin[a]-1j*np.einsum('bc,cij->bij',eps[a],V)for a in range(3)])
        spin_only=np.array([np.kron(np.eye(14),S[a])@V-V@np.kron(np.eye(5),S[a])for a in range(3)])
        value=np.einsum('h,Ahij->Aij',pvalues[1:5],HB)
        derivative=np.einsum('h,ahk,Akij->aAij',pvalues[1:5],E[:,1:5,1:5],HB)
        derivative_time=np.einsum('h,ahk,Akij->aAij',pvalues[1:5],E[:,1:5,1:5],HBt)
        jacobian=R*body_q
        physical_gradient=np.einsum('ja,aAik->Ajik',np.linalg.inv(jacobian),derivative)
        physical_gradient_time=np.einsum('ja,aAik->Ajik',np.linalg.inv(jacobian),derivative_time)-Rt/R*physical_gradient
        check=dict(rectangular_source_body_Leibniz_rows=maxabs(leibniz),
            total_spin_plus_orbital_vector_covariance_rows=maxabs(total),
            direct_n0_to_n1_reproduction_rows=maxabs(V[:,18:90,:18]-source['direct_n0_to_n1_per_unit_e']),
            direct_n1_to_n0_reproduction_rows=maxabs(V[:,:18,18:90]-source['direct_n1_to_n0_per_unit_e']),
            source_operator_n2_output_norm=float(np.linalg.norm(V[:,90:,:])),
            next_n2_to_n3_operator_norm=float(np.linalg.norm(nextV)),
            nonzero_spin_only_commutator_norm=float(np.linalg.norm(spin_only)),
            local_point_insertion_norm=float(np.linalg.norm(value)),
            local_physical_coordinate_gradient_norm=float(np.linalg.norm(physical_gradient)))
        if max(check[k]for k in ('rectangular_source_body_Leibniz_rows','total_spin_plus_orbital_vector_covariance_rows',
            'direct_n0_to_n1_reproduction_rows','direct_n1_to_n0_reproduction_rows'))>2e-10:
            raise ArithmeticError('actual full18 angular source identity failed '+str(check))
        if check['source_operator_n2_output_norm']==0 or check['next_n2_to_n3_operator_norm']==0:
            raise ArithmeticError('nonzero reached/next angular image was erased')
        data=dict(direct_probe_out252_in90_per_unit_e=V,
            direct_probe_coordinate_time_out252_in90_per_unit_e=Vt,
            direct_probe_body_derivative_out252_in90_per_unit_e=dV,
            direct_probe_literal_transpose_in90_out252=V.transpose(0,2,1),
            direct_probe_next_n3_out288_n2_in162_per_unit_e=nextV,
            coordinate_point_insertion=value,coordinate_point_physical_gradient=physical_gradient,
            coordinate_point_physical_gradient_time=physical_gradient_time,
            local_canonical_momentum_commutator=-1j*physical_gradient,
            right_body_to_physical_coordinate_jacobian=jacobian,
            source_H_B_coefficients_per_unit_e=HB,source_H_B_coordinate_time_per_unit_e=HBt,
            wall_radius=np.array(R),wall_radius_coordinate_time=np.array(Rt),
            angular_source_body_Leibniz_rows=leibniz,total_spin_orbital_covariance_rows=total)
        name=f'stage_{j:04d}_complete_reached_angular_probe.npz';npz(out/name,data)
        archives[name]=sha256((out/name).read_bytes()).hexdigest();records.append(dict(stage=j,checks=check))
    exact_strings=[dict(output=o,source=h,input=i,value=str(v))for(o,h,i),v in sorted(exact.items())]
    report=dict(classification='EXACT_COMPLETE_ONE_N1_PROBE_ANGULAR_IMAGE_AND_ACTUAL_FULL18_SOURCE_APPLICATION',
        source_parent=SOURCE,input_harmonics='n0+n1:5; all18 spin/weak/family fibers',
        output_harmonics='n0+n1+n2:14; all18 fibers',operator_shape=[3,252,90],
        coefficient_order='harmonic-major; full18 fiber fastest',
        core_controls=controls,records=records,exact_real_Gaunt_coefficients=exact_strings,
        exact_Gaunt_convention='sqrt((n1+1)(n2+1)/(N+1))*CG_m*CG_k, transformed by the actual exact real harmonic frame; independently checked against original degree12 Haar quadrature.',
        first_order_scope='Complete one multiplication on DECLARED n0+n1 inputs. Unperturbed inverse may stay in these shells only if its actual boundary/domain preserves harmonic level.',
        further_angular_data_required='n2 inputs immediately produce nonzero n3. Repeated multiplication has an unbounded ladder; no finite angular cap is declared closed.',
        spin_orbital_scope='Exact coordinate isotropy orbital L for conjugation fixing gI, plus native full18 S. Vector covariance is structural; no global physical spin state, spin eigenstate, rest frame or moment is selected.',
        momentum_scope='Local canonical [p_j,H_B]=-i partial_Xj H_B at gI; X=R*q and exact body-to-coordinate Jacobian. Not an external Fourier/LSZ momentum or Pauli extraction.',
        literal_coefficients_conjugated=False,physical_retarded_inverse_evaluated=False,
        source_or_D5_or_history_campaign_restarted=False,physical_Gamma_B=None,physical_muon_moment=None,
        unit_e_only=True,tree_g_equals_two_inserted=False,full_physical_angular_tail_closed=False,
        numerical_identity_guard=2e-10,archives=archives,input_hashes=pins,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    encoded=json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n'
    (out/'result.json').write_text(encoded,encoding='utf8',newline='\n')
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(output=str(out),result_sha256=sha256(encoded.encode()).hexdigest(),
                          angular_core_sha256=archives['exact_angular_core.npz'],records=records)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.output)
