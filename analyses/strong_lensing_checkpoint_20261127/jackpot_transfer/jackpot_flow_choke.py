"""Declared flow-driven projected transfer proxy; not a flow detection."""
from jackpot_annular_tide import terms,run,bounds,P,json,np,x,w,pair
a,b=bounds
weights=w*x*x*(1-x)**2/(a+(b-a)*x)
screened=float((weights@x)/weights.sum())
out={}
control=run(bounds,'ordinary_shear')
ref=control['held_out_B_error_mas']
for label,c in [('coherent',None),('flip_at_midpoint',.5),('inner_tide_cancelled_by_transition',screened)]:
    rows=run(bounds,'both',c)
    r=np.linalg.norm(pair,axis=1)
    pp,dp=terms(r,a,b,c)
    if label=='inner_tide_cancelled_by_transition':
        assert abs(dp[1])<2e-15 and abs(dp[0])>1e-4
    rows['deflection_per_unit_at_A_B_arcsec']=np.abs(dp).tolist()
    rows['transition_fraction']=c
    rows['transition_arcsec']=None if c is None else a+(b-a)*c
    out[label]=rows
    print(label,rows,flush=True)
assert abs(ref-345.834)<.01
(P/'jackpot_flow_choke.json').write_text(json.dumps(dict(control=control,variants=out),indent=2)+'\n')
