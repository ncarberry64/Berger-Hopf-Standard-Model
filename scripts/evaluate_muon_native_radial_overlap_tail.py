"""Certify and evaluate the original coupled radial matching tail/contours."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_native_radial_overlap_tail import (
    radial_schur_pencil,radial_schur_application,certify_projected_radial_tail,
    radial_tail_quadrature,radial_soft_path_poles,radial_cluster_contour_residue,
    radial_detoured_soft_covector)
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,matching_folder):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    inp=Path(matching_folder);inp=inp if inp.is_absolute()else ROOT/inp
    if out.exists():raise FileExistsError('preserve previous tail applications')
    out.mkdir(parents=True)
    receipt=json.loads((inp/'result.json').read_bytes());pins=dict(receipt['input_hashes'])
    def pin(p):
        p=Path(p);p=p if p.is_absolute()else ROOT/p
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pin(inp/'result.json');archives={};records=[]
    def save(name,obj):
        arrays={}
        def pack(v,key):
            if isinstance(v,np.ndarray):arrays[key]=v;return dict(array_key=key,shape=list(v.shape))
            if isinstance(v,dict):return{k:pack(a,key+'_'+k)for k,a in v.items()}
            if isinstance(v,(tuple,list)):return[pack(a,key+'_'+str(j))for j,a in enumerate(v)]
            if isinstance(v,np.generic):return pack(v.item(),key)
            if isinstance(v,complex):return dict(real=v.real,imag=v.imag)
            return v
        rec=pack(obj,'data');p=out/name;deterministic_archive(p,arrays)
        if p.stat().st_size>10*1024**2:raise ArithmeticError('archive publication limit exceeded')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest());return rec
    for side in('incoming','outgoing'):
        file=inp/f'{side}_coupled_scalar_matching.npz';pin(file);a=np.load(file)
        if sha256(file.read_bytes()).hexdigest()!=receipt['archives'][file.name]['sha256']:
            raise RuntimeError('frozen scalar matching archive changed')
        rec=next(r for r in receipt['records']if r['kind']=='coupled_radial_matching'and r['side']==side)['record']
        pref='data_coupled_matching_';T=a[pref+'original_trace_map'];D=a[pref+'canonical_radial_dual_wall']
        pencil=radial_schur_pencil(a[pref+'original_proper_frequency_coefficients'],T.T@D,a[pref+'original_frame_rows'])
        b=rec['calibrated_external_covector_probes'][1]
        args=dict(matched_mass_action=b['matched_internal_and_external_fermion_mass_action'],
            fixed_Y=b['fixed_Y'],kinetic_residue=rec['coupled_matching']['actual_scalar_kinetic_residue'])
        cert,U=certify_projected_radial_tail(pencil,**args,precision_bits=192)
        # The exact same-coordinate reference has |tail|<=Y²/(16pi²)
        # (exp(-32)+exp(-64)/2). The following sum is widened upward;
        # no cancellation of near-equal rounded tails is claimed.
        from flint import arb,ctx
        old=ctx.prec;ctx.prec=192
        try:
            e=(-arb(32)).exp();reference=arb(args['fixed_Y'])**2/(16*arb.pi()**2)*(e+e**2/2)
            reference_upper=float(np.nextafter(float(reference.upper()),np.inf))
            subtraction_upper=float(np.nextafter(float((reference+arb(cert['reached_omitted_tail_absolute_upper'])).upper()),np.inf))
        finally:ctx.prec=old
        cert.update(same_coordinate_reference_tail_absolute_upper=reference_upper,
            same_coordinate_subtracted_tail_absolute_upper=subtraction_upper,
            near_equal_tail_cancellation_claimed=False)
        quads=[radial_tail_quadrature(pencil,**args,order=q)for q in(8,12)]
        checks=[radial_schur_application(pencil,w)for w in(.1,1.,10.,cert['omega_start_lower'])]
        poles=radial_soft_path_poles(pencil)
        roots=poles['all_omega_companion_roots'];ids=poles['positive_real_path_candidate_indices'];groups=[]
        for i in sorted(ids,key=lambda i:roots[i].real):
            if not groups or abs(roots[i].real-roots[groups[-1][0]].real)>1e-4:groups.append([int(i)])
            else:groups[-1].append(int(i))
        circles=[];contours=[]
        for group in groups:
            center=float(np.mean(roots[group].real));radius=.001
            others=np.setdiff1d(np.arange(len(roots)),group)
            separation=float(np.min(abs(roots[others]-center)))
            radius=min(radius,separation/4,center/10)
            if np.max(abs(roots[group]-center))>=radius:
                raise ArithmeticError('candidate cluster requires a larger complete circle')
            circles.append((center,radius))
            cc=[radial_cluster_contour_residue(pencil,center=center,radius=radius,**args,order=q)for q in(24,48)]
            contours.append(dict(companion_indices=np.array(group),nearest_other_root_distance=separation,
                applications=cc,weighted_residue_order_difference=cc[1]['soft_covector_cluster_residue']-cc[0]['soft_covector_cluster_residue']))
        reference=a[pref+'same_coordinate_reference_coefficients'];mu2=float(-reference[0,0,0].real/reference[2,0,0].real)
        branches=[radial_detoured_soft_covector(pencil,circles,**args,reference_mass_squared=mu2,order=q)for q in(16,24)]
        pole_record=save(f'{side}_poles_and_bypasses.npz',dict(poles=poles,cluster_circles=np.asarray(circles),
            cluster_contours=contours,detoured_applications=branches))
        action_record=save(f'{side}_exact_schur_and_tail.npz',dict(pencil=pencil,whitening_preconditioner=U,
            reconstructed_original_applications=checks,tail_quadratures=quads))
        norms=dict(omitted_tail_absolute_upper=cert['reached_omitted_tail_absolute_upper'],
            same_coordinate_subtracted_tail_upper=subtraction_upper,
            tail_value_real=float(quads[-1]['tail_covector_value'].real),
            tail_order_difference_absolute=float(abs(quads[1]['tail_covector_value']-quads[0]['tail_covector_value'])),
            candidate_cluster_count=len(circles),
            original_reaction_resolved_residual_max=float(max(np.max(abs(v['original_reaction_resolved_residual']))for v in checks)),
            lower_reached_value_real=float(branches[-1]['lower_reached_covector'].real),
            lower_reached_value_imag=float(branches[-1]['lower_reached_covector'].imag),
            upper_reached_value_imag=float(branches[-1]['upper_reached_covector'].imag),
            upper_minus_lower_imag=float(branches[-1]['upper_minus_lower'].imag),
            branch_order_difference_absolute=float(abs(branches[1]['lower_reached_covector']-branches[0]['lower_reached_covector'])))
        records.append(dict(side=side,certificate=cert,action_archive=f'{side}_exact_schur_and_tail.npz',
            action_record=action_record,pole_archive=f'{side}_poles_and_bypasses.npz',pole_record=pole_record,norms=norms))
        print(json.dumps(dict(stage='radial_tail_and_contour',side=side,**norms),sort_keys=True),flush=True)
    for name in('src/bhsm/interface/muon_native_radial_overlap_tail.py',Path(__file__),
        'tests/test_muon_native_radial_overlap_tail.py','scripts/evaluate_muon_reached_trace_action.py'):pin(name)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):
        raise RuntimeError('consumed source changed during the application')
    result=dict(classification='CERTIFIED_EXACT_STORED_PROJECTED_COUPLED_RADIAL_TAIL_WITH_EVALUATED_POLE_BYPASSES',
        input_hashes=pins,archives=archives,records=records,
        frequency_owner='raw Lorentz_forms only; proper C(z)=K_L/N+i z(B_L-B_L.T)+z² N M_L; continue once z=i omega',
        constraint_elimination='literal all64 At equations; independent left/right Schur placements; all16 named Ar frames reconstructed as reactions',
        tail_proof='Arb verified U^T sym(M-tJ-t²K)U >=(1-delta)I for all0<=t<=t32; source-directed energy bound integrated analytically',
        pole_scope='all numerical companion poles and both independent radial source residues; cluster Cauchy returns and upper/lower analytic bypasses evaluated. Pole locations/bypass quadrature are not interval-certified.',
        original_unresolved_quadrature_scope='frozen y0..32 straight-path value retained as pre-contour diagnostic; it is not a certified integral through active poles',
        local_free_Feynman_owner_is_the_same_unstable_finite_action_domain=False,
        adopted_native_Feynman_or_retarded_loop_branch_selected=False,
        fixed_Y_refitted=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='Uniform y>32 tail and pole exclusion are outward certificates for exact stored coefficients/sources only. Matrix production, continuum/angular complements, finite-to-native contour/domain and external-pole matching remain separate. Contour/order differences are numerical diagnostics, not arithmetic bounds. No principal value or infinitesimal Feynman prescription is invented for the off-shell finite pencil.')
    file=out/'result.json';file.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(result_sha256=sha256(file.read_bytes()).hexdigest(),archives=len(archives))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--matching-folder',type=Path,default=Path('artifacts/muon_native_local_overlap_matching_20261011/run_3'))
    print(json.dumps(materialize(p.parse_args().output,p.parse_args().matching_folder),sort_keys=True),flush=True)
