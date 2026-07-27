"""User-authored runtime content boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_RUNTIME_BYTES = 1_000_000
MAX_RUNTIME_DEPTH = 32


def _depth(value: Any, level: int = 0) -> int:
    if level > MAX_RUNTIME_DEPTH:
        raise ValueError("runtime payload exceeds maximum depth")
    if isinstance(value, dict):
        return max((_depth(k, level + 1) for k in value), default=level) if not value else max(
            [_depth(k, level + 1) for k in value] + [_depth(v, level + 1) for v in value.values()]
        )
    if isinstance(value, (list, tuple)):
        return max((_depth(v, level + 1) for v in value), default=level)
    if not isinstance(value, (str, int, float, bool, bytes, type(None))):
        raise ValueError("runtime payload is not JSON-like")
    return level


def validate_runtime_payload(value: Any) -> None:
    _depth(value)
    if isinstance(value, bytes):
        size = len(value)
    else:
        size = len(json.dumps(value, ensure_ascii=False, allow_nan=False).encode())
    if size > MAX_RUNTIME_BYTES:
        raise ValueError("runtime payload exceeds maximum bytes")


@dataclass(frozen=True, slots=True)
class RuntimeContentRef:
    path: str
    source_label: str
    provenance: str = "user-authored"

    def __post_init__(self) -> None:
        if self.provenance != "user-authored":
            raise ValueError("runtime provenance must be user-authored")
        if not self.source_label.strip():
            raise ValueError("runtime source label is required")

    @classmethod
    def validated(
        cls, path: str | Path, runtime_root: str | Path, source_label: str
    ) -> "RuntimeContentRef":
        candidate = Path(path)
        root = Path(runtime_root).resolve(strict=True)
        resolved = (root / candidate).resolve(strict=True) if not candidate.is_absolute() else candidate.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError("runtime content escapes configured root") from exc
        from openrpg_cli.data import DATA_ROOT

        bundled = DATA_ROOT.resolve()
        if resolved == bundled or bundled in resolved.parents:
            raise ValueError("runtime content cannot use bundled SRD data root")
        return cls(str(resolved), source_label)
