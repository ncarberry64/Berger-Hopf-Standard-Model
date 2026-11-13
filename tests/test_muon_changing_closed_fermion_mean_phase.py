import numpy as np
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_primal_native_phase_adjoint import native_phase_midpoint_map
from bhsm.interface.muon_changing_closed_fermion_mean import changing_n0_heat_mean_target


def test_changing_phase_heat_target_against_actual_affine_cell_variation():
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    maps=native_phase_midpoint_map(phase['representation']);n=maps['coordinates']['x_count']
    d=np.zeros(maps['raw_from_phase'].shape[1]);d[[0,37,n-4,2*n,2*n+37,3*n]]=[.1,.05,.02,.1,.03,.04]
    a=changing_n0_heat_mean_target(phase,cutoff=1e-11,quadrature_order=8)
    def value(step):
        p=dict(phase);p['arrays']=dict(phase['arrays']);r=phase['arrays'][phase['stage_key']].copy()
        r[0]+=step*(maps['raw_from_phase']@d);p['arrays'][phase['stage_key']]=r
        return changing_n0_heat_mean_target(p,cutoff=1e-11,quadrature_order=8)['paired_Y2_value']
    step=2e-5;fd=(value(step)-value(-step))/(2*step)
    exact=a['paired_phase_gradient']@d
    np.testing.assert_allclose(exact,fd,rtol=3e-6,atol=2e-24)
