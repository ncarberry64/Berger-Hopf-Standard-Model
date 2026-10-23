"""One bounded original canonical67 tangent attribution from immutable cells."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_stored_fiber_canonical_tangent import (
    exact_fiber_ward_lift,stored_original_canonical_tangent,stored_endpoint_constitutive_tangent,
)
from bhsm.interface.muon_fixed_parent_finite_shooting import ward_canonical_input
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve exact-stored tangent applications')
    pins={};archives={};folder=ROOT/source
    def read(name):
        p=folder/name;pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    base=read('action_and_shooting_rows.npz');candidate=read('candidate.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation']
    raw=candidate['raw_pair'][1];Pi=candidate['own_child_Pi']
    frame=canonical_central_frame(raw,rep);C=frame['literal_generators'][:106].T
    # Derive the same fixed two Ward pivot coordinates from the retained
    # canonical chart, while constructing the derivative contact through
    # its independently action-owned generators at this candidate.
    packet=ward_canonical_input(raw,rep,np.zeros(104,complex))
    piv=packet['named_momentum_pivots'];contact=np.zeros((2,106),complex)
    # The original E contains −C_piv^-1*dC*Pi in its four H columns.
    # Rebuild dC*Pi directly, rather than inheriting its rounded solve.
    from bhsm.interface.muon_trace_enriched_charged_current_response import enriched_central_profiles
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
    coords=generic_coordinate_lift(rep['gauge_labels'])
    at=np.asarray(coords['At_indices']);central=[i for i in at if rep['gauge_labels'][i]['internal']==3]
    wall=rep['wall_trace_map'][0,3,central]@enriched_central_profiles(rep)['theta_coefficients']
    G=higgs_u2_real_representation()['real_generators'][3]
    contact[:,102:106]=-np.outer(wall,G.T@Pi[102:106])
    lift=exact_fiber_ward_lift(base['canonical_embedding'],base['actual_fiber67'],C,contact,piv)
    out.mkdir(parents=True)
    def save(name,values):
        arrays={k:v for k,v in values.items()if isinstance(v,np.ndarray)}
        _compressed_npz(out/name,arrays)
        p=out/name
        if p.stat().st_size>=10*1024**2:raise ValueError('split tangent output')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('initial_literal_Ward_fiber.npz',dict(lift,ward_map=C,ward_position_contact=contact,pivots=piv,
        original_embedding=base['canonical_embedding'],original_fiber=base['actual_fiber67']))
    hi,lo=lift['canonical_direction_high'],lift['canonical_direction_low'];history=[]
    F=frame['named_frame_covectors']
    for k in range(2):
        stage=read(f'stage_{k:04d}.npz');end=read(f'endpoint_{k:04d}.npz')
        print(json.dumps(dict(stage='original_stored67_cell',cell=k)),flush=True)
        a=stored_original_canonical_tangent(stage['stage_Hessian'],stage['coordinate_step'].item(),F,hi,lo)
        save(f'cell_{k:04d}_all67_original_rows.npz',a)
        hi,lo=a['canonical_final_high'],a['canonical_final_low']
        endpoint=stored_endpoint_constitutive_tangent(end['endpoint_Hessian'],F,hi,lo)
        save(f'endpoint_{k:04d}_all67_original_phase.npz',endpoint)
        # Explicitly compare independent original-row solve to the binary
        # Cayley product previously used for the same fiber.
        cayley=end['canonical_transfer']@(base['canonical_embedding']@base['actual_fiber67'])if k==0 else end['canonical_transfer']@cayley
        rec=dict(cell=k,original358_upper=a['original_rows_upper'],framed360_upper=a['framed_rows_upper'],
            named_frame_reaction_upper=a['reaction_rows_upper'],assembly_difference_upper=a['assembly_difference_upper'],
            literal_transpose_rows_upper=a['literal_transpose_rows_upper'],literal_pairing_difference_upper=a['literal_pairing_difference_upper'],
            endpoint_original146_upper=endpoint['original_rows_upper'],endpoint_framed148_upper=endpoint['framed_rows_upper'],
            endpoint_named_frame_reaction_upper=endpoint['reaction_rows_upper'],
            canonical_difference_from_binary_Cayley_norm=float(np.linalg.norm(hi+lo-cayley)))
        history.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
    save('final_full67_canonical_transfer_image.npz',dict(canonical_high=hi,canonical_low=lo,binary_Cayley_image=cayley))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):
            path=Path(path);pins[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
    for path in (Path(__file__),ROOT/'tests/test_muon_stored_fiber_canonical_tangent.py'):
        pins[path.relative_to(ROOT).as_posix()]=sha256(path.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('same stored source changed')
    result=dict(classification='EVALUATED_EXACT_STORED_ALL67_ORIGINAL_CANONICAL_TANGENT_ATTRIBUTION',
        input_hashes=pins,archives=archives,history=history,precision_bits=192,
        initial_Ward_before_upper=lift['ward_before_upper'],initial_Ward_after_upper=lift['ward_after_upper'],
        initial_dependent_Pi_correction_norm=float(np.linalg.norm(lift['dependent_Pi_correction_high'])),
        original_action_reexecuted=False,source_or_base_state_changed=False,
        initial_only_Ward_rounding_repaired=True,free_initial_canonical_coordinates_changed=False,
        operator_contract='Exact stored binary H and h before coefficient product assembly; original358+F2 and endpoint146+F2, literal transpose independent.',
        root='No nonlinear retraction, actual action coefficient, truncation, exterior, formation or physical pole certificate.',
        original_guard=2e-10,error_scope='Outward Acb arithmetic on the supplied finite stored matrices only.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='stored67_complete',result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.source,a.output)
