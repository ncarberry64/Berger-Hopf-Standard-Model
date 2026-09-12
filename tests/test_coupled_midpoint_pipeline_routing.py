"""Keep original proof dependencies immutable while changing input producers."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_affine_hs_midpoint_domain as original_domain
import certify_n12_gate7_affine_midpoint_eigenpair_pilot as original_pair
import certify_n12_gate7_affine_physical_value_pilot as original_values
import certify_n12_gate7_coupled_normalized_physical_value as normalized
import certify_n12_gate7_coupled_hs_midpoint_domain as domain
import certify_n12_gate7_coupled_midpoint_eigenpair_pilot as pair


def test_private_adapters_preserve_original_dependency_graph():
    assert original_domain.values is original_values
    assert normalized.midpoint is original_domain
    assert original_pair.midpoint is original_domain
    assert domain.engine is not original_domain and domain.engine.values is normalized
    assert pair.engine is not original_pair and pair.engine.midpoint is domain
    assert domain.WORK!=original_domain.WORK and pair.WORK!=original_pair.WORK
    assert domain.ALGORITHM!=original_domain.ALGORITHM and pair.ALGORITHM!=original_pair.ALGORITHM


def test_adapter_source_is_added_before_verification(monkeypatch):
    for module in (domain,pair):
        checked=[]
        monkeypatch.setattr(module,'original_load_inputs',lambda index:dict(binding=dict(files={})))
        monkeypatch.setattr(module.p,'verify_sources',lambda binding:checked.append(dict(binding['files'])))
        source=module.load_inputs(13)
        key=module.p.df.file_key(Path(module.__file__))
        assert key in source['binding']['files'] and checked[-1]==source['binding']['files']
