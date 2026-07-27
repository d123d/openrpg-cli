"""SRD 5.2.1 spell adapters — declarative effect mappings.

Each adapter maps a spell's mechanical text to structured effects
that the engine resolves through the existing command pipeline.
"""

from __future__ import annotations

from openrpg_cli.effects import (
    AttackEffect, BuffEffect, ConditionEffect, DamageEffect, DurationKind,
    HealEffect, SaveAbility, SaveEffect, SpellAdapter, TargetKind, DamageType, Condition,
)


def _mod(expr: str) -> str:
    """Wrap modifier expression for engine resolution."""
    return expr


# === Cantrips ===

FIRE_BOLT = SpellAdapter(
    name="Fire Bolt", level=0, school="evocation",
    casting_time="1 action", range="120 feet",
    components=("V", "S"), duration="Instantaneous",
    effects=(
        AttackEffect(
            attack_bonus=_mod("spell_attack"),
            damage=DamageEffect("1d10", DamageType.FIRE),
        ),
    ),
)

PRESTIDIGITATION = SpellAdapter(
    name="Prestidigitation", level=0, school="transmutation",
    casting_time="1 action", range="10 feet",
    components=("V", "S"), duration="Up to 1 hour",
    effects=(),  # Utility cantrip, no combat effects
)

MAGE_HAND = SpellAdapter(
    name="Mage Hand", level=0, school="conjuration",
    casting_time="1 action", range="30 feet",
    components=("V", "S"), duration="1 minute",
    effects=(),  # Utility, no combat effects
)

DRUIDCRAFT = SpellAdapter(
    name="Druidcraft", level=0, school="transmutation",
    casting_time="1 action", range="30 feet",
    components=("V", "S"), duration="Instantaneous",
    effects=(),  # Utility cantrip
)

# === Level 1 Spells ===

SHIELD = SpellAdapter(
    name="Shield", level=1, school="abjuration",
    casting_time="1 reaction", range="Self",
    components=("V", "S"), duration="1 round",
    effects=(
        BuffEffect(armor_class=5, duration=DurationKind.ROUNDS, duration_value=1),
    ),
)

MAGIC_MISSILE = SpellAdapter(
    name="Magic Missile", level=1, school="evocation",
    casting_time="1 action", range="120 feet",
    components=("V", "S"), duration="Instantaneous",
    effects=(
        DamageEffect("1d4+1", DamageType.FORCE),
        DamageEffect("1d4+1", DamageType.FORCE),
        DamageEffect("1d4+1", DamageType.FORCE),
    ),
)

CURE_WOUNDS = SpellAdapter(
    name="Cure Wounds", level=1, school="evocation",
    casting_time="1 action", range="Touch",
    components=("V", "S"), duration="Instantaneous",
    effects=(
        HealEffect(dice="1d8", modifier=0),  # + spellcasting modifier
    ),
)

BURNING_HANDS = SpellAdapter(
    name="Burning Hands", level=1, school="evocation",
    casting_time="1 action", range="Self (15-foot cone)",
    components=("V", "S"), duration="Instantaneous",
    effects=(
        SaveEffect(
            ability=SaveAbility.DEX, dc=_mod("spell_dc"),
            on_save={
                "failure": (DamageEffect("3d6", DamageType.FIRE),),
                "success": (),  # half damage on save
            },
        ),
    ),
)

CHARM_PERSON = SpellAdapter(
    name="Charm Person", level=1, school="enchantment",
    casting_time="1 action", range="30 feet",
    components=("V", "S"), duration="1 hour",
    effects=(
        SaveEffect(
            ability=SaveAbility.WIS, dc=_mod("spell_dc"),
            on_save={
                "failure": (ConditionEffect(condition=Condition.CHARMED, duration=DurationKind.MINUTES, duration_value=60),),
                "success": (),
            },
        ),
    ),
)

SLEEP = SpellAdapter(
    name="Sleep", level=1, school="enchantment",
    casting_time="1 action", range="90 feet",
    components=("V", "S", "M"), duration="1 minute",
    effects=(
        ConditionEffect(condition=Condition.UNCONSCIOUS, duration=DurationKind.MINUTES, duration_value=1),
    ),
)

# === Level 2 Spells ===

SCORCHING_RAY = SpellAdapter(
    name="Scorching Ray", level=2, school="evocation",
    casting_time="1 action", range="120 feet",
    components=("V", "S"), duration="Instantaneous",
    effects=(
        AttackEffect(
            attack_bonus=_mod("spell_attack"),
            damage=DamageEffect("2d6", DamageType.FIRE),
        ),
        AttackEffect(
            attack_bonus=_mod("spell_attack"),
            damage=DamageEffect("2d6", DamageType.FIRE),
        ),
        AttackEffect(
            attack_bonus=_mod("spell_attack"),
            damage=DamageEffect("2d6", DamageType.FIRE),
        ),
    ),
)

MISTY_STEP = SpellAdapter(
    name="Misty Step", level=2, school="conjuration",
    casting_time="1 bonus action", range="Self",
    components=("V"), duration="Instantaneous",
    effects=(),  # Teleportation utility
)

HOLD_PERSON = SpellAdapter(
    name="Hold Person", level=2, school="enchantment",
    casting_time="1 action", range="60 feet",
    components=("V", "S", "M"), duration="Concentration, up to 1 minute",
    concentration=True,
    effects=(
        SaveEffect(
            ability=SaveAbility.WIS, dc=_mod("spell_dc"),
            on_save={
                "failure": (
                    ConditionEffect(condition=Condition.PARALYZED, duration=DurationKind.CONCENTRATION),
                ),
                "success": (),
            },
        ),
    ),
)

# === Level 3 Spells ===

FIREBALL = SpellAdapter(
    name="Fireball", level=3, school="evocation",
    casting_time="1 action", range="150 feet",
    components=("V", "S", "M"), duration="Instantaneous",
    effects=(
        SaveEffect(
            ability=SaveAbility.DEX, dc=_mod("spell_dc"),
            on_save={
                "failure": (DamageEffect("8d6", DamageType.FIRE),),
                "success": (),
            },
        ),
    ),
)

LIGHTNING_BOLT = SpellAdapter(
    name="Lightning Bolt", level=3, school="evocation",
    casting_time="1 action", range="Self (100-foot line)",
    components=("V", "S", "M"), duration="Instantaneous",
    effects=(
        SaveEffect(
            ability=SaveAbility.DEX, dc=_mod("spell_dc"),
            on_save={
                "failure": (DamageEffect("8d6", DamageType.LIGHTNING),),
                "success": (),
            },
        ),
    ),
)

HASTE = SpellAdapter(
    name="Haste", level=3, school="transmutation",
    casting_time="1 action", range="30 feet",
    components=("V", "S", "M"), duration="Concentration, up to 1 minute",
    concentration=True,
    effects=(
        BuffEffect(
            armor_class=2,
            duration=DurationKind.CONCENTRATION,
        ),
    ),
)

CLEANSING_TOUCH = SpellAdapter(
    name="Counterspell", level=3, school="abjuration",
    casting_time="1 reaction", range="60 feet",
    components=("S"), duration="Instantaneous",
    effects=(),  # Reaction, counters a spell
)

# === Level 4 Spells ===

FIRE_SHIELD = SpellAdapter(
    name="Fire Shield", level=4, school="evocation",
    casting_time="1 action", range="Self",
    components=("V", "S", "M"), duration="10 minutes",
    effects=(
        BuffEffect(
            duration=DurationKind.MINUTES, duration_value=10,
        ),
    ),
)

# === Level 5 Spells ===

CONE_OF_COLD = SpellAdapter(
    name="Cone of Cold", level=5, school="evocation",
    casting_time="1 action", range="Self (60-foot cone)",
    components=("V", "S", "M"), duration="Instantaneous",
    effects=(
        SaveEffect(
            ability=SaveAbility.CON, dc=_mod("spell_dc"),
            on_save={
                "failure": (DamageEffect("8d8", DamageType.COLD),),
                "success": (),
            },
        ),
    ),
)

# === Spell Registry ===

SRD_SPELLS: dict[str, SpellAdapter] = {
    spell.name.lower().replace(" ", "-").replace("'", ""): spell
    for spell in [
        FIRE_BOLT, PRESTIDIGITATION, MAGE_HAND, DRUIDCRAFT,
        SHIELD, MAGIC_MISSILE, CURE_WOUNDS, BURNING_HANDS,
        CHARM_PERSON, SLEEP,
        SCORCHING_RAY, MISTY_STEP, HOLD_PERSON,
        FIREBALL, LIGHTNING_BOLT, HASTE,
        FIRE_SHIELD, CONE_OF_COLD,
    ]
}
