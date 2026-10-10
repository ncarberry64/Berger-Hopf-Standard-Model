"""Fixed-Y source heat on freshly solved, current-normalized response columns.

This consumes the full Maxwell/Higgs action response to the enriched
angular duals, including source-frame motion before Gauss reduction.
It does not borrow the old eight-Q Higgs response or mean contact.  The
base and Dirichlet product core retain their explicit finite-germ scope.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicHermiteSpline

from .muon_birth_candidate_geometry_action import ROOT
from .muon_native_coupled_source_heat import retained_corrected_scalar_photon_response,_first_response_blocks
from .muon_native_current_component_heat import current_geometric_photon_component,component_response_fermion_image
from .muon_native_product_factor_graph import _finite,_source_core_samples,_family_shell_heat_forms
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian,lepton_current_hilbert_representation
from .muon_parent_retarded_hypercharge import compact_trace_pulse

REACHED='artifacts/muon_reached_trace_action_20261010/run_2'
RECEIPT_SHA256='dcd8e15171b54f61718779ae1b8b9d2dedfc221c1db8f19a40e4fd9fb22d8ca8'


def retained_current_reached_response(repository=ROOT):
    """Bind actual source400 and solved H80/rates with pinned owner evidence."""
    root=Path(repository);folder=root/REACHED;raw=(folder/'result.json').read_bytes()
    if sha256(raw).hexdigest()!=RECEIPT_SHA256:raise ValueError('pinned fresh reached response receipt changed')
    receipt=json.loads(raw);records=[dict(path=REACHED+'/result.json',bytes=len(raw),sha256=RECEIPT_SHA256)]
    if not receipt['actual_new_reached_source_response'] or receipt['scalar_Maxwell_relative_normalization']!=8:
        raise ValueError('fresh same-action normalized source response required')
    for path,digest in receipt['input_hashes'].items():
        if sha256((root/path).read_bytes()).hexdigest()!=digest:raise ValueError('fresh response action owner changed: '+path)
    loaded={}
    for name in ('contact.npz','source.npz','velocity.npz'):
        data=(folder/name).read_bytes();info=receipt['array_archives'][name]
        if len(data)!=info['bytes'] or sha256(data).hexdigest()!=info['sha256']:
            raise ValueError('fresh response archive changed: '+name)
        records.append(dict(path=REACHED+'/'+name,bytes=len(data),sha256=info['sha256']))
        with np.load(folder/name,allow_pickle=False) as archive:loaded[name]={k:archive[k].copy() for k in archive.files}
    contact,source,velocity=(loaded[k] for k in ('contact.npz','source.npz','velocity.npz'))
    times=_finite(contact['times'],'reached response times',real=True)
    H=_finite(contact['intrinsic_H_response'],'fresh H80 response',(len(times),80,8),real=True)
    Hd=_finite(velocity['velocity'][:,320:400],'fresh H80 velocity',H.shape,real=True)
    if times.ndim!=1 or np.any(np.diff(times)<=0) or times[0]!=0:raise ValueError('future finite response time grid required')
    base=retained_corrected_scalar_photon_response(root)
    if times[-1]!=base['representation']['length']:raise ValueError('source and operator numerical core disagree')
    component=current_geometric_photon_component(base,0.)
    b=_finite(source['current_angular_response'],'fresh angular response',(240,8))
    image=component_response_fermion_image(component,dict(basis_response=b))
    cut=_finite(source['cut_b_source_coefficients'],'fresh full400 cut coefficients',(400,8),real=True)
    if not np.array_equal(cut[160:],b.real) or np.any(cut[:160]):raise ValueError('source trace does not match the newly solved angular response')
    return dict(base=base,times=times,H80=H,H80_rate=Hd,H80_spline=CubicHermiteSpline(times,H,Hd),
        source_image=image,cut_b_source_coefficients=cut,receipt=receipt,source_records=records,
        duration=base['duration'],time_shift=base['time_shift'],genuine_mixed_response=None,
        old_original_Q8_H_response_used=False,physical_history_or_native_domain_selected=False)


def reached_fixed_y_source_vertices(response, coordinate_time):
    """Actual moving photon direction plus fresh sourced fixed-Y LR mass."""
    t=float(coordinate_time);u=t-response['time_shift']
    if not np.isfinite(t) or u<response['times'][0] or u>response['times'][-1]:raise ValueError('no fresh reached vertex extrapolation')
    base=response['base'];h=response['H80_spline'](u).reshape(4,20,8).transpose(2,1,0)
    hd=response['H80_spline'](u,1).reshape(4,20,8).transpose(2,1,0)
    H=np.stack((h[:,:,0]+1j*h[:,:,2],h[:,:,1]+1j*h[:,:,3]),axis=-1)
    Hdot=np.stack((hd[:,:,0]+1j*hd[:,:,2],hd[:,:,1]+1j*hd[:,:,3]),axis=-1)
    from .muon_native_product_factor_graph import finite_common_family_intrinsic_operator
    op=finite_common_family_intrinsic_operator(t,base['coefficients'],base['representation'],base['reference'])
    Tb=1/np.sqrt(2*np.pi**2*op['R4']);pulse=float(compact_trace_pulse(u,response['duration'])[0])
    return dict(gauge=Tb*pulse*response['source_image']['unit_radius_b_source_image']/op['R4'],
        scalar=fixed_y_higgs_hamiltonian(H.reshape(160,2)).reshape(8,20,18,18),
        scalar_rate=fixed_y_higgs_hamiltonian(Hdot.reshape(160,2)).reshape(8,20,18,18),
        complex_H_response=H,current_T_b=Tb,profile=pulse,
        source_motion_count=1,genuine_second_mass_vertex=None,
        scalar_response_is_from_fresh_full_action=True,old_Q8_response_substituted=False)


def reached_first_response_heat_core(response, *, time_nodes,quadrature_order,family_indices=(1,2)):
    """Contact and source images from the actual new gauge/H first response."""
    nodes=_finite(time_nodes,'fresh reached heat nodes',real=True)
    if nodes.ndim!=1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):raise ValueError('increasing finite core nodes required')
    if nodes[0]<response['time_shift'] or nodes[-1]>0:raise ValueError('no fresh heat extrapolation')
    if type(quadrature_order) is not int or quadrature_order<2:raise ValueError('quadrature order>=2 required')
    families=tuple(family_indices)
    if not families or len(set(families))!=len(families) or any(type(f) is not int or f not in (0,1,2) for f in families):
        raise ValueError('distinct retained families required')
    base=response['base'];samples=_source_core_samples(base['coefficients'],base['representation'],base['reference'],nodes,np.ones((len(nodes),8)),quadrature_order)
    for s in samples:
        t=nodes[s['cell']]+s['x']*s['h'];v=reached_fixed_y_source_vertices(response,t)
        s['vertices']={k:v[k] for k in ('gauge','scalar')}
    angular=response['source_image']['angular'];D=angular['derivative_matrices'];labels=angular['harmonic_labels']
    Y=lepton_current_hilbert_representation()['family_Y']
    if np.any(Y-np.diag(np.diag(Y))):raise ValueError('diagonal owned fixed-Y family action required')
    result={}
    for f in families:
        fiber=np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f]);complement=np.array([i for i in range(18) if i not in fiber])
        if any(np.max(abs(s['W'][np.ix_(fiber,complement)]))>1e-14 for s in samples):raise ValueError('family decomposition not invariant')
        zero=_family_shell_heat_forms(samples,len(nodes),None,fiber)
        contacts={k:np.zeros((8,8,len(zero['eigenvalues'])),complex) for k in ('gauge','scalar','interference')};shells={}
        for n in (1,3):
            ids=np.array([i for i,l in enumerate(labels) if l[0]==n]);shell=_family_shell_heat_forms(samples,len(nodes),D[:,ids][:,:,ids],fiber)
            first,contact=_first_response_blocks(samples,len(nodes),zero,shell,fiber,ids)
            for k in contacts:contacts[k]+=contact[k]
            shells[str(n)]=dict(eigenvalues=shell['eigenvalues'],first_jet_n0=first,full_shell_scalar_count=len(ids),
                all_complementary_eigenmodes_retained=True,generalized_eigen_residual_relative=shell['generalized_eigen_residual_relative'])
        result[str(f)]=dict(inherited_family=('heavy','middle','light')[f],fixed_Y=float(Y[f,f]),n0_eigenvalues=zero['eigenvalues'],
            first_response_contact_spectral_diagonal=contacts,intermediate_shells=shells,generalized_eigen_residual_relative=zero['generalized_eigen_residual_relative'])
    return dict(families=result,time_nodes=nodes,quadrature_order=quadrature_order,
        actual_fresh_H_response_included=True,current_source_T_b_motion_retained=True,
        original_Q8_heat_or_coupled_response_substituted=False,
        normalization='fresh current b duals -> beta=Tb(currentR4)b and fixed-Y actual H80 response; no extra e,QNORM or family factor',
        total_genuine_mixed_H_geometry_domain_response_included=False,
        complete_native_heat_or_Pauli_evaluated=False)
