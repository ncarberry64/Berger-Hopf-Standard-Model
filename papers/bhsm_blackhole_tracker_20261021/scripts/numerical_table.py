from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
j=json.loads((ROOT/'results/tracker_response.json').read_text())
g=j['geometry'];e=j['exterior'];s=j['physical_state'];x=j['experiment']
rows=[('Mass',r'$10^9M_\odot$'),('Worldtube / Einstein radius',f"{e['r0_pc']:.1f} / {g['rE_pc']:.2f} pc"),
      ('Screening radius',f"{e['rV_pc']/1000:.5f} kpc"),
      ('Worldtube compactness',r'$%.3g\times10^{-6}$'%(e['worldtube_compactness']*1e6)),
      ('Boundary amplitude / optical amplitude',r'$%.3g\times10^{-16}$ / $%.3g\times10^{-13}$'%(s['boundary_amplitude']*1e16,s['dimensionless_lens_amplitude']*1e13)),
      ('Joint-pair nuisance rank',str(x['full_pair']['nuisance_rank'])),
      ('Projected envelope singular values',', '.join(f'{v:.5f}' for v in x['full_pair']['projected_signal_singular_values'])),
      ('Retained column-norm fractions',', '.join(f'{v:.5f}' for v in x['full_pair']['retained_signal_norm_fractions'])),
      ('Largest tested physical coordinate shift',r'$%.3g\times10^{-5}$ nanoarcsec'%(s['max_position_shift_nanoarcsec']*1e5)),
      ('Tested physical log-flux-ratio shift',r'$%.3g\times10^{-12}$'%(s['log_flux_ratio_shift']*1e12))]
txt=r'''\begin{table}[t]
\centering\small
\caption{Declared conditional example and local information result. The last
two rows use the small supplied state at source $(0.9,0.6)$; the singular
values use unit optical phase amplitudes and the stated dimensionless data metric.}
\begin{tabular}{p{.49\linewidth}p{.42\linewidth}}
\toprule Quantity & Value\\\midrule
'''
txt+='\n'.join(a+' & '+b+r'\\' for a,b in rows)
txt+='\n'+r'\bottomrule\end{tabular}\label{tab:numeric}\end{table}'+'\n'
(ROOT/'manuscript/numerical_table.tex').write_text(txt,encoding='utf8')
print('Numerical manuscript table generated from tracker_response.json.')
