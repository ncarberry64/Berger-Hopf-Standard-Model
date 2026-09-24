"""Reuse a frozen same-family enclosure without deleting its expression.

These facts constrain the actual physical family, not arbitrary independent
choices of every auxiliary error leaf. No physical radius is reduced.
"""
from types import MethodType
from flint import arb
from bhsm.interface.shared_expression_graph import Expression,pair,restore
from bhsm.interface.sparse_affine_enclosure import SparseAffine


def install(domain,facts):
    if not hasattr(domain,'certified_enclosures'):
        domain.certified_enclosures={}
        original_export=domain.export
        def export(self,roots,**kwargs):
            result=original_export(roots,**kwargs)
            result['certified_enclosures']=self.certified_enclosures
            result['auxiliary_leaves_constrained_to_actual_physical_family']=True
            return result
        domain.export=MethodType(export,domain)
    for index,fact in facts.items():
        i=int(index);bound=restore(fact['ball'])
        value=domain.compiled(Expression(domain,i))
        center=bound.mid()
        inherited_tail=(value.r+abs(value.c-center).upper()).upper()
        radius=(bound.rad()+value.linear_bound()).upper()
        if not radius.is_finite() or not inherited_tail.is_finite():
            raise ArithmeticError('finite certified expression enclosure required')
        # f-center-a.theta lies in both the translated existing tail and
        # I-center-a.theta. Recenter at the certified interval midpoint.
        # Taking the smaller symmetric tail preserves the original signed
        # coefficients and exact DAG expression.
        domain.bounds[i]=SparseAffine(domain.backend,center,value.coefficients,min(inherited_tail,radius))
        domain.certified_enclosures[str(i)]=fact
