"""Bind observed finite radial stabilization; no exterior or continuum gate."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import sys
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import numpy as np


def run(repository,base,output):
    root,base,out=map(lambda p:Path(p).resolve(),(repository,base,output))
    if out.exists():raise FileExistsError(out)
    pins={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def field(z,key):return z[key+'_high']+z[key+'_low']
    def metrics(a,b):
        denominator=max(np.linalg.norm(a),np.linalg.norm(b))
        return dict(absolute_max=float(np.max(abs(b-a))),difference_norm=float(np.linalg.norm(b-a)),
                    relative=float(np.linalg.norm(b-a)/denominator)if denominator else 0.,
                    zero_denominator=bool(denominator==0),finer_norm=float(np.linalg.norm(b)))
    def exact_mid(z,p):
        values=[]
        for part in ('real','imag'):
            m=z[p+'_'+part+'_mid_mantissa'].astype(float)
            values.append(np.ldexp(m,z[p+'_'+part+'_mid_exponent'].astype(int)))
        return values[0]+1j*values[1]
    def coefficient(order,repeat):return base/('coefficients_extension_run_'+str(repeat)if order==192 else 'coefficients_run_'+str(repeat))/f'order{order}'
    repeat_pairs=[]
    for order in (64,96,128,192):
        a,b=coefficient(order,1),coefficient(order,2)
        files=[f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz'for j in range(2)]
        if order!=64:files+=['result.json']
        hashes={}
        for name in files:
            pa,pb=a/name,b/name
            if pa.read_bytes()!=pb.read_bytes():raise ValueError('Independent coefficient repeat differs: '+str(pa))
            hashes[name]=sha256(pa.read_bytes()).hexdigest()
        repeat_pairs.append(dict(kind='actual_coefficient_integration',order=order,left=str(a),right=str(b),files=hashes))
    for order in (128,192):
        for role in ('reduced','field','lepton'):
            a,b=base/f'order{order}_{role}_run_1',base/f'order{order}_{role}_run_{3 if role=="lepton"else 2}'
            names=sorted(p.name for p in a.iterdir()if p.is_file())
            if names!=sorted(p.name for p in b.iterdir()if p.is_file()):raise ValueError('Independent repeat file sets differ')
            hashes={}
            for name in names:
                if (a/name).read_bytes()!=(b/name).read_bytes():raise ValueError('Independent response repeat differs: '+str(a/name))
                hashes[name]=sha256((a/name).read_bytes()).hexdigest()
            repeat_pairs.append(dict(kind='actual_'+role+'_evaluation',order=order,left=str(a),right=str(b),files=hashes))
    baseline48=[]
    oldfolder=root/'artifacts/muon_angular_retarded_polynomial_20261015/coefficients/coefficients_run_1'
    for j in range(2):
        name=f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz'
        old,new=read(oldfolder/name),read(base/'coefficients_run_1/order48'/name)
        if set(old)!=set(new):raise ValueError('48-point reproduction changed array keys')
        for k in old:
            if old[k].dtype!=new[k].dtype or old[k].shape!=new[k].shape or old[k].tobytes()!=new[k].tobytes():
                raise ValueError('48-point reproduction changed array bytes: '+k)
        baseline48.append(dict(stage=j,all_array_payload_bytes_identical=True,
            zip_archive_bytes_identical=(oldfolder/name).read_bytes()==(base/'coefficients_run_1/order48'/name).read_bytes(),
            scope='Array payload identity; ZIP entry ordering/metadata are not required to match the historical container.'))
    controls=[]
    for lo,hi in ((64,96),(96,128),(128,192)):
        coef=[]
        for j in range(2):
            a=read(coefficient(lo,1)/f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz')
            b=read(coefficient(hi,1)/f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz')
            # All source and coordinate operands are held fixed, even the tiny terms.
            for k in ('raw268','actual_raw_coordinate_time','coordinate_time','coordinate_step','Q','Q_coordinate_time','interior_field_lift',
                      'named_wall_lift','wall_and_frame_rows','wall_value_map','frame_rows'):
                if not np.array_equal(a[k],b[k]):raise ValueError('Refinement changed a held operand: '+k)
            coef.append(dict(stage=j,forms={k:metrics(a[k],b[k])for k in ('M','B_forward','B_reverse','K')}))
        aroot,broot=base/f'order{lo}_field_run_1',base/f'order{hi}_field_run_1'
        samples=[]
        for p in sorted(aroot.glob('cell_*_one_sided_node.npz'))+sorted(aroot.glob('cell_*_same_stage_retarded_n1_midpoint.npz')):
            a,b=read(p),read(broot/p.name)
            sample={k:metrics(field(a,k),field(b,k))for k in ('actual_total_field336','free_position196','free_momentum196')}
            if 'actual_total_coordinate_rate336_high'in a:sample['actual_total_coordinate_rate336']=metrics(field(a,'actual_total_coordinate_rate336'),field(b,'actual_total_coordinate_rate336'))
            for name,ids in (('At64',slice(0,64)),('gauge256',slice(64,320)),('natural_H16',slice(320,336))):
                sample[name]=metrics(field(a,'actual_total_field336')[ids],field(b,'actual_total_field336')[ids])
            samples.append(dict(file=p.name,metrics=sample))
        polynomials=[]
        for piece in range(3):
            a=read(aroot/f'piece_{piece:03d}_certified_canonical_polynomial_and_source.npz')
            b=read(broot/f'piece_{piece:03d}_certified_canonical_polynomial_and_source.npz')
            prefixes=sorted(k.rsplit('_real_mid_mantissa',1)[0]for k in a if k.startswith('canonical_shifted_coefficient_')and k.endswith('_real_mid_mantissa'))
            finer_prefixes=sorted(k.rsplit('_real_mid_mantissa',1)[0]for k in b if k.startswith('canonical_shifted_coefficient_')and k.endswith('_real_mid_mantissa'))
            if prefixes!=finer_prefixes:raise ValueError('Canonical polynomial coefficient sets differ; compare the full zero-padded union before admission')
            if not np.array_equal(a['sigma_bounds'],b['sigma_bounds']):raise ValueError('Canonical polynomial piece parameter bounds differ')
            wa=read(aroot/f'piece_{piece:03d}_certified_wall96_polynomial.npz')
            wb=read(broot/f'piece_{piece:03d}_certified_wall96_polynomial.npz')
            for key in ('sigma_bounds','coordinate_bounds','stage'):
                if not np.array_equal(wa[key],wb[key]):raise ValueError('Physical coordinate bounds of radial polynomial pieces differ: '+key)
            aa=np.array([exact_mid(a,p)for p in prefixes]);bb=np.array([exact_mid(b,p)for p in prefixes])
            polynomials.append(dict(piece=piece,shifted_w_polynomial_coefficients=metrics(aa,bb),
                canonical_start392=metrics(field(a,'canonical_start392'),field(b,'canonical_start392')),
                canonical_end392=metrics(field(a,'canonical_end392'),field(b,'canonical_end392')),
                shifted_w_scope='w=z-B1Q. Coefficients are compared in this explicitly shifted chart; actual z endpoints and full336 samples are reported separately.'))
        a=read(base/f'order{lo}_lepton_run_1/finite_polynomial_angular_response.npz')
        b=read(base/f'order{hi}_lepton_run_1/finite_polynomial_angular_response.npz')
        lepton={k:metrics(a[k],b[k])for k in a if k!='proper_duration'}
        controls.append(dict(lower=lo,higher=hi,coefficient_forms=coef,field_samples=samples,canonical_polynomials=polynomials,
            angular_lepton=lepton,max_full336_field_relative=max(s['metrics']['actual_total_field336']['relative']for s in samples),
            max_full336_rate_relative=max(s['metrics'].get('actual_total_coordinate_rate336',{'relative':0})['relative']for s in samples),
            max_canonical_endpoint_relative=max(p[k]['relative']for p in polynomials for k in ('canonical_start392','canonical_end392')),
            max_shifted_polynomial_coefficient_relative=max(p['shifted_w_polynomial_coefficients']['relative']for p in polynomials)))
    baseline=root/'artifacts/muon_angular_retarded_polynomial_20261015/coefficients/coefficients_run_1/result.json'
    providers=read(baseline)['input_hashes'];verified={}
    for name,digest in providers.items():
        p=Path(name);p=p if p.is_absolute()else root/p
        if sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Original owner/provider changed: '+str(p))
        verified[str(p)]=digest
    for name in ('bhsm_muon_same_epoch_n1_radial_quadrature_20261015.py','bhsm_muon_radial_response_orchestrator_20261015.py',
                 'bhsm_muon_radial_response_binding_20261015.py'):
        p=Path(__file__).parent/name;verified[str(p)]=sha256(p.read_bytes()).hexdigest()
    for name in ('bhsm_muon_same_stage_n1_reduced_sources_20261015.py','bhsm_muon_shifted_polynomial_retarded_n1_20261015.py',
                 'bhsm_polynomial_angular_retarded_lepton_20261015.py','bhsm_finite_angular_retarded_lepton_20261015.py',
                 'bhsm_exact_action_balls.py','bhsm_baton_zoo_exact_acb_packets.py'):
        p=root/'audits'/name;verified[str(p)]=sha256(p.read_bytes()).hexdigest()
    summaries={str(q):dict(field=read(base/f'order{q}_field_run_1/result.json'),lepton=read(base/f'order{q}_lepton_run_1/result.json'))for q in (64,96,128,192)}
    # Byte hashes are rechecked at the end, after all numerical comparisons.
    for p,h in pins.items():
        if sha256(Path(p).read_bytes()).hexdigest()!=h:raise ValueError('Input changed during comparison')
    for p,h in verified.items():
        if sha256(Path(p).read_bytes()).hexdigest()!=h:raise ValueError('Provider changed during comparison')
    finest=controls[-1]
    observed=max(finest['max_full336_field_relative'],finest['max_full336_rate_relative'],
        finest['max_canonical_endpoint_relative'],finest['max_shifted_polynomial_coefficient_relative'])
    result=dict(classification='OBSERVED_SAME_FROZEN_BASIS_RADIAL_QUADRATURE_STABILIZATION_OF_PROPAGATED_WEAK_FIELD',
        baseline48_array_reproduction=baseline48,comparisons=controls,repeat_pairs=repeat_pairs,input_hashes=pins,verified_original_inputs_and_providers=verified,
        original_336_sample_rows={q:v['field']['original_row_upper_bounds']for q,v in summaries.items()},
        finite_lepton_checks={q:dict(
            finite_B_difference_max=max(c['relative_B_difference']for c in v['lepton']['finite_B_difference_checks']),
            quadrature_difference_max=max(max(c['H_relative'],c['gauge_relative'])for c in v['lepton']['quadrature_checks']),
            temporal_E_product_rule_relative=v['lepton']['temporal_E_product_rule_relative'],
            gauge_response_norm=v['lepton']['gauge_response_norm'],
            nonzero_natural_H_response_norm=v['lepton']['nonzero_natural_H_response_norm'])for q,v in summaries.items()},
        observed128_to192_all_reported_field_rate_canonical_relative_max=observed,
        observed_finite_relative_stabilization_target=2e-10,observed_finite_relative_stabilization_pass=bool(observed<=2e-10),
        quadrature_comparison_is_outward_or_continuum_error_bound=False,
        radial_Galerkin_basis_refinement_or_physical_exterior_convergence_established=False,
        prescribed_wall_equality_not_used_as_interior_convergence_proof=True,
        source_D5_background_profile_history_canonical_pairing_campaigns_restarted=False,
        actual_physical_outgoing_derivative_passed=False,physical_two_spin_normalization=None,
        physical_magnetic_moment=None,coupled_matching_corrections_applied=0,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(out.read_bytes()).hexdigest(),maximum_observed_relative=observed,
        controls=[{k:v for k,v in c.items()if k.startswith('max_')}for c in controls])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--base',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.base,a.output)
