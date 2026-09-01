# First-HS recentered endpoint-rate consistency

The earlier endpoint adapter evaluated the normalized field using an inherited
descriptor and only afterward stored the selected eigenvalue as the recentered
descriptor.  Its endpoint state and descriptor were therefore paired with a
rate evaluated at a different augmented state.

This repair keeps every endpoint state and recentered descriptor unchanged and
directly reevaluates the retained exact field at that pair.  The old rates are
retained only as superseded diagnostics.  The repaired endpoint data become a
collocation source only after all exact midpoint fields are replayed.
