"""Typed, bounded character grant choice DAG."""

from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

GRANT_KINDS = frozenset({"skill", "save", "weapon", "armor", "tool", "language", "expertise"})


@dataclass(frozen=True, slots=True)
class ChoiceNode:
    id: str
    source_key: str
    kind: str
    minimum: int
    maximum: int
    eligible: tuple[str, ...]
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Grant:
    kind: str
    key: str
    source_key: str


@dataclass(frozen=True, slots=True)
class GrantProjection:
    grants: tuple[Grant, ...]
    proficiency_bonus: int
    by_kind: Mapping[str, tuple[str, ...]]


def resolve_choices(
    nodes: tuple[ChoiceNode, ...], choices: Mapping[str, tuple[str, ...]]
) -> tuple[Grant, ...]:
    if len(nodes) > 1024:
        raise ValueError("choices: too many nodes")
    index = {n.id: n for n in nodes}
    if len(index) != len(nodes):
        raise ValueError("choices: duplicate node id")
    unknown = set(choices) - set(index)
    if unknown:
        raise ValueError(f"choices: unknown nodes {sorted(unknown)}")
    visiting: set[str] = set()
    done: set[str] = set()

    def visit(node: ChoiceNode) -> None:
        if node.id in visiting:
            raise ValueError(f"choices.{node.id}: cycle")
        if node.id in done:
            return
        visiting.add(node.id)
        for dep in node.dependencies:
            if dep not in index:
                raise ValueError(f"choices.{node.id}: missing dependency {dep}")
            visit(index[dep])
        visiting.remove(node.id)
        done.add(node.id)

    for node in nodes:
        visit(node)
    grants: list[Grant] = []
    for node in sorted(nodes, key=lambda n: n.id):
        if node.kind not in GRANT_KINDS:
            raise ValueError(f"choices.{node.id}.kind: invalid")
        values = choices.get(node.id, ())
        if not node.minimum <= len(values) <= node.maximum:
            raise ValueError(f"choices.{node.id}: expected {node.minimum}..{node.maximum}")
        if len(values) != len(set(values)):
            raise ValueError(f"choices.{node.id}: duplicate")
        if any(v not in node.eligible for v in values):
            raise ValueError(f"choices.{node.id}: ineligible")
        grants.extend(Grant(node.kind, value, node.source_key) for value in values)
    return tuple(sorted(grants, key=lambda g: (g.kind, g.key, g.source_key)))


def project_grants(grants: tuple[Grant, ...], total_level: int) -> GrantProjection:
    from .progression import proficiency_bonus

    known = {(g.kind, g.key) for g in grants}
    for g in grants:
        if g.kind not in GRANT_KINDS or not g.source_key:
            raise ValueError("grant: forged or invalid")
        if g.kind == "expertise" and ("skill", g.key) not in known and ("tool", g.key) not in known:
            raise ValueError(f"expertise.{g.key}: underlying proficiency required")
    by = {kind: tuple(sorted({g.key for g in grants if g.kind == kind})) for kind in GRANT_KINDS}
    return GrantProjection(
        tuple(sorted(set(grants), key=lambda g: (g.kind, g.key, g.source_key))),
        proficiency_bonus(total_level),
        MappingProxyType(by),
    )
