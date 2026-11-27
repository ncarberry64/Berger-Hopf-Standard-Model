# HE 0435−1223: anisotropic scalar trace and flux transmission control

Use the radial stellar R1 coefficient on both sides of each candidate launch radius, with the primary Sluse group astrometric axis and velocity-dispersion SIS proxy. Inside, source by the exact angular (l=2) of the offset group's matter density. Outside, prescribe an incident scalar profile equal to the exact (l=2) of the *isolated nonlinear spherical* group R1 solution, plus a homogeneous radial-stellar decaying response. The decaying response is integrated backward from 100 Mpc, not assigned the flat Laplace power at 20–120 kpc. For exterior (f_o=g+c v) and identical conormal operator (a_* d/dr), the interior obeys (f_i'-(v'/v)f_i=g'-(v'/v)g). This conditions both value and flux. There is no free layer, tuned amplitude, or timing input.

| Launch radius (kpc) | (a_*/C) | Matched boundary value / isolated value | Relative trace/flux mismatch | (l=2) inner-15 kpc pairwise deflection (mas) | Implied exterior forcing / actual local matter (J_2) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 31.89 | 1.151 | ≤1.6e−16 | .000745 | −619 |
| 40 | 11.92 | 1.167 | ≤1.6e−16 | .001017 | −58.4 |
| 80 | 4.39 | 1.162 | ≤3.2e−16 | .001387 | −4.55 |
| 120 | 2.54 | 1.157 | ≤3.4e−16 | .001665 | −.737 |

The flux residual is a structural check by construction, not evidence of a correct exterior. The forcing ratio exposes a specific failure: the implied exterior source (\mathcal L_* g) does not equal the actual group quadrupole source. The latter is small near the galaxy and does not normalize the total tide. The optics column compares the **same interior path window** and has a 2.24× range as the exterior driving prescription changes. Outer rays, rearranged group self-screening, and nonlinear angular mode mixing remain unsolved. The anisotropic scalar lensing contribution is not a prediction to the quoted digits. This experiment explains why one cannot finish the physical calculation using an isolated incident group field and formal flux equality alone.

Replay: `PYTHONDONTWRITEBYTECODE=1 python he0435_radial_exterior_l2.py`. Results: `he0435_radial_exterior_l2.json`.
