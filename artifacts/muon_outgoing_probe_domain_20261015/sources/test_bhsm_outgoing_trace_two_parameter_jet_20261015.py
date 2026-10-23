"""Independent checks of the caller-supplied mixed outgoing-domain pairing."""
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from bhsm_outgoing_trace_two_parameter_jet_20261015 import outgoing_trace_two_parameter_pairing


def product(a,b):
    return (a[0]@b[0],a[1]@b[0]+a[0]@b[1],
        a[2]@b[0]+a[0]@b[2],
        a[3]@b[0]+a[1]@b[2]+a[2]@b[1]+a[0]@b[3])


def fixture():
    rng=np.random.default_rng(30917)
    def mats(shape):return tuple((rng.normal(size=shape)+1j*rng.normal(size=shape))/7 for _ in range(4))
    F=mats((3,2));S=list(mats((3,3)));S[0]+=np.eye(3);S=tuple(S)
    V=tuple(np.vstack((np.eye(2)if i==0 else np.zeros((2,2)),f))for i,f in enumerate(F))
    W=tuple(np.hstack((-f,np.eye(3)if i==0 else np.zeros((3,3))))for i,f in enumerate(F))
    C=product(S,W)
    T=list(mats((5,3)));A=mats((2,3))[0]
    T[0]=V[0]@A+np.vstack((np.zeros((2,3)),np.linalg.solve(S[0],np.diag([0.,1.2,1.3]))))
    R=np.eye(3)[:,:1].astype(complex);L=R.T.copy();a=A[:,:1]
    return C,V,tuple(T),R,L,a,S,F


def apply(C,V,T,R,L,a):
    return outgoing_trace_two_parameter_pairing(**dict(zip((
        'annihilator','annihilator_energy','annihilator_magnetic','annihilator_energy_magnetic',
        'allowed_trace','allowed_trace_energy','allowed_trace_magnetic','allowed_trace_energy_magnetic',
        'joined_trace','joined_trace_energy','joined_trace_magnetic','joined_trace_energy_magnetic',
        'right_mode','left_mode','allowed_coordinates'),(*C,*V,*T,R,L,a))))


def maximum(a):return float(np.max(np.abs(a)))


def checks():
    C,V,T,R,L,a,S,F=fixture();q=apply(C,V,T,R,L,a)
    chains=max(maximum(q[k])for k in ('energy_chain_rule_rows','magnetic_chain_rule_rows','energy_magnetic_chain_rule_rows'))
    identities=max(maximum(q[k])for k in ('allowed_trace_rows','allowed_trace_energy_rows','allowed_trace_magnetic_rows','allowed_trace_energy_magnetic_rows'))
    H=(np.array([[1.2,.3j],[.1,1.4]],complex),
       np.array([[.2j,.1],[.3,-.2]],complex),
       np.array([[.1,-.1j],[.2j,.3]],complex),
       np.array([[.2,.1j],[.3j,.4]],complex))
    changed=apply(C,product(V,H),T,R,L,np.linalg.solve(H[0],a))
    same_first=max(maximum(changed[k]-q[k])for k in ('transverse_energy_pairing','transverse_magnetic_pairing'))
    mixed=lambda x:x['mixed_joined_transport_and_allowed_trace_pairing']+x['mixed_first_domain_contacts']
    same_mixed=maximum(mixed(changed)-mixed(q))
    missing_mixed=maximum(q['mixed_first_domain_contacts'])
    changed_transport=maximum(changed['mixed_joined_transport_and_allowed_trace_pairing']-q['mixed_joined_transport_and_allowed_trace_pairing'])
    # Independent finite differences of polynomial C(E,B)T(E,B), never a pole path.
    poly=lambda j,e,b:j[0]+e*j[1]+b*j[2]+e*b*j[3]
    def Gamma(e,b):
        f=poly(F,e,b);s=poly(S,e,b)
        return s@np.hstack((-f,np.eye(3)))@poly(T,e,b)
    steps=(-2,-1,1,2);weights=np.array([1.,-8.,8.,-1.])/12;h=.025
    fdE=sum(w*Gamma(i*h,0.)for i,w in zip(steps,weights))/h
    fdB=sum(w*Gamma(0.,i*h)for i,w in zip(steps,weights))/h
    fdEB=sum(we*wb*Gamma(i*h,j*h)for i,we in zip(steps,weights)for j,wb in zip(steps,weights))/h**2
    differences=max(maximum(fdE-q['gamma_energy']),maximum(fdB-q['gamma_magnetic']),maximum(fdEB-q['gamma_energy_magnetic']))
    # Off-pole discrepancies remain in the exact identity instead of being projected away.
    damagedT=list(T);damagedT[0]=T[0]+.1
    damaged=apply(C,V,damagedT,R,L,a)
    damaged_chain=max(maximum(damaged[k])for k in ('energy_chain_rule_rows','magnetic_chain_rule_rows','energy_magnetic_chain_rule_rows'))
    damaged_contact=max(maximum(damaged[k])for k in ('off_pole_or_nonannihilating_energy_contacts','off_pole_or_nonannihilating_magnetic_contacts','off_pole_or_nonannihilating_mixed_contacts'))
    # Nonannihilating jets likewise cannot silently pass as an actual outgoing frame.
    damagedV=list(V);damagedV[3]=V[3]+.2
    bad=apply(C,damagedV,T,R,L,a)
    bad_chain=maximum(bad['energy_magnetic_chain_rule_rows'])
    bad_identity=maximum(bad['allowed_trace_energy_magnetic_rows'])
    return dict(chain_rule_max=chains,annihilator_jet_identity_max=identities,
        allowed_basis_first_invariance_max=same_first,allowed_basis_mixed_invariance_max=same_mixed,
        omitted_first_domain_contacts_mixed_error=missing_mixed,
        transport_only_allowed_basis_change=changed_transport,
        independent_polynomial_E_B_EB_difference_max=differences,
        off_pole_chain_rule_max=damaged_chain,retained_off_pole_contact_max=damaged_contact,
        nonannihilating_jet_chain_rule_max=bad_chain,retained_nonannihilating_mixed_identity_max=bad_identity)


def test_exact_trace_basis_changes_and_domain_contacts():
    c=checks()
    assert max(c[k]for k in ('chain_rule_max','annihilator_jet_identity_max','allowed_basis_first_invariance_max','allowed_basis_mixed_invariance_max'))<2e-14
    assert c['omitted_first_domain_contacts_mixed_error']>1e-3
    assert c['transport_only_allowed_basis_change']>1e-3


def test_independent_bivariate_difference():
    assert checks()['independent_polynomial_E_B_EB_difference_max']<2e-10


def test_off_pole_and_nonannihilating_contacts_stay_explicit():
    c=checks()
    assert max(c['off_pole_chain_rule_max'],c['nonannihilating_jet_chain_rule_max'])<2e-14
    assert min(c['retained_off_pole_contact_max'],c['retained_nonannihilating_mixed_identity_max'])>1e-3


def test_shape_validation_never_adds_missing_zero_jets():
    C,V,T,R,L,a,*_=fixture()
    broken=list(C);broken[3]=np.zeros((1,1))
    try:apply(broken,V,T,R,L,a)
    except ValueError:return
    raise AssertionError('missing mixed trace rows were silently accepted')
