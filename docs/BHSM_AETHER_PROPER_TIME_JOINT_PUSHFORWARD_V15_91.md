# BHSM v15.91: proper-time joint pushforward

The physical period uses boundary proper time,

\[
 d\tau=N_b(t)dt,
 \qquad
 \Gamma_{\rm cyc}=\int_0^{T_*}d\tau\,\Gamma_{\rm proper}(t)
 +\Gamma_{\rm reset}.
\]

For

\[
 ds_5^2=-N^2dt^2+C^2(d\chi+\beta dt)^2+r^2d\Omega_3^2,
\]

an interior radial diffeomorphism fixed at the boundary gives zero-shift
gauge. The local magnetic and electric weights are then

\[
 I_B=\int d\chi\,\mathcal KWN\frac{C}{r},
 \qquad
 I_E=\int d\chi\,\mathcal KW\frac{Cr}{N},
\]

and proper boundary normalization gives

\[
 K_B=\frac{R_bI_B}{N_b},
 \qquad
 K_E=\frac{N_bI_E}{R_b}.
\]

Using the same proper-time measure for these gauge derivatives and the
composite determinant gives

\[
 \overline K_B=813.476975,
 \qquad \overline K_E=2717.004292,
\]

\[
 Z_H^{\rm proper}=0.00176673551,
 \qquad Y_f^{\rm proper}=23.7910840I_3.
\]

The proper logarithmic mean scale is

\[
 \mu_{\rm proper}=0.97837264\,\ell_\kappa^{-1}.
\]

The gauge-cone test is not satisfied:

\[
 \frac{\overline K_E}{\overline K_B}=3.33998918,
 \qquad
 c_{\rm gauge}/c_{\rm metric}
 =\sqrt{\overline K_B/\overline K_E}=0.54717654.
\]

Accordingly, the coordinate-time averages in v15.86 and v15.89 remain valid
frozen-slice diagnostics but are superseded as physical cycle averages. Gauge
and Yukawa have not been separated: all corrected values are outputs of one
proper-time \(\Gamma_{\rm cyc}\). The next calculation is the full
shift-covariant frequency-dependent DtN Schur complement, including the event
and reset gluing contribution.
