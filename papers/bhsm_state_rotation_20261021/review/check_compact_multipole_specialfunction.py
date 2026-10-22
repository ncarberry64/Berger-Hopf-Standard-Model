"""Independent exact exterior-shape check for the source-action review.

No horizon/source amplitude is selected. rho=r/rV; C and rV scale out.
"""
import json
from pathlib import Path
import numpy as np
from scipy.special import hyp2f1, gamma


def main():
    rho=np.geomspace(1e-3,1e3,151)
    t=-rho**-3
    ratio=(1+rho**-3/4)/(1+rho**-3)
    checks=[]
    for ell in [1,2,3]:
        power=-(ell+1)
        a,b,c=(ell+1)/2,(ell+2)/6,(2*ell+4)/3
        H=hyp2f1(a,b,c,t)
        Ht=a*b/c*hyp2f1(a+1,b+1,c+1,t)
        Htt=a*(a+1)*b*(b+1)/(c*(c+1))*hyp2f1(a+2,b+2,c+2,t)
        f=rho**power*H
        fp=power*rho**(power-1)*H+3*rho**(power-4)*Ht
        fpp=(power*(power-1)*rho**(power-2)*H
              +(6*power-12)*rho**(power-5)*Ht+9*rho**(power-8)*Htt)
        terms=np.array([fpp,2*ratio*fp/rho,-ell*(ell+1)*ratio*f/rho**2])
        residual=np.max(abs(terms.sum(axis=0))/abs(terms).sum(axis=0))
        record={'ell':ell,'maximum_scaled_ODE_residual':float(residual),
                'rho_min':float(rho[0]),'rho_max':float(rho[-1]),
                'deep_log_slope':float(rho[0]*fp[0]/f[0]),
                'far_log_slope':float(rho[-1]*fp[-1]/f[-1])}
        if ell==1:
            translation=2*rho**-2/(1+np.sqrt(1+rho**-3))
            record['translation_relative_error']=float(np.max(abs(f-translation)/f))
            assert record['translation_relative_error']<2e-13
        assert residual<2e-12
        checks.append(record)
    result={'status':'INDEPENDENT_CONDITIONAL_EXTERIOR_SHAPE_CHECK_PASS',
            'horizon_or_source_amplitude_selected':False,'checks':checks,
            'ell2_deep_asymptotic_coefficient':float(gamma(8/3)*gamma(5/6)/(gamma(3/2)*gamma(2)))}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
