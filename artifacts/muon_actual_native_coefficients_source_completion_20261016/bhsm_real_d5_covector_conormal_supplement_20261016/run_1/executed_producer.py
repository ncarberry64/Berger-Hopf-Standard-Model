"""Actual fixed-material-face conormal contacts for the frozen covector binding.

Consumes saved real coefficients and pure declared trial functions only. The
positive coframe normal, Lorentz wall clock, and outgoing domain are distinct.
No D5/action/profile/history calculation or physical-domain choice is made.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PRIMARY='artifacts/muon_real_coupled_open_operator_20261016/source_first_run_1'


def execute(binding_folder,insertion_folder,output):
    base,ins,out=map(lambda p:Path(p).resolve(),(binding_folder,insertion_folder,output))
    out.mkdir(parents=True,exist_ok=False)
    producer=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(producer);pins={}
    def pin(p,expected=None):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('Frozen operand changed: '+str(p))
        pins[p.relative_to(ROOT).as_posix()if p.is_relative_to(ROOT)else str(p)]=h
        return p
    def load(p,expected=None):
        p=pin(p,expected)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def scale(s,v):return np.asarray(s).reshape((-1,)+(1,)*(v.ndim-1))*v
    def compare(a,b):return float(np.max(abs(a-b)/np.maximum(1,np.maximum(abs(a),abs(b))),initial=0))
    sys.path.insert(0,str(ROOT/'src'))
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    bm=load(base/'result.json','4a159edd6d1c5c2d392c1dfe69b70b1c802a8b2bd385df1483fac5d9297a8779')
    ba=load(base/'actual_full1920_positive_covector_binding.npz',bm['archive']['sha256'])
    if not bm['real_positive_coframe_same_covector_connection_premise']or bm['physical_E_dictionary']:
        raise ValueError('Exact scoped positive real-coframe binding required')
    primary=load(PRIMARY+'/application.npz','7da8ddd5fa4bda397aa6a2d50e845338a3ef92fb3f0e837a5a6d0d166915e177')
    im=load(ins/'result.json')
    pin(ins/'executed_producer.py','4a9ea459bb95a3f470562098c9d82509c982677997542f86ed3626f968e9ded3')
    tp=pin('audits/bhsm_real_full_d5_source_first_application_20261016.py','c96814490c43faa21b35a4b2f14926d48929fa60cc6f2af774a148225dd65aa9')
    spec=importlib.util.spec_from_file_location('frozen_covector_boundary_trial_owner',tp)
    trialowner=importlib.util.module_from_spec(spec);spec.loader.exec_module(trialowner)
    full=full_d5_localized_lepton_trace();arrays={};records=[]
    for side in('incoming','outgoing'):
        c={k[len(side+'_input_'):]:v for k,v in primary.items()if k.startswith(side+'_input_')}
        N,C,R,z=(c[k]for k in('lapse','radial_coframe','radius','coordinate_shift'))
        Nx,Cx,Rx,zx=(c[k+'_first'][0]for k in('lapse','radial_coframe','radius','coordinate_shift'))
        if any(np.any(a.imag!=0)for a in(N,C,R,z,Nx,Cx,Rx,zx)):
            raise ValueError('The adjoint/current derivative is the supplied REAL time axis')
        delta,deltax=ba[side+'_delta_scalar_body'],ba[side+'_delta_scalar_body_first'][0]
        mu,mux=ba[side+'_fermion_geometric_density'],ba[side+'_fermion_geometric_density_first'][0]
        s,sx=ba[side+'_input_output_density_isometry'],ba[side+'_input_output_density_isometry_first'][0]
        ell=np.sqrt(N*N+C*C*z*z);ellx=(N*Nx+C*Cx*z*z+C*C*z*zx)/ell
        invnormal=ell/(N*C);invnormalx=invnormal*(ellx/ell-Nx/N-Cx/C)
        surface=ell*R**3;surfacex=surface*(ellx/ell+3*Rx/R)
        temporal=mu/N;temporalx=mux/N-mu*Nx/N**2
        traceweight=ell/C;traceweightx=ellx/C-ell*Cx/C**2
        for name,value in dict(positive_levelset_clock=ell,positive_levelset_clock_time=ellx,
                positive_coordinate_normal_norm=invnormal,positive_coordinate_normal_norm_time=invnormalx,
                positive_levelset_density=surface,positive_levelset_density_time=surfacex,
                density_isometric_surface_weight=traceweight,density_isometric_surface_weight_time=traceweightx,
                temporal_conormal_primitive=temporal,temporal_conormal_primitive_time=temporalx).items():arrays[side+'_'+name]=value
        tr=trialowner.declared_trials(c['radial_points'],1920)
        v,vx=(tr[j].reshape(5,3,2,4,16,5,3)for j in(0,3))
        for eps in(-1,1):
            tag=f'{side}_eta{eps}';name=tag+'_compact_application.npz'
            receipt=im['archives'][name];h=receipt['sha256']if isinstance(receipt,dict)else receipt
            old=load(ins/name,h);p=tag+'_recovered_'
            if not np.array_equal(v[:4],old[p+'value'])or not np.array_equal(vx[:4],old[p+'value_time']):
                raise ValueError('The wall extension must use exactly the declared saved trial functions')
            alpha=np.array([full['gamma5D_'+b][0]@full['gamma5D_'+b][4]for b in('particle','conjugate')])
            I=np.eye(4,dtype=complex)
            betad=-z[:,None,None,None]/N[:,None,None,None]*I+1j*eps*alpha[None]/C[:,None,None,None]
            betadx=(-zx/N+z*Nx/N**2)[:,None,None,None]*I-1j*eps*alpha[None]*(Cx/C**2)[:,None,None,None]
            act=lambda a,u:np.einsum('qbst,qfbtion->qfbsion',a,u,optimize=True)
            contact=scale(delta,v);contactx=scale(deltax,v)+scale(delta,vx)
            radial=scale(mu,act(betad,contact))
            radialx=scale(mux,act(betad,contact))+scale(mu,act(betadx,contact)+act(betad,contactx))
            timeflux=scale(temporal,contact);timefluxx=scale(temporalx,contact)+scale(temporal,contactx)
            unit=scale(1/invnormal,act(betad,contact))
            unitx=scale(1/invnormal,act(betadx,contact)+act(betad,contactx))-scale(invnormalx/invnormal,unit)
            surface_identity=compare(radial,scale(surface,unit))
            surface_first_identity=compare(radialx,scale(surfacex,unit)+scale(surface,unitx))
            isometry=compare(radial,scale(s,scale(N,act(betad,scale(s,contact)))))
            isometryx=compare(radialx,scale(sx,scale(N,act(betad,scale(s,contact))))+
                scale(s,scale(Nx,act(betad,scale(s,contact)))+scale(N,act(betadx,scale(s,contact))+
                act(betad,scale(sx,contact)+scale(s,contactx)))))
            for key,a in dict(radial_conormal_adjoint_principal=betad,radial_conormal_adjoint_principal_time=betadx,
                    radial_conormal_density_factor=mu[:,None,None,None]*betad,
                    radial_conormal_density_factor_time=mux[:,None,None,None]*betad+mu[:,None,None,None]*betadx,
                    radial_contact_on_declared_trial=radial,radial_contact_on_declared_trial_time=radialx,
                    temporal_contact_on_declared_trial=timeflux,temporal_contact_on_declared_trial_time=timefluxx,
                    unit_normal_contact_on_declared_trial=unit,unit_normal_contact_on_declared_trial_time=unitx,
                    wall_radial_contact=radial[-1:],wall_radial_contact_time=radialx[-1:],
                    wall_temporal_contact=timeflux[-1:],wall_temporal_contact_time=timefluxx[-1:]).items():arrays[tag+'_'+key]=a
            # Independent MP70 literal derivative of the complete actual WALL
            # spin-vector product, not a derivative of the assembled formula.
            mp.mp.dps=70
            m=lambda a:mp.mpc(float(np.real(a)),float(np.imag(a)))
            wall=4;branch=0;sample=v[wall,0,branch,:,0,0,0];samplex=vx[wall,0,branch,:,0,0,0]
            G=mp.matrix([[m(q)for q in row]for row in alpha[branch]])
            def literal(x):
                val=lambda key:m(c[key][wall])+x*m(c[key+'_first'][0,wall])
                n,cr,zz,f,ft,fr=(val(k)for k in('lapse','radial_coframe','coordinate_shift','eta_profile','eta_profile_coordinate_time','eta_profile_radial'))
                r=val('radius');density=n*cr*r**3
                d=-(1+mp.j)*(ft-zz*fr)/n*mp.cot(f)
                B=-zz/n*mp.eye(4)+mp.j*eps*G/cr
                return density*B*(d*mp.matrix([m(sample[i])+x*m(samplex[i])for i in range(4)]))
            lit=literal(mp.mpf(0));litx=mp.diff(literal,mp.mpf(0))
            actual=radial[wall,0,branch,:,0,0,0];actualx=radialx[wall,0,branch,:,0,0,0]
            mpvalue=max(float(abs(m(actual[j])-lit[j])/max(1,abs(lit[j])))for j in range(4))
            mpfirst=max(float(abs(m(actualx[j])-litx[j])/max(1,abs(litx[j])))for j in range(4))
            if max(surface_identity,surface_first_identity,isometry,isometryx,mpvalue,mpfirst)>2e-10:
                raise ArithmeticError('Actual positive conormal contact identity failed')
            records.append(dict(side=side,eta_orientation=eps,wall_radial_contact_norm=float(np.linalg.norm(radial[-1])),
                wall_radial_contact_time_norm=float(np.linalg.norm(radialx[-1])),
                wall_temporal_contact_norm=float(np.linalg.norm(timeflux[-1])),wall_temporal_contact_time_norm=float(np.linalg.norm(timefluxx[-1])),
                positive_surface_identity_scaled=surface_identity,positive_surface_identity_first_scaled=surface_first_identity,
                density_isometry_scaled=isometry,density_isometry_first_scaled=isometryx,
                independent_actual_MP70_wall_value_scaled=mpvalue,independent_actual_MP70_wall_time_scaled=mpfirst,
                exact_core_trial_epoch_identity=True))
    archive=out/'actual_covector_positive_conormal_contacts.npz';_compressed_npz(archive,arrays)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):pin(Path(p).resolve())
    pin(Path(__file__))
    report=dict(classification='ACTUAL_REAL_POSITIVE_COVECTOR_FIXED_MATERIAL_CONORMAL_CONTACT_SUPPLEMENT',
        producer_sha256=sha256(producer).hexdigest(),input_and_source_sha256=dict(sorted(pins.items())),
        archive=dict(name=archive.name,bytes=archive.stat().st_size,sha256=sha256(archive.read_bytes()).hexdigest()),records=records,
        positive_real_coframe_same_covector_premise=True,actual_wall_trial_extension_checked=True,
        material_wall_coordinate_fixed=True,extra_wall_speed_added=False,Lorentz_surface_clock_reused=False,
        unsquared_Green_principal_changed=False,full_native_wall_conormal_or_domain_evaluated=False,
        outgoing_domain_or_physical_energy_field_derivative_or_moment=False,original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(records),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--binding-folder',required=True,type=Path)
    p.add_argument('--insertion-folder',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    try:execute(a.binding_folder,a.insertion_folder,a.output)
    except Exception as e:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),
            source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
