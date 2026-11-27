"""Normalized stationary radial Haar energy, in common coordinate units."""
import json
from pathlib import Path
results=[]
for D in (10.,100.,1000.,10000.):
    # Both collars have a forced trace gap D, and total resistance D^2+1.
    # The named region always ends at s=2. The outer interval [2,3] is regular.
    J=D/(D**2+1)
    E=0.5*J*J*(D**2+1)
    for name, left, right in [('shrinking neck',0.,1/D),('extended degeneration',1.,2.)]:
        L=right-left
        a=L/D**2
        strain_patch=.5*a*(J/a)**2*L
        strain_ext=.5*J*J
        assert abs(strain_patch+strain_ext-E)<1e-14
        results.append(dict(gap=D,geometry=name,patch=[left,right],area=a,flow=J,total_energy=E,
                            patch_energy=strain_patch,regular_outer_energy=strain_ext))
Path(__file__).with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results[-2:],indent=2))
