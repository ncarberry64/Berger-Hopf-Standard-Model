# Saved child-response residual partition, 19 October 2026

This diagnostic continues from `9a6c7766`. It consumes the saved actual
three-point and seventeen-point child applications, their original
coefficient probes, and their saved data. It performs no new field,
background, coefficient, Green, native or source solve. It neither chooses
a physical homogeneous state nor reconstructs an unarchived old field.
The numerical diagnosis is therefore evidence about the existing
coordinate-column response, not an additional physical state or a new
formation admission.

The saved event and input trace rows are small. The original differential
equation is not small on the held birth and incoming faces, and its
independent interior defects remain large. Those three statements refer
to different equations and must be retained together. The unchanged
physical admission threshold is `2e-10`; none of the results below
establishes physical admission.

## Inputs, equations and retained freedom

The executed diagnostic owner is
`src/bhsm/interface/muon_d5_saved_response_diagnostics.py`, SHA256
`de1e5fb4ee919049ea481e013c0ee6cd5cf045fcfbffe1651079a2e95361720f`.
The checkpoint is
`C:/Users/carbe/Downloads/BHSM_CAUSAL_DATA_20261019/RESPONSE_DIAGNOSTICS_v1/`.
Its `result.json` SHA256 is
`5e5346ac0e57c38fe5d8525b75a071b55f9370604c82eb99918f96308627610a`.
`BEFORE.json`, `executed_source_owner.py`, `executed_driver.py`, every
case receipt and every diagnostic array are preserved there. The result
pins every consumed archive, not merely its containing directory.

The primary original receipts, under
`artifacts/muon_d5_fermion_event_child_20261019/core/`, are:

| Receipt | SHA256 |
| --- | --- |
| `CHILD_CELL_v2/core_result.json` | `4bb17bde294bb73e25f3203e39a476d9dbbbe53426c0eaaf6fb5da1d01de06d6` |
| `CHILD_COEFFICIENT_PROBES_v1/result.json` | `825403d1698aa0d40a0cdc11c67de2a3263f03b44bfa95ad8709977ee8571484` |
| `CHILD_CORNER_v1/result.json` | `c16332838de041eafd2e83e3dbd4e7e8992aa729f50e43988cbf5ba7a4f12c20` |
| `EVENT_CHILD_CORNER_v1/result.json` | `42eb46a1b2be6e5fa988bca5a7a30a18f831b5d82f9338489f009a33cb478e00` |
| `CHILD_RADIAL17_v1/result.json` | `38be8cc1db2ab48510d037ba28ec8720d1ddd79415668bbdb019faba1a6d7ddb` |

For the original unsquared equation the executed contractions are

\[
 L[\Phi]=T\partial_t\Phi+R\partial_r\Phi+K\Phi,
\]
\[
 \delta L=(\delta T)\partial_t\Phi+(\delta R)\partial_r\Phi
 +(\delta K)\Phi+T\partial_t\delta\Phi
 +R\partial_r\delta\Phi+K\delta\Phi.
\]

All six first-variation terms are explicit. The source is a supplied
variation, not a conjugate of the field. Missing source arrays are
rejected. Unknown physical directions are not filled with zeros.

The three-point diagnostic covers all twelve candidate/eta/channel
cases, full384 carriers, three families and the matched MUON weak8
restrictions. The seventeen-point diagnostic covers both candidate maps,
both eta collars, both charge branches, and the consumed seed and
homogeneous channels: sixteen cases, each with its saved nine source
directions. All3660 parent homogeneous coordinates are retained;624 are
stored active columns in the consumed homogeneous subset. The same
parent homogeneous coordinates are shared by the two eta responses.
The112 additional birth coordinates per targeted weak8 branch and all
other fullcarrier data remain unassigned. A coordinate partial on the
evaluated data is not a declaration that its complementary physical data
vanish.

## Which original rows were enforced and which were held

The characteristic discretization enforces the original bulk equation
at positive-time interior nodes and the outgoing evolution rows at the
two radial faces. The latter are

\[
 Q_{\rm out}^{\dagger}T^{-1}L=0,
\quad
 \delta(T^{-1}L)=T^{-1}\delta L
       -T^{-1}(\delta T)T^{-1}L.
\]

It supplies birth values and future incoming characteristic values as
data. A small defect in those input trace equations is not a small
defect in their differential compatibility with the bulk equation.

For the saved candidate2, plus-eta, MUON particle weak8 homogeneous
columns, the seventeen-point application gives the following component
maxima at the original six time nodes. These are unweighted original
coordinate-column norms. Interior/birth rows use `L`; characteristic
face rows use `Q^dagger T^-1 L`.

| Row partition | Value | Particular supplied source |
| --- | ---: | ---: |
| Enforced positive-time interior `L` | `3.23379113e-6` | `1.29699707e-4` |
| Enforced outgoing evolution | `6.68689609e-7` | `6.10351563e-5` |
| Held incoming evolution | `5.09310554e8` | `1.08285427e11` |
| Held birth `L` | `3.30369891e8` | `4.89118315e10` |
| Independent nine interior points, original `L` | `1.28242771e7` | `2.40856463e9` |

For the same case, the supplied birth-value trace defect is
`1.23338839e-15` and its source defect is `1.51378909e-13`.
The supplied incoming trace defects are `1.66533454e-16` and
`3.10862447e-14`. The much larger held differential defects above remain
active despite these small input trace errors. The enforced absolute
differential defects also remain above the physical guard.

Raw consumed three-point nodal fields were not archived. Their
corresponding enforced-nodal partition is explicitly absent, with the
existing finite-stage receipts retained. No old Hermite reconstruction
has been performed to fill that gap. The original three-point
independent probes and all archived seventeen-point nodal values are
consumed directly. Only the particular supplied source has archived
seventeen-point nodal fields; the free-map and normal-rate directions
retain their independent-probe results without an invented nodal
partition.

## Corner compatibility and temporal data are separate checks

With `A=T^-1 R`, `P=T^-1 K`, the necessary first incoming corner germ is

\[
 \dot b(0)+Q_{\rm in}^{\dagger}
       [A\partial_r\Phi_0+P\Phi_0]=0.
\]

Its derivative includes both state and vertex terms, using
`delta(T^-1)=-T^-1 delta(T) T^-1`. The diagnostic differentiates the
supplied six-node incoming polynomial and the supplied birth
polynomial. It does not select a future incoming history.

For the same seventeen-point case, the separately evaluated incoming
time germ has maximum `2.9881406005923763e7`; the opposite PDE-implied
germ has maximum `2.9881406005924296e7`. Their difference is
`5.32716513e-7`. The source germs are `4.2204321955040894e9` and
`4.220432195504178e9`, with difference `8.86917114e-5`.
These absolute nonpasses and their cancellation scale are both
recorded. They do not imply compatibility of every higher time germ or
of the entire boundary history. The saved original corner-matrix
receipt, the directly regrouped germ, and their differing floating
summation errors are retained rather than replacing one by the other.

The three-point and seventeen-point incoming data arrays agree bitwise
for this case, for both value and source. Their common numerical time
interval has width `3.5264971511981203e-9`. The supplied incoming
polynomial has these coordinate diagnostics:

| Quantity | Value data | Particular source data |
| --- | ---: | ---: |
| Maximum input coefficient | `0.702511323` | `32.6499401` |
| Maximum coordinate first time derivative | `6.61104166e8` | `3.04089101e10` |
| Maximum coordinate second time derivative | `3.24845926e18` | `1.61458830e20` |
| Largest last-two Chebyshev modes / largest mode | `0.139751781` | `0.148406465` |
| Interval width times first derivative maximum | `2.33138196` | `107.236935` |
| Interval width squared times second derivative maximum | `40.3984311` | `2007.93142` |

The actual last-two value-mode maxima are `0.0456506417` and
`0.0447976909`. The high-mode content is present in the unchanged
temporal boundary data independently of the radial refinement. It is
not a temporal convergence estimate, a bound on missing modes, a new
physical incoming history, or permission to assign that history.
The seventeen-point field itself has a last-two-mode ratio
`0.0393358571`, and its particular source has ratio `0.101850827`.
No temporal refinement is performed in this diagnostic.

## Amplitudes and original differential terms

At the same independent nine points, the largest evaluated field
coefficient is `0.789588407` and its particular-source coefficient is
`45.1235036`. The coordinate time and radial gradients have maxima
`6.22584920e7` and `6.78573161e7`; their source gradients have maxima
`9.37897846e9` and `6.69110823e9`. These are amplitudes of particular
response columns. They are not amplitudes of a normalized physical
packet or a selected homogeneous combination.

| Original independent-point term | Component maximum |
| --- | ---: |
| `T Phi_t` | `8.85564932e7` |
| `R Phi_r` | `7.57383415e7` |
| `K Phi` | `2.72038509` |
| Sum `L` | `1.28242771e7` |
| `(delta T) Phi_t` | `8.71376381e7` |
| `(delta R) Phi_r` | `6.96493815e9` |
| `(delta K) Phi` | `57.1664781` |
| `T (delta Phi)_t` | `1.33406611e10` |
| `R (delta Phi)_r` | `7.75932910e9` |
| `K delta Phi` | `161.136754` |
| Sum `delta L` | `2.40856463e9` |

The maxima are evaluated separately and need not occur at the same
point or column. The value defect divided by the sum of the three term
maxima is `0.0780564823`; the analogous six-term source ratio is
`0.0855555189`. These conditioning diagnostics do not alter any norm,
rescale the physical guard, or establish a small error. They show that
the independent defects are appreciable in the derivative terms,
whereas the body term is much smaller for this coordinate application.
They alone do not prove a unique discretization mechanism or a
continuum bound.

The previously executed targeted radial comparison remains intact:
the three-point full384 plus homogeneous coordinate-column defect was
`5.88332129e8` in value and `2.95968264e10` in the particular source;
the targeted seventeen-point weak8 particle result is
`1.28242771e7` and `2.40856463e9`. Its input temporal polynomial is
unchanged. This comparison is about the recorded targeted subset;
neither the other fullcarrier directions nor the continuum are
certified by it. No further refinement has been attempted here.

## Norm, validation and next operand

Every case records unweighted original-coordinate component maxima,
Frobenius norms, shapes and source-slot identities. The interval-scaled
numbers above are conditioning information only. An admitted physical
unit conversion, a selected causal state, complete Cauchy/current norm
and complete physical domain variations are not provided by this
diagnostic. Their values remain `None` in its receipts. No physical
field amplitude, physical proper-time derivative or physical error
bound is inferred by relabeling these coordinate columns.

Three focused tests passed. They check the six original source terms,
complex-linear source placement, explicit missing-source rejection,
analytic polynomial bulk and corner germs, and the separation of chart
conditioning from physical norms. The existing numerical nonpasses and
the failed historical applications remain unchanged. No physical data
are selected by those tests.

`NEXT_OPERAND`: determine and consume the actual causal birth/outer data
from the original preparation and coupled equations, then apply the
saved original residual operators to that same particular-plus-shared-h
combination. Retain the independent incoming and higher birth ports,
both candidate maps, both eta collars and all3660 homogeneous
coordinates until their equations determine them. The adopted beams,
conditional incoming prescription, exact pair statistics, calibration,
once-only local/native accounting and physical guard are unchanged.
