"""Protect all physical formulas outside the four documented call groups."""
import ast
import inspect
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_current_green_mixed_transverse_all_endpoints as original
import certify_n12_gate7_batched_mixed_physical_graph as batched


def test_regrouped_graph_preserves_every_other_parent_statement():
    parent=ast.parse(inspect.getsource(original._mixed_axis_map)).body[0]
    child=ast.parse(inspect.getsource(batched.batched_axis_map)).body[0]
    def target(node):
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name):
            return node.targets[0].id
        return None
    assignments={target(node):node for node in parent.body if target(node)}
    replacements={
        'first_u':'''first_u, first_V, second = _batch_fixed(
            cert,state,dense_maps,out_reduced,fixed,raw_u,raw_V)''',
        'H_u_psi_V':'''H_u_psi_V, H_u_qV, H_u_hV, H_V_psi_u, H_V_qu, H_V_hu = _batch_first(
            cert,state,dense_maps,out_reduced,p_V,q_V,h_V_full,p_u,q_u,h_u_full,raw_u,raw_V)''',
        'gradient_uv':'''gradient_uv = _affine_contraction(
            cert,state,dense_maps,out_full,raw_u,raw_V).reshape(cert.STATE,count)''',
        'cR':'''cR, first_cR_u, first_cR_V, second_cR = _batch_scalar(
            cert,state,dense_maps,raw_u,raw_V,p,p_u,p_V,p_uv,last,last_u,last_V,last_uv)''',
    }
    removed={'first_V','second','H_V_psi_u','H_u_qV','H_V_qu','H_u_hV','H_V_hu',
             'h_u_full','h_V_full','first_cR_u','first_cR_V','second_cR'}
    expected=[]
    for node in parent.body:
        name=target(node)
        if name in replacements:
            if name=='H_u_psi_V':
                expected.extend(assignments[n] for n in ('h_u_full','h_V_full'))
            expected.extend(ast.parse(replacements[name]).body)
        elif name not in removed: expected.append(node)
    parent.body=expected; parent.name=child.name
    assert ast.dump(parent,include_attributes=False)==ast.dump(child,include_attributes=False)
