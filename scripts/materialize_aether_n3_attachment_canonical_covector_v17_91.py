"""Materialize the v17.91 attachment canonical covector."""
from pathlib import Path

from bhsm.interface.aether_n3_attachment_canonical_covector_v17_91 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
