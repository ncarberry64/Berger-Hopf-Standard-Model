"""Preserve Arb input-direction balls in the unchanged physical Hessian graph."""
import ast
import hashlib
import inspect
import numpy as np
from flint import arb

PARENT_FUNCTION_SHA256='465C94EFF0CA2635F0DAE155BCBAD2CF89518170958C7BBCA685BB147883004E'


def direction_scalar(value):
    """Keep an existing enclosure; retain the parent's conversion for floats."""
    result=value if isinstance(value,arb) else arb(float(value))
    if not result.is_finite():raise ValueError('finite physical direction required')
    return result


def build_ball_direction_graph(parent):
    """Change only the two input-direction leaf conversions of a pinned graph.

    No action contraction, eigenline, response solve, or chain-rule operation
    is changed. Other numerical inputs keep their original binary64 meaning.
    """
    source=inspect.getsource(parent.batched_axis_map)
    if hashlib.sha256(source.encode()).hexdigest().upper()!=PARENT_FUNCTION_SHA256:
        raise RuntimeError('physical Hessian parent graph changed')
    tree=ast.parse(source);changed=[]
    class Leaves(ast.NodeTransformer):
        def visit_Call(self,node):
            if ast.dump(node,include_attributes=False)==ast.dump(ast.parse('arb(float(value))',mode='eval').body,include_attributes=False):
                changed.append(node.lineno)
                return ast.copy_location(ast.Call(func=ast.Name(id='_direction_scalar',ctx=ast.Load()),
                                                  args=[ast.Name(id='value',ctx=ast.Load())],keywords=[]),node)
            return self.generic_visit(node)
    for statement in tree.body[0].body:
        if isinstance(statement,ast.Assign) and len(statement.targets)==1 and isinstance(statement.targets[0],ast.Name):
            if statement.targets[0].id in ('u','V'):Leaves().visit(statement)
    if len(changed)!=2:raise RuntimeError('exactly two direction conversions required')
    ast.fix_missing_locations(tree)
    namespace=dict(vars(parent));namespace['_direction_scalar']=direction_scalar
    exec(compile(tree,'<pinned physical Hessian with Arb direction leaves>','exec'),namespace)
    evaluate=namespace['batched_axis_map']
    def checked(state,descriptor,weights,reference,axis_direction,transverse_directions):
        axis=np.asarray(axis_direction,dtype=object);directions=np.asarray(transverse_directions,dtype=object)
        if axis.shape!=(99,) or directions.ndim!=2 or directions.shape[0]!=99 or directions.shape[1]==0:
            raise ValueError('one 99-dimensional axis and nonempty compatible direction columns required')
        # Coercion remains in the two original leaf locations; the wrapper
        # checks layout only and does not change their dependence structure.
        return evaluate(state,descriptor,weights,reference,axis,directions)
    return checked
