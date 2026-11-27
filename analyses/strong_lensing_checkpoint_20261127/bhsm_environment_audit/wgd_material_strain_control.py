"""Exact fluid density/energy pushforward toy, not a BHSM Weyl source."""
import json,math
from pathlib import Path
from scipy.integrate import quad
p=Path(__file__).resolve().parent
tab=json.loads((p/'wgd_extended_seam_bracket.json').read_text())
H0=67.4; omega=.31; G=4.300917270036279e-9
density=3*H0**2*omega*(1.23**3)/(8*math.pi*G)
ivar=3*quad(lambda x:x*x*(3-10*x*x+7*x**4)**2,0,1)[0]
def J(x,a):return (1+a*(1-x*x)**2)**2*(1+a*(1-x*x)*(1-5*x*x))
rows=[]
for a in [.06,.03,.015,.0075]:
 vol=3*quad(lambda x:x*x*J(x,a),0,1)[0]
 q=1.5*quad(lambda x:x*x*(1/J(x,a)-1),0,1,epsabs=1e-14)[0]
 assert abs(vol-1)<1e-13 and q>0
 rows.append(dict(a=a,physical_volume_ratio=vol,stored_energy_over_rest_energy=q,
                  quadratic_prediction=a*a*ivar/2,exact_to_quadratic=q/(a*a*ivar/2)))
s=[]
for row in tab['results'][:2]:
 r=row['geom_threshold_sensitivity_toy'][1]['seams'][-1]['rstar_kpc']
 M=4*math.pi/3*(r/1000)**3*density
 s.append(dict(outer_geom_R_kpc=r,ambient_rest_mass_msun=M,
               mass_equivalent_toy_stored_energy_at_3pct_msun=M*rows[1]['stored_energy_over_rest_energy']))
out={'scope':'Flat homogeneous conserved fluid with e(n)=rho0*c^2*n/n0 +(rho0*c^2/2)*(n/n0)^2, uses generous causal K=rho0 c^2 at base. Not an actual cosmic EOS, BHSM field stress, or projected gravitational bound; rest mass exact invariant. Geometry radii imported from separate control solely for scaling.',
 'ambient_rho_msun_per_Mpc3':density,'mean_squared_strain_coeff':ivar,'amplitude_sensitivity':rows,'scale_at_today_RH_outer_geom_radii':s}
(p/'wgd_material_strain_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
