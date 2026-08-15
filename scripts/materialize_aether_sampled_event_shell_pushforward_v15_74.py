from pathlib import Path

from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
