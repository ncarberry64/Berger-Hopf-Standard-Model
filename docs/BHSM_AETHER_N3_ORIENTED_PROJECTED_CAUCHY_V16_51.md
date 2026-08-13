# BHSM N=3 derivative-oriented projected Cauchy continuation v16.51

At v16.49, the assembled-Hessian direction and the measured derivative of the
exactly projected residual disagree in sign. This checkpoint measures both
orientations, chooses only a genuinely negative projected directional
derivative, derives its Cauchy radius, and rejects zero-radius roundoff as
descent using a strict reduction margin.

This corrects the solver geometry exposed by v16.50. It does not alter the
BHSM action, physical variables, event, or common pushforward requirement.
