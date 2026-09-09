from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_factored_physical_hessian_errors as backend


def test_factored_algorithm_has_explicit_distinct_source_binding(monkeypatch):
    def original(interval):
        return {'state':'unchanged'},dict(algorithm='original',interval=interval,arrays={'state':'same'},sources={}), 'old'
    monkeypatch.setattr(backend,'_original_load',original)
    values,binding,fingerprint=backend.load_inputs(5)
    assert values=={'state':'unchanged'}
    assert binding['algorithm']==backend.ALGORITHM
    assert binding['arrays']=={'state':'same'}
    assert 'src/bhsm/interface/factored_arb_integrand.py' in binding['sources']
    assert 'scripts/derive_n12_gate7_factored_physical_hessian_errors.py' in binding['sources']
    assert fingerprint!='old'
    assert backend.load_inputs(5)[2]==fingerprint


def test_worker_prepares_original_jets_before_temporary_integrand_change(tmp_path,monkeypatch):
    campaign=backend.campaign;original=campaign.graph.cert._integrand;events=[]
    for name in ('WORK','worker','load_inputs'):
        monkeypatch.setattr(campaign,name,getattr(campaign,name))
    monkeypatch.setattr(backend,'_installed',False)
    def prepare(interval,expected):
        assert campaign.graph.cert._integrand is original
        events.append('original preparation')
        return {'state':np.zeros(campaign.graph.cert.STATE)},{},expected
    def compute(interval,row,expected):
        assert campaign.graph.cert._integrand is not original
        events.append('factored computation')
        return {'interval':interval,'row':row}
    monkeypatch.setattr(campaign,'prepare_worker',prepare)
    monkeypatch.setattr(campaign,'point_directory',lambda i:tmp_path)
    monkeypatch.setattr(backend,'_original_worker',compute)
    assert backend.worker(1,2,'expected')=={'interval':1,'row':2}
    assert events==['original preparation','factored computation']
    assert campaign.graph.cert._integrand is original
