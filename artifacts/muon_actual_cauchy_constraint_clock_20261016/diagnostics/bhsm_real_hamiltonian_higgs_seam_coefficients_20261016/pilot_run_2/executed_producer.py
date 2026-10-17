"""Action-derived weak Hamiltonian Higgs seam on all1200 common columns.

Consumes frozen Lorentz seam coefficients only. The original Hamiltonian
output conversion is -Gamma0 K_L; scalar W placement is checked against
the existing intrinsic/surface native owner, never installed as a D5 bulk
mass or a squared delta. Ambient normal factors/domain remain explicit.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
from scipy.sparse import csr_matrix

ROOT=Path(__file__).resolve().parents[1]
PRIMARY='artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'


def compare(a,b):
    a,b=np.asarray(a),np.asarray(b)
    return dict(absolute=float(np.max(abs(a-b),initial=0)),
        max_entry_scaled=float(np.max(abs(a-b)/np.maximum(1,np.maximum(abs(a),abs(b))),initial=0)))


def sparse(z,key):
    return csr_matrix((z[key+'_data'],z[key+'_indices'],z[key+'_indptr']),shape=tuple(z[key+'_shape']))


def store(out,key,a):
    a=csr_matrix(a);a.eliminate_zeros()
    for suffix,value in (('data',a.data),('indices',a.indices),('indptr',a.indptr),('shape',np.asarray(a.shape))):
        out[key+'_'+suffix]=value


def coefficient_gram(V,Vt,gaunt):
    angular=np.einsum('ohk,opk->hp',gaunt.conj(),gaunt)
    inner=np.einsum('cij,dij->cd',V.conj(),V)
    first=np.einsum('cij,dij->cd',Vt.conj(),V)+np.einsum('cij,dij->cd',V.conj(),Vt)
    return np.einsum('cd,hp->chdp',inner,angular).reshape(80,80),np.einsum('cd,hp->chdp',first,angular).reshape(80,80)


def norms(L,Lt,G,Gt):
    L,Lt=L.toarray(),Lt.toarray()
    value=np.einsum('iz,iz->z',L,G@L).real
    first=(np.einsum('iz,iz->z',Lt,G@L)+np.einsum('iz,iz->z',L,Gt@L)+np.einsum('iz,iz->z',L,G@Lt)).real
    return value,first


def run(repository,seam_folder,output):
    root,folder,out=map(lambda p:Path(p).resolve(),(repository,seam_folder,output))
    if out.exists():raise FileExistsError('Preserve independent coefficient applications')
    pins={}
    def pin(path):
        p=Path(path);p=p if p.is_absolute()else root/p
        key=p.relative_to(root).as_posix()if p.is_relative_to(root)else str(p)
        pins[key]=sha256(p.read_bytes()).hexdigest();return p
    def read(path):
        p=pin(path)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_owned_native_product_connection import native_real_action_vertices
    import mpmath as mp
    mp.mp.dps=80
    meta=read(folder/'result.json')
    if pins[str(folder/'result.json')if not(folder/'result.json').is_relative_to(root)else(folder/'result.json').relative_to(root).as_posix()]!='bac39253088ff2d69363ceb79163b2d6809cd1d8cc1f7b69199d59c47cf3ba8c':
        raise ValueError('Exact frozen same-real seam receipt required')
    if sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!='3339d14ade6a8dd9bc2cdc008390de70251874aa2bb3c46814b922d625171fe0':
        raise ValueError('Wrong Lorentz seam application epoch')
    def arc(name):
        z=read(folder/name)
        if sha256((folder/name).read_bytes()).hexdigest()!=meta['archives'][name]['sha256']:raise ValueError('Frozen seam operand changed')
        return z
    incidence=arc('common_angular_and_full_trace_incidence.npz')
    gaunt=incidence['gaunt_full55_real20_input5']
    if gaunt.shape!=(55,20,5)or meta['common_dimension']!=1200:raise ValueError('Complete common/angular maps required')
    full=full_d5_localized_lepton_trace()
    if not np.array_equal(full['localized_lepton18_trace_lift'],incidence['full384_localized18_lift']):raise ValueError('Full carrier changed')
    G0=np.kron(np.eye(3),full['gamma5D_self_dual128'][0]);G0s=csr_matrix(G0)
    clifford_check=compare(G0@G0,np.eye(384))
    if clifford_check['absolute']>2e-14:raise ValueError('Original constant time Clifford required')
    primary=read(PRIMARY+'/application.npz')
    if pins[PRIMARY+'/application.npz']!='7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177':raise ValueError('No new primal/source epoch')
    arrays=dict(gaunt_full55_real20_input5=gaunt,full384_localized18_lift=incidence['full384_localized18_lift'],
        full384_retained_complement=incidence['full384_retained_complement'])
    store(arrays,'constant_original_Gamma0',G0)
    records=[];literal=[]
    # A fixed complex source is combined only AFTER the real-coordinate maps.
    z=(np.cos(np.arange(1,1201)*.127)+1j*np.sin(np.arange(1,1201)*.193))/np.sqrt(1200)
    arrays['literal_complex_common_direction']=z
    left=np.cos(np.arange(1,385)*.173)+1j*np.sin(np.arange(1,385)*.219)
    right=np.sin(np.arange(1,385)*.097)+1j*np.cos(np.arange(1,385)*.131)
    # Independent bilinear test rows, not a physical state or source dual.
    ao=np.cos(np.arange(1,56)*.157)+1j*np.sin(np.arange(1,56)*.221)
    bi=np.sin(np.arange(1,6)*.231)+1j*np.cos(np.arange(1,6)*.113)
    gh=np.einsum('o,ohk,k->h',ao,gaunt,bi)
    def mc(x):return mp.mpc(float(np.real(x)),float(np.imag(x)))
    def vector_product(B,v,transpose=False):
        B=csr_matrix(B);ans=[mp.mpc(0)for _ in range(B.shape[1]if transpose else B.shape[0])]
        for i in range(B.shape[0]):
            for p in range(B.indptr[i],B.indptr[i+1]):
                j=B.indices[p]
                if transpose:ans[j]+=mc(B.data[p])*mc(v[i])
                else:ans[i]+=mc(B.data[p])*mc(v[j])
        return ans
    for side in('incoming','outgoing'):
        print(json.dumps(dict(stage='Hamiltonian_weak_seam_coefficients',side=side)),flush=True)
        a=arc(side+'_common_higgs_seam_coefficients.npz')
        c={k[len(side+'_input_'):]:v for k,v in primary.items()if k.startswith(side+'_input_')}
        H,Ht=a['H_real'],a['H_real_time'];rho,rhot=float(a['original_surface_density']),float(a['original_surface_density_time'])
        s,st=a['bulk_density_isometry'].item(),a['bulk_density_isometry_time'].item()
        if s.imag!=0 or st.imag!=0 or s.real<=0:raise ValueError('Same real density isometry required')
        V=a['fixed_real_Higgs_vertices'];native=native_real_action_vertices(float(c['radius'][-1]),float(c['surface_proper_clock_rate'][-1]))['vertices'][20:24]
        native_check=compare(V,native)
        if native_check['absolute']!=0:raise ValueError('The existing intrinsic scalar W vertex must be exactly the same owned action term')
        P=np.diag(np.r_[np.ones(12),np.zeros(6)]);Q=np.eye(18)-P
        HV=rho*V;HVt=rhot*V
        arrays[side+'_intrinsic_native_scalar_vertices']=native
        arrays[side+'_surface_Hamiltonian_intrinsic_vertices']=HV
        arrays[side+'_surface_Hamiltonian_intrinsic_vertices_time']=HVt
        arrays[side+'_surface_Hamiltonian_intrinsic_background']=rho*a['background_intrinsic_mass']
        arrays[side+'_surface_Hamiltonian_intrinsic_background_time']=rhot*a['background_intrinsic_mass']+rho*a['background_intrinsic_mass_time']
        GI,GIt=coefficient_gram(HV,HVt,gaunt)
        allchannels={};checks={};frames={}
        for sheet in('plus','minus'):
            B=sparse(a,sheet+'_right_numerator').toarray();Bt=sparse(a,sheet+'_right_numerator_time').toarray()
            C=sparse(a,sheet+'_Dirac_bar_left_numerator').toarray();Ct=sparse(a,sheet+'_Dirac_bar_left_numerator_time').toarray()
            ER=sparse(a,sheet+'_mode_right_numerator').toarray();ERt=sparse(a,sheet+'_mode_right_numerator_time').toarray()
            EL=sparse(a,sheet+'_mode_Dirac_bar_left_numerator').toarray()@G0
            ELt=sparse(a,sheet+'_mode_Dirac_bar_left_numerator_time').toarray()@G0
            frames[sheet]=dict(B=B,Bt=Bt,C=C,Ct=Ct,ER=ER,ERt=ERt,EL=EL,ELt=ELt)
            checks[sheet+'_real_base_current_Riesz']=compare(G0@C,B.conj().T)
            checks[sheet+'_real_time_current_Riesz']=compare(G0@Ct,Bt.conj().T)
        for label,ls,rs,PL,PR in(('LR','plus','minus',P,Q),('RL','minus','plus',Q,P)):
            l,r=frames[ls],frames[rs]
            old=np.array([sparse(a,f'{label}_ambient_numerator_vertex{k}').toarray()for k in range(4)])
            oldt=np.array([sparse(a,f'{label}_ambient_numerator_vertex{k}_time').toarray()for k in range(4)])
            W=-np.einsum('ij,cjk->cik',G0,old);Wt=-np.einsum('ij,cjk->cik',G0,oldt)
            CV=np.einsum('ij,cjk,kl->cil',PL,V,PR)
            direct=rho*np.einsum('ij,cjk,kl->cil',l['B'].conj().T,CV,r['B'])
            directt=rhot*np.einsum('ij,cjk,kl->cil',l['B'].conj().T,CV,r['B'])
            directt+=rho*np.einsum('ij,cjk,kl->cil',l['Bt'].conj().T,CV,r['B'])
            directt+=rho*np.einsum('ij,cjk,kl->cil',l['B'].conj().T,CV,r['Bt'])
            checks[label+'_independent_weak_scalar']=compare(W,direct)
            checks[label+'_independent_weak_scalar_time']=compare(Wt,directt)
            pull=np.einsum('ij,cjk,kl->cil',l['EL'],W,r['ER'])
            pullt=np.einsum('ij,cjk,kl->cil',l['ELt'],W,r['ER'])+np.einsum('ij,cjk,kl->cil',l['EL'],Wt,r['ER'])+np.einsum('ij,cjk,kl->cil',l['EL'],W,r['ERt'])
            checks[label+'_intrinsic_native_scalar_recovery']=compare(pull,rho*CV)
            checks[label+'_intrinsic_native_scalar_recovery_time']=compare(pullt,rhot*CV)
            Wd=W/(s*s);Wdt=Wt/(s*s)-2*st*W/(s*s*s)
            ELd,ELdt=s*l['EL'],st*l['EL']+s*l['ELt'];ERd,ERdt=s*r['ER'],st*r['ER']+s*r['ERt']
            checks[label+'_density_recovery']=compare(np.einsum('ij,cjk,kl->cil',ELd,Wd,ERd),rho*CV)
            checks[label+'_density_recovery_time']=compare(np.einsum('ij,cjk,kl->cil',ELdt,Wd,ERd)+np.einsum('ij,cjk,kl->cil',ELd,Wdt,ERd)+np.einsum('ij,cjk,kl->cil',ELd,Wd,ERdt),rhot*CV)
            GW,GWt=coefficient_gram(W,Wt,gaunt)
            checks[label+'_unitary_output_Gram']=compare(GW,a[label+'_complete_operator_coefficient_Gram'])
            checks[label+'_unitary_output_Gram_time']=compare(GWt,a[label+'_complete_operator_coefficient_Gram_time'])
            allchannels[label]=(W,Wt,GW,GWt,CV,l,r)
            background=np.einsum('c,cij->ij',H,W)
            backgroundt=np.einsum('c,cij->ij',Ht,W)+np.einsum('c,cij->ij',H,Wt)
            checks[label+'_background']=compare(background,-G0@sparse(a,label+'_ambient_background_numerator').toarray())
            checks[label+'_background_time']=compare(backgroundt,-G0@sparse(a,label+'_ambient_background_numerator_time').toarray())
            store(arrays,f'{side}_{label}_Hamiltonian_background_numerator',background)
            store(arrays,f'{side}_{label}_Hamiltonian_background_numerator_time',backgroundt)
            for k in range(4):
                store(arrays,f'{side}_{label}_Hamiltonian_vertex{k}_numerator',W[k])
                store(arrays,f'{side}_{label}_Hamiltonian_vertex{k}_numerator_time',Wt[k])
                store(arrays,f'{side}_{label}_density_isometric_Hamiltonian_vertex{k}_numerator',Wd[k])
                store(arrays,f'{side}_{label}_density_isometric_Hamiltonian_vertex{k}_numerator_time',Wdt[k])
            arrays[f'{side}_{label}_operator_coefficient_Gram']=GW;arrays[f'{side}_{label}_operator_coefficient_Gram_time']=GWt
        checks['real_normal_condition_LR_RL_Hermitian_numerators']=compare(allchannels['LR'][0].conj().transpose(0,2,1),allchannels['RL'][0])
        checks['real_normal_condition_LR_RL_Hermitian_numerators_time']=compare(allchannels['LR'][1].conj().transpose(0,2,1),allchannels['RL'][1])
        for tent in(-1,1):
            tag=f'{side}_tent{tent}';L=sparse(a,f'tent{tent}_common_scalar_map');Lt=sparse(a,f'tent{tent}_common_scalar_map_time')
            store(arrays,tag+'_common_scalar_map',L);store(arrays,tag+'_common_scalar_map_time',Lt)
            ni,nit=norms(L,Lt,GI,GIt);arrays[tag+'_all1200_intrinsic_norm_squared']=ni;arrays[tag+'_all1200_intrinsic_norm_squared_time']=nit
            checks[f'tent{tent}_all1200_intrinsic_norms']=compare(ni,a[f'tent{tent}_all1200_intrinsic_operator_norm_squared'])
            checks[f'tent{tent}_all1200_intrinsic_norms_time']=compare(nit,a[f'tent{tent}_all1200_intrinsic_operator_norm_squared_time'])
            dh=(L@z).reshape(4,20)@gh;dht=(Lt@z).reshape(4,20)@gh
            for label,(W,Wt,GW,GWt,CV,l,r)in allchannels.items():
                n,nt=norms(L,Lt,GW,GWt);arrays[tag+'_'+label+'_all1200_norm_squared']=n;arrays[tag+'_'+label+'_all1200_norm_squared_time']=nt
                checks[f'tent{tent}_{label}_all1200_norms']=compare(n,a[f'tent{tent}_{label}_all1200_ambient_numerator_norm_squared'])
                # Independent literal weak scalar polynomial, all source
                # directions combined complex-linearly before evaluation.
                lv=vector_product(l['B'].conj().T,left,transpose=True);lt=vector_product(l['Bt'].conj().T,left,transpose=True)
                rv=vector_product(r['B'],right);rt=vector_product(r['Bt'],right)
                M=[[sum((mc(dh[c])*mc(CV[c,i,j])for c in range(4)),mp.mpc(0))for j in range(18)]for i in range(18)]
                Mt=[[sum((mc(dht[c])*mc(CV[c,i,j])for c in range(4)),mp.mpc(0))for j in range(18)]for i in range(18)]
                def weak(t):
                    return (mc(rho)+t*mc(rhot))*sum(((lv[i]+t*lt[i])*(M[i][j]+t*Mt[i][j])*(rv[j]+t*rt[j])for i in range(18)for j in range(18)),mp.mpc(0))
                derivative=mc(rhot)*sum((lv[i]*M[i][j]*rv[j]for i in range(18)for j in range(18)),mp.mpc(0))
                derivative+=mc(rho)*sum((lt[i]*M[i][j]*rv[j]+lv[i]*Mt[i][j]*rv[j]+lv[i]*M[i][j]*rt[j]for i in range(18)for j in range(18)),mp.mpc(0))
                errors=[]
                for power in(5,11,17):
                    h=mp.mpf(2)**(-power);fd=(weak(-2*h)-8*weak(-h)+8*weak(h)-weak(2*h))/(12*h)
                    errors.append(dict(step_power=-power,absolute=mp.nstr(abs(fd-derivative),30),scaled=mp.nstr(abs(fd-derivative)/max(1,abs(fd),abs(derivative)),30)))
                saved_value=np.einsum('i,ij,j->',left,np.einsum('c,cij->ij',dh,W),right)
                saved_time=np.einsum('i,ij,j->',left,np.einsum('c,cij->ij',dht,W)+np.einsum('c,cij->ij',dh,Wt),right)
                literal.append(dict(side=side,tent=tent,channel=label,coefficient_polynomial_degree=4,
                    independent_complex_common_direction_no_source_conjugation=True,value=mp.nstr(weak(0),55),time=mp.nstr(derivative,55),FD4_controls=errors,
                    saved_compact_coefficient_value=compare(saved_value,complex(weak(0))),saved_compact_coefficient_time=compare(saved_time,complex(derivative))))
        if max(v['max_entry_scaled']for v in checks.values())>2e-10:raise ArithmeticError('Weak Hamiltonian coefficient identity failed')
        records.append(dict(side=side,coordinate_time=next(z['coordinate_time']for z in meta['records']if z['side']==side),
            actual_surface_rho_L=rho,actual_surface_rho_L_time=rhot,native_intrinsic_scalar_vertex_identity=native_check,
            controls=checks,unknown_LR_factor='1/(u_L_plus*u_R_minus)',unknown_RL_factor='1/(u_L_minus*u_R_plus)',
            unknown_factor_time='-alpha*(u_Ldot/u_L+u_Rdot/u_R)',
            real_Riesz_Hermitian_mass_condition='u_L_sigma=conj(u_R_sigma) at a real branch; not assigned',
            independent_H80_operator_norm_squared_min=float(np.min(ni[1120:])),dependent_scalar_map_retained=True))
    out.mkdir(parents=True);archive=out/'actual_common1200_weak_Hamiltonian_Higgs_seam_coefficients.npz';_compressed_npz(archive,arrays)
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and name.startswith('bhsm.')and Path(p).resolve().is_relative_to(root):pin(Path(p).resolve())
    pin(Path(__file__));producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer)
    report=dict(classification='ACTION_DERIVED_SAME_REAL_COMMON1200_WEAK_HAMILTONIAN_HIGGS_SEAM',source_sha256=sha256(producer).hexdigest(),
        input_and_source_hashes=dict(sorted(pins.items())),archive=dict(name=archive.name,sha256=sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size),records=records,
        literal_MP80_same_frozen_coefficient_controls=literal,common_dimension=1200,one_sheet_carrier=384,two_eta_sheet_carrier=768,connected_angular_output=55,
        original_weak_operator='K_L,seam=-rho_L Cbar M B',Hamiltonian_output_map='W_seam=-Gamma0 K_L,seam=+rho_L Gamma0 Cbar M B',
        original_Dirac_bar_Gamma0_count=1,separate_Hamiltonian_output_Gamma0_is_not_second_Dirac_bar_normalization=True,
        original_binary64_time_Clifford_square_residual=clifford_check,original_Gamma0_entries_renormalized_or_dropped=False,
        intrinsic_surface_native_scalar_W_vertex_exactly_identified=True,full384_extension_from_original_seam_not_reduced_point_completion=True,
        scalar_term_on_original_intrinsic_surface_stratum_only=True,new_D5_bulk_Higgs_mass_added=False,new_intrinsic_kinetic_added=False,
        complete_known_all1200_operator_coefficients_and_time_evaluated=True,complex_common_source_coefficients_conjugated=False,
        same_frozen_real_primary_and_seam_epoch=True,actual_D5_history_source_normal_profile_campaigns_replayed=0,
        surface_clock='original Lorentz ell_L; no positive ell_E replacement',density_pullback='both input/output by s=sqrt(C R^3); numerator rho_L/s^2=ell_L/C',
        ambient_normal_values_and_source_jets=None,full_ambient_normalized_seam_evaluated=False,
        native_full_Dstrat_operator_or_global_coercive_transmission_domain_proved=False,delta_squared_or_H1_domain_used=False,
        physical_outgoing_energy_field_source_domain_derivative_pass=False,original_coupled_corrections=0,
        physical_Maxwell_all226_after_pass=False,physical_normalized_two_spin_state=None,physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(archive=report['archive'],max_scaled_identity=max(z['max_entry_scaled']for r in records for z in r['controls'].values()))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',default=ROOT,type=Path)
    p.add_argument('--seam-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();run(a.repository,a.seam_folder,a.output)
