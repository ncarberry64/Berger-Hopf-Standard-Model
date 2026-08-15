# BHSM N=3 covector-consistent soft-branch curvature v16.53

The terminal soft eigenvalue remains spectrally isolated at v16.49, but the
old `1e-4` scalar second-difference stencil leaves its local ordered-eigenvalue
chart for terminal scale perturbations. This checkpoint instead differentiates
the normalized event covector itself at `1e-5`, within the audited smooth
chart, and tests its merit direction after exact event-multiplier elimination.

This corrects an upstream numerical curvature object. It adds no physical
variable, branch, event, or independent normalization.
