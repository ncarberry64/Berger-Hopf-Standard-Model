# BHSM N=3 third direct-residual JFNK v18.43

This calculation applies the measured v18.42 direct response to one bounded
right-mapped square-KKT proposal cycle. It changes no residual row or physical
acceptance condition.

The resulting direction leaves the measured response plateau with relative
change `0.021724142951282`; GMRES returns `info=1` and relative exact linear
residual `0.803797031478029`. The Newton model is therefore invalidated. Its
line is nevertheless evaluated independently. The lowest exact-merit candidate
has norm `0.816723990665515`, reduction `0.007538395533142`, and positive eta,
pending the complete-child gate.
