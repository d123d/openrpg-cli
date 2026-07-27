"""SRD 5.2.1 creature adapters — declarative stat block mappings.

Each adapter maps a creature's stat block to structured actions
that the engine resolves through the existing command pipeline.
"""

from __future__ import annotations

from openrpg_cli.effects import (
    ActionAdapter, AttackEffect, ConditionEffect, DamageEffect, CreatureAdapter,
    DamageType, DurationKind, TargetKind, Condition,
)


# === CR 1/4 Creatures ===

GOBLIN = CreatureAdapter(
    name="Goblin", size="Small", type="humanoid",
    ac=15, hp=7, hit_dice="2d6", speed=30,
    str_score=8, dex_score=14, con_score=10, int_score=10, wis_score=8, cha_score=8,
    senses=("darkvision 60ft",), cr="1/4", xp=50,
    traits=(
        ActionAdapter(name="Nimble Escape", action_type="trait", effects=()),
    ),
    actions=(
        ActionAdapter(name="Scimitar", action_type="action", effects=(
            AttackEffect(attack_bonus=4, damage=DamageEffect("1d6+2", DamageType.SLASHING), reach=5),
        )),
        ActionAdapter(name="Shortbow", action_type="action", effects=(
            AttackEffect(attack_bonus=4, damage=DamageEffect("1d6+2", DamageType.PIERCING), reach=80),
        )),
    ),
)

SKELETON = CreatureAdapter(
    name="Skeleton", size="Medium", type="undead",
    ac=13, hp=13, hit_dice="2d8+4", speed=30,
    str_score=10, dex_score=14, con_score=15, int_score=6, wis_score=8, cha_score=5,
    senses=("darkvision 60ft",), cr="1/4", xp=50,
    actions=(
        ActionAdapter(name="Shortsword", action_type="action", effects=(
            AttackEffect(attack_bonus=4, damage=DamageEffect("1d6+2", DamageType.PIERCING), reach=5),
        )),
        ActionAdapter(name="Shortbow", action_type="action", effects=(
            AttackEffect(attack_bonus=4, damage=DamageEffect("1d6+2", DamageType.PIERCING), reach=80),
        )),
    ),
)

ZOMBIE = CreatureAdapter(
    name="Zombie", size="Medium", type="undead",
    ac=8, hp=22, hit_dice="3d8+9", speed=20,
    str_score=13, dex_score=6, con_score=16, int_score=3, wis_score=6, cha_score=5,
    senses=("darkvision 60ft",), cr="1/4", xp=50,
    traits=(
        ActionAdapter(name="Undead Fortitude", action_type="trait", effects=()),
    ),
    actions=(
        ActionAdapter(name="Slam", action_type="action", effects=(
            AttackEffect(attack_bonus=3, damage=DamageEffect("1d6+1", DamageType.BLUDGEONING), reach=5),
        )),
    ),
)

# === CR 1 Creatures ===

WOLF = CreatureAdapter(
    name="Wolf", size="Medium", type="beast",
    ac=13, hp=11, hit_dice="2d8+2", speed=40,
    str_score=12, dex_score=15, con_score=12, int_score=3, wis_score=12, cha_score=6,
    senses=("darkvision 60ft",), cr="1/4", xp=50,
    traits=(
        ActionAdapter(name="Pack Tactics", action_type="trait", effects=()),
    ),
    actions=(
        ActionAdapter(name="Bite", action_type="action", effects=(
            AttackEffect(attack_bonus=4, damage=DamageEffect("2d4+2", DamageType.PIERCING), reach=5),
        )),
    ),
)

OGRE = CreatureAdapter(
    name="Ogre", size="Large", type="giant",
    ac=11, hp=59, hit_dice="7d10+21", speed=40,
    str_score=19, dex_score=8, con_score=16, int_score=5, wis_score=7, cha_score=6,
    senses=("darkvision 60ft",), cr="2", xp=450,
    actions=(
        ActionAdapter(name="Greatclub", action_type="action", effects=(
            AttackEffect(attack_bonus=6, damage=DamageEffect("2d8+4", DamageType.BLUDGEONING), reach=5),
        )),
        ActionAdapter(name="Javelin", action_type="action", effects=(
            AttackEffect(attack_bonus=6, damage=DamageEffect("2d6+4", DamageType.PIERCING), reach=30),
        )),
    ),
)

# === CR 2 Creatures ===

BUGBEAR = CreatureAdapter(
    name="Bugbear", size="Medium", type="humanoid",
    ac=16, hp=27, hit_dice="5d8+5", speed=30,
    str_score=15, dex_score=14, con_score=13, int_score=8, wis_score=11, cha_score=9,
    senses=("darkvision 60ft",), cr="1", xp=200,
    traits=(
        ActionAdapter(name="Brute", action_type="trait", effects=()),
        ActionAdapter(name="Surprise Attack", action_type="trait", effects=()),
    ),
    actions=(
        ActionAdapter(name="Morningstar", action_type="action", effects=(
            AttackEffect(attack_bonus=4, damage=DamageEffect("2d8+2", DamageType.PIERCING), reach=5),
        )),
        ActionAdapter(name="Javelin", action_type="action", effects=(
            AttackEffect(attack_bonus=4, damage=DamageEffect("2d6+2", DamageType.PIERCING), reach=30),
        )),
    ),
)

# === CR 3 Creatures ===

ETTIN = CreatureAdapter(
    name="Ettin", size="Large", type="giant",
    ac=12, hp=85, hit_dice="10d10+30", speed=40,
    str_score=21, dex_score=8, con_score=17, int_score=6, wis_score=10, cha_score=6,
    senses=("darkvision 60ft",), cr="4", xp=1100,
    traits=(
        ActionAdapter(name="Battle Reactions", action_type="trait", effects=()),
    ),
    actions=(
        ActionAdapter(name="Multiattack", action_type="action", effects=()),
        ActionAdapter(name="Maul", action_type="action", effects=(
            AttackEffect(attack_bonus=7, damage=DamageEffect("2d6+5", DamageType.BLUDGEONING), reach=5),
        )),
        ActionAdapter(name="Maul", action_type="action", effects=(
            AttackEffect(attack_bonus=7, damage=DamageEffect("2d6+5", DamageType.BLUDGEONING), reach=5),
        )),
    ),
)

# === CR 5 Creatures ===

TROLL = CreatureAdapter(
    name="Troll", size="Large", type="giant",
    ac=15, hp=84, hit_dice="8d10+40", speed=30,
    str_score=18, dex_score=13, con_score=20, int_score=7, wis_score=9, cha_score=7,
    senses=("darkvision 60ft",), cr="5", xp=1800,
    traits=(
        ActionAdapter(name="Keen Smell", action_type="trait", effects=()),
        ActionAdapter(name="Regeneration", action_type="trait", effects=()),
    ),
    actions=(
        ActionAdapter(name="Multiattack", action_type="action", effects=()),
        ActionAdapter(name="Bite", action_type="action", effects=(
            AttackEffect(attack_bonus=7, damage=DamageEffect("1d6+4", DamageType.PIERCING), reach=5),
        )),
        ActionAdapter(name="Claw", action_type="action", effects=(
            AttackEffect(attack_bonus=7, damage=DamageEffect("2d6+4", DamageType.SLASHING), reach=5),
        )),
    ),
)

# === CR 7 Creatures ===

VAMPIRE = CreatureAdapter(
    name="Vampire", size="Medium", type="undead",
    ac=16, hp=144, hit_dice="17d8+68", speed=30,
    str_score=18, dex_score=18, con_score=18, int_score=17, wis_score=15, cha_score=18,
    senses=("darkvision 120ft",), cr="13", xp=10000,
    traits=(
        ActionAdapter(name="Shapechanger", action_type="trait", effects=()),
        ActionAdapter(name="Legendary Resistance", action_type="trait", effects=()),
        ActionAdapter(name="Regeneration", action_type="trait", effects=()),
    ),
    actions=(
        ActionAdapter(name="Multiattack", action_type="action", effects=()),
        ActionAdapter(name="Unarmed Strike", action_type="action", effects=(
            AttackEffect(attack_bonus=9, damage=DamageEffect("1d8+4", DamageType.BLUDGEONING), reach=5),
        )),
        ActionAdapter(name="Charm", action_type="action", effects=(
            SaveEffect(
                ability="WIS", dc="spell_dc",
                on_save={"failure": (ConditionEffect(condition=Condition.CHARMED, duration=DurationKind.HOURS, duration_value=24),)},
            ),
        ) if False else ActionAdapter(name="Charm", action_type="action", effects=())),
    ),
)

# === Creature Registry ===

SRD_CREATURES: dict[str, CreatureAdapter] = {
    creature.name.lower().replace(" ", "-"): creature
    for creature in [
        GOBLIN, SKELETON, ZOMBIE, WOLF, OGRE,
        BUGBEAR, ETTIN, TROLL, VAMPIRE,
    ]
}
