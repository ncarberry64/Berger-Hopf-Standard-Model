# BHSM Neutral Dimensionful Scale

Status: `OPEN_MISSING_NEUTRAL_SCALE`.

BHSM currently distinguishes dimensionless neutrino propagation closure from physical eV/GeV mass closure.

A physical eV/GeV neutrino mass requires an artifact-backed or explicitly conditional neutral dimensionful scale.

The local audit finds no eligible neutral unit anchor. The boundary package
provides dimensionless `tau`, `sigma`, and `kappa_H`; the neutral operator
provides dimensionless `K_nu`, `g_nu`, `beta_nu`, and `kappa_nu`. The author
ontology names `dmu_boundary dt`, but neither its physical dimension nor its
normalization is supplied. No artifact maps the neutral curvature threshold to
an energy.

The W-anchored interface example is an empirical calibration path and is not
eligible for this theorem. Electron-neutrino limits and PDG/reference values
remain comparison-only.

The electron-neutrino upper limit is a comparison reference only and is never used to set the neutral scale.

A dimensionless BHSM response is not, by itself, a physical eV/GeV mass.

The next required object is an action-backed physical normalization of the
neutral boundary measure or background stiffness, together with a derived
threshold-to-energy map.

The v1.1 legacy corpus now supplies an artifact-backed curvature mass
functional. It narrows the missing bridge to a physical neutral propagation
radius and a physical response-to-curvature map; it does not supply either
quantity by itself.
