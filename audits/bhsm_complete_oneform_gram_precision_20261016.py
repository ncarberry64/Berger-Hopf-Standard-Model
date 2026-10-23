"""Complete the same finite one-form Gram from evaluated MP coefficient blocks.

No settled B solve is repeated. The high-precision radial difference bound
comes from all-entry unrounded component comparisons, not rounded identity.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
from scipy import sparse

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_changing_lorenz_tensor_precision_20261016 as tensor
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def read_component(folder):
    folder=Path(folder)
    report=json.loads((folder/'result.json').read_bytes())
    return folder,report,sha256((folder/'result.json').read_bytes()).hexdigest()


def execute(values,ordinary,output):
    out=Path(output)
    if out.exists():raise FileExistsError(out)
    vf,v,vh=read_component(values);of,o,oh=read_component(ordinary)
    assert v['classification']=='MP_SAME_AFFINE_REAL_CELL_COEFFICIENT_AND_LORENZ_VALUES'
    assert o['classification']=='MP_ORDINARY_COVECTOR_GRAM_ON_SAME_AFFINE_REAL_CELL'
    assert v['quadrature_rule_mode']=='mp' and v['anchored_response_order']==96
    assert v['temporal_order_per_half']==6
    assert v['coupled_corrections']==o['coupled_matching_corrections_applied']==0
    pins={}
    for report in (v,o):
        for rel,h in report['source_and_owner_sha256'].items():
            if rel in pins:assert pins[rel]==h,rel
            pins[rel]=h
    assert sha256((of/'ordinary_Gram.npz').read_bytes()).hexdigest()==o['numerical_sha256']
    arrays,records={},[]
    with np.load(of/'ordinary_Gram.npz',allow_pickle=False)as z:
        for side in ('incoming','outgoing'):
            assert [r['radial_order'] for r in v['records'] if r['side']==side]==[32,64,128]
            assert [r['radial_order'] for r in o['records'] if r['side']==side]==[64,128]
            previous=None
            for q in (64,128):
                vr=next(r for r in v['records'] if r['side']==side and r['radial_order']==q)
                gr=next(r for r in o['records'] if r['side']==side and r['radial_order']==q)
                assert gr['temporal_order_per_half']==6 and gr['anchored_response_order']==96
                assert gr['exact_identity_factor_dimension']==80 and gr['identity_internal_dimension']==4 and gr['identity_harmonic_dimension']==20
                p=vf/f'{side}_radial{q}/forms.npz'
                assert sha256(p.read_bytes()).hexdigest()==vr['numerical_sha256']
                with np.load(p,allow_pickle=False)as a:B=tensor.load_matrix(a,'B')
                assert B.shape==(320,1200) and np.array_equal(B[:,1120:],np.zeros((320,80)))
                g=z[f'{side}_radial{q}_ordinary_Gram10']
                assert g.shape==(10,10)
                Goo=sparse.kron(sparse.csr_matrix(g),sparse.eye(80),format='csr')
                Bord=sparse.csr_matrix(B[:,:800]);Bghost=sparse.csr_matrix(B[:,800:1120])
                full=sparse.bmat([[Goo,Bord.T],[Bord,Bghost]],format='csr')
                tensor.save_matrix(arrays,f'{side}_radial{q}_one_form_Gram',full.toarray())
                record=dict(side=side,radial_order=q,complete_one_form_dimension=1120,
                    source_B_numerical_sha256=vr['numerical_sha256'],
                    scalar80_not_part_of_this_Gram=True,identity80_is_Kronecker_factor_not_multiplicity=True,
                    rounded_symmetry_defect=float(sparse.linalg.norm(full-full.T)))
                if previous is not None:
                    # All entries of the four blocks have exactly the same
                    # denominator as their parent component comparisons.
                    b=vr['full_unrounded_MP_adjacent_rule_comparisons']['B']
                    c=gr['full_unrounded_MP_adjacent_rule']
                    with mp.workdps(80):
                        reported=[mp.mpf(b['max_entry_scaled']),mp.mpf(c['max_entry_scaled'])]
                        # Allow the 65-significant-digit report serialization
                        # generously; this is not an interval error enclosure
                        # of the underlying MP coefficient/quadrature solve.
                        bound=max(x+abs(x)*mp.mpf('1e-62') for x in reported)
                    record.update(all_entry_unrounded_radial_scaled_upper=mp.nstr(bound,65),
                        adjacent_orders_explicitly_guarded=[64,128],
                        bound_scope='numerical MP80 arithmetic comparison plus serialized-decimal margin; not an outward interval coefficient or continuum error certificate',
                        bound_derivation='max(all-entry B bound, all100-entry Goo10 bound); exact transpose, subblocks and I80 lift preserve entrywise scaling',
                        component_bound_below_scaled_2e_minus10=bound<=mp.mpf('2e-10'),
                        rounded_full_matrix_comparison=tensor.compare(previous,full.toarray()))
                records.append(record);previous=full.toarray()
    out.mkdir(parents=True)
    _compressed_npz(out/'complete_one_form_Gram.npz',arrays)
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for rel,h in pins.items():assert sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
    result=dict(classification='COMPLETE_FINITE_ONEFORM_GRAM_FROM_SAME_MP_COEFFICIENT_BLOCKS',
        records=records,source_and_owner_sha256=dict(sorted(pins.items())),
        input_result_sha256=dict(MP_values=vh,ordinary_Gram=oh),
        numerical_sha256=sha256((out/'complete_one_form_Gram.npz').read_bytes()).hexdigest(),
        all1200_common_Gram_or_scalar_blocks_completed=False,
        all15_form_convergence=False,physical_operator_or_outgoing_domain_selected=False,
        physical_source_field_domain_derivative_pass=False,coupled_matching_corrections_applied=0,
        physical_normalized_muon_spins=None,muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--values',required=True);p.add_argument('--ordinary',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();execute(a.values,a.ordinary,a.output)
