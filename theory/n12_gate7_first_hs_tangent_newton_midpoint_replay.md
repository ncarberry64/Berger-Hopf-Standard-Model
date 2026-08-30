# Exact midpoint replay of the intrinsic tangent step

For every one of the 370 intervals, the Hermite--Simpson midpoint is rebuilt
from the tangent-corrected, nonlinearly constraint-projected endpoints and
their exact endpoint fields.  The retained exact field oracle is evaluated at
every rebuilt midpoint.  The resulting 99-dimensional shooting residual is
compared directly with the accepted first-HS residual.

Only strict nonlinear reduction accepts the intrinsic tangent derivative as
progress.  This remains numerical center construction, not a continuous
interval shadow or a Gate-7 promotion.
