"""Evaluate complete reached direct+chronological-mean cutoff partial and return."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from flint import arb,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_magnetic_full_cutoff_contact import (
    magnetic_cutoff_even_y2_partial,enclosed_source_return_cutoff_partial)
from evaluate_muon_reached_trace_action import deterministic_archive


def read_packet(path,receipt,archive,classification):
    folder=ROOT/path;r=json.loads((folder/receipt).read_bytes())
    if r['classification']!=classification:raise ValueError('same evaluated producer required')
    hashes=dict(r['input_hashes'])
    for p,h in hashes.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
    h=sha256((folder/archive).read_bytes()).hexdigest()
    if h!=r['archive']['sha256']:raise ValueError('evaluated archive changed')
    hashes[(folder/archive).relative_to(ROOT).as_posix()]=h
    hashes[(folder/receipt).relative_to(ROOT).as_posix()]=sha256((folder/receipt).read_bytes()).hexdigest()
    with np.load(folder/archive,allow_pickle=False) as f:data={k:f[k].copy() for k in f.files}
    return r,data,hashes


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    direct,da,refs=read_packet('artifacts/muon_magnetic_native_source_heat_20261011/run_1','source_heat.json','source_heat.npz',
        'EVALUATED_ACTIVE_MAGNETIC_GAUGE_PLUS_H_SAME_CELL_HEAT_SOURCE_PAIR')
    mean,ma,mh=read_packet('artifacts/muon_magnetic_cutoff_mean_contact_20261011/run_1','result.json','application.npz',
        'EVALUATED_EXPLICIT_CUTOFF_DERIVATIVE_OF_TRUE_BIRTH_CHRONOLOGICAL_MEAN_HEAT')
    returned,ra,rh=read_packet('artifacts/muon_chronological_native_return_20261011/run_3','result.json','application.npz',
        'EVALUATED_SAME_ACTION_MAGNETIC_NATIVE_RETURN_WITH_TRUE_BIRTH_CHRONOLOGICAL_MEAN')
    for more in (mh,rh):
        for p,h in more.items():
            if p in refs and refs[p]!=h:raise ValueError('different background/source owners')
            refs[p]=h
    arrays={};rows=[]
    for side in ('incoming','outgoing'):
        poly=dict(n0_pencil=tuple(da[side+'_n0_pencil_'+str(i)] for i in range(3)),
            contact=tuple(da[side+'_contact_'+str(i)] for i in range(3)),shells={})
        for n in ('1','3'):
            stem=side+'_shells_'+n
            poly['shells'][n]=dict(pencil=tuple(da[stem+'_pencil_'+str(i)] for i in range(3)),
                first_source=tuple(da[stem+'_first_source_'+str(i)] for i in range(3)))
        for row in (r for r in mean['records'] if r['side']==side):
            c=row['cutoff_probe'];label=side+'_q_'+str(row['q_probe']).replace('.','p')
            calculated=magnetic_cutoff_even_y2_partial(poly,c)
            refined=magnetic_cutoff_even_y2_partial(poly,c,contour_radius=32768.,contour_order=64,lag_order=96)
            d=calculated['paired_middle_minus_light_partial'];df=refined['paired_middle_minus_light_partial']
            m=ma[label+'_partial_cutoff_mean_contact_center'];ml=ma[label+'_partial_cutoff_mean_contact_lower'];mu=ma[label+'_partial_cutoff_mean_contact_upper']
            dl=np.zeros((3,3));du=dl.copy()
            with ctx.workprec(192):
                for i in range(3):
                    for j in range(3):
                        a,b=arb(float(ml[i,j])),arb(float(mu[i,j]))
                        value=(arb(float(d['available_source_pair'][i,j].real))+(a+b)/2+arb(0,(b-a)/2))/2
                        if not value.is_zero():
                            dl[i,j]=np.nextafter(float(value.lower()),-np.inf)
                            du[i,j]=np.nextafter(float(value.upper()),np.inf)
            di=d['available_source_pair'][:3,:3].imag/2
            a=enclosed_source_return_cutoff_partial(ra[side+'_bare_source_action'][:3,:3],
                ra[label+'_applied_native_real_lower'][:3,:3],ra[label+'_applied_native_real_upper'][:3,:3],
                ra[label+'_applied_native_imaginary'][:3,:3],dl,du,di)
            for name,value in d.items():arrays[label+'_direct_partial_'+name]=value
            arrays[label+'_graded_full_partial']=(d['available_source_pair']+m)/2
            arrays[label+'_graded_full_partial_real_lower']=dl;arrays[label+'_graded_full_partial_real_upper']=du
            arrays[label+'_graded_full_partial_imaginary']=di
            for name,value in a.items():
                if isinstance(value,np.ndarray):arrays[label+'_'+name]=value
            z=dict(side=side,q_probe=row['q_probe'],cutoff_probe=c,
                direct_square_contact_partial_trace=float(np.trace(d['source_square_contact']).real),
                first_ordered_partial_trace=float(np.trace(d['ordered_two_insertion']).real),
                opposite_ordered_partial_trace=float(np.trace(d['opposite_order_two_insertion']).real),
                ungraded_direct_partial_trace=float(np.trace(d['available_source_pair']).real),
                graded_mean_partial_trace=float(np.trace(m).real/2),
                graded_full_partial_trace=float(np.trace(arrays[label+'_graded_full_partial']).real),
                graded_full_partial_norm=float(np.linalg.norm(arrays[label+'_graded_full_partial'])),
                direct_contour_lag_refinement_norm=float(np.linalg.norm(d['available_source_pair']-df['available_source_pair'])),
                source_return_cutoff_partial_norm=float(np.linalg.norm(a['source_return_cutoff_partial'])),
                differentiated_source_equation_residual_upper=a['differentiated_source_equation_residual_upper'])
            rows.append(z);print(json.dumps(z,sort_keys=True),flush=True)
    for name in ('muon_magnetic_full_cutoff_contact','muon_magnetic_cell_source_heat','muon_magnetic_cutoff_mean_contact'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    receipt=dict(classification='EVALUATED_SAME_BACKGROUND_DIRECT_MEAN_AND_SOURCE_RETURN_CUTOFF_PARTIAL',
        input_hashes=refs,archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,
        sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),records=rows,
        direct_contact_and_both_ordered_insertions_and_chronological_mean_included=True,
        partial_at_fixed_actual_fields_source_mean_and_bare_action=True,
        missing_total_derivatives='mean_c, source/field/domain/Gram motion and bare action gamma(c) must be supplied by the same physical formation/response solve',
        same_fermion_statistics_factor_applied_once=.5,
        source_return_promoted_to_quantum_photon_Green=False,
        complete_overlap_subtracted_Pauli_cutoff_cancellation_claimed=False,
        error_scope='Arb192 exact stored source/mean/inverse interval algebra only; direct cutoff target binary assembly, contour/eigen rounding, mean/target formation, higher Y, continuum, relative completion and physical Pauli matching excluded')
    (out/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=receipt['classification'],archive=receipt['archive'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
