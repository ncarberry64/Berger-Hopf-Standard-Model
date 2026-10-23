"""Independent volume quadrature and geodesic finite-difference checks."""
from pathlib import Path
import json
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from angular_geometry import harmonic_basis, normalization, embedding, screen, harmonic, screen_hessian_tf


def second_difference(a, x, v, radius, h):
    plus = np.cos(h) * x + np.sin(h) * v
    minus = np.cos(h) * x - np.sin(h) * v
    return (harmonic(a, plus, radius) + harmonic(a, minus, radius)
            - 2. * harmonic(a, x, radius)) / (radius * h)**2


def run():
    radius = 1. / np.sqrt(.018)
    names, matrices = harmonic_basis()
    ug, uw = leggauss(32); u = .5 * np.pi * (ug + 1.); uw *= .5 * np.pi
    mu, mw = leggauss(12)
    phi = 2. * np.pi * np.arange(24) / 24.
    uu, mm, pp = np.meshgrid(u, mu, phi, indexing="ij")
    x = np.stack([np.cos(uu), np.sin(uu)*np.sqrt(1.-mm**2)*np.cos(pp),
                  np.sin(uu)*np.sqrt(1.-mm**2)*np.sin(pp), np.sin(uu)*mm], axis=-1)
    weights = radius**3 * np.sin(uu)**2 * uw[:, None, None] * mw[None, :, None] * (2.*np.pi/24.)
    vals = normalization(radius) * np.einsum("...i,kij,...j->...k", x, matrices, x)
    gram = np.einsum("pi,pj,p->ij", vals.reshape(-1, 9), vals.reshape(-1, 9), weights.reshape(-1))
    directions = [np.array(v, float) / np.linalg.norm(v) for v in [(0,0,1), (1,2,3), (-2,1,1), (1,-3,.4)]]
    receipts = []
    for h in [1.e-3, 5.e-4, 2.5e-4]:
        hessian_error = 0.; laplacian_error = 0.; zero_channel = 0.
        for u0 in [.27, .8, 1.7, 2.8]:
            for n in directions:
                x0 = embedding(u0, n)
                e = screen(n)
                tangents = [np.r_[-np.sin(u0), np.cos(u0)*n], np.r_[0.,e[:,0]], np.r_[0.,e[:,1]]]
                for k, a in enumerate(matrices):
                    second = [second_difference(a, x0, v, radius, h) for v in tangents]
                    mixed = second_difference(a, x0, (tangents[1]+tangents[2])/np.sqrt(2.), radius, h)
                    h12 = mixed - .5*(second[1]+second[2])
                    numeric = np.array([[.5*(second[1]-second[2]), h12], [h12, .5*(second[2]-second[1])]])
                    exact = screen_hessian_tf(a, n, radius)
                    hessian_error = max(hessian_error, float(np.max(np.abs(numeric-exact))))
                    laplacian_error = max(laplacian_error, abs(sum(second)+8.*harmonic(a,x0,radius)/radius**2))
                    if k < 4:
                        zero_channel = max(zero_channel, float(np.max(np.abs(numeric))))
        receipts.append({"geodesic_step_radians":h,"screen_hessian_max_absolute_error":hessian_error,
                         "laplacian_max_absolute_error":laplacian_error,"monopole_dipole_max_numeric_tf":zero_channel})
    result = {"sphere_radius_in_c_over_H0":radius,"basis_order":names,
              "normalization":normalization(radius),"quadrature_gram_matrix":gram.tolist(),
              "normalization_max_absolute_error":float(np.max(np.abs(gram-np.eye(9)))),
              "finite_difference_checks":receipts,
              "analytic_shear_rank_by_sector":{"monopole":0,"dipole":0,"quadrupole":5},
              "scope":"first-order scalar smooth-background optical screen forcing; not full strong-lens shear"}
    assert result["normalization_max_absolute_error"] < 5.e-13
    assert receipts[-1]["screen_hessian_max_absolute_error"] < 2.e-10
    assert receipts[-1]["laplacian_max_absolute_error"] < 5.e-10
    out = ROOT / "artifacts" / "angular_geometry_checks.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"normalization_error":result["normalization_max_absolute_error"],"last_fd":receipts[-1]},indent=2))


if __name__ == "__main__":
    run()
