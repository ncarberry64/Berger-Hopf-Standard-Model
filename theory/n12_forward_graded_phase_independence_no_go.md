# N12 graded phase-independence no-go

The retained matter-domain no-go leaves one unchanged-action escape route: a
theorem that the complete graded Gate-7 response is independent of every
surviving boundary phase. Ward/BRST does not provide such a structural
identity.

For the common scalar Cayley subfamily, the exact half-line temporal relative
heat trace is

```text
Tr(exp(-t K_h)-exp(-t K_0))
  = [exp(h^2 t) erfc(h sqrt(t))-1]/2.
```

At `t=h=1` this is `-0.2862082119220965`. The retained matter spatial
supertrace after the exact longitudinal/ghost cancellation is

```text
4 sum_(m>=1) m^2 exp(-a m^2)
-48 sum_(n>=0) (n+1)(n+2) exp(-a(n+3/2)^2).
```

At `a=1`, a 20-level sum plus an analytic Gaussian integral tail enclosure is
strictly below `-8.9`, with remainder below `1e-150`. Their product is
therefore strictly positive. The graded heat response changes with the
allowed matter phase at one heat time, so no mode-by-mode or heat-time Ward/
BRST phase-independence identity exists.

This does not promote one heat time to the complete regulated `E1` integral
and does not exclude a highly nontrivial cancellation for the actual full
history at the one retained regulator. Such an actual theorem would have to
cover the entire surviving Cayley family. In its absence, the exact next
action-native object is the normal matter boundary generator already missing
from the retained action. No phase or boundary term is added.
