"""Pin the implemented construction contracts; perform no physical solve."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path


def inspect(repository):
    root=Path(repository).resolve()
    specifications={
        'muon_holomorphic_child_action.py':['_affine_geometry','Parent/reference are the SAME','p=_affine_geometry'],
        'muon_holomorphic_two_arm_action.py':['def holomorphic_two_arm_action','not declared a solved canonical parent'],
        'muon_fixed_parent_finite_shooting.py':['terminal graph is REQUIRED','terminal_matrix,terminal_source'],
        'muon_sigma_normal_collar_transport.py':['outside actual canonical history'],
        'muon_outgoing_trace_energy_jet.py':['Only transverse motion','subspace=-C@VE@a'],
        'ae31_c2_local_em_ward_identity.py':['Ward_identity_determines_F2'],
        'ae4_stratified_dirac_zeta_induced_owner.py':['does not pretend','numerical_ell_star_evaluated_on_current_C2'],
    }
    records=[]
    for name,needles in specifications.items():
        path=root/'src/bhsm/interface'/name;raw=path.read_bytes();lines=raw.decode('utf8').splitlines()
        spans=[]
        for needle in needles:
            indices=[i for i,line in enumerate(lines)if needle in line]
            if not indices:raise ValueError('Source contract anchor absent: '+name+' '+needle)
            for i in indices:spans.append(dict(anchor=needle,line=i+1,
                context_start=max(0,i-2)+1,context=lines[max(0,i-2):min(len(lines),i+3)]))
        records.append(dict(path=path.relative_to(root).as_posix(),sha256=sha256(raw).hexdigest(),spans=spans))
    return dict(classification='REPEATABLE_SOURCE_INSPECTION_OF_PHYSICAL_CONTINUATION_CONSTRUCTION_BOUNDARY',
        sources=records,inspection_producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        physical_continuation_evaluated=False,physical_full_derivative_passed=False,
        physical_two_spin_normalization=None,muon_magnetic_moment=None,coupled_matching_corrections_applied=0,
        new_physics_or_numerical_solver_runs=0,source_inspection_is_not_a_physics_calculation=True)


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('--repository',required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    payload=(json.dumps(inspect(args.repository),sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.write_bytes(payload);print(sha256(payload).hexdigest())
