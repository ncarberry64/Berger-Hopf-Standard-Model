"""Exercise the optional joint route from a noneditable installed wheel.

Run with the installed venv Python -I, outside the checkout. This probe uses an
independent analytic synthetic control; --sourcepack and --result additionally
verify real published native data and an archived state without new fitting.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
from importlib import metadata
from urllib.request import urlopen

import numpy as np
import astropy
import scipy
import bhtracker
from bhtracker.joint_mass_v2 import JointData, JointModel, earth_heliocentric_ne, fit_joint
from bhtracker.joint_report import validate_result
from bhtracker.report import export_result, replay_analysis
from bhtracker.server import import_joint_sourcepack, make_server, joint_summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--sourcepack',type=Path)
    parser.add_argument('--result',type=Path)
    args=parser.parse_args()
    prefix=Path(sys.prefix).resolve();package=Path(bhtracker.__file__).resolve()
    if not package.is_relative_to(prefix):raise RuntimeError('Probe must import a wheel installed inside its isolated venv')
    direct=metadata.distribution('bhsm-blackhole-tracker').read_text('direct_url.json')
    if direct and json.loads(direct).get('dir_info',{}).get('editable'):raise RuntimeError('Editable installs do not satisfy the joint release check')
    times=np.r_[np.linspace(2455480,2456100,80),np.linspace(2455740,2455790,70)]
    angular_times=np.linspace(2455780,2459700,24)
    ra,dec=267.91745833,-29.89063889
    def separation(t):
        direction=np.array([np.cos(1.7),np.sin(1.7)])
        impact=np.array([-direction[1],direction[0]])
        return -.08*impact+((t-2455760.)/240.)[:,None]*direction+.12*earth_heliocentric_ne(t,ra,dec)
    q=separation(times);u2=np.sum(q*q,axis=1)
    # Independently image-summed magnification and centroid-minus-source law.
    mag=20.-2.5*np.log10(1+.05*((u2+2)/np.sqrt(u2*(u2+4))-1))
    qa=separation(angular_times)
    angular=np.array([3.,-4.])+((angular_times-2456500.)/365.25)[:,None]*np.array([-2.,3.])-.13*(earth_heliocentric_ne(angular_times,ra,dec)-earth_heliocentric_ne([2456500.],ra,dec)[0])+4.8*qa/(np.sum(qa*qa,axis=1)+2)[:,None]
    document={'schema':'bhtracker.native_joint_mass.v1','target':'SYNTHETIC-INSTALLED-JOINT-CONTROL',
              'time_coordinate':'JD_TDB','reference_jd_tdb':2456500.,'ra_deg':ra,'dec_deg':dec,
              'metadata':{'synthetic':True,'ra_axis':'EAST_TANGENT_ALPHA_COS_DEC','time_and_frame_provenance':'Analytic synthetic control, not empirical evidence.'},
              'analysis':{'bounds':{'t0_jd_tdb':[2455700.,2455830.],'tE_days':[20.,2000.],
                                    'u0_heliocentric':[-1.,1.],'pi_E':[0.,1.],'theta_E_mas':[.01,40.],
                                    'relative_frame_source_parallax_mas':[-1.,1.]},
                          'initial_guess':{'t0_jd_tdb':2455760.,'tE_days':240.,'u0_absolute':.08,'pi_E':.12}},
              'photometry':[{'source_row_id':f'synthetic-photo-{i}','time_jd_tdb':float(t),'instrument':'OGLE','magnitude':float(y),'magnitude_error':.01} for i,(t,y) in enumerate(zip(times,mag))],
              'astrometry':[{'source_row_id':f'synthetic-angle-{i}','exposure_midpoints_jd_tdb':[float(t)],'visit_id':str(i),'filter':'F814W','north_mas':float(y[0]),'east_mas':float(y[1]),'north_error_mas':.03,'east_error_mas':.03} for i,(t,y) in enumerate(zip(angular_times,angular))]}
    data=JointData(document);model=JointModel(data)
    initial=np.array([-4.9,np.log(240.)+.001,-.079,1.701,.121,20.001,.0501])
    fitted=fit_joint(data,initial_states=[initial],max_nfev=150)
    expected=4.8/(8.14385327673037*.12)
    if fitted.get('parameters',{}).get('mass_msun') is None or abs(fitted['parameters']['mass_msun']/expected-1)>2e-7:raise RuntimeError('Installed joint noiseless mass recovery failed')
    if fitted['objective_deviance']>1e-12:raise RuntimeError('Installed joint control predictions failed')
    null=np.array(fitted['best_internal_state']);null[4]=0.
    if model.evaluate(null,details=True)['parameters']['mass_msun'] is not None:raise RuntimeError('Zero parallax must leave mass unavailable')
    receipt={'schema':'bhtracker.installed_joint_probe.v1','passed':True,'prefix':str(prefix),'bhtracker_file':str(package),'editable':False,
             'versions':{'product':metadata.version('bhsm-blackhole-tracker'),'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'astropy':astropy.__version__},
             'synthetic_control':{'identified_as_synthetic':True,'expected_mass_msun':expected,'fitted_mass_msun':fitted['parameters']['mass_msun'],'objective_deviance':fitted['objective_deviance'],'zero_parallax_mass_unavailable':True,'scientific_source_sha256':fitted['scientific_source_sha256']}}
    with tempfile.TemporaryDirectory(prefix='bhtracker installed joint ') as temporary:
        root=Path(temporary);export_result(fitted,root/'synthetic')
        receipt['synthetic_replay']=replay_analysis(root/'synthetic',root/'synthetic-replayed')
        if args.sourcepack:
            raw=args.sourcepack.read_bytes();native=import_joint_sourcepack(raw)
            receipt['native_sourcepack']={'archive_sha256':hashlib.sha256(raw).hexdigest(),'summary':joint_summary(native)}
        if args.result:
            value=json.loads(args.result.read_text(encoding='utf-8-sig'))
            _,_,receipt['archived_state_replay']=validate_result(value)
            export_result(value,root/'native');receipt['native_export_replay']=replay_analysis(root/'native',root/'native-replayed')
            receipt['archived_result_sha256']=hashlib.sha256(args.result.read_bytes()).hexdigest()
            receipt['archived_mass_status']=value['mass_status']
            receipt['qualification']='Recorded state replay is numerical verification, not scientific acceptance or optimization.'
    server=make_server(0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        checks={}
        for path in ['/joint','/joint.js','/api/health']:
            with urlopen(f'http://127.0.0.1:{server.server_port}{path}',timeout=10) as response:
                body=response.read();checks[path]={'status':response.status,'bytes':len(body)}
                if response.status!=200 or not body:raise RuntimeError('Installed joint web resource failed')
        receipt['installed_web_resources']=checks
    finally:
        server.shutdown();server.server_close();server.executor.shutdown(wait=True,cancel_futures=True);thread.join(timeout=10)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'product':receipt['versions']['product'],'fitted_synthetic_mass_msun':fitted['parameters']['mass_msun'],'actual_observations_imported':bool(args.sourcepack),'archived_state_replayed':bool(args.result),'output':str(args.output.resolve())}))


if __name__=='__main__':main()
