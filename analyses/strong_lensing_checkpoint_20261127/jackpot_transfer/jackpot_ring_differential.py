"""Nominal circular-aperture differential and geometric tide leverage."""
import json,math
from pathlib import Path
p=Path(__file__).parent
d=json.loads((p/'jackpot_equilibrium_calibration.json').read_text())
a,b=d['apertures_kpc']; t0,t1=d['total_projected_Msun']
area=math.pi*(b*b-a*a)
out=dict(width_kpc=b-a,annulus_area_kpc2=area,total_delta_projected_Msun=t1-t0,
         average_total_Sigma_Msun_pc2=(t1-t0)/area/1e6,common_plane_total_bend_change=(t1/t0)*(a/b)-1,
         models={})
for tag in ('Salpeter','Chabrier'):
    s0,s1=d[tag]['stars_Msun']; n0=t0-s0-1.6e9;n1=t1-s1-1.6e9
    out['models'][tag]=dict(added_stars_Msun=s1-s0,added_excess_Msun=n1-n0,
        excess_fraction_of_annulus_mass=(n1-n0)/(t1-t0),
        average_excess_Sigma_Msun_pc2=(n1-n0)/area/1e6,
        excess_Msun=[n0,n1],
        effective_bend_fractional_change=(n1/n0)*(a/b)-1)
j=json.loads((p/'jackpot_annular_tide.json').read_text())
i,o=sorted(j['source3_radii_arcsec'])
a,b=j['rings_arcsec']
assert i<a<b<o
out['coherent_tide_outer_over_inner_angle_bounds']=[q**4/(i*o**3) for q in (a,b)]
assert out['total_delta_projected_Msun']>0
(p/'jackpot_ring_differential.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
