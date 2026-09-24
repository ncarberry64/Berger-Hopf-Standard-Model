from pathlib import Path
import numpy as np

p = Path(
    "artifacts/action_extension/"
    "BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz"
)

with np.load(p, allow_pickle=False) as z:

    print("=" * 100)
    print("GATE-7 GREEN-IMAGE AMPLITUDE INVENTORY")
    print("=" * 100)

    print("\nKEYS:")
    for k in z.files:
        a = np.asarray(z[k])

        if np.issubdtype(a.dtype, np.number):
            finite = np.asarray(a, dtype=float)
            vals = finite[np.isfinite(finite)]

            if vals.size:
                lo = float(vals.min())
                hi = float(vals.max())
            else:
                lo = hi = float("nan")

            print(
                f"{k:60s} "
                f"shape={str(a.shape):20s} "
                f"dtype={str(a.dtype):10s} "
                f"range=[{lo:+.6e},{hi:+.6e}]"
            )
        else:
            print(
                f"{k:60s} "
                f"shape={str(a.shape):20s} "
                f"dtype={str(a.dtype)}"
            )

    unit_key = "current_center_green_image_unit_mid"

    if unit_key not in z:
        raise KeyError(unit_key)

    U = np.asarray(z[unit_key], dtype=float)

    phi = U[14]
    phi /= np.linalg.norm(phi)

    print()
    print("=" * 100)
    print("ARRAYS COMPATIBLE WITH AXIS-14")
    print("=" * 100)

    for k in z.files:

        if k == unit_key:
            continue

        try:
            a = np.asarray(z[k], dtype=float)
        except Exception:
            continue

        # Same 2-D family shape: examine row 14.
        if (
            a.ndim == 2
            and a.shape[0] > 14
            and a.shape[1] == 74
        ):
            v = a[14]

            n = float(np.linalg.norm(v))

            if n > 0:
                projection = float(v @ phi)
                cosine = projection / n

                print()
                print("KEY =", k)
                print("row14 norm       =", f"{n:.16e}")
                print("projection on φ  =", f"{projection:+.16e}")
                print("cosine with φ    =", f"{cosine:+.16e}")
                print(
                    "orthogonal norm    =",
                    f"{np.linalg.norm(v-projection*phi):.16e}",
                )

        # One vector in the same physical input space.
        elif a.ndim == 1 and a.shape[0] == 74:

            n = float(np.linalg.norm(a))

            if n > 0:
                projection = float(a @ phi)
                cosine = projection / n

                print()
                print("KEY =", k)
                print("vector norm      =", f"{n:.16e}")
                print("projection on φ  =", f"{projection:+.16e}")
                print("cosine with φ    =", f"{cosine:+.16e}")

    print()
    print("=" * 100)
    print("SCALAR / SCALE-LIKE ENTRIES")
    print("=" * 100)

    for k in z.files:

        kl = k.lower()

        if any(
            word in kl
            for word in (
                "norm",
                "scale",
                "radius",
                "amplitude",
                "charge",
                "green",
                "current",
                "weight",
                "coefficient",
            )
        ):
            a = np.asarray(z[k])

            if a.size <= 100:
                print()
                print(k, "=", a)

print("\nDONE")
