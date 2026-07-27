"""Stable public façade for normalized SRD rules."""

from __future__ import annotations
from functools import lru_cache
from srd_cli.character_rules import CharacterRules
from srd_cli.combat_rules import CombatRules
from srd_cli.normalized import NormalizedRepository


class RulesAPI:
    """Read-only rules API. Lookups require exact normalized name or primary key."""

    def __init__(self, normalized: NormalizedRepository | None = None) -> None:
        source = normalized or NormalizedRepository()
        self.repository = source.repository
        self._character = CharacterRules(source)
        self._combat = CombatRules(source)

    def list_classes(self):
        return self._character.classes

    def get_class(self, identity: str):
        return self._character.get_class(identity)

    def list_species(self):
        return self._character.species

    def get_species(self, identity: str):
        return self._character.get_species(identity)

    def list_backgrounds(self):
        return self._character.backgrounds

    def get_background(self, identity: str):
        return self._character.get_background(identity)

    def list_feats(self):
        return self._character.feats

    def get_feat(self, identity: str):
        return self._character.get_feat(identity)

    def list_spells(self):
        return self._character.spells

    def get_spell(self, identity: str):
        return self._character.get_spell(identity)

    def list_creatures(self):
        return self._combat.creatures

    def get_creature(self, identity: str):
        return self._combat.get_creature(identity)

    def list_weapons(self):
        return self._combat.weapons

    def get_weapon(self, identity: str):
        return self._combat.get_weapon(identity)


@lru_cache(maxsize=1)
def get_rules_api() -> RulesAPI:
    return RulesAPI()
