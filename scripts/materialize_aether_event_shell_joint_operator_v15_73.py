from pathlib import Path

from bhsm.interface.aether_event_shell_joint_operator_v15_73 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
