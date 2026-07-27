"""Pure deterministic gameplay engine with cycle-safe lazy exports."""

from .rng import GameRNG

__all__ = ["GameRNG", "ReductionResult", "reduce_command"]


def __getattr__(name: str):
    if name in {"ReductionResult", "reduce_command"}:
        from .reducer import ReductionResult, reduce_command

        return {"ReductionResult": ReductionResult, "reduce_command": reduce_command}[name]
    raise AttributeError(name)
