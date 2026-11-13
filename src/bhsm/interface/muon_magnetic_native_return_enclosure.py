"""Preserve certified mean entry intervals in the inserted magnetic return."""
from __future__ import annotations
import numpy as np
from flint import acb,acb_mat,arb,ctx


def enclosed_magnetic_return(bare,real_lower,real_upper,imaginary,*,precision_bits=192):
    """Invert the exact three-axis inclusion, with interval native entries.

    The real bounds certify stored direct plus exact-stored adjoint mean.
    The imaginary entries retain their stored direct rounding. Source,
    direct heat formation, continuum and physical loop errors are excluded.
    This is not a quantum photon propagator or a Pauli amplitude.
    """
    values=[np.asarray(v) for v in (bare,real_lower,real_upper,imaginary)]
    if any(v.shape!=(8,8) or not np.isrealobj(v) or not np.isfinite(v).all() for v in values):
        raise ValueError('four complete real padded-eight magnetic coefficient arrays required')
    if any(np.any(v[3:]) or np.any(v[:,3:]) for v in values):
        raise ValueError('only three inserted axes have exact complementary zero columns')
    B,lo,hi,im=[v[:3,:3] for v in values]
    if np.any(lo>hi):raise ValueError('ordered certified entry bounds required')
    if type(precision_bits) is not int or precision_bits<128:raise ValueError('certified precision>=128 required')
    with ctx.workprec(precision_bits):
        A0=acb_mat([[float(x) for x in row] for row in B])
        # arb(float) binds the binary endpoint exactly. Hull construction
        # includes its complete interval, without a binary midpoint first.
        real=lambda i,j:(arb(float(lo[i,j]))+arb(float(hi[i,j])))/2+arb(0,
            (arb(float(hi[i,j]))-arb(float(lo[i,j])))/2)
        R=acb_mat([[acb(real(i,j),arb(float(im[i,j]))) for j in range(3)] for i in range(3)])
        I=acb_mat(np.eye(3).tolist());U0=A0.solve(I);U=(A0+R).solve(I);delta=-U0*R*U
        defect=U-U0-delta;residual=(A0+R)*U-I
        if not all(defect[i,j].contains(0) for i in range(3) for j in range(3)):
            raise ArithmeticError('interval return identity failed')
        down=lambda v:float(np.nextafter(float(v.lower()),-np.inf)) if not v.is_zero() else 0.
        up=lambda v:float(np.nextafter(float(v.upper()),np.inf)) if not v.is_zero() else 0.
        part=lambda component,f:np.array([[f(getattr(delta[i,j],component)) for j in range(3)] for i in range(3)])
        center=np.array([[complex(float(delta[i,j].real.mid()),float(delta[i,j].imag.mid())) for j in range(3)] for i in range(3)])
        return dict(stable_native_return=center,
            stable_native_return_real_lower=part('real',down),stable_native_return_real_upper=part('real',up),
            stable_native_return_imag_lower=part('imag',down),stable_native_return_imag_upper=part('imag',up),
            interval_inverse_residual_upper=max(up(abs(residual[i,j])) for i in range(3) for j in range(3)),
            interval_return_identity_defect_upper=max(up(abs(defect[i,j])) for i in range(3) for j in range(3)),
            active_source_indices=[0,1,2],spectral_conditioning_shift_added=False,
            pseudoinverse_or_absent_axis_inverse_used=False,native_real_entry_intervals_retained=True,
            source_return_promoted_to_quantum_propagator=False,
            error_scope='exact stored bare form, certified real mean plus stored direct, stored imaginary rounding; direct formation, response/ODE, heat truncation, native completion, overlap and soft-Pauli errors excluded')
