"""Reproduce equivalent, preconditioned enclosures of the same local operator."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import numpy as np
import certify_n12_gate7_component_centered_uniform_physical_local_defects as base
from bhsm.interface import preconditioned_physical_hs_defect as reordered

engine=base.engine;p=base.p
old_load=base.load_inputs;old_evaluate=base.evaluate;old_theory=base.THEORY
WORK=base.WORK=engine.WORK=ROOT/'artifacts/flagship_integration/.preconditioned_component_centered_uniform_physical_local_defect_work'
THEORY=engine.THEORY=ROOT/'theory/n12_gate7_preconditioned_local_hs.md'
ALGORITHM=engine.ALGORITHM='PRECONDITIONED_COMPONENT_CENTERED_UNIFORM_PHYSICAL_HS_LOCAL_ENCLOSURE_ARB512_V1'


def load_inputs(index):
    source=old_load(index)
    for file in (Path(__file__),Path(reordered.__file__),old_theory,THEORY):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    p.verify_sources(source['binding'])
    return source


def evaluate(source):
    original,report=old_evaluate(source)
    candidates={'original':original}
    args=[source[key] for key in ('left_df','midpoint_df','right_df','step','trial_left','trial_right','test','frozen_left','frozen_right')]
    for method in ('solve_first','preconditioned_chain','combined_endpoint_coefficient'):
        blocks=reordered.local_defect_blocks(*args,association=method,initial_endpoint_fixed=source['index']==0)
        candidates[method]={name:np.array(block.entries(),dtype=object).reshape(74,74) for name,block in blocks.items()}
    arrays={};counts={}
    for name in ('C','DL','DR'):
        arrays[name]=np.empty((74,74),dtype=object);counts[name]={method:0 for method in candidates}
        for index in np.ndindex((74,74)):
            if not all(matrix[name][index].overlaps(original[name][index]) for matrix in candidates.values()):
                raise ArithmeticError('equivalent physical local enclosures disagree')
            method=min(candidates,key=lambda method:candidates[method][name][index].rad())
            arrays[name][index]=candidates[method][name][index];counts[name][method]+=1
    report.update(fixed_preconditioner_applied_before_uncertain_products=True,
        equivalent_association_selection_counts=counts,
        entrywise_smallest_radius_among_equivalent_enclosures=True,
        physical_inputs_and_frozen_operator_changed=False)
    p.verify_sources(source['binding'])
    return arrays,report


engine.load_inputs=load_inputs;engine.evaluate=evaluate
main=base.main
if __name__=='__main__':main()
