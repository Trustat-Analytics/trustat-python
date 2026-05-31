from __future__ import annotations

from trustat import ChannelInfo
from trustat._models._base import TrustatModel


def test_forward_compat_preserves_unknown_fields():
    # A field the API adds in the future must be kept, not dropped or rejected.
    raw = {"channel_id": 1, "title": "X", "source": "telegram", "shiny_new_2027_field": "keep me"}
    ch = ChannelInfo.model_validate(raw)
    assert ch.channel_id == 1
    assert ch.shiny_new_2027_field == "keep me"  # type: ignore[attr-defined]
    assert ch.model_dump()["shiny_new_2027_field"] == "keep me"


def test_models_inherit_base():
    assert issubclass(ChannelInfo, TrustatModel)


def test_repr_hides_none():
    ch = ChannelInfo.model_validate({"channel_id": 1})
    text = repr(ch)
    assert "channel_id=1" in text
    assert "title=None" not in text  # None fields hidden for a clean repr
