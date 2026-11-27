"""Inclination control, fixed three-dimensional separation, and fixed weak R1 forcing."""
from symmetric_neighbors import *
rows=[]
for case in cases:
    incl=[30.,45.,float(np.rad2deg(np.arccos(1/np.sqrt(3)))),60.,75.]
    data=[one(*case,1300,60,tilt_deg=i) for i in incl]
    rings=[d['rings'] for d in data]
    for k,baseline in enumerate(rings[1]):
        for i,test in zip(incl,rings):
            m=np.cos(np.deg2rad(i))**2
            a=test[k]
            for key,coeff in [('tide_linear_sky_mean_mas',2*(3*m-1)),('tide_linear_axis_minus_perp_mas',2*(1-m)),('tide_quadratic_true_monopole_mas',1.)]:
                assert np.isclose(a[key],coeff*baseline[key],rtol=1e-8,atol=1e-14)
    rows+=data
(P/'tide_projection_control.json').write_text(json.dumps(rows,indent=2)+'\n')
for a in rows:
    r=a['rings'][0]
    print(a['system'],a['tilt_deg'],1000*r['tide_linear_sky_mean_mas'],1000*r['tide_quadratic_true_monopole_mas'])
