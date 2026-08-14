# BHSM N=3 second refreshed complete-merit Newton v18.03

This calculation refreshes the adopted v17.32-equivalent physical Jacobian at
the v18.02 event.  It keeps the original 376-row action residual, uses no
handcrafted direction mixture, and accepts global trial states by decrease of
the coupled norm plus the eta domain.  Event-to-complete-child reconstruction
remains the required final acceptance gate for any selected trial.

Nonzero motion, momentum, and time dependence are not rejection criteria.
Only constraint-consistent relative evolution and positive-duration
persistence determine whether a reconstructed child is complete.
