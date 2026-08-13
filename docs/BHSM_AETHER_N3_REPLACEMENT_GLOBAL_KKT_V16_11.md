# BHSM anchored N=3 replacement KKT v16.11

The selected reset is constant on its event component. Therefore its ten
(N=3) reset coordinates are fixed, and the reset also anchors cycle time.
The square event-constrained replacement problem has

\[
 23(10)+24(6)+1_T+1_{\rho_{\rm event}}=376
\]

unknowns. Its equations are the 375 stationarity equations of

\[
 \Gamma_Q=\Gamma_{\rm attached}^{\zeta}-\Gamma_{\rm SM}^{\zeta}
          +\Gamma_{\rm SM}^{\rm heat}
\]

plus the Euler--Dirac event equation. The former 386 count retained the ten
fixed reset coordinates, introduced a redundant phase multiplier, and omitted
the multiplier of the event equation.

The initial collocation seed is sampled only from the strictly admissible
portion of the independently reintegrated N=3 orbit. The common heat geometry
force is evaluated on that same seed using the gauge--ghost--rank16--HS direct
sum. It is not inserted as a local acceleration; it is a block of the global
replacement action whose complete 376-variable derivative is the next solve.
