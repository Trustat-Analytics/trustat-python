#!/usr/bin/env python3
"""Regenerate src/trustat/_models/models.py from the OpenAPI snapshot.

Models are GENERATED and must never be hand-edited — re-run this when the API
contract changes (refresh codegen/openapi_snapshot.json first), and commit the
result. The base class and forward-compat config live in _models/_base.py.

    python scripts/generate_models.py

Requires: pip install datamodel-code-generator
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "codegen" / "openapi_snapshot.json"
OUT = ROOT / "src" / "trustat" / "_models" / "models.py"

CMD = [
    "datamodel-codegen",
    "--input", str(SPEC),
    "--input-file-type", "openapi",
    "--output", str(OUT),
    "--output-model-type", "pydantic_v2.BaseModel",
    "--base-class", "trustat._models._base.TrustatModel",
    "--use-standard-collections",
    "--use-union-operator",
    "--use-annotated",
    "--target-python-version", "3.10",
    "--disable-timestamp",
    # Every field optional: a field the API later drops must not break an older SDK
    # (paired with extra="allow" in the base for added fields = full forward-compat).
    "--force-optional",
    "--use-field-description",
    "--use-schema-description",
]


def main() -> int:
    if not SPEC.exists():
        print(f"missing spec: {SPEC}", file=sys.stderr)
        return 1
    print("generating", OUT.relative_to(ROOT))
    return subprocess.call(CMD)


if __name__ == "__main__":
    raise SystemExit(main())
