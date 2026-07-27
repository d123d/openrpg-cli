"""SRD 5.2.1 weapon adapters — declarative weapon mappings.

All 38 SRD weapons with properties, damage, and costs.
"""

from __future__ import annotations

from openrpg_cli.effects import DamageType, WeaponAdapter


# === Simple Melee Weapons ===

CLUB = WeaponAdapter(name="Club", damage="1d4", damage_type=DamageType.BLUDGEONING, properties=("light",), weight=2, cost="1sp", category="simple")
DAGGER = WeaponAdapter(name="Dagger", damage="1d4", damage_type=DamageType.PIERCING, properties=("finesse", "light", "thrown(20/60)"), weight=1, cost="2gp", category="simple")
GREATCLUB = WeaponAdapter(name="Greatclub", damage="1d8", damage_type=DamageType.BLUDGEONING, properties=("two-handed",), weight=10, cost="2sp", category="simple")
MACE = WeaponAdapter(name="Mace", damage="1d6", damage_type=DamageType.BLUDGEONING, properties=(), weight=4, cost="5gp", category="simple")
QUARTERSTAFF = WeaponAdapter(name="Quarterstaff", damage="1d6", damage_type=DamageType.BLUDGEONING, properties=("versatile(1d8)",), weight=4, cost="5sp", category="simple")
SICKLE = WeaponAdapter(name="Sickle", damage="1d4", damage_type=DamageType.SLASHING, properties=("light",), weight=2, cost="1gp", category="simple")
SPEAR = WeaponAdapter(name="Spear", damage="1d6", damage_type=DamageType.PIERCING, properties=("thrown(20/60)", "versatile(1d8)"), weight=3, cost="1gp", category="simple")

# === Simple Ranged Weapons ===

LIGHT_CROSSBOW = WeaponAdapter(name="Light Crossbow", damage="1d8", damage_type=DamageType.PIERCING, properties=("loading", "range(80/320)"), weight=5, cost="25gp", category="simple", range_normal=80, range_long=320)
DART = WeaponAdapter(name="Dart", damage="1d4", damage_type=DamageType.PIERCING, properties=("finesse", "thrown(20/60)"), weight=0.25, cost="5sp", category="simple", range_normal=20, range_long=60)
SHORTBOW = WeaponAdapter(name="Shortbow", damage="1d6", damage_type=DamageType.PIERCING, properties=("two-handed", "range(80/320)"), weight=2, cost="25gp", category="simple", range_normal=80, range_long=320)
SLING = WeaponAdapter(name="Sling", damage="1d4", damage_type=DamageType.BLUDGEONING, properties=("range(30/120)"), weight=0, cost="1sp", category="simple", range_normal=30, range_long=120)

# === Martial Melee Weapons ===

BATTLEAXE = WeaponAdapter(name="Battleaxe", damage="1d8", damage_type=DamageType.SLASHING, properties=("versatile(1d10)",), weight=4, cost="10gp", category="martial")
FLAIL = WeaponAdapter(name="Flail", damage="1d8", damage_type=DamageType.BLUDGEONING, properties=(), weight=2, cost="10gp", category="martial")
GLAIVE = WeaponAdapter(name="Glaive", damage="1d10", damage_type=DamageType.SLASHING, properties=("heavy", "reach", "two-handed"), weight=6, cost="20gp", category="martial")
GREATAXE = WeaponAdapter(name="Greataxe", damage="1d12", damage_type=DamageType.SLASHING, properties=("heavy", "two-handed"), weight=7, cost="30gp", category="martial")
GREATSWORD = WeaponAdapter(name="Greatsword", damage="2d6", damage_type=DamageType.SLASHING, properties=("heavy", "two-handed"), weight=6, cost="50gp", category="martial")
HALBERD = WeaponAdapter(name="Halberd", damage="1d10", damage_type=DamageType.SLASHING, properties=("heavy", "reach", "two-handed"), weight=6, cost="20gp", category="martial")
LANCE = WeaponAdapter(name="Lance", damage="1d12", damage_type=DamageType.PIERCING, properties=("reach", "special"), weight=6, cost="10gp", category="martial")
LONGSWORD = WeaponAdapter(name="Longsword", damage="1d8", damage_type=DamageType.SLASHING, properties=("versatile(1d10)",), weight=3, cost="15gp", category="martial")
MAUL = WeaponAdapter(name="Maul", damage="2d6", damage_type=DamageType.BLUDGEONING, properties=("heavy", "two-handed"), weight=10, cost="10gp", category="martial")
MORNINGSTAR = WeaponAdapter(name="Morningstar", damage="1d8", damage_type=DamageType.PIERCING, properties=(), weight=4, cost="15gp", category="martial")
PIKE = WeaponAdapter(name="Pike", damage="1d10", damage_type=DamageType.PIERCING, properties=("heavy", "reach", "two-handed"), weight=18, cost="5gp", category="martial")
RAPIER = WeaponAdapter(name="Rapier", damage="1d8", damage_type=DamageType.PIERCING, properties=("finesse"), weight=2, cost="25gp", category="martial")
SCIMITAR = WeaponAdapter(name="Scimitar", damage="1d6", damage_type=DamageType.SLASHING, properties=("finesse", "light"), weight=3, cost="25gp", category="martial")
SWORD_SHORT = WeaponAdapter(name="Shortsword", damage="1d6", damage_type=DamageType.PIERCING, properties=("finesse", "light"), weight=2, cost="10gp", category="martial")
TRIDENT = WeaponAdapter(name="Trident", damage="1d6", damage_type=DamageType.PIERCING, properties=("thrown(20/60)", "versatile(1d8)"), weight=4, cost="5gp", category="martial")
WAR_PICK = WeaponAdapter(name="War pick", damage="1d8", damage_type=DamageType.PIERCING, properties=(), weight=2, cost="5gp", category="martial")
WARHAMMER = WeaponAdapter(name="Warhammer", damage="1d8", damage_type=DamageType.BLUDGEONING, properties=("versatile(1d10)",), weight=2, cost="15gp", category="martial")
WHIP = WeaponAdapter(name="Whip", damage="1d4", damage_type=DamageType.SLASHING, properties=("finesse", "reach"), weight=3, cost="2gp", category="martial")

# === Martial Ranged Weapons ===

BLOWGUN = WeaponAdapter(name="Blowgun", damage="1", damage_type=DamageType.PIERCING, properties=("loading", "range(25/100)"), weight=1, cost="10gp", category="martial", range_normal=25, range_long=100)
HEAVY_CROSSBOW = WeaponAdapter(name="Heavy Crossbow", damage="1d10", damage_type=DamageType.PIERCING, properties=("heavy", "loading", "range(100/400)", "two-handed"), weight=18, cost="50gp", category="martial", range_normal=100, range_long=400)
LONGBOW = WeaponAdapter(name="Longbow", damage="1d8", damage_type=DamageType.PIERCING, properties=("heavy", "two-handed", "range(150/600)"), weight=2, cost="50gp", category="martial", range_normal=150, range_long=600)
NET = WeaponAdapter(name="Net", damage="0", damage_type=DamageType.SLASHING, properties=("special", "range(5/15)"), weight=3, cost="1gp", category="martial", range_normal=5, range_long=15)

# === Weapon Registry ===

SRD_WEAPONS: dict[str, WeaponAdapter] = {
    weapon.name.lower().replace(" ", "-").replace("'", ""): weapon
    for weapon in [
        CLUB, DAGGER, GREATCLUB, MACE, QUARTERSTAFF, SICKLE, SPEAR,
        LIGHT_CROSSBOW, DART, SHORTBOW, SLING,
        BATTLEAXE, FLAIL, GLAIVE, GREATAXE, GREATSWORD, HALBERD, LANCE,
        LONGSWORD, MAUL, MORNINGSTAR, PIKE, RAPIER, SCIMITAR, SWORD_SHORT,
        TRIDENT, WAR_PICK, WARHAMMER, WHIP,
        BLOWGUN, HEAVY_CROSSBOW, LONGBOW, NET,
    ]
}
