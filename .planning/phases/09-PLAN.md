# Phase 9: SRD Effect Adapters — Plan

**Goal**: Structured SRD spells, creature abilities, items, and traits execute through declarative effects.
**Depends on**: Phase 7 (Turn, Action & Space Engine)
**Requirements**: FX-01, FX-02, FX-03, FX-04, FX-05

## Architecture

### Effect DSL (FX-01)

Core effect types as frozen dataclasses:

```python
@dataclass(frozen=True)
class Effect:
    kind: str  # 'attack', 'save', 'damage', 'heal', 'condition', 'move', 'area', 'repeat', 'summon', 'spend'
    target: TargetSelector  # 'self', 'single', 'all_enemies', 'all_allies', 'area锥/球/线/柱'
    params: Mapping[str, Any]  # kind-specific parameters

@dataclass(frozen=True)  
class AttackEffect(Effect):
    kind: str = 'attack'
    attack_bonus: int | str  # flat or modifier expression
    damage: str | None = None  # '2d6+3'
    damage_type: str | None = None
    on_hit: tuple[Effect, ...] = ()
    on_crit: tuple[Effect, ...] = ()

@dataclass(frozen=True)
class SaveEffect(Effect):
    kind: str = 'save'
    ability: str  # 'dex', 'wis', etc.
    dc: str | int = 'spell_dc'
    on_save: dict[str, tuple[Effect, ...]] = field(default_factory=dict)  # 'success': (), 'failure': (), 'critical': ()
```

### Spell Adapters (FX-02)

Each SRD spell gets a declarative adapter:

```python
SPELLS = {
    'fire-bolt': SpellAdapter(
        name='Fire Bolt',
        level=0,
        school='evocation',
        casting_time='1 action',
        range='120 feet',
        components=['V', 'S'],
        duration='Instantaneous',
        effects=(
            AttackEffect(
                attack_bonus='spell_attack',
                damage='1d10',
                damage_type='fire',
            ),
        ),
    ),
    'shield': SpellAdapter(
        name='Shield',
        level=1,
        school='abjuration',
        casting_time='1 reaction',
        range='Self',
        components=['V', 'S'],
        duration='1 round',
        effects=(
            BuffEffect(armor_class=5, duration='end_of_next_turn'),
        ),
    ),
}
```

### Creature Adapters (FX-03)

```python
CREATURES = {
    'goblin-warrior': CreatureAdapter(
        name='Goblin Warrior',
        ac=15, hp=7, speed=30,
        actions=(
            MultiAttackAction(
                attacks=('scimitar', 'shortbow'),
            ),
            MeleeAction(name='scimitar', bonus=4, damage='1d6+2', damage_type='slashing'),
            RangedAction(name='shortbow', bonus=4, damage='1d6+2', damage_type='piercing', range=(80, 320)),
        ),
        traits=(
            NimbleEscape(advantage_on='stealth'),
        ),
    ),
}
```

### Weapon/Item Adapters (FX-04)

```python
WEAPONS = {
    'longsword': WeaponAdapter(
        name='Longsword',
        damage='1d8',
        damage_type='slashing',
        properties=['versatile(1d10)'],
        weight=3,
        cost='15gp',
    ),
}
```

### Coverage Report (FX-05)

Generated JSON report listing:
- Supported spells/creatures/weapons with adapter status
- Unsupported mechanics with reasons
- Coverage percentage per category

## Implementation Steps

### Step 1: Effect DSL Core
- Define `Effect`, `TargetSelector`, `DamageEffect`, `SaveEffect`, `BuffEffect`
- Implement `resolve()` method for each effect type
- Add effect composition (effects can contain other effects)
- Test: effects compose correctly, resolve deterministically

### Step 2: Spell Adapters
- Start with 20 most-used SRD spells (cantrips + level 1-3)
- Each adapter maps spell text to declarative effects
- Test: each adapter resolves correctly in isolation

### Step 3: Creature Adapters  
- Start with 10 SRD creatures (goblin, skeleton, zombie, wolf, etc.)
- Each adapter maps stat block to structured actions
- Test: creature turns resolve correctly

### Step 4: Weapon/Item Adapters
- All 38 SRD weapons with properties
- Basic magic item effects (+1 weapon, +1 armor, etc.)
- Test: equipment modifies attacks correctly

### Step 5: Integration
- Connect adapters to turn engine
- Effects execute through command/event pipeline
- Test: full combat round with spells and creatures

### Step 6: Coverage Report
- Audit all SRD content against adapters
- Generate supported/unsupported matrix
- Test: report is accurate and complete

## Success Criteria

1. 20+ spells resolve through declarative effects
2. 10+ creatures have structured action adapters
3. All 38 SRD weapons have adapters
4. Coverage report names every supported and unsupported corpus mechanic
5. All existing tests still pass
6. New tests cover each adapter type
