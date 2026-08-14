# BHSM N=3 complete-child merit promotion (v18.00)

The v17.83 direct Newton step was previously rejected solely because the
absolute event component increased slightly, even though the true 376-row
norm decreased and the eta domain remained positive. Now that the complete
event-to-child map exists, the correct acceptance rule is available.

The first direct trial is promoted only after re-solving its perturbed child
correspondence. The reconstructed child matches the event traces, seven local
constraints, two attachment momenta, and resolved dynamic flux balance; it
also remains eta-hyperregular through a positive evolution step.

The event component is still required to vanish at final convergence, but it
is not an independent line-search merit function. A small temporary increase
in one component is not a particle or motion defect when the coupled norm
decreases and the event still creates a complete persistent child.

No 377th KKT row, handcrafted direction mixture, or new numerical
infrastructure is introduced. Physical N=3 continuation resumes from this
promoted 376-variable state.
