"""Attribute saved-Hessian widths; counterfactuals are not physical bounds."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import numpy as np
import diagnose_n12_gate7_saved_coupled_hessian_normalization_v2 as base

original=base.normalization.normalized_mixed
original_load=base.engine.load_inputs


def midpoint(value):
    if isinstance(value,dict):return {k:midpoint(v) for k,v in value.items()}
    if isinstance(value,np.ndarray):
        return np.array([v.mid() for v in value.flat],dtype=object).reshape(value.shape)
    return value.mid()


def attributed(*args,**kwargs):
    result,proof=original(*args,**kwargs)
    cases={}
    def measure(label,transform):
        operands=list(args)
        for i in (8,9,10):operands[i]=dict(operands[i])
        transform(operands)
        # Formal arithmetic sensitivity only: midpoint substitutions generally
        # violate the coupled-family constraints. No physical enclosure follows.
        candidate,_=original(*operands,**kwargs)
        cases[label]=float(max(v.rad() for v in candidate.flat))
    def replace_fields(a,indices,fields):
        for i in indices:
            for key in fields:a[i][key]=midpoint(a[i][key])
    measure('mixed_line_exact',lambda a:replace_fields(a,[10],['psi']))
    measure('mixed_response_exact',lambda a:replace_fields(a,[10],['hard','border']))
    measure('mixed_scalar_exact',lambda a:replace_fields(a,[10],['cpsi','remainder']))
    measure('all_mixed_exact',lambda a:replace_fields(a,[10],list(a[10])))
    measure('all_first_variations_exact',lambda a:replace_fields(a,[8,9],list(a[8])))
    def scalar_exact(a):
        a[6]=midpoint(a[6]);a[7]=midpoint(a[7]);replace_fields(a,[8,9,10],['cpsi','remainder'])
    measure('all_scalar_variations_exact',scalar_exact)
    def base_exact(a):
        for i in (0,2,3,4,5,6,7):a[i]=midpoint(a[i])
    measure('base_operands_exact',base_exact)
    proof.update(counterfactual_expression_radius_diagnostics=cases,
        counterfactual_values_are_not_physical_enclosures=True,
        counterfactuals_may_violate_coupled_identities=True)
    return result,proof


def load(index):
    source=original_load(index);p=base.engine.p
    for file in (Path(__file__),Path(base.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    return source


base.normalization.normalized_mixed=attributed
base.engine.load_inputs=load
if __name__=='__main__':base.main()
