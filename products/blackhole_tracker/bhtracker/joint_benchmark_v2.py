"""Strict, versioned import of the independently sourced 2023 known-system route.

No old 2022 HST times are repaired/reinterpreted. Exact author files remain
embedded with their source-row identities; this is a new data version.
"""
import base64
import hashlib
import json
from pathlib import Path,PureWindowsPath
import re
import numpy as np
from .joint_mass_v2 import JOINT_SCHEMA,JointData,hjd_utc_to_tdb

EXPECTED={
 'OGLE-2011-BLG-0462-new.txt':'94001c1310dcb25ac72f033b1be076221d338501dcf0caee789228c4e318bd28',
 'LamLu2023v2__hst_data_table.txt':'11b548a323a00515bd2b117ad05a457308384409ac76de55f1a5fea0bdf240a3',
 'LAM_LU_2023_HST_EXPOSURE_TIME_MAPPING.json':'25e218c9987f593540a9fdcdd5123ae70db992ebcf5fe7d647c60eff22fc63f0',
}


def import_2023_benchmark(directory,*,all_ogle_rows=False,clock_offset_seconds=0.):
    from astropy.time import Time
    from astropy.coordinates import EarthLocation
    from astropy import units as u
    directory=Path(directory);native={}
    for filename,expected in EXPECTED.items():
        raw=(directory/filename).read_bytes();actual=hashlib.sha256(raw).hexdigest()
        if actual!=expected:raise ValueError(f'Frozen native source hash mismatch: {filename}')
        native[filename]={'sha256':actual,'raw_bytes_base64':base64.b64encode(raw).decode('ascii')}
    mapping=json.loads((directory/'LAM_LU_2023_HST_EXPOSURE_TIME_MAPPING.json').read_text())
    headers=json.loads((directory/'MAST_2023_Table2_header_receipt.json').read_text())
    header_raw=(directory/'MAST_2023_Table2_header_receipt.json').read_bytes()
    if hashlib.sha256(header_raw).hexdigest()!=mapping['header_receipt_sha256']:raise ValueError('HST header mapping receipt hash mismatch')
    byroot={r['header']['ROOTNAME']:r for r in headers['results']}
    byvisit={(r['calendar_date'],r['filter']):r for r in mapping['rows']}
    ogle=[]
    for line_number,line in enumerate((directory/'OGLE-2011-BLG-0462-new.txt').read_text().splitlines(),1):
        if not line.strip() or line.lstrip().startswith('#'):continue
        fields=line.split()
        if len(fields)!=4:raise ValueError('Expected four native OGLE columns')
        hjd,mag,error,seeing=map(float,fields)
        ogle.append({'source_row_id':f'Mroz2022-Zenodo20056044:line:{line_number}','source_line_number':line_number,'native_HJD':hjd,'magnitude':mag,'magnitude_error':error,'seeing_pixels':seeing,
            'selection_status':'INCLUDED' if all_ogle_rows or 2455376<=hjd<=2457700 else 'EXCLUDED_PUBLICATION_WINDOW'})
    selected=[r for r in ogle if r['selection_status']=='INCLUDED']
    ra,dec=267.9174583333,-29.89063888889
    # Geocentre approximation to actual Las Campanas light time is bounded by
    # Earth radius/c=0.0213sec, covered separately in the +/-120sec clock screen.
    site=EarthLocation.from_geocentric(0*u.m,0*u.m,0*u.m)
    times=hjd_utc_to_tdb([r['native_HJD'] for r in selected],ra,dec,site,clock_offset_seconds)
    phot=[dict(row,time_jd_tdb=float(t),instrument='OGLE') for row,t in zip(selected,times)]
    astro=[];filter_name=None
    for line_number,line in enumerate((directory/'LamLu2023v2__hst_data_table.txt').read_text().splitlines(),1):
        if line.startswith('F'):filter_name=line.split()[0]
        if not re.match(r'^\d{4}-\d{2}-\d{2}',line):continue
        date=line.split()[0];numbers=re.findall(r'([-+]?\d+(?:\.\d+)?)\s*\$\\pm\$\s*([-+]?\d+(?:\.\d+)?)',line)
        if len(numbers)!=3:raise ValueError('Expected native HST east,north,magnitude pairs')
        (east,se),(north,sn),(mag,sm)=[tuple(map(float,pair)) for pair in numbers]
        m=byvisit[(date,filter_name)];exposures=[]
        for root,expected_sha in zip(m['rootnames'],m['source_header_prefix_sha256']):
            h=byroot[root]
            if h['sha256']!=expected_sha:raise ValueError('Mapped header identity mismatch')
            hp=directory/'MAST_header_prefixes'/PureWindowsPath(h['archived_path']).name
            # Archived receipt paths are Windows provenance only; use a platform-independent basename.
            if hashlib.sha256(hp.read_bytes()).hexdigest()!=expected_sha:raise ValueError('Archived complete primary header hash mismatch')
            exposures.append({'rootname':root,'mjd_utc_start':h['header']['EXPSTART'],'mjd_utc_end':h['header']['EXPEND'],'duration_seconds':h['header']['EXPTIME'],'header_sha256':expected_sha,'source_url':h['url']})
        mid=Time([(e['mjd_utc_start']+e['mjd_utc_end'])/2 for e in exposures],format='mjd',scale='utc').tdb.jd.tolist()
        window=Time([m['mjd_utc_window_start'],m['mjd_utc_window_end']],format='mjd',scale='utc').tdb.jd.tolist()
        sid=f'LamLu2023v2-HST-Table2:line:{line_number}'
        common={'source_row_id':sid,'source_line_number':line_number,'native_calendar_date':date,'filter':filter_name,'visit_id':date,'exposure_midpoints_jd_tdb':mid,'exposure_window_jd_tdb':window,'native_exposure_metadata':exposures,
          'combined_epoch_status':'UNKNOWN_ORIGINAL_WEIGHTS; ALL_ACTUAL_MIDPOINTS_BASELINE; FULL_WINDOW_SENSITIVITY'}
        astro.append(dict(common,north_mas=north,east_mas=east,north_error_mas=sn,east_error_mas=se))
        phot.append(dict(common,source_row_id=sid+':photometry',instrument='HST_'+filter_name,time_jd_tdb=float(np.mean(mid)),magnitude=mag,magnitude_error=sm))
    if len(ogle)!=15533 or len(astro)!=21:raise ValueError('Frozen source row count mismatch')
    document={'schema':JOINT_SCHEMA,'data_version':'OGLE-Mroz2022-corrected_LamLu2023v2-HST21-MAST82.v1','target':'OGLE-2011-BLG-0462/MOA-2011-BLG-191','time_coordinate':'JD_TDB','reference_jd_tdb':2456000.,'ra_deg':ra,'dec_deg':dec,'ephemeris':'builtin',
      'metadata':{'ra_axis':'EAST_TANGENT_ALPHA_COS_DEC','time_and_frame_provenance':{
        'OGLE':'Native full HJD. Underlying clock unspecified in author deposit; explicitly assumed HJD_UTC, inverted heliocentric light time at geocentre then converted TDB. Earth-surface light time <=0.0213sec omitted; +/-120sec clock sensitivity required.',
        'OGLE_clock_offset_seconds':clock_offset_seconds,'HST':'Calendar dates mapped by program/filter/count/duration to82 complete MAST FLC primary headers. UTC default crosschecked to DATE/TIME-OBS; exposure midpoints derived. Original combined centroid/photometry weighting unknown; full-window sensitivity required.',
        'frame':'Published relative alpha_star/east,delta/north tangent plane, inherited Lam2022 ApJS26055 section5. Relative frame position/motion/parallax nuisance; no absolute Gaia transform asserted.'},
        'selection':'All15533 source rows retained. Primary fit uses published2023 HJD2455376..2457700 window; all-row sensitivity mandatory.' if not all_ogle_rows else 'All15533 author OGLE source rows included sensitivity.',
        'calibration':'Published2023 neighbor-bias corrections and additive photometric/astrometric errors are already applied. No2022 filter correction reapplied. Full cross-covariance not supplied.',
        'licenses':[{'source':'LamLu2023 arXiv2308.03302v2','license':'CC-BY4.0','url':'https://arxiv.org/abs/2308.03302'},{'source':'Mroz2022 correctedOGLE Zenodo20056044','license':'CC-BY4.0','url':'https://doi.org/10.5281/zenodo.20056044'}],
        'source_urls':['https://arxiv.org/src/2308.03302v2','https://zenodo.org/api/records/20056044/files/OGLE-2011-BLG-0462-new.txt/content']},
      'native_files':native,'native_OGLE_all_rows':ogle,'photometry':phot,'astrometry':astro}
    return JointData(document)
