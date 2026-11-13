"""Actual retarded scalar response in the source-paired finite Dirac core.

The first response is loaded from the same-action constrained parent+H
producer.  Its scalar mass insertion is not replaced by zero and its pulse
is the SAME raw eight-Q wall direction.  This module extends the frozen
fixed-field component without changing its source or artifacts.  The
genuine mixed response is a distinct reached action term, not affine-zero.
No finite local chart is promoted to physical C1/E0/stop or native heat.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicHermiteSpline

from .muon_birth_candidate_geometry_action import ROOT
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian, lepton_current_hilbert_representation
from .muon_native_product_factor_graph import (
    _finite, _source_core_samples, _family_shell_heat_forms,
    _ordered_heat_lag, _ordered_cutoff_heat_lag,
    retained_eight_q_fermion_source_image,
)
from .muon_parent_maxwell_corrected_retarded import load_corrected_iterate
from .muon_moving_geometric_action import retained_state
from .muon_parent_retarded_hypercharge import compact_trace_pulse


RESPONSE='artifacts/muon_parent_maxwell_corrected_retarded_20261010/run_3'
RESPONSE_HASHES={
    'result.json':'f94bf8920356f27176de9a00278c13f5d90cedcb207e7a78d67f6ac7f082de93',
    'application.npz':'7908eb2bb8faf3f054fad2b9b6e65751f3589adf04e823da69283fe9dbb775f1',
    'operator.npz':'a54ca77e1b5815517c9fc42578528d3b2fc8d173c683089428854d9d5449ac0e',
}


def retained_corrected_scalar_photon_response(repository=ROOT):
    """Bind the actual H80 response, its rates, and its exact source pulse."""
    repository=Path(repository);folder=repository/RESPONSE
    records=[]
    for name,expected in RESPONSE_HASHES.items():
        raw=(folder/name).read_bytes();actual=sha256(raw).hexdigest()
        if actual!=expected:raise ValueError('pinned corrected scalar response mismatch: '+name)
        records.append(dict(path=RESPONSE+'/'+name,bytes=len(raw),sha256=actual))
    receipt=json.loads((folder/'result.json').read_bytes())
    if not receipt['Higgs_sector_in_retarded_operator'] or receipt['scalar_trace_chart']!='material_reference':
        raise ValueError('actual intrinsic H and material trace producer required')
    if receipt['free_wall_child_interface_exterior_return_included']:
        raise ValueError('this bridge is for the retained prescribed-trace parent response')
    with np.load(folder/'application.npz',allow_pickle=False) as archive:
        times=_finite(archive['times'],'retained response times',real=True)
        H=_finite(archive['intrinsic_H_response'],'actual H80 response',(len(times),80,8),real=True)
        rates=_finite(archive['velocity'][:,320:400],'actual H80 temporal rates',H.shape,real=True)
    if np.any(np.diff(times)<=0) or times[0]!=0 or times[-1]!=receipt['final_time']:
        raise ValueError('retained response time/domain identity changed')
    coefficients,representation,_=load_corrected_iterate(repository)
    if representation['length']!=receipt['final_time']:
        raise ValueError('scalar response and finite common family use different time charts')
    return dict(times=times,H80=H,H80_rate=rates,H80_spline=CubicHermiteSpline(times,H,rates),
        duration=receipt['duration'],time_shift=-receipt['final_time'],
        coefficients=coefficients,representation=representation,reference=retained_state(repository),
        source=retained_eight_q_fermion_source_image(repository),source_records=records,
        receipt=receipt,repository=repository,
        H_response_order='real component major (ReH1,ReH2,ImH1,ImH2) x20 real harmonics x8 raw beta',
        source_profile='same retained compact_trace_pulse(u,D), D=L/3; t=u-L is local coefficient chart',
        genuine_H_mixed_response=None,
        physical_history_or_native_domain_selected=False)


def corrected_response_source_vertices(response, coordinate_time):
    """Apply fixed Y to the actual odd Higgs response and add raw-Q gauge.

    The mass and gauge maps act on all eighteen inherited Weyl entries.
    Every n1/n3 scalar label is retained.  The wall parent radial gauge
    trial is zero, prescribed temporal/radial source traces are zero,
    and the spatial source uses its actual same compact pulse.  These are
    producer/domain statements at this wall, not general field zeros.
    """
    t=float(coordinate_time);u=t-response['time_shift']
    if not np.isfinite(t) or u<response['times'][0] or u>response['times'][-1]:
        raise ValueError('source vertex cannot extrapolate the retained response')
    h=response['H80_spline'](u).reshape(4,20,8).transpose(2,1,0)
    hd=response['H80_spline'](u,1).reshape(4,20,8).transpose(2,1,0)
    complex_H=np.stack((h[:,:,0]+1j*h[:,:,2],h[:,:,1]+1j*h[:,:,3]),axis=-1)
    complex_H_rate=np.stack((hd[:,:,0]+1j*hd[:,:,2],hd[:,:,1]+1j*hd[:,:,3]),axis=-1)
    mass=fixed_y_higgs_hamiltonian(complex_H.reshape(160,2)).reshape(8,20,18,18)
    mass_rate=fixed_y_higgs_hamiltonian(complex_H_rate.reshape(160,2)).reshape(8,20,18,18)
    pulse=float(compact_trace_pulse(u,response['duration'])[0])
    return dict(complex_H_response=complex_H,complex_H_response_rate=complex_H_rate,
        fixed_Y_mass_vertex=mass,fixed_Y_mass_vertex_rate=mass_rate,
        raw_gauge_unit_radius_vertex=pulse*response['source']['unit_radius_source_image'].reshape(8,20,18,18),
        pulse=pulse,coefficient_time=t,response_time=u,
        angular_order=response['source']['angular']['harmonic_labels'],
        temporal_wall_source_zero_provenance='retained prescribed spatial Q trace has At=Ar=0; parent radial phi(WALL)=0',
        extra_e_Tb_or_family_factor_applied=False,
        genuine_mixed_mass_vertex=None)


def _first_response_blocks(samples,node_count,zero,shell,fiber,angular_ids):
    """Independent gauge, scalar and interference first-response pairings."""
    size=shell['size'];d0=6*node_count;dn=size*node_count
    first={k:np.zeros((8,dn,d0),complex) for k in ('gauge','scalar')}
    contact={k:np.zeros((8,8,d0,d0),complex) for k in ('gauge','scalar','interference')}
    eye0=np.eye(6);eyen=np.eye(size);count=size//6
    for s in samples:
        i,x,h=s['cell'],s['x'],s['h']
        W=s['W'][np.ix_(fiber,fiber)];omega=s['Omega_t'][np.ix_(fiber,fiber)]
        B0=W+omega/s['N'];Bn=shell['principal']/s['R']+np.kron(np.eye(count),B0)
        A0=np.concatenate((-eye0/(h*s['N'])+(1-x)*B0,eye0/(h*s['N'])+x*B0),axis=1)
        An=np.concatenate((-eyen/(h*s['N'])+(1-x)*Bn,eyen/(h*s['N'])+x*Bn),axis=1)
        V0=np.concatenate(((1-x)*eye0,x*eye0),axis=1)
        Vn=np.concatenate(((1-x)*eyen,x*eyen),axis=1)
        X={}
        for key in ('gauge','scalar'):
            vertex=s['vertices'][key][:,angular_ids][:,:,fiber][:,:,:,fiber].reshape(8,size,6)
            X[key]=vertex@V0
            local=An.conj().T@X[key]+Vn.conj().T@(vertex@A0)
            first[key][:,i*size:(i+2)*size,i*6:(i+2)*6]+=s['weight']*local
            g=np.einsum('Aki,Bkj->ABij',X[key].conj(),X[key])
            contact[key][:,:,i*6:(i+2)*6,i*6:(i+2)*6]+=s['weight']*(g+g.transpose(1,0,2,3))
        g=np.einsum('Aki,Bkj->ABij',X['gauge'].conj(),X['scalar'])
        g+=np.einsum('Aki,Bkj->ABij',X['scalar'].conj(),X['gauge'])
        contact['interference'][:,:,i*6:(i+2)*6,i*6:(i+2)*6]+=s['weight']*(g+g.transpose(1,0,2,3))
    f={}
    for key,F in first.items():
        F=F[:,shell['interior']][:,:,zero['interior']]
        f[key]=np.einsum('ni,Anm,mj->Aij',shell['vectors'].conj(),F,zero['vectors'],optimize=True)
    c={}
    for key,C in contact.items():
        C=C[:,:,zero['interior']][:,:,:,zero['interior']]
        c[key]=np.einsum('mi,ABmn,ni->ABi',zero['vectors'].conj(),C,zero['vectors'],optimize=True)
    return f,c


def corrected_first_response_heat_core(response,*,time_nodes,quadrature_order,family_indices=(1,2)):
    """Execute complete source-reached core with the solved H80 first jets."""
    nodes=_finite(time_nodes,'coupled source heat nodes',real=True)
    if nodes.ndim!=1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):
        raise ValueError('at least three increasing coupled heat nodes required')
    if nodes[0]<response['time_shift'] or nodes[-1]>0:
        raise ValueError('coupled source heat cannot extrapolate the local chart')
    if type(quadrature_order) is not int or quadrature_order<2:
        raise ValueError('explicit coupled heat quadrature order>=2 required')
    families=tuple(family_indices)
    if not families or len(set(families))!=len(families) or any(type(f) is not int or f not in (0,1,2) for f in families):
        raise ValueError('distinct inherited family indices0,1,2 required')
    samples=_source_core_samples(response['coefficients'],response['representation'],response['reference'],
        nodes,np.ones((len(nodes),8)),quadrature_order)
    # Both gauge and scalar use the SAME actual source clock, not an unrelated
    # constant pulse from the earlier fixed-field demonstration.
    for s in samples:
        t=nodes[s['cell']]+s['x']*s['h']
        v=corrected_response_source_vertices(response,t)
        s['vertices']=dict(gauge=v['raw_gauge_unit_radius_vertex']/s['R'],scalar=v['fixed_Y_mass_vertex'])
    angular=response['source']['angular'];D=angular['derivative_matrices'];labels=angular['harmonic_labels']
    Y=lepton_current_hilbert_representation()['family_Y']
    if np.max(abs(Y-np.diag(np.diag(Y))))!=0:
        raise ValueError('separate family trace requires the retained diagonal fixed Y')
    result={}
    for family in families:
        fiber=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
        complement=np.array([i for i in range(18) if i not in fiber])
        if any(np.max(abs(s['W'][np.ix_(fiber,complement)]))>1e-14 for s in samples):
            raise ValueError('computed background is not family invariant')
        zero=_family_shell_heat_forms(samples,len(nodes),None,fiber)
        contacts={k:np.zeros((8,8,len(zero['eigenvalues'])),complex) for k in ('gauge','scalar','interference')}
        shells={}
        for n in (1,3):
            ids=np.array([i for i,l in enumerate(labels) if l[0]==n])
            shell=_family_shell_heat_forms(samples,len(nodes),D[:,ids][:,:,ids],fiber)
            f,c=_first_response_blocks(samples,len(nodes),zero,shell,fiber,ids)
            for key in contacts:contacts[key]+=c[key]
            shells[str(n)]=dict(eigenvalues=shell['eigenvalues'],first_jet_n0=f,
                full_shell_scalar_count=len(ids),all_complementary_eigenmodes_retained=True,
                generalized_eigen_residual_relative=shell['generalized_eigen_residual_relative'])
        result[str(family)]=dict(inherited_family=('heavy','middle','light')[family],fixed_Y=float(Y[family,family]),
            n0_eigenvalues=zero['eigenvalues'],first_response_contact_spectral_diagonal=contacts,
            intermediate_shells=shells,generalized_eigen_residual_relative=zero['generalized_eigen_residual_relative'])
    return dict(families=result,time_nodes=nodes,quadrature_order=quadrature_order,
        actual_H_response_included=True,
        source_scope='same compact raw-beta pulse and solved H80 from corrected constrained retarded producer',
        mixed_factor_jet_from_actual_mean_H_second_response=None,
        remaining_geometric_and_domain_first_response_included=False,
        first_response_complete_n0_image='all n1+n3 x full lepton family fibers, not eight-source heat',
        complete_total_source_pair_heat_evaluated=False,physical_native_domain_closed=False)


def corrected_first_response_heat_application(core,parameter,*,integrate_cutoff=False):
    """Evaluate reached gauge/scalar/cross terms without subtracting totals.

    This returns the mixed contact built from first jets and both insertion
    terms.  It does not set A_vJ=0: the genuine scalar-mean and complete
    coupled geometry/domain contribution remains a named unevaluated term.
    """
    value=float(parameter)
    if not np.isfinite(value) or value<=0:raise ValueError('positive explicit heat-function parameter required')
    rows={}
    for name,f in core['families'].items():
        lam=f['n0_eigenvalues']
        weight=(-np.exp(-value*lam)/lam if integrate_cutoff else -value*np.exp(-value*lam))
        contacts={k:np.einsum('ABi,i->AB',c,weight) for k,c in f['first_response_contact_spectral_diagonal'].items()}
        pairs={k:np.zeros((8,8),complex) for k in contacts};errors={k:0. for k in contacts}
        for shell in f['intermediate_shells'].values():
            small,large=(_ordered_cutoff_heat_lag(lam,shell['eigenvalues'],value) if integrate_cutoff
                         else _ordered_heat_lag(lam,shell['eigenvalues'],value))
            g,h=shell['first_jet_n0']['gauge'],shell['first_jet_n0']['scalar']
            def evaluate(lag):
                return dict(gauge=np.einsum('Aji,Bji,ji->AB',g.conj(),g,lag),
                    scalar=np.einsum('Aji,Bji,ji->AB',h.conj(),h,lag),
                    interference=np.einsum('Aji,Bji,ji->AB',g.conj(),h,lag)+
                                 np.einsum('Aji,Bji,ji->AB',h.conj(),g,lag))
            a,b=evaluate(small),evaluate(large)
            for key in pairs:pairs[key]+=b[key];errors[key]+=float(np.linalg.norm(b[key]-a[key]))
        components={k:dict(source_square_contact=contacts[k],ordered_two_insertion=pairs[k],
            opposite_order_two_insertion=pairs[k].T,
            reached_first_response_pair=contacts[k]+pairs[k]+pairs[k].T,
            scalar_kernel_quadrature_refinement_absolute_Frobenius_difference=errors[k]) for k in contacts}
        rows[name]=dict(inherited_family=f['inherited_family'],components=components,
            reached_first_response_pair_sum=sum(c['reached_first_response_pair'] for c in components.values()),
            genuine_mixed_scalar_mean_contact=None,
            full_geometry_domain_and_overlap_response=None,
            complete_total_source_pair_heat=None)
    return dict(parameter=value,cutoff_integral_to_infinity=integrate_cutoff,families=rows,
        first_solved_H_mass_vertices_included=True,
        genuine_mixed_response_not_assigned_affine_zero=True,
        normalization='raw-beta gauge plus fixed-Y actual scalar response; no extra e,T_b,statistics or overlap factor',
        physical_cutoff_or_complete_native_Pauli_selected=False)
