import numpy as np
from bhsm.interface.muon_em_normal_connector_source import (
    analytic_FE2_values,apply_wall_source_branch,source_cell_field_chart)
import pytest


def test_original_FE2_clock_continuation_keeps_bilinear_variables():
    total=.4
    np.testing.assert_allclose(analytic_FE2_values(.1,total,0),[.5,0])
    np.testing.assert_allclose(analytic_FE2_values(.3,total,1),[.5,.5])
    z=.3+.07j
    np.testing.assert_allclose(analytic_FE2_values(z,total,1),[.5-.35j,.5+.35j])
    rng=np.random.default_rng(76)
    c=rng.normal(size=(2,24,4,3))+1j*rng.normal(size=(2,24,4,3))
    v=rng.normal(size=(24,6,6))+1j*rng.normal(size=(24,6,6))
    p=analytic_FE2_values(z,total,1);ps=analytic_FE2_values(z.conjugate(),total,1)
    d=dict(vertices=v,vertices_sharp=v.conj().transpose(0,2,1),
           temporal_values=p,reflected_temporal_values=ps)
    result=apply_wall_source_branch(d,c,reflected=True)
    expected=sum(ps[l]*np.einsum('cij,chb->hijb',d['vertices_sharp'],c[l])for l in range(2))
    np.testing.assert_allclose(result,expected)
    assert np.linalg.norm(result-apply_wall_source_branch(d,c.conjugate(),reflected=True))>1


def test_original_field_corner_cannot_be_crossed_by_one_polynomial_extension():
    nodes=dict(source_cell=np.array([0,0]),weight=np.ones(2),
               proper_time=np.array([.19,.21]),coordinate_anchor=np.zeros(2),
               total_proper_clock=.4)
    with pytest.raises(ValueError,match='split a source germ'):
        source_cell_field_chart(nodes,0)
    nodes['proper_time']=np.array([.21,.23])
    chart=source_cell_field_chart(nodes,0)
    assert chart['source_element']==1
    assert chart['proper_center']==pytest.approx(.22)
