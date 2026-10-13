import numpy as np
from bhsm.interface.muon_coupled_birth_full_application import trace_action_forms,attachment_schur


def test_signed_common_ports_independent_dual_sector_and_parameter():
    rng=np.random.default_rng(1729)
    A=rng.normal(size=(7,7))+1j*rng.normal(size=(7,7));A+=5*np.eye(7)
    dA=rng.normal(size=A.shape)+1j*rng.normal(size=A.shape)
    E=np.eye(7)[:3];F=np.eye(7)[3:4];C=np.eye(3)
    parent=.3*A+np.diag(np.arange(7))*.03
    app=trace_action_forms(A,E,F,C,dict(parent=parent,child=A-parent),dA)
    assert np.max(abs(app['original_right_rows']))<2e-15
    assert np.max(abs(app['original_left_rows']))<2e-15
    assert np.max(abs(app['sector_sum_difference']))<2e-15
    assert np.max(abs(app['border_action_identity']))<2e-15
    assert np.linalg.norm(app['left']-app['right'])>.1
    h=2e-6
    plus=trace_action_forms(A+h*dA,E,F,C,dict(all=A+h*dA),dA)
    minus=trace_action_forms(A-h*dA,E,F,C,dict(all=A-h*dA),dA)
    fd=(plus['common_action_form']-minus['common_action_form'])/(2*h)
    assert np.linalg.norm(fd-app['common_action_parameter'])<2e-9
    s=attachment_schur(app['common_action_form'])
    assert np.max(abs(s['attachment_natural_rows']))<1e-15
    direct=app['common_action_form'][2,2]-app['common_action_form'][2,:2]@np.linalg.solve(
        app['common_action_form'][:2,:2],app['common_action_form'][:2,2])
    assert abs(direct-s['normal_form'])<1e-15
