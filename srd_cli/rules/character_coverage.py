"""Explicit mechanic support registry; availability never implies execution."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from srd_cli.normalized import NormalizedRepository


class SupportDisposition(str, Enum):
    STRUCTURED = "structured"
    STRUCTURAL_ONLY = "structural-only"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class CoverageEntry:
    source_key: str
    table: str
    disposition: SupportDisposition
    reason: str


TABLES = ("ClassFeature.json", "SpeciesTrait.json", "BackgroundBenefit.json", "FeatBenefit.json")


def build_coverage(repo: NormalizedRepository | None = None) -> tuple[CoverageEntry, ...]:
    repo = repo or NormalizedRepository()
    rows = [
        CoverageEntry(
            x.pk,
            table,
            SupportDisposition.STRUCTURAL_ONLY,
            "structural grant available; procedural prose requires typed adapter",
        )
        for table in TABLES
        for x in repo.load(table)
    ]
    keys = [x.source_key for x in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("coverage: duplicate source key")
    return tuple(sorted(rows, key=lambda x: (x.table, x.source_key)))


def validate_coverage(
    entries: tuple[CoverageEntry, ...], repo: NormalizedRepository | None = None
) -> None:
    expected = {
        (table, x.pk) for table in TABLES for x in (repo or NormalizedRepository()).load(table)
    }
    actual = {(x.table, x.source_key) for x in entries}
    if len(actual) != len(entries) or actual != expected:
        raise ValueError("coverage: unknown, duplicate, stale, or missing entry")
    if any(not x.reason.strip() for x in entries):
        raise ValueError("coverage: reason must not be blank")
