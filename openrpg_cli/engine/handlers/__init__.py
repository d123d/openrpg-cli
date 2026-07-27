"""Command handler groups."""

from .core import (
    handle_character,
    handle_create,
    handle_damage,
    handle_death_operation,
    handle_effect,
    handle_heal,
    handle_legacy,
    handle_phase7,
    handle_put,
    handle_resolve,
    handle_roll,
)

__all__ = [
    "handle_character",
    "handle_create",
    "handle_damage",
    "handle_death_operation",
    "handle_effect",
    "handle_heal",
    "handle_legacy",
    "handle_phase7",
    "handle_put",
    "handle_resolve",
    "handle_roll",
]
