"""Apply the finite-cutoff Schur correction to pinned actual magnetic operators."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import argparse,ast,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_intrinsic_scalar_regulator_correction import (
    scalar_regulator_source_application,intrinsic_scalar_gaussian_embedding_contract,
)
from bhsm.interface.muon_magnetic_mixed_green import _mixed_vertices
from evaluate_muon_reached_trace_action import deterministic_archive


def source_record(path,symbols):
    data=(ROOT/path).read_bytes();tree=ast.parse(data)
    spans={n.name:dict(line=n.lineno,end_line=n.end_lineno)
           for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
           and n.name in symbols}
    if set(spans)!=set(symbols):raise ValueError('action source symbol changed')
    return dict(path=path,sha256=sha256(data).hexdigest(),symbols=spans)


def materialize(output,*,source):
    folder=Path(source);folder=folder if folder.is_absolute() else ROOT/folder
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous reduction applications')
    data=(folder/'result.json').read_bytes();md=json.loads(data)
    if md['classification']!='EVALUATED_MAGNETIC_SOURCE_DIRECTED_INTRINSIC_HIGGS_LEPTON_MIXED_GREEN_DERIVATIVE':
        raise ValueError('actual all-family mixed Green source owner required')
    hashes=dict(md['input_hashes']);hashes[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    for p,h in hashes.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed source changed: '+p)
    archives={}
    for name,info in md['array_archives'].items():
        data=(folder/name).read_bytes()
        if len(data)!=info['bytes'] or sha256(data).hexdigest()!=info['sha256']:
            raise ValueError('consumed operator archive changed: '+name)
        hashes[(folder/name).relative_to(ROOT).as_posix()]=info['sha256']
        with np.load(folder/name,allow_pickle=False) as f:archives[name]={k:f[k].copy() for k in f.files}
    arrays={};rows=[];c=md['common_cutoff_probe'];source_arrays=archives['scalar_sources.npz']
    for side in ('incoming','outgoing'):
        scalar={k:source_arrays[side+'_'+k] for k in (
            'positive_H_odd','positive_H_even','delta_positive_H_even_odd')}
        scalar['action_Gram_scalar']=next(r['action_Gram_scalar'] for r in md['records'] if r['side']==side)
        gaunt=source_arrays[side+'_gaunt_even_odd_source'];families={}
        for family in range(3):
            prefix=side+'_family_'+str(family)+'_'
            operators=archives[side+'_family_'+str(family)+'_fermion_operators.npz']
            d={k[len(prefix):]:v for k,v in operators.items()}
            B0,B1,B1H=_mixed_vertices(gaunt,source_arrays[prefix+'bare_scalar_mass_vertices'])
            d.update(mixed_vertex_n0_odd=B0,mixed_vertex_n1_Hodd=B1,mixed_vertex_n1_Heven=B1H)
            r=scalar_regulator_source_application(d,scalar,c,series_terms=md['refined_series_terms'])
            families[str(family)]=r
            for kind in ('scalar_first_reduction','finite_cutoff_correction'):
                for place in ('forward','reverse'):
                    for name,value in r[kind][place].items():
                        arrays[prefix+kind+'_'+place+'_'+name]=value
            rows.append(dict(side=side,family=family,common_cutoff_probe=c,
                scalar_first_forward_norm=float(np.linalg.norm(r['scalar_first_reduction']['forward']['total'])),
                finite_cutoff_correction_forward_norm=float(np.linalg.norm(r['finite_cutoff_correction']['forward']['total'])),
                scalar_first_reverse_norm=float(np.linalg.norm(r['scalar_first_reduction']['reverse']['total'])),
                finite_cutoff_correction_reverse_norm=float(np.linalg.norm(r['finite_cutoff_correction']['reverse']['total'])),
                maximum_input_kernel_series_tail_upper=r['maximum_input_kernel_series_tail_upper']))
        for kind in ('scalar_first_reduction','finite_cutoff_correction'):
            for place in ('forward','reverse'):
                for name in families['1'][kind][place]:
                    paired=families['1'][kind][place][name]-families['2'][kind][place][name]
                    arrays[side+'_paired_middle_minus_light_'+kind+'_'+place+'_'+name]=paired
        for place in ('forward','reverse'):
            for name in families['1']['scalar_first_reduction'][place]:
                a=arrays[side+'_paired_middle_minus_light_scalar_first_reduction_'+place+'_'+name]
                b=arrays[side+'_paired_middle_minus_light_finite_cutoff_correction_'+place+'_'+name]
                common=archives['application.npz'][side+'_paired_middle_minus_light_'+place+'_'+name+'_refined']
                arrays[side+'_reconstruction_difference_'+place+'_'+name]=a+b-common
        print(json.dumps(dict(side=side,common_cutoff_probe=c,
            paired_correction_forward_norm=float(np.linalg.norm(arrays[side+'_paired_middle_minus_light_finite_cutoff_correction_forward_total'])),
            paired_scalar_first_forward_norm=float(np.linalg.norm(arrays[side+'_paired_middle_minus_light_scalar_first_reduction_forward_total'])),
            reconstruction_difference_norm=float(np.linalg.norm(arrays[side+'_reconstruction_difference_forward_total']))),sort_keys=True),flush=True)
    citations=[source_record(p,names) for p,names in (
        ('src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',['action_composition_contract','first_variation_and_pole_gate','charged_lepton_yukawa_operator']),
        ('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',['microscopic_owner_contract']),
        ('src/bhsm/interface/muon_magnetic_open_lepton_vertex.py',['canonical_open_field_vertices']),
        ('src/bhsm/interface/muon_intrinsic_higgs_positive_green.py',['intrinsic_higgs_cell_jacobi']),
    )]
    for record in citations:hashes[record['path']]=record['sha256']
    for name in ('muon_intrinsic_scalar_regulator_correction','muon_common_cutoff_green_kernel'):
        p='src/bhsm/interface/'+name+'.py';hashes[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise RuntimeError('consumed source changed during application')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2:raise ValueError('lossless application exceeds public cap')
    result=dict(classification='EVALUATED_ACTUAL_INTRINSIC_SCALAR_SCHUR_FINITE_CUTOFF_CORRECTION',
        input_hashes=hashes,source_records=citations,records=rows,
        archive=dict(path='application.npz',sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),bytes=(out/'application.npz').stat().st_size),
        action_embedding=intrinsic_scalar_gaussian_embedding_contract(),
        kernel_difference_equations=dict(
            numerator='C2=L2(p,q;c)-exp(-cq)/(pq)',
            fermion_square='C3FFH=L3(p,pprime,q;c)-exp(-cq)/(p*pprime*q)',
            scalar_insertion='C3FHH=L3(p,q,qprime;c)-L2(q,qprime;c)/p'),
        correction_region='unreduced total proper time >=c with scalar proper time below c',
        both_square_placements_numerator_and_scalar_contacts_retained=True,
        gaussian_open_exchange_sign_applied_to_native_graph=False,
        complete_mixed_D_strat_first_second_jets_and_relative_completion_evaluated=False,
        no_action_definition_ambiguity_claim=True,physical_a_mu=None,physical_g_mu=None,
        error_scope='actual pinned finite-cell binary64 contractions and resolved kernel subtraction; exact-stored kernel series tails separate, no contraction/assembly/eigensystem/differential-image/continuum/native or Pauli enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],archive=result['archive'],records=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_magnetic_mixed_green_20261011/run_3'))
    a=p.parse_args();print(json.dumps(materialize(a.output,source=a.source),sort_keys=True))
