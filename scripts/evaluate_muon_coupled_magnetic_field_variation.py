"""Execute actual corrected magnetic deltaK on one matching joint domain."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_coupled_magnetic_field_variation import corrected_magnetic_first_field_interpolation,changing_coupled_magnetic_variation
from bhsm.interface.muon_even_coupled_temporal_field import complete_even_angular_blocks
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve every prior physical-source application')
    refs={};receipts={};arrays={}
    folders={
        'source':ROOT/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1',
        'odd':ROOT/'artifacts/muon_parent_positive_coupled_temporal_20261011/run_1',
        'even':ROOT/'artifacts/muon_even_coupled_temporal_field_20261011/run_3'}
    for name,folder in folders.items():
        p=folder/'result.json';b=p.read_bytes();r=json.loads(b);receipts[name]=r
        refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest();refs.update(r['input_hashes'])
    def load(group,name):
        p=folders[group]/name;b=p.read_bytes();r=receipts[group]
        rec=r.get('array_archives',r.get('numerical_files'))[name]
        if len(b)!=rec['bytes']or sha256(b).hexdigest()!=rec['sha256']:raise ValueError('consumed complete array changed: '+str(p))
        refs[p.relative_to(ROOT).as_posix()]=rec['sha256']
        with np.load(p,allow_pickle=False)as f:return{k:f[k]for k in f.files}
    angular=retained_full_q_angular_space(ROOT);even=complete_even_angular_blocks();records=[];files={};out.mkdir(parents=True)
    for side in ('incoming','outgoing'):
        primal,phase_array,velocity,contacts=[load('source',side+'_'+s+'.npz')for s in ('primal_and_source','phase','velocity','contacts')]
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes']);sampler=corrected_magnetic_first_field_interpolation(primal,phase_array,velocity,contacts)
        odd=load('odd',side+'_hilbert.npz');samples=load('even',side+'_samples.npz')
        eg=np.zeros((1960,1960));hg=np.zeros((560,560))
        for j,block in enumerate(even['blocks']):
            h=load('even',side+'_block_'+str(j)+'_hilbert.npz');ids=block['harmonic_indices']
            gi=(np.arange(56)[:,None]*35+ids).ravel();hi=(np.arange(16)[:,None]*35+ids).ravel()
            eg[np.ix_(gi,gi)]=h['one_form_Gram_per_kappa'];hg[np.ix_(hi,hi)]=h['ghost_Gram_per_kappa']
        app=changing_coupled_magnetic_variation(phase,angular,sampler,times=samples['quadrature_times'],weights=samples['quadrature_weights'],
            even_one_form_Gram=eg,odd_one_form_Gram=odd['one_form_Gram_per_kappa'],even_ghost_Gram=hg,odd_ghost_Gram=odd['ghost_Gram_per_kappa'],
            progress=lambda r:print(json.dumps(dict(side=side,stage='complete_magnetic_coupled_variation',**r),sort_keys=True),flush=True))
        norms={k:float(np.linalg.norm(v))for k,v in app.items()if isinstance(v,np.ndarray)}
        # Lossless angular blocks preserve every element of the full arrays.
        # A source axis/purpose is split only to retain the public file cap.
        keys=[k for k,v in app.items()if isinstance(v,np.ndarray)]
        for axis in range(3):
            for j,block in enumerate(even['blocks']):
                ie=(np.arange(60)[:,None]*35+block['harmonic_indices']).ravel()
                gi=(np.arange(56)[:,None]*35+block['harmonic_indices']).ravel()
                for purpose,selected in (('action',keys[:2]),('contacts',keys[2:5]),('Gram_weak',keys[5:])):
                    vals={k:app[k][axis][ie if app[k].shape[1]==2100 else gi]for k in selected}
                    vals['field_indices']=ie;vals['gauge_field_indices']=gi
                    p=out/(side+'_axis_'+str(axis)+'_block_'+str(j)+'_'+purpose+'.npz');deterministic_archive(p,vals)
                    if p.stat().st_size>10*1024**2:raise ValueError('complete source block exceeds public cap')
                    files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest(),arrays=sorted(vals))
        p=out/(side+'_samples.npz');deterministic_archive(p,samples);files[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
        records.append(dict(side=side,source_count=3,field_variation_shape=[3,2100,1200],norms=norms,samples=app['sample_records']))
        del app
    sources=[
        'src/bhsm/interface/muon_coupled_magnetic_field_variation.py','src/bhsm/interface/muon_coupled_gauge_magnetic_source.py',
        'src/bhsm/interface/muon_coupled_higgs_magnetic_source.py','src/bhsm/interface/muon_coupled_field_angular_images.py',
        'tests/test_muon_coupled_magnetic_field_variation.py','tests/test_muon_coupled_gauge_magnetic_source.py',Path(__file__).relative_to(ROOT).as_posix()]
    for p in sources:refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same source/action input changed during full magnetic variation')
    r=dict(classification='EVALUATED_SAME_CHANGING_COUPLED_FIELD_MAGNETIC_ACTION_AND_GRAM_VARIATION',input_hashes=refs,array_archives=files,records=records,
        field_domain='complete even2100/odd1200 gauge, dependent DG gauge/H and independent H; exact angular spectators only reorganize all coordinates',
        source_domain='actual3 physical e-normalized magnetic first fields of corrected chronological full488 response; n3 value/rate exactlyzero guarded',
        source_clock='futureu in botharms; incomingcoordinate u-L and childcoordinate u; algebraic At cubic and SAME derivative, dynamic/wall Hermite values+rates',
        normalization='MAXWELL_TO_CAP once on YM/Lorenz; real2Re2*w_mu/V on intrinsic; source electriccharge already included once',
        complete_YM_curvature_contact_and_DH_offshell_contact=True,
        Lorenz_fixing_differentiated_after_complete_time_radial_weak_integration=True,
        ghost_Gram_source_variation_zero_reason='eta scalar Gram independent of A at fixed geometry; DG image and FP form remain source dependent',
        independent_sector_inverses_used=False,new_Rxi_mass_or_statistical_factor_or_cutoff_selected=False,
        physical_P_strat_Wick_graded_Sigma_or_LSZ_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 same12time/allradial weak integration, inherited Gaunt and saved-field interpolation; no outward interpolation/action/eigensolver/continuum or physical readout error certificate')
    (out/'result.json').write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=r['classification'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(materialize(p.parse_args().output),sort_keys=True))
