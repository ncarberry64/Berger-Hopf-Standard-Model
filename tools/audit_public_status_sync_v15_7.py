#!/usr/bin/env python3
"""Print and enforce the v15.7 public-status synchronization contract."""
from __future__ import annotations

import json

from bhsm.interface.public_status_sync_v15_7 import audit_payload


def main() -> int:
    payload = audit_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
