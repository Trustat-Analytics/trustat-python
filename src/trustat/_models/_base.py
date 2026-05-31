"""Base class for all generated Trustat response models.

Hand-written (the code generator is configured to make every model inherit from
this via ``--base-class``). Configured for **forward-compatibility**: fields the
API adds in the future are preserved (``extra="allow"``) instead of being dropped
or rejected, so an older SDK keeps working against a newer API.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class TrustatModel(BaseModel):
    """Pydantic v2 base for Trustat API models."""

    model_config = ConfigDict(
        extra="allow",  # keep unknown/new server fields instead of dropping them
        populate_by_name=True,  # accept either the field name or its alias
        protected_namespaces=(),  # allow fields like ``model_*`` without warnings
    )

    def __repr_args__(self) -> Any:  # pragma: no cover - cosmetic
        # Hide ``None`` values from the repr so model objects read cleanly in a REPL.
        return [(k, v) for k, v in super().__repr_args__() if v is not None]
