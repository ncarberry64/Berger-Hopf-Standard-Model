from pathlib import Path
import json, numpy as np, pytest
from bhsm.interface.completion.master_action_bh_susceptibility_v14_82 import *

def test_version():
    assert VERSION=="v14.82"
def test_response():
    assert np.allclose(solve_response(np.diag([2.,4.]),np.array([2.,8.])),[1,2])
def test_bad_K():
    with pytest.raises(ValueError): solve_response(np.array([[-1.]]),np.array([1.]))
def test_scalar_chi():
    assert scalar_chi(np.eye(2),np.array([1.,2.]),np.array([3.,4.]))==-11
def test_matrix_chi():
    T=np.array([[[3.,1.],[1.,4.]]])
    assert np.allclose(matrix_chi(np.eye(1),np.array([2.]),T,np.zeros((2,2))),[[-6,-2],[-2,-8]])
def test_response_payload_signs():
    p=response_payload(); assert p["softening_witness_chi"]*p["stiffening_witness_chi"]<0
def test_schur():
    assert abs(schur(np.array([[2.]]),np.array([[1.]]),np.array([[4.]]))[0,0]-1.75)<1e-14
def test_schur_fd():
    assert schur_payload()["finite_difference_residual"]<1e-8
def test_attachment_reference():
    assert abs(attachment_mu(.181391690148362,1.)-.08620600507952429)<1e-14
def test_attachment_partials():
    for h,k in ((.2,1),(.5,.8),(2,.3),(1,1)):
        a,b=attachment_partials(h,k); assert a>0 and b>0
def test_attachment_chi_signs():
    assert attachment_chi(.2,1,-.1,-.2)>0
    assert attachment_chi(.2,1,.1,.2)<0
def test_attachment_payload():
    p=attachment_payload(); assert p["partials_positive"] and p["physical_attachment_chi"] is None
def test_critical_drive():
    D=critical_drive(.2,.5,.01,1,.5)
    assert abs(.2-.5*D+.01**2*3.5)<1e-14
def test_provenance():
    p=provenance_payload()
    assert p["can_compute_physical_chi_now"] is False
    assert all(x["BH_source"] is False for x in p["repo_sources"])
def test_bridge():
    p=bridge_payload(); assert p["physical_driver_derived"] is False
    assert any(s=="DERIVED_V14_82" for _,s in p["rows"])
def test_status():
    p=status_payload(); assert p["FULL_BHSM_COMPLETE"] is False and p["PHYSICAL_EXECUTION_BLOCKED"] is True
def test_completion():
    p=completion_payload()
    assert p["validation_passed"] is True
    assert p["physical_chi_b"] is None
    assert p["physical_execution_allowed"] is False
def test_artifacts():
    assert len(artifact_payloads())==8
def test_determinism(tmp_path:Path):
    a=materialize(tmp_path/"a"); b=materialize(tmp_path/"b")
    for x,y in zip(a,b):
        assert x.read_bytes()==y.read_bytes(); json.loads(x.read_text())
