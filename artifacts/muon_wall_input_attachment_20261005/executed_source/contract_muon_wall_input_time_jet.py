"""Source-restricted cotangent of the known intrinsic principal time Gram.

This differentiates only the known input functional at the actual radial
projection. It is not an admissible native domain/source variation.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np


def run(source,out):
    if out.exists():raise FileExistsError('fresh output required')
    out.mkdir(parents=True)
    path=source/'node3_projected_intrinsic_kinetic.npz'
    with np.load(path,allow_pickle=False) as z:a={k:np.array(z[k]) for k in z.files}
    d=len(a['source_coordinates']);T=a['F1'][:,:d];P=a['F1'][:,d:];mu=float(a['M4'])
    derivative=mu*(P.conj().T@T+T.conj().T@P)
    c=a['source_coordinates'];contraction=np.vdot(c,derivative@c)
    np.savez_compressed(out/'principal_time_input_cotangent.npz',
        derivative_Cpp_under_delta_Theta_Xi=derivative,actual_Theta_time_action=P,
        delta_Theta_Xi_time_action=T,M4=mu,source_coordinates=c,output_contraction=contraction)
    result=dict(classification='known intrinsic principal-time input functional; not native wall or Pauli sensitivity',
        variation='delta_Theta_p=Xi_A at fixed instantaneous kinetic symbol; no native attachment selected',
        equation='delta Cpp=mu4*((c_tau Theta_p)^dagger c_tau delta_Theta+(c_tau delta_Theta)^dagger c_tau Theta_p)',
        derivative_norm=float(np.linalg.norm(derivative)),source_contraction_real=float(contraction.real),
        source_contraction_imag=float(contraction.imag),new_parent_points=0,new_stationary_solve=False,
        native_wall_variation_justified=False,physical_a_mu=None,physical_g_mu=None)
    for name,value in (('result.json',result),('input_hashes.json',dict(source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))):
        (out/name).write_bytes((json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.source,a.output)
