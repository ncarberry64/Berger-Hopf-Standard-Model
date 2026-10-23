"""BHSM meaning of the existing optical fit, without adding a second force.

The dictionary changes interpretation and reporting, not the likelihood.
It does not infer a microscopic state from a coarse optical parameter.
"""

import math
from copy import deepcopy
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from .forward import C, GM_SUN, PC
from .provenance import project_citation


@lru_cache(maxsize=1)
def _source_provenance():
    base=Path(__file__).resolve().parent/'theory'
    manifest=json.loads((base/'BHSM_INTERPRETATION_MANIFEST.json').read_text())
    for entry in manifest['sources']:
        if hashlib.sha256((base/entry['path']).read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('BHSM interpretation source hash mismatch: '+entry['path'])
    return manifest


def spherical_boundary(mass_msun, radius_pc, sigma_mass_msun=None):
    """Same monopole in a static, spherical, flat-reference boundary description."""
    mass=float(mass_msun);radius=float(radius_pc)
    if not math.isfinite(mass) or not math.isfinite(radius) or mass<=0 or radius<=0:
        raise ValueError('positive finite mass and boundary radius required')
    mass_length=GM_SUN*mass/(C*C*PC)
    compactness=2*mass_length/radius
    if not compactness<1:
        raise ValueError('static spherical boundary must lie outside 2GM/c2')
    lapse=math.sqrt(1-compactness)
    deficit=compactness/(1+lapse)
    delta_k=deficit/radius
    by_mass=mass*2/(1+lapse)
    sigma=None if sigma_mass_msun is None else float(sigma_mass_msun)
    if sigma is not None and (not math.isfinite(sigma) or sigma<0):
        raise ValueError('mass uncertainty must be nonnegative and finite or null')
    return {
        'status':'AVAILABLE','radius_pc':radius,
        'curvature_deficit_pc_inverse':delta_k,
        'curvature_deficit_sigma_pc_inverse':None if sigma is None else GM_SUN*sigma/(C*C*PC*radius*radius*lapse),
        'boundary_energy_over_Msun_c2':by_mass,
        'boundary_energy_sigma_over_Msun_c2':None if sigma is None else sigma/lapse,
        'mixed_curvature_velocity2_km2_s2':GM_SUN*mass/(radius*PC*1e6),
        'reconstructed_monopole_msun':by_mass-GM_SUN*by_mass*by_mass/(2*C*C*radius*PC),
        'geometry':'Principal extrinsic-curvature deficit of the enclosing sphere on the static spatial slice of the spherical Schwarzschild-equivalent ordinary monopole; flat Euclidean reference subtraction.',
        'qualification':'The radius is supplied, and errors condition on it. These are alternative representations of the same monopole, not a second mass or the full nonspherical/environmental boundary energy. Changing the enclosing radius is not physical mass drift.',
    }


def bhsm_interpretation(family,estimates=None,uncertainty=None,model=None,fit_status=None):
    provenance=_source_provenance()
    contract_path=Path(__file__).resolve().parent/'theory'/provenance['interpretation_contract_path']
    core_surface=json.loads(contract_path.read_text(encoding='utf8'))
    interpretation={
        'interpretation_schema_version':2,
        'interpretation_revision':'2026-10-22',
        'framework':'BHSM',
        'project_citation':project_citation(),
        'model_role':'One compact-configuration optical response in the adopted BHSM Einstein/GHY sector, described in boundary/envelope language.',
        'one_potential_rule':'Equivalent ordinary-gravity and BHSM envelope descriptions represent the same fitted lens potential and are counted once. A separately derived response is added only when it is a distinct term of the same physical model.',
        'parameter_meanings':[
            {'parameter':'mass_msun',
             'interpretation':('Action metric/source mass of the adopted conditional R1 compact configuration; the predicted optical response includes its scalar term.' if family=='r1' else 'Effective gravitational monopole of the compact configuration in the adopted BHSM exterior description.'),
             'qualification':'It is the mass coefficient of the fitted optical model. It does not by itself determine a microscopic state, a surface energy, a horizon radius or a topological charge.'},
            {'parameter':'center_mas / proper_motion_mas_yr',
             'interpretation':'Reference position and observer-frame translation of that same boundary/envelope optical response.',
             'qualification':'This tracks the center of the adopted exterior template in the supplied frame; source freedom and environmental structure remain in the inference.'},
            {'parameter':'compact_quad',
             'interpretation':'Projected compact angular structure, which can represent a coarse boundary/envelope deformation when its physical source is specified.',
             'qualification':'A coefficient alone does not select a BHSM surface mode. An equivalent envelope quadrupole is not added again as an independent force.'},
            {'parameter':'shear / convergence',
             'interpretation':'Tidal and focusing terms of the surrounding optical environment.',
             'qualification':'They are fitted environmental freedoms, not automatically intrinsic deformations of the compact configuration.'},
        ],
        'inference_scope':'The ordinary fit is usable with this BHSM interpretation. Agreement with the ordinary lens response is allowed; a non-GR residual is not required. The fit alone does not uniquely identify the microscopic theory or a horizon.',
        'conditional_extension':(
            'R1 evaluates an explicitly conditional scalar boundary-to-metric response from the adopted effective action. Its flux and boundary-state assumptions remain separate from the ordinary mass/motion interpretation.'
            if family=='r1' else
            'No separate scalar deformation was requested. The ordinary monopole, motion and admitted shape terms retain their BHSM interpretation without an additional envelope force.'),
        'weyl_convention':'The tracker propagates W_full=Phi+Psi. A BHSM source using W_topo=(Phi_topo+Psi_topo)/2 contributes 2*W_topo to that same full Weyl response, not a second copy of an already represented term.',
        'core_surface':core_surface,
    }
    if family=='r1':
        boundary={'status':'NOT_ASSUMED_FOR_R1_METRIC','reason':'The Schwarzschild boundary identity is not substituted into the modified R1 metric. Its total boundary energy needs the corresponding metric and reference subtraction.'}
    elif fit_status=='FIT_REJECTED':
        boundary={'status':'NOT_REPORTED_FOR_REJECTED_FIT'}
    elif fit_status=='INSUFFICIENT_INFORMATION':
        boundary={'status':'NOT_REPORTED_FOR_UNRESOLVED_MASS'}
    elif estimates is not None and model is not None:
        try:
            boundary=spherical_boundary(estimates['mass_msun'],model['r0_pc'],(uncertainty or {}).get('mass_msun'))
        except (ValueError,KeyError,OverflowError) as error:
            boundary={'status':'NOT_ADMITTED','reason':str(error)}
    else:
        boundary={'status':'NOT_EVALUATED'}
    interpretation['spherical_boundary']=boundary
    interpretation['source_provenance']=deepcopy(provenance)
    return interpretation
