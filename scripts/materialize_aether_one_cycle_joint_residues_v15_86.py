from pathlib import Path

from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
