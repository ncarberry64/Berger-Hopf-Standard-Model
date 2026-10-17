"""Actual common1200-to-full384 D5 insertions on saved REAL source germs.

No completed D5/source/history action is repeated. Saved Lorentz point
actions are converted algebraically, keeping A0 and assigned formal phase
separate. The common gauge product reaches all55 n<=4 harmonics.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
from scipy import sparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_full_d5_common_gauge_insertion import (
    common_material_gauge_maps,full_d5_gauge_spin_factors,apply_material_insertion,
    internal_material_actions,material_pairing,material_source_gram,
    common_form_pullback,common_source_square_action)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_parent_positive_brst_ghost import ghost_radial_values,smooth_ghost_temporal_values
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

SOURCE='artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'
BASE='artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1'
EXPECTED={SOURCE+'/result.json':'d15def102e329c38f35b62c137d8398aa72eeda626924498a426246d66c88df1',
    SOURCE+'/application.npz':'7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177',
    BASE+'/result.json':'06867e31959910ec21385e8491bd5b794060c68e8404ae0524e3d0c9b544faa6',
    BASE+'/application.npz':'c67363c17adfb519f399614463d5a13dbcd019aa53246d452421eea8ba982455'}


def compare(a,b):
    a,b=np.asarray(a),np.asarray(b);d=abs(a-b)
    return dict(absolute=float(np.max(d)),max_entry_scaled=float(np.max(d/np.maximum(1,np.maximum(abs(a),abs(b))))))


def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def real(a,name):
    a=np.asarray(a)
    if np.iscomplexobj(a) and np.any(a.imag!=0):raise ValueError('No complex field projection: '+name)
    if not np.isfinite(a).all():raise ValueError('finite supplied operand required')
    return np.asarray(a.real,float)


def scale(a,u):return np.asarray(a).reshape((-1,)+(1,)*(u.ndim-1))*u


def recover_actions(c,full,trials,DL,DLx,energy):
    """Independent Dtau expression, saved DL, and both exact phase identities."""
    u,ur,ut,ux,urx,utx,_,_=trials;q,D,n=u.shape;h=D//384
    resh=lambda a:a.reshape(q,3,2,4,16,h,n)
    u,ur,ut,ux,urx,utx,DL,DLx=map(resh,(u,ur,ut,ux,urx,utx,DL,DLx))
    N,z,h0,ell=(c[k] for k in('lapse','coordinate_shift','geometric_time_contact','surface_proper_clock_rate'))
    Nx,zx,h0x,ellx=(c[k+'_first'][0] for k in('lapse','coordinate_shift','geometric_time_contact','surface_proper_clock_rate'))
    A,Ax=c['gauge_connection_material'],c['gauge_connection_material_first'][0]
    g=np.array([full['unitTr16_gauge_particle'],full['unitTr16_gauge_particle'].conj()])
    O=np.einsum('qc,bcij->qbij',(A[:,0]-z[:,None]*A[:,1])/N[:,None],g)
    Ox=np.einsum('qc,bcij->qbij',(Ax[:,0]-zx[:,None]*A[:,1]-z[:,None]*Ax[:,1])/N[:,None]
        -(A[:,0]-z[:,None]*A[:,1])*Nx[:,None]/N[:,None]**2,g)
    apply=lambda a,v:np.einsum('qbij,qfbsjhn->qfbsihn',a,v,optimize=True)
    Dt=scale(1/N,ut-scale(z,ur))+scale(h0,u)+apply(O,u)
    Dtx=scale(1/N,utx-scale(zx,ur)-scale(z,urx))-scale(Nx/N**2,ut-scale(z,ur))
    Dtx+=scale(h0x,u)+scale(h0,ux)+apply(Ox,u)+apply(O,ux)
    G0=np.array([full['gamma5D_particle'][0],full['gamma5D_conjugate'][0]])
    gamma0=lambda v:np.einsum('bst,qfbtihn->qfbsihn',G0,v,optimize=True)
    phase=scale(energy*ell/N,u);phasex=scale(energy*(ellx/N-ell*Nx/N**2),u)+scale(energy*ell/N,ux)
    A0=(1+1j)*Dt-gamma0(DL)+phase;A0x=(1+1j)*Dtx-gamma0(DLx)+phasex
    return dict(value=u,value_time=ux,Dtau=Dt,Dtau_time=Dtx,A0=A0,A0_time=A0x,
        formal=A0-1j*phase,formal_time=A0x-1j*phasex,
        original_lorentz=DL,original_lorentz_time=DLx)


def save_map(arrays,name,L):
    L=L.tocsr();arrays[name+'_data']=L.data;arrays[name+'_indices']=L.indices
    arrays[name+'_indptr']=L.indptr;arrays[name+'_shape']=np.array(L.shape)


def original_lorentz_gauge_control(material,spin,gen,gaunt,value,c,full,eps,Yg,Yi,Yo):
    """Literal original iGamma connection placements, no split-factor S."""
    acted=apply_material_insertion(material,spin,gen,gaunt,value)
    ids=np.array([0,17,len(Yg)//2,len(Yg)-1]);P=Yg[ids];I=Yi[ids];O=Yo[ids]
    field=np.einsum('ph,qmch->qpmc',P,material)
    v=np.einsum('pk,qfbsikn->qfbspin',I,value)
    result=np.empty_like(v)
    for b,branch in enumerate(('particle','conjugate')):
        gamma=full['gamma5D_'+branch]
        gauge=np.einsum('qpmc,cij->qpmij',field,gen[b])
        # Contract internal before fixed spin; this is the original unsquared
        # Lorentz coefficient, with Gamma0 exactly once in its time term.
        U=np.einsum('qpmij,qfspjn->qfmspin',gauge,v[:,:,b],optimize=True)
        temporal=U[:,:,0]-scale(c['coordinate_shift'],U[:,:,1])
        temporal=scale(1/c['lapse'],temporal)
        DL=1j*np.einsum('st,qftpin->qfspin',gamma[0],temporal)
        DL+=scale(1/c['radial_coframe'],1j*eps*np.einsum('st,qftpin->qfspin',gamma[4],U[:,:,1]))
        for a in range(3):DL+=scale(1/c['radius'],1j*np.einsum('st,qftpin->qfspin',gamma[a+1],U[:,:,a+2]))
        result[:,:,b]=(1+1j)*temporal-np.einsum('st,qftpin->qfspin',gamma[0],DL)
    reconstructed=np.einsum('po,qfbsion->qfbspin',O,acted)
    return compare(reconstructed,result)


def execute(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve independent actual applications')
    pins={}
    def pin(rel):
        p=ROOT/rel;h=sha256(p.read_bytes()).hexdigest()
        if rel in EXPECTED and h!=EXPECTED[rel]:raise ValueError('Frozen input epoch changed: '+rel)
        pins[rel]=h;return p
    report=json.loads(pin(SOURCE+'/result.json').read_bytes())
    if report['classification']!='ACTUAL_REAL_FULL384_D5_FROZEN_CELL_SOURCE_FIRST_APPLICATION':raise ValueError('Exact full384 source application required')
    with np.load(pin(SOURCE+'/application.npz'),allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    base=json.loads(pin(BASE+'/result.json').read_bytes())
    with np.load(pin(BASE+'/application.npz'),allow_pickle=False) as z:rep={k:z[k].copy() for k in('affine_profile_reference_states','affine_interior_projection')}
    rep.update(affine_wall_coefficient=base['affine_profile_enrichment']['wall_coefficient'],
        affine_complement_norm=base['affine_profile_enrichment']['boundary_anchored_complement_norm'])
    sourceowner=imported('saved_full_d5_trial_owner',pin('audits/bhsm_real_full_d5_source_first_application_20261016.py'))
    commonowner=imported('saved_common_profile_owner',pin('audits/bhsm_real_ew_higgs_fp_common_forms_20261016.py'))
    angular=scalar_s3_discretization(4);labels=np.array(angular['real_basis_labels'],object)
    ids=np.array([i for i,l in enumerate(labels) if l[0] in(1,3)])
    E=angular['real_angular_derivative_matrices'][:,ids][:,:,ids]
    Yg=angular['real_basis_values'][:,ids];Yi=angular['basis_values'][:,:5];Yo=angular['basis_values'];haar=angular['haar_weights']
    gaunt=np.einsum('p,po,ph,pk->ohk',haar,Yo.conj(),Yg,Yi,optimize=True)
    product=np.einsum('po,ohk->phk',Yo,gaunt,optimize=True)
    product_control=compare(product,Yg[:,:,None]*Yi[:,None,:])
    EO=angular['angular_derivative_matrices'];EI=EO[:,:5,:5]
    leibniz=np.einsum('aop,phk->aohk',EO,gaunt)-np.einsum('ojk,ajh->aohk',gaunt,E)-np.einsum('ohl,alk->aohk',gaunt,EI)
    if max(product_control['max_entry_scaled'],float(np.max(abs(leibniz))))>2e-12:raise ArithmeticError('Complete angular product incidence failed')
    full=full_d5_localized_lepton_trace();records=[];out.mkdir(parents=True)
    arrays=dict(gaunt_full55_real20_input5=gaunt,gaunt_independent_left=gaunt.conj().transpose(2,1,0),source_real_derivatives=E,input_complex_derivatives=EI,
        target_complex_derivatives=EO,source_real_harmonic_indices=ids)
    x,w=np.polynomial.legendre.leggauss(4);rho=np.r_[(x+1)*WALL/2,WALL];rw=w*WALL/2*(2*np.pi**2)
    radial=ghost_radial_values(rho);basis,basisr=trace_enriched_radial_basis(rep,rho)
    for side in('incoming','outgoing'):
        prefix=side+'_input_';c={k[len(prefix):]:real(v,k) for k,v in saved.items() if k.startswith(prefix)}
        raw=c.pop('raw');rawtime=c.pop('rawtime')
        if not np.array_equal(c['radial_points'],rho):raise ValueError('No radial/source epoch splice')
        entries=[r for r in report['records'] if r['side']==side and r['angular_level']==1]
        if len(entries)!=2 or entries[0]['coordinate_time']!=entries[1]['coordinate_time']:raise ValueError('Single same-clock source germ required')
        t0=float(entries[0]['coordinate_time']);length=2*abs(t0)
        phase='artifacts/muon_finite_normal_phase_20261011/incoming_run_1' if side=='incoming' else 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
        receipt=json.loads(pin(phase+'/result.json').read_bytes())
        if receipt['steps']!=1 or abs(receipt['span'])!=length:raise ValueError('No source-clock rescaling')
        A=c['gauge_connection_material'];At=c['gauge_connection_material_first'][0]
        independent=np.einsum('ri,ifc->rfc',basis,raw[100:180].reshape(4,5,4))
        independent[:,2:]+=M*(c['mechanical_profile'][:,0,None,None]-1)
        if compare(A,independent)['absolute']>1e-13:raise ValueError('Wrong saved source/reference basis')
        Ar=np.einsum('ri,ifc->rfc',basisr,raw[100:180].reshape(4,5,4));Ar[:,2:]+=M*c['mechanical_profile'][:,2,None,None]
        tg=smooth_ghost_temporal_values([length/2],length)[0]
        arrays[side+'_raw']=raw;arrays[side+'_rawtime']=rawtime
        for k,a in c.items():arrays[side+'_c_'+k]=a
        energy=float(report['off_shell_phase_frequency'])
        core={k:(v[:, :4] if k.endswith('_first') else v[:4]) for k,v in c.items() if (k.endswith('_first') or v.shape[:1]==(5,))}
        trials=sourceowner.declared_trials(rho[:4],384*5)
        for eps in(-1,1):
            tag=f'{side}_eta{eps}'
            actions=recover_actions(core,full,trials,saved[f'{side}_n1_eta{eps}_point_value'],saved[f'{side}_n1_eta{eps}_point_first'],energy)
            F=full_d5_gauge_spin_factors(c,full,sheet_orientation=eps)
            S,Sx,G=F['spin'][:4],F['spin_time'][:4],F['carrier_generators']
            T=internal_material_actions(S,G,actions['value'])
            Tx=internal_material_actions(Sx,G,actions['value'])+internal_material_actions(S,G,actions['value_time'])
            matGram,matGramx,gram_factors=material_source_gram(T,gaunt,Tx,return_factors=True)
            mu=c['volume_density'][:4];mux=c['volume_density_first'][0,:4]
            weights,weightsx=rw*mu,rw*mux
            embed=lambda a:np.pad(a,((0,0),(0,0),(0,0),(0,0),(0,0),(0,50),(0,0)))
            oldpos=np.einsum('q,qfbsika,qfbsikn->an',weights,actions['formal'].conj(),actions['formal'])
            oldposx=np.einsum('q,qfbsika,qfbsikn->an',weightsx,actions['formal'].conj(),actions['formal'])
            oldposx+=np.einsum('q,qfbsika,qfbsikn->an',weights,actions['formal_time'].conj(),actions['formal'])
            oldposx+=np.einsum('q,qfbsika,qfbsikn->an',weights,actions['formal'].conj(),actions['formal_time'])
            baseline=dict(value=compare(oldpos,saved[f'{side}_n1_eta{eps}_positive_value']),
                first=compare(oldposx,saved[f'{side}_n1_eta{eps}_positive_first']))
            for tent_sign in(-1,1):
                temporal=np.r_[1.,tent_sign*2/length,tg[0,:2],tg[1,:2],tg[:,2]]
                maps=[common_material_gauge_maps(A[j],At[j],Ar[j],E,radial[j],temporal) for j in range(5)]
                for j,m in enumerate(maps):
                    literal,_=commonowner.trial_maps(A[j],At[j],Ar[j],E,radial[j],temporal)
                    for key,got in zip(('value','time','radial'),literal[:3]):
                        key2={'value':'material_value_map','time':'material_value_map_time','radial':'material_value_map_radial'}[key]
                        if compare(m[key2].toarray()[:,:1120],got.reshape(400,1120))['max_entry_scaled']>2e-12:raise ArithmeticError('Original common incidence mismatch: '+key)
                xtag=tag+f'_tent{tent_sign}'
                branch={}
                for placement in('A0','formal'):
                    aa,ax=actions[placement],actions[placement+'_time']
                    R=material_pairing(embed(aa).conj(),T,gaunt)
                    Rx=material_pairing(embed(ax).conj(),T,gaunt)+material_pairing(embed(aa).conj(),Tx,gaunt)
                    K,Kx=common_form_pullback(R,maps[:4],weights,material_pair_time=Rx,weights_time=weightsx)
                    K=K+K.conj().transpose(0,2,1);Kx=Kx+Kx.conj().transpose(0,2,1)
                    arrays[xtag+'_'+placement+'_common_K_partial']=K;arrays[xtag+'_'+placement+'_common_K_time_partial']=Kx
                    branch[placement]=dict(K_partial_norm=float(np.linalg.norm(K)),K_time_partial_norm=float(np.linalg.norm(Kx)),
                        independent_H80_bulk_norm=float(np.linalg.norm(K[1120:])),Hermitian_defect=float(np.max(abs(K-K.conj().transpose(0,2,1)))))
                zz=(np.cos(np.arange(1,1201)*.173)+.3*np.sin(np.arange(1,1201)*.119))/np.sqrt(1200);zz[800:1120]*=length
                zz3=np.zeros(1200);zz3[:1120]=zz[:1120];zz3[:800]=zz[:800]
                # Keep all original n3 source columns; this selection is only
                # a separate literal quadratic check, not a column removal.
                for p in range(14):zz3[p*80:p*80+16]=0
                mats=np.array([(m['material_value_map']@zz).reshape(5,4,20) for m in maps[:4]])
                ins=apply_material_insertion(mats,S,G,gaunt,actions['value'])
                matsx=np.array([(m['material_value_map_time']@zz).reshape(5,4,20) for m in maps[:4]])
                insx=apply_material_insertion(matsx,S,G,gaunt,actions['value'])
                insx+=apply_material_insertion(mats,Sx,G,gaunt,actions['value'])
                insx+=apply_material_insertion(mats,S,G,gaunt,actions['value_time'])
                mats3=np.array([(m['material_value_map']@zz3).reshape(5,4,20) for m in maps[:4]])
                ins3=apply_material_insertion(mats3,S,G,gaunt,actions['value'])
                zc=zz+1j*np.roll(zz,7)
                materialc=np.array([(m['material_value_map']@zc).reshape(5,4,20) for m in maps[:4]])
                xr=apply_material_insertion(materialc,S,G,gaunt,actions['value'])
                xl=apply_material_insertion(materialc,F['spin_left'][:4],F['carrier_generators_left'],
                    gaunt.conj().transpose(2,1,0),embed(actions['A0']))
                complex_direct=np.einsum('q,qfbsion,qfbsion->',weights,embed(actions['A0']).conj(),xr)
                complex_direct+=np.einsum('q,qfbsikn,qfbsikn->',weights,actions['value'].conj(),xl)
                K0=arrays[xtag+'_A0_common_K_partial']
                complex_basis=np.einsum('z,zii->',zc,K0)
                complex_control=compare(complex_direct,complex_basis)
                literal_control=original_lorentz_gauge_control(mats,S,G,gaunt,actions['value'],core,full,eps,Yg,Yi,Yo)
                h,hx=common_source_square_action(zz,maps[:4],matGram,weights,material_gram_time=matGramx,weights_time=weightsx)
                direct=2*np.einsum('q,qfbsion,qfbsion->',weights,ins.conj(),ins).real
                quadratic=compare(zz@h,direct)
                directx=2*np.einsum('q,qfbsion,qfbsion->',weightsx,ins.conj(),ins).real
                directx+=4*np.einsum('q,qfbsion,qfbsion->',weights,ins.conj(),insx).real
                quadraticx=compare(zz@hx,directx)
                if quadratic['max_entry_scaled']>2e-12:raise ArithmeticError('Complete source-square action control failed')
                arrays[xtag+'_common_source_square_on_declared_direction']=h
                arrays[xtag+'_common_source_square_time_on_declared_direction']=hx
                for j,m in enumerate(maps):
                    for k in('coefficient','coefficient_time','coefficient_radial'):arrays[xtag+f'_r{j}_'+k]=m[k]
                    for k in('material_value_map','material_value_map_time','material_value_map_radial'):save_map(arrays,xtag+f'_r{j}_'+k,m[k])
                walltrials=sourceowner.declared_trials(rho[4:],384*5)
                wallu=walltrials[0].reshape(1,3,2,4,16,5,3);wallux=walltrials[3].reshape(1,3,2,4,16,5,3)
                ma=(maps[4]['material_value_map']@zz).reshape(1,5,4,20)
                maxx=(maps[4]['material_value_map_time']@zz).reshape(1,5,4,20)
                xi=apply_material_insertion(ma,F['spin'][4:],G,gaunt,wallu)
                xix=apply_material_insertion(maxx,F['spin'][4:],G,gaunt,wallu)
                xix+=apply_material_insertion(ma,F['spin_time'][4:],G,gaunt,wallu)
                xix+=apply_material_insertion(ma,F['spin'][4:],G,gaunt,wallux)
                betad=F['material_radial_principal'][4:].conj().transpose(0,1,3,2)
                betadx=F['material_radial_principal_time'][4:].conj().transpose(0,1,3,2)
                actbeta=lambda a,v:np.einsum('qbst,qfbtion->qfbsion',a,v,optimize=True)
                wm,wmx=c['volume_density'][4:],c['volume_density_first'][0,4:]
                radial_flux=scale(wm,actbeta(betad,xi))
                radial_fluxx=scale(wmx,actbeta(betad,xi))+scale(wm,actbeta(betadx,xi)+actbeta(betad,xix))
                temporal_flux=scale(wm/c['lapse'][4:],xi)
                temporal_fluxx=scale(wmx/c['lapse'][4:]-wm*c['lapse_first'][0,4:]/c['lapse'][4:]**2,xi)+scale(wm/c['lapse'][4:],xix)
                for k,a in dict(radial_flux=radial_flux,radial_flux_time=radial_fluxx,temporal_flux=temporal_flux,temporal_flux_time=temporal_fluxx).items():
                    arrays[xtag+'_declared_direction_wall_'+k]=a
                branch.update(source_square_control=quadratic,source_square_time_control=quadraticx,source_square_value=float(direct),
                    independent_analytic_left_complex_source_control=complex_control,
                    literal_original_Lorentz_gauge_coefficient_control=literal_control,
                    complete_n3_insertion_norm=float(np.linalg.norm(ins3)),complete_n3_output_complement_norm=float(np.linalg.norm(ins3[...,5:,:])),
                    wall_radial_conormal_insertion_norm=float(np.linalg.norm(radial_flux)),
                    wall_temporal_conormal_insertion_norm=float(np.linalg.norm(temporal_flux)),
                    original_unsquared_Green_gauge_partial_exact_zero=True,
                    source_square_map_unknown_H_seam=True)
                records.append(dict(side=side,coordinate_time=t0,eta_orientation=eps,tent_one_sided_sign=tent_sign,
                    saved_primal_and_source_epoch_exact=True,original_common1200_incidence_checked=True,
                    native_recovery_saved_assigned_phase_form_control=baseline,applications=branch))
            for k in('spin','spin_time','carrier_generators','spin_left','spin_left_time','carrier_generators_left',
                'material_radial_principal','material_radial_principal_time','temporal_principal','temporal_principal_time'):
                arrays[tag+'_'+k]=F[k]
            for k,a in actions.items():arrays[tag+'_recovered_'+k]=a
            _compressed_npz(out/(tag+'_source_Gram_factors.npz'),gram_factors)
            print(dict(side=side,eta=eps,source_Gram_Hermitian=float(np.max(abs(matGram-matGram.conj().transpose(0,2,1)))),phase_recovery=baseline),flush=True)
    # Separate exact named arrays without re-encoding/splitting any numeric
    # entry. No monolithic all-directions action tensor is constructed.
    for side in('incoming','outgoing'):
        _compressed_npz(out/(side+'_saved_geometry.npz'),{k:v for k,v in arrays.items() if k.startswith(side+'_') and '_eta' not in k})
        for eps in(-1,1):
            tag=f'{side}_eta{eps}'
            _compressed_npz(out/(tag+'_compact_application.npz'),{k:v for k,v in arrays.items() if k.startswith(tag+'_')})
    _compressed_npz(out/'angular_product_incidence.npz',{k:v for k,v in arrays.items() if not k.startswith(('incoming_','outgoing_'))})
    for name,mod in list(sys.modules.items()):
        path=getattr(mod,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).is_relative_to(ROOT):pin(Path(path).relative_to(ROOT).as_posix())
    pin(Path(__file__).relative_to(ROOT).as_posix());(out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()) for p in sorted(out.glob('*.npz'))}
    if max(a['bytes'] for a in archives.values())>10*1024*1024:raise ArithmeticError('Split original compact archive before publication')
    result=dict(classification='ACTUAL_SAME_REAL_PRIMAL_COMMON1200_TO_FULL384_D5_GAUGE_INSERTION',records=records,
        all_original_common_gauge_and_DG_profiles_retained=True,common_dimension=1200,full_carrier_dimension=384,
        input_fermion_harmonics=5,source_gauge_harmonics=20,complete_product_output_harmonics=55,
        angular_product_point_control=product_control,angular_product_Leibniz_max_absolute=float(np.max(abs(leibniz))),
        common_gauge_partial_Gram_and_density_variation_exact_zero=True,actual_density_time_first_retained=True,
        independent_H80_zero_is_bulk_only=True,Higgs_seam_insertion_evaluated=False,
        source_square_Hessian_compact_action_on_all1200=True,source_square_includes_full55_product_complement=True,
        numerically_applied_saved_trial_columns=3,full_native_K_M_matrices_or_spectral_cotangent_evaluated=False,
        gauge_connection_shift_temporal_radial_spatial_vertices_all_retained=True,independent_analytic_left_supported=True,
        source_coefficients_conjugated=False,formal_phase_parameter=float(report['off_shell_phase_frequency']),
        A0_recovered_separately_from_assigned_formal_phase=True,physical_native_energy_conversion_identified=False,
        actual_spectral_states_or_heat_weights_inserted=False,statistics_or_native_quotient_selected=False,
        physical_native_application_complete=False,physical_exterior_or_total_domain_response=None,
        new_history_source_profile_D5_action_campaigns=0,original_coupled_corrections=0,
        physical_energy_field_source_domain_derivative_pass=False,physical_Maxwell226_after_pass=False,
        normalized_physical_two_spin_muon=None,physical_muon_magnetic_moment=None,
        archives=archives,input_and_source_sha256=dict(sorted(pins.items())))
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    a=p.parse_args();execute(a.output)
