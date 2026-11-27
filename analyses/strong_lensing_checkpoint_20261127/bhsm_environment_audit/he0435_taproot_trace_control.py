"""Scalar fixed-trace analog, not a physical BHSM singularity law."""
import json
import numpy as np
from pathlib import Path
root=Path(__file__).parent
lengths=json.loads((root/'he0435_seed_surface_flux.json').read_text())
direction=json.loads((root/'he0435_group_direction.json').read_text())
offset=np.linalg.norm(direction['offset_normalized_arcsec'])
sep=offset*7.026976/1.182
out={}
for choice in ('slope_matched','aperture_matched'):
    ell=lengths[choice]['L_kpc']
    out[choice]={}
    for D in (ell,sep):
        z=D/ell
        c=-np.expm1(-z)/z
        K=np.array([[1,c],[c,1]])
        same=np.linalg.solve(K,[1,1])
        opposite=np.linalg.solve(K,[1,-1])
        assert np.allclose(same,1/(1+c))
        assert np.allclose(opposite,[1/(1-c),-1/(1-c)])
        assert np.linalg.eigvalsh(K)[0]>0
        assert same[0]<1 and opposite[0]>1
        out[choice][str(D)]=dict(separation_kpc=D,length_kpc=ell,transfer_relative_to_self=c,
            same_trace_relative_source=same.tolist(),opposite_trace_relative_source=opposite.tolist())
out['scope']='Prescribed normalized traces, positive finite B, one local Euclidean 3D static field. Projected group centroid distance is a scale check only, not an identified singularity or known spatial separation. L is inherited from earlier diagnostic trials, not predicted. Opposite traces are a signed perturbation test, not observed or an extra positive mass.'
(root/'he0435_taproot_trace_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
