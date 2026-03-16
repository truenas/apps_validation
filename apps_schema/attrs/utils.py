from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseSchema

ATTRIBUTES_SCHEMA: dict[str, type[BaseSchema]] = {}
