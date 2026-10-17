"""Actual-input source checks; these are not physical anomaly tests."""
from pathlib import Path
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss
import pytest
try:
    from muon_local_source_jet import full_local_source,contact_forms,evaluated_child_forms
except ModuleNotFoundError:
    from bhsm.interface.muon_local_source_jet import full_local_source,contact_forms,evaluated_child_forms

HERE=Path(__file__).resolve().parent
INPUTS=HERE/'source_inputs.npz'
if not INPUTS.exists():INPUTS=HERE.parent/'artifacts/muon_source_jet_20261002/source_inputs.npz'

@lru_cache(None)
def data():
    with np.load(INPUTS,allow_pickle=False) as z:raw={k:np.array(z[k]) for k in z.files}
    parts={p:{k.split('__',1)[1]:v for k,v in raw.items() if k.startswith(p+'__')}
           for p in ('angular','body','frame','mixed')}
    s=full_local_source(parts['angular'],raw['gamma'])
    c=contact_forms(s)
    f=evaluated_child_forms(s,c,parts['body'],parts['frame'],parts['mixed'])
    return raw,parts,s,c,f


def test_saved_source_clifford_and_conjugate_charge_frames():
    raw,p,s,c,f=data()
    assert np.linalg.norm(s['V_retained']-p['mixed']['canonical_B_H_photon_source_unit'])<3e-14
    assert np.array_equal(s['gamma0_output']@s['Xi_complete'],s['V_complete'])
    assert s['charge_conjugation_residual']<2e-14
    for name in ['C_input','C_output']:
        C=s[name]
        assert np.linalg.norm(C@C.conj()-np.eye(len(C)))<3e-14
    U=s['Dirac_to_LR_columns'];g=s['gamma_LR'];gamma5=1j*g[0]@g[1]@g[2]@g[3]
    assert np.allclose(gamma5,np.diag([-1,-1,1,1]),atol=1e-15)
    # The independent saved frame and source caches must agree with a
    # single coordinate/orthonormal conversion, without the action index.
    frame=p['frame'];R=np.exp(frame['log_radius'])
    assert np.allclose(frame['coordinate_oneform_per_canonical_b_nodes']/R,
                       frame['canonical_physical_volume_factor_nodes'],rtol=2e-15)
    expected=np.exp(-1.5*.5*(frame['log_radius'][:-1]+frame['log_radius'][1:]))/np.sqrt(2*np.pi**2)
    assert np.allclose(expected,p['mixed']['physical_volume_source_factor'],rtol=2e-15)


def test_full_source_against_independent_haar_quadrature():
    raw,p,s,c,f=data()
    # Direct SU(2) matrix-coefficient integration, using symmetric tensor
    # square for n2. No CG/Gaunt routine or saved current is used here.
    y,w=leggauss(6);y=(y+1)/2;w=w/2
    angles=np.arange(12)*2*np.pi/12
    yy,aa,bb=np.meshgrid(y,angles,angles,indexing='ij')
    weights=np.repeat(w,144)/144
    z1=np.sqrt(1-yy.ravel())*np.exp(1j*aa.ravel())
    z2=np.sqrt(yy.ravel())*np.exp(1j*bb.ravel())
    g=np.empty((len(z1),2,2),complex)
    g[:,0,0]=z1;g[:,0,1]=z2;g[:,1,0]=-z2.conj();g[:,1,1]=z1.conj()
    sym=np.array([[1,0,0],[0,1/np.sqrt(2),0],[0,1/np.sqrt(2),0],[0,0,1]])
    square=np.einsum('qij,qkl->qikjl',g,g).reshape(-1,4,4)
    spin1=np.einsum('ia,qij,jb->qab',sym,square,sym)
    Y={0:np.ones((len(z1),1,1)),1:np.sqrt(2)*g,2:np.sqrt(3)*spin1}
    gauge=np.einsum('acmk,qmk->qac',s['real_mode_coefficients'],Y[1])
    assert np.abs(gauge.imag).max()<3e-15
    source=np.zeros((len(z1),2,10),complex);target=np.zeros((len(z1),2,28),complex)
    for i,(n,spin,m,k) in enumerate(s['input_labels']):
        source[:,spin,i]=Y[int(n)][:,(n-m)//2,(n-k)//2]
    for i,(n,spin,m,k) in enumerate(s['output_labels']):
        target[:,spin,i]=Y[int(n)][:,(n-m)//2,(n-k)//2]
    applied=np.einsum('qac,cst,qti->qasi',gauge,s['sigma'],source)
    integral=np.einsum('q,qso,qasi->aoi',weights,target.conj(),applied)
    # Absolute Frobenius tolerance for 864 summed binary64 quadrature terms;
    # this rounding check is not an outward physical error certificate.
    assert np.linalg.norm(integral-s['J_complete'])<2e-12
    summed=np.einsum('aaij->ij',c['contact_full'])
    assert np.linalg.norm(summed-16*np.eye(20))<4e-14
    P=p['mixed']['current_generated_projector_canonical20'];P0=np.zeros_like(P)
    P0[[0,1,10,11],[0,1,10,11]]=1
    tail=np.einsum('aaij->ij',c['contact_connected_complement'])
    assert np.linalg.norm(P@tail@P-(32/3)*(P-P0))<4e-14
    # This actual positive contact would be lost by squaring the saved block.
    assert np.linalg.norm(P@tail@P)>30


def test_actual_history_forms_against_direct_first_order_pairing():
    raw,p,s,c,f=data();frame=p['frame'];body=p['body'];mixed=p['mixed']
    E=mixed['external_n0_test_frame_E0']
    W=mixed['Gamma_s_unit_source_fermion_boson_external'].reshape(20,32)
    kin=body['kinetic_generator'];mass=body['mass_generator'];ret=s['retained_output_indices']
    x=frame['log_radius'];h=frame['proper_durations']
    nodes,weights=leggauss(12)
    a,i,j=np.unravel_index(np.abs(f['child_q_A_integrated']).argmax(),f['child_q_A_integrated'].shape)
    direct=0j;pair=0j;gram=0j
    # A supplied nonzero mass here is solely an arithmetic-control parameter;
    # the executed physical-input packet neither chooses nor evaluates it.
    for e,dt in enumerate(h):
        H=(x[e+1]-x[e])/dt
        for node,w in zip(nodes,weights):
            logR=x[e]+(node+1)/2*(x[e+1]-x[e])
            fR=np.exp(-1.5*logR)/np.sqrt(2*np.pi**2)
            T=np.concatenate([E,fR*W],axis=1)
            Td=np.concatenate([np.zeros_like(E),-1.5*H*fR*W],axis=1)
            canonical=1j*Td-(np.exp(-logR)*kin+.73*mass)@T
            D=np.zeros((56,36),complex);D[ret]=canonical
            Va=fR*s['V_complete'][a]@T
            derivative=D.conj().T@Va+Va.conj().T@D
            VB=fR*s['V_complete'][0]@T
            direct+=dt*w/2*derivative[i,j]
            pair+=dt*w/2*(2*VB.conj().T@VB)[4,4]
            gram+=dt*w/2*(T.conj().T@T)[4,4]
    assert direct==pytest.approx(f['child_q_A_integrated'][a,i,j],rel=2e-13,abs=2e-18)
    assert pair==pytest.approx(f['child_q_AB_integrated'][0,0,4,4],rel=2e-13,abs=2e-18)
    assert gram==pytest.approx(f['child_M_test_Gram'][4,4],rel=2e-13,abs=2e-18)
    assert np.array_equal(f['local_mass_first_jet_coefficient'],np.zeros_like(f['local_mass_first_jet_coefficient']))
    assert np.array_equal(f['child_mesh_source_trace_residual'],np.zeros(46))
