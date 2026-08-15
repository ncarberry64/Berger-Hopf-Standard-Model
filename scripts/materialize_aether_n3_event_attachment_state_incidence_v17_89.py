"""Materialize the v17.89 event attachment-state incidence map."""
from pathlib import Path

from bhsm.interface.aether_n3_event_attachment_state_incidence_v17_89 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
