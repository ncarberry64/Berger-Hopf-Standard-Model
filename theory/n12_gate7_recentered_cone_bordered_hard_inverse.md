# N=12 Gate-7 recentered-cone bordered hard inverse

The certified branch-24 boundary gap and selected-projector graph are now
composed on every one of the 3,009 cells in the common recentered-cone mesh.
For the normalized bordered descriptor, its instantaneous singular values are
the two unit border values together with the hard spectral distances
`abs(lambda_j-lambda_24)`.  The inverse norm is therefore bounded without
inverting a kinetic, Euler--Dirac, or history block.

The moving selected-line chart contributes the explicit condition factor
`(1+m)/(1-m)`, where `m` is the certified projector motion on that cell.
Thus each charted inverse bound is the product of this factor and
`max(1,1/gap)`.  This closes only the homogeneous hard inverse.  The complete
internal AE2 seam/right-hand side must still be assembled before any physical
response or zero-external-source statement is made.

The maximum charted inverse bound is `6.1001606088956e6`; the maximum chart
condition factor is `1.051975462181501`.  Both are certified on all 3,009
quarter-corrected carrier cells.
