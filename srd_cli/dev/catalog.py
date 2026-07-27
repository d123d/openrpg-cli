"""Complete generic player-experience catalog for SRD CLI development.

Catalog describes interaction space. It does not claim every described mechanic is
implemented or sourced directly by SRD 5.2.1. Status and authority remain explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExperienceDomain(str, Enum):
    CHARACTER = "character"
    PROGRESSION = "progression"
    RESOURCES = "resources"
    COMBAT = "combat"
    MAGIC = "magic"
    EXPLORATION = "exploration"
    TRAVEL = "travel"
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    INVESTIGATION = "investigation"
    SURVIVAL = "survival"
    DOWNTIME = "downtime"
    PARTY = "party"
    WORLD = "world"
    NARRATIVE = "narrative"
    SYSTEM = "system"


class CapabilityStatus(str, Enum):
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    PLANNED = "planned"
    FRAMEWORK = "generic-framework"
    UNSUPPORTED = "unsupported"


class RulesAuthority(str, Enum):
    SRD = "srd-5.2.1"
    ENGINE = "engine-policy"
    RUNTIME = "runtime-user-content"


@dataclass(frozen=True, slots=True)
class ActionDescriptor:
    id: str
    title: str
    description: str
    domains: tuple[ExperienceDomain, ...]
    target_kinds: tuple[str, ...]
    resolution: str
    costs: tuple[str, ...]
    status: CapabilityStatus
    authority: RulesAuthority
    phase: int
    requirement: str


@dataclass(frozen=True, slots=True)
class SituationDescriptor:
    id: str
    title: str
    description: str
    domain: ExperienceDomain
    triggers: tuple[str, ...]
    player_goals: tuple[str, ...]
    action_ids: tuple[str, ...]
    stakes: tuple[str, ...]
    status: CapabilityStatus
    authority: RulesAuthority
    phase: int
    requirement: str


def _a(
    identity: str,
    title: str,
    description: str,
    domains: tuple[ExperienceDomain, ...],
    targets: tuple[str, ...],
    resolution: str,
    costs: tuple[str, ...],
    status: CapabilityStatus,
    phase: int,
    requirement: str,
    authority: RulesAuthority = RulesAuthority.SRD,
) -> ActionDescriptor:
    return ActionDescriptor(
        identity, title, description, domains, targets, resolution, costs,
        status, authority, phase, requirement,
    )


D = ExperienceDomain
IMPL = CapabilityStatus.IMPLEMENTED
P = CapabilityStatus.PARTIAL
N = CapabilityStatus.PLANNED
F = CapabilityStatus.FRAMEWORK
SRD = RulesAuthority.SRD
ENG = RulesAuthority.ENGINE
RUN = RulesAuthority.RUNTIME


ACTIONS: tuple[ActionDescriptor, ...] = (
    _a("create-character", "Create Character", "Choose legal SRD identity, class, species, background, feat, abilities, equipment, and spells.", (D.CHARACTER,), ("self",), "validated choice graph", (), P, 8, "CHAR-21"),
    _a("inspect-character", "Inspect Character", "Read authoritative statistics, proficiencies, resources, equipment, effects, and provenance.", (D.CHARACTER, D.SYSTEM), ("self", "ally"), "read-only projection", (), P, 8, "CHAR-22"),
    _a("advance-level", "Advance Level", "Apply XP or milestone advancement, class choices, features, and derived-stat changes.", (D.PROGRESSION,), ("self",), "progression reducer", ("xp or milestone",), N, 8, "CHAR-20"),
    _a("manage-inventory", "Manage Inventory", "Acquire, drop, transfer, stow, retrieve, equip, unequip, and count carried objects.", (D.CHARACTER, D.RESOURCES), ("self", "ally", "object"), "inventory transaction", ("interaction or activity",), N, 8, "CHAR-23"),
    _a("attune-item", "Attune Item", "Bind or release attunement while enforcing limits, prerequisites, and rest requirements.", (D.CHARACTER, D.MAGIC, D.RESOURCES), ("self", "object"), "resource transition", ("rest time", "attunement slot"), N, 8, "CHAR-23"),
    _a("spend-resource", "Spend Resource", "Consume a bounded class, item, spell, hit-die, charge, currency, or activity resource.", (D.RESOURCES,), ("self", "object"), "atomic resource transaction", ("named resource",), P, 8, "CHAR-24"),
    _a("recover-resource", "Recover Resource", "Restore resources through explicit recharge, rest, service, or effect rules.", (D.RESOURCES,), ("self", "ally"), "recovery hook", ("time or service",), P, 8, "CHAR-25"),
    _a("ability-check", "Ability Check", "Attempt uncertain task using an ability, proficiency, modifiers, advantage, and a target DC.", (D.EXPLORATION, D.SOCIAL, D.INVESTIGATION, D.SURVIVAL), ("self", "object", "environment"), "d20 test", ("time",), IMPL, 6, "RES-01"),
    _a("saving-throw", "Saving Throw", "Resist an effect using an ability save against an explicit DC.", (D.COMBAT, D.MAGIC, D.ENVIRONMENT), ("self", "ally", "enemy"), "d20 test", (), IMPL, 6, "RES-01"),
    _a("contest", "Contest", "Resolve opposed efforts with explicit participants, abilities, and tie policy.", (D.COMBAT, D.SOCIAL, D.EXPLORATION), ("self", "ally", "enemy"), "opposed d20 tests", ("time",), IMPL, 6, "RES-01"),
    _a("attack", "Attack", "Make weapon, unarmed, or spell attack against a legal target; engine resolves hit, critical, damage, and defenses.", (D.COMBAT,), ("enemy", "object"), "attack roll and damage", ("action or reaction",), P, 7, "TURN-03"),
    _a("cast-magic", "Magic", "Cast a prepared or known spell with components, targets, range, slots, concentration, and effect adapter checks.", (D.MAGIC, D.COMBAT), ("self", "ally", "enemy", "object", "area"), "spell effect adapter", ("action type", "spell slot", "components"), P, 9, "FX-02"),
    _a("move", "Move", "Spend speed to change relative range or grid position while respecting terrain, occupancy, and hazards.", (D.COMBAT, D.EXPLORATION, D.TRAVEL), ("self", "position"), "space transition", ("movement",), IMPL, 7, "TURN-05"),
    _a("dash", "Dash", "Gain extra movement for current turn through explicit action cost.", (D.COMBAT, D.EXPLORATION), ("self",), "budget transition", ("action",), IMPL, 7, "TURN-03"),
    _a("disengage", "Disengage", "Move without provoking opportunity attacks for current turn.", (D.COMBAT,), ("self",), "timed turn effect", ("action",), IMPL, 7, "TURN-03"),
    _a("dodge", "Dodge", "Focus on defense until next turn, modifying eligible attacks and saves.", (D.COMBAT,), ("self",), "timed turn effect", ("action",), IMPL, 7, "TURN-03"),
    _a("help", "Help", "Aid another actor's next eligible check or attack under explicit proximity and timing rules.", (D.COMBAT, D.EXPLORATION, D.SOCIAL), ("ally",), "advantage source", ("action",), IMPL, 7, "TURN-03"),
    _a("hide", "Hide", "Attempt to become hidden using visibility, cover, concealment, and opposed perception rules.", (D.COMBAT, D.EXPLORATION), ("self", "observers"), "ability check and visibility state", ("action",), IMPL, 7, "TURN-03"),
    _a("influence", "Influence", "Attempt to change another actor's attitude, decision, or cooperation without overriding agency.", (D.SOCIAL,), ("ally", "enemy", "npc"), "social test and consequence", ("action or scene beat",), P, 7, "TURN-03"),
    _a("ready", "Ready", "Prepare a legal action with explicit perceivable trigger and reaction execution.", (D.COMBAT,), ("self", "trigger", "target"), "deferred command", ("action", "reaction"), IMPL, 7, "TURN-03"),
    _a("search", "Search", "Actively locate hidden creatures, objects, hazards, tracks, or evidence.", (D.EXPLORATION, D.INVESTIGATION), ("area", "object", "creature"), "ability check and discovery", ("action or time"), P, 7, "TURN-03"),
    _a("study", "Study", "Recall or analyze information about creatures, objects, clues, magic, places, or phenomena.", (D.INVESTIGATION, D.MAGIC), ("object", "creature", "clue", "environment"), "ability check and knowledge result", ("action or time"), P, 7, "TURN-03"),
    _a("utilize", "Utilize", "Use a nonmagical object, tool, device, service, or environmental feature.", (D.EXPLORATION, D.ENVIRONMENT, D.DOWNTIME), ("object", "environment"), "item or runtime adapter", ("action or interaction",), P, 7, "TURN-03"),
    _a("grapple", "Grapple", "Attempt to seize and control another creature under size, reach, and escape rules.", (D.COMBAT,), ("enemy",), "attack replacement and save", ("attack",), IMPL, 7, "TURN-04"),
    _a("shove", "Shove", "Attempt to push or knock prone another creature under size and reach rules.", (D.COMBAT,), ("enemy",), "attack replacement and save", ("attack",), IMPL, 7, "TURN-04"),
    _a("react", "Reaction", "Respond to an explicit trigger using one legal reaction and once-per-round budget.", (D.COMBAT, D.MAGIC), ("trigger", "self", "ally", "enemy"), "triggered command", ("reaction",), IMPL, 7, "TURN-02"),
    _a("interact-environment", "Interact with Environment", "Open, close, lift, break, manipulate, activate, or examine a runtime-authored feature.", (D.ENVIRONMENT, D.EXPLORATION), ("object", "environment"), "interaction or ability check", ("interaction or action",), N, 11, "SCENE-04"),
    _a("travel", "Travel", "Advance through runtime-authored routes with pace, time, roles, supplies, and encounter checks.", (D.TRAVEL, D.SURVIVAL), ("party", "route", "destination"), "activity clock", ("time", "supplies"), F, 11, "SCENE-04", ENG),
    _a("navigate", "Navigate", "Determine or maintain direction, route, and progress under terrain and visibility constraints.", (D.TRAVEL, D.SURVIVAL), ("route", "environment"), "ability check and progress clock", ("travel role", "time"), F, 11, "SCENE-04", ENG),
    _a("track", "Track", "Follow signs left by creatures or groups across runtime-authored terrain and time.", (D.EXPLORATION, D.SURVIVAL), ("creature", "trail", "environment"), "ability check and discovery", ("time",), F, 11, "SCENE-04", ENG),
    _a("forage", "Forage", "Search runtime-authored terrain for food, water, and useful natural resources.", (D.SURVIVAL,), ("environment", "party"), "ability check and resource result", ("time",), F, 12, "SCENE-08", ENG),
    _a("camp", "Camp", "Establish shelter, assign watches, consume supplies, and resolve rest interruptions.", (D.SURVIVAL, D.PARTY), ("party", "environment"), "activity scene", ("time", "supplies"), F, 12, "SCENE-08", ENG),
    _a("short-rest", "Short Rest", "Spend hit dice and trigger eligible short-rest recovery without erasing ongoing consequences.", (D.RESOURCES, D.SURVIVAL), ("self", "party"), "rest reducer", ("time", "hit dice"), N, 8, "CHAR-25"),
    _a("long-rest", "Long Rest", "Resolve sleep, watch, recovery, recharge, interruption, and once-per-period limits.", (D.RESOURCES, D.SURVIVAL), ("self", "party"), "rest reducer", ("time", "supplies"), N, 8, "CHAR-25"),
    _a("administer-aid", "Administer Aid", "Stabilize, heal, treat, or assist an injured creature using legal features, items, or services.", (D.SURVIVAL, D.RESOURCES), ("self", "ally"), "vitality or effect transition", ("action", "item or spell"), P, 6, "RES-04"),
    _a("death-save", "Death Save", "Resolve unconscious player-character survival progression without auto-revival.", (D.CHARACTER, D.COMBAT), ("self",), "death-save reducer", (), IMPL, 6, "RES-04"),
    _a("communicate", "Communicate", "Speak, signal, write, gesture, or use telepathy when language and circumstances permit.", (D.SOCIAL, D.PARTY), ("ally", "enemy", "npc", "group"), "runtime communication", ("time",), F, 11, "SCENE-03", RUN),
    _a("negotiate", "Negotiate", "Exchange proposals, concessions, promises, leverage, and consequences with explicit participant agency.", (D.SOCIAL, D.WORLD), ("npc", "group", "faction"), "social scene and clocks", ("time", "leverage"), F, 11, "SCENE-03", ENG),
    _a("trade", "Trade", "Buy, sell, barter, hire, or pay for SRD services using explicit prices and inventory changes.", (D.SOCIAL, D.RESOURCES, D.WORLD), ("npc", "service", "object"), "atomic transaction", ("currency or goods",), N, 12, "SCENE-07"),
    _a("investigate", "Investigate", "Form questions, inspect evidence, connect clues, test hypotheses, and record discoveries.", (D.INVESTIGATION,), ("clue", "object", "scene", "creature"), "discovery graph and tests", ("time",), F, 11, "SCENE-05", ENG),
    _a("solve-problem", "Solve Problem", "Manipulate runtime-authored puzzle state using declared rules without hidden answer invention.", (D.INVESTIGATION, D.ENVIRONMENT), ("puzzle", "object", "environment"), "runtime state machine", ("time", "attempt"), F, 11, "SCENE-05", RUN),
    _a("pursue", "Pursue or Escape", "Gain or lose ground in a chase using movement, obstacles, hazards, and bounded clocks.", (D.EXPLORATION, D.COMBAT), ("creature", "route"), "challenge clock", ("movement", "effort"), F, 11, "SCENE-06", ENG),
    _a("craft", "Craft", "Convert declared materials, tools, proficiency, time, and cost into a runtime-authored result.", (D.DOWNTIME, D.RESOURCES), ("object", "project"), "project clock", ("time", "materials", "currency"), F, 12, "SCENE-07", ENG),
    _a("train", "Train", "Advance a runtime-authored training project through time, instruction, checks, and costs.", (D.DOWNTIME, D.PROGRESSION), ("self", "teacher", "project"), "project clock", ("time", "currency"), F, 12, "SCENE-07", ENG),
    _a("research", "Research", "Gather and evaluate information through sources, services, checks, time, and discovery clocks.", (D.DOWNTIME, D.INVESTIGATION), ("source", "project"), "project and discovery clocks", ("time", "currency"), F, 12, "SCENE-07", ENG),
    _a("work", "Work", "Perform a runtime-authored job or service for time, checks, payment, and consequences.", (D.DOWNTIME, D.WORLD), ("project", "employer"), "activity clock", ("time",), F, 12, "SCENE-07", ENG),
    _a("coordinate-party", "Coordinate Party", "Assign roles, marching order, shared resources, group checks, and declared plans.", (D.PARTY,), ("party", "ally"), "party state transition", ("time",), N, 10, "ENC-02"),
    _a("manage-relationship", "Manage Relationship", "Record runtime-authored trust, conflict, obligation, reputation, and faction consequences.", (D.PARTY, D.WORLD, D.SOCIAL), ("ally", "npc", "faction"), "relationship clocks", ("scene consequence",), F, 12, "SCENE-09", RUN),
    _a("perform-rite", "Perform Rite", "Resolve runtime-authored vows, rites, devotion, omens, and spiritual obligations without invented divine facts.", (D.WORLD, D.NARRATIVE), ("self", "group", "symbol"), "activity scene and consequence", ("time", "declared offering"), F, 12, "SCENE-10", RUN),
    _a("pursue-objective", "Pursue Objective", "Advance, fail, revise, or complete an explicit objective through engine-recorded consequences.", (D.NARRATIVE,), ("objective", "scene"), "objective clock", ("action or scene beat",), F, 10, "ENC-05", ENG),
    _a("transition-scene", "Transition Scene", "Move participants and retained consequences into another runtime-authored scene.", (D.NARRATIVE, D.SYSTEM), ("scene", "party"), "scene transition", ("time",), N, 10, "ENC-05"),
    _a("save-game", "Save Game", "Persist canonical state, command/event log, RNG state, and runtime-content references.", (D.SYSTEM,), ("game",), "canonical serialization", (), IMPL, 5, "KERN-04"),
    _a("resume-game", "Resume Game", "Load, migrate, validate, and continue canonical state without changing deterministic history.", (D.SYSTEM,), ("game",), "migration and replay validation", (), IMPL, 5, "KERN-04"),
    _a("replay-game", "Replay Game", "Recompute state from recorded commands/events and verify snapshot hashes.", (D.SYSTEM,), ("game",), "deterministic replay", (), IMPL, 5, "KERN-04"),
)


def _s(
    identity: str,
    title: str,
    description: str,
    domain: ExperienceDomain,
    triggers: tuple[str, ...],
    goals: tuple[str, ...],
    actions: tuple[str, ...],
    stakes: tuple[str, ...],
    status: CapabilityStatus,
    phase: int,
    requirement: str,
    authority: RulesAuthority = RulesAuthority.SRD,
) -> SituationDescriptor:
    return SituationDescriptor(
        identity, title, description, domain, triggers, goals, actions, stakes,
        status, authority, phase, requirement,
    )


SITUATIONS: tuple[SituationDescriptor, ...] = (
    _s("character-origin", "Character Origin", "Player establishes legal identity, capabilities, equipment, and initial resources.", D.CHARACTER, ("new game", "replacement character"), ("create playable character", "understand capabilities"), ("create-character", "inspect-character", "manage-inventory"), ("legality", "future options"), P, 8, "CHAR-21"),
    _s("character-advancement", "Advancement", "Character earns progression and makes level, feature, subclass, or multiclass choices.", D.PROGRESSION, ("xp threshold", "milestone", "training"), ("grow capabilities", "preserve legality"), ("advance-level", "inspect-character"), ("permanent build choices", "derived stats"), N, 8, "CHAR-20"),
    _s("resource-pressure", "Resource Pressure", "Character decides when to spend or conserve limited health, spells, features, items, time, and currency.", D.RESOURCES, ("damage", "limited uses", "scarce supplies", "deadline"), ("survive", "retain future options"), ("spend-resource", "recover-resource", "short-rest", "long-rest", "administer-aid"), ("attrition", "opportunity cost"), P, 8, "CHAR-24"),
    _s("combat-encounter", "Combat Encounter", "Hostile actors enter initiative and resolve turns until objectives, retreat, surrender, victory, or defeat.", D.COMBAT, ("hostility", "ambush", "failed negotiation"), ("survive", "protect allies", "achieve objective"), ("attack", "cast-magic", "move", "dash", "disengage", "dodge", "help", "hide", "ready", "grapple", "shove", "react", "utilize"), ("hp", "resources", "position", "death", "objective"), P, 7, "TURN-03"),
    _s("ambush-surprise", "Ambush and Surprise", "Awareness, hiding, perception, and initiative determine initial restrictions and advantage.", D.COMBAT, ("hidden threat", "stealth approach"), ("avoid surprise", "gain favorable opening"), ("hide", "search", "ability-check", "attack", "move"), ("first-turn economy", "position"), IMPL, 7, "TURN-01"),
    _s("positioning-terrain", "Positioning and Terrain", "Characters move through range, cover, visibility, obstacles, hazards, mounts, or water.", D.ENVIRONMENT, ("movement", "ranged action", "hazard", "difficult terrain"), ("reach target", "gain protection", "avoid hazard"), ("move", "dash", "disengage", "interact-environment", "utilize"), ("movement", "exposure", "separation"), IMPL, 7, "TURN-05"),
    _s("injury-dying", "Injury, Dying, and Recovery", "Damage, healing, temporary HP, zero HP, death saves, stabilization, and recovery alter survival state.", D.CHARACTER, ("damage", "zero hp", "healing"), ("stay conscious", "stabilize ally", "recover"), ("saving-throw", "administer-aid", "death-save", "recover-resource"), ("death", "unconsciousness", "resources"), IMPL, 6, "RES-04"),
    _s("conditions-effects", "Conditions and Ongoing Effects", "Timed conditions, concentration, exhaustion, defenses, and repeated effects constrain choices.", D.MAGIC, ("spell", "hazard", "creature trait", "fatigue"), ("end harmful effect", "maintain benefit", "adapt tactics"), ("saving-throw", "cast-magic", "spend-resource", "administer-aid"), ("action legality", "damage", "duration"), P, 9, "FX-01"),
    _s("social-contact", "Social Contact", "Characters communicate with actors whose goals, attitudes, knowledge, and agency remain explicit.", D.SOCIAL, ("meeting", "request", "conflict", "rumor"), ("learn", "persuade", "build trust", "avoid escalation"), ("communicate", "influence", "ability-check", "study"), ("attitude", "information", "obligation"), F, 11, "SCENE-03", RUN),
    _s("negotiation-conflict", "Negotiation and Social Conflict", "Participants exchange leverage, offers, threats, deception, insight, and concessions.", D.SOCIAL, ("competing goals", "trade", "truce", "interrogation"), ("reach agreement", "protect interests", "detect deception"), ("negotiate", "influence", "contest", "ability-check", "trade"), ("agreement", "reputation", "hostility"), F, 11, "SCENE-03", ENG),
    _s("exploration-discovery", "Exploration and Discovery", "Characters examine runtime-authored places, objects, routes, signs, and hidden features.", D.EXPLORATION, ("new scene", "unknown feature", "missing route"), ("understand surroundings", "find opportunities", "avoid danger"), ("search", "study", "interact-environment", "utilize", "move", "track"), ("time", "discovery", "hazard"), F, 11, "SCENE-04", RUN),
    _s("travel-journey", "Travel and Journey", "Party chooses route, pace, roles, supplies, watches, and responses to travel events.", D.TRAVEL, ("leave scene", "distant destination"), ("arrive", "preserve supplies", "avoid becoming lost"), ("travel", "navigate", "track", "forage", "camp", "coordinate-party"), ("time", "supplies", "exhaustion", "encounters"), F, 11, "SCENE-04", ENG),
    _s("hazard-trap", "Hazard and Trap", "Characters notice, understand, avoid, disable, endure, or recover from declared dangers.", D.ENVIRONMENT, ("trigger", "warning sign", "unsafe terrain"), ("avoid harm", "disable danger", "cross safely"), ("search", "study", "utilize", "saving-throw", "ability-check", "administer-aid"), ("damage", "condition", "lost time", "blocked route"), F, 11, "SCENE-06", RUN),
    _s("chase-escape", "Chase, Pursuit, and Escape", "Participants gain or lose ground while navigating obstacles, fatigue, visibility, and route choices.", D.EXPLORATION, ("flee", "pursue", "race", "capture attempt"), ("escape", "catch target", "protect group"), ("pursue", "dash", "move", "ability-check", "help"), ("capture", "separation", "exhaustion"), F, 11, "SCENE-06", ENG),
    _s("investigation-mystery", "Investigation and Mystery", "Characters gather evidence, question sources, form hypotheses, and unlock discoveries.", D.INVESTIGATION, ("unexplained event", "missing person", "unknown object"), ("identify truth", "find next lead", "avoid false conclusion"), ("investigate", "search", "study", "communicate", "ability-check"), ("time", "misdirection", "discovery"), F, 11, "SCENE-05", RUN),
    _s("puzzle-obstacle", "Puzzle and Problem", "Characters alter runtime-authored puzzle state through declared affordances and consequences.", D.INVESTIGATION, ("locked mechanism", "sequence", "riddle", "logic obstacle"), ("understand rules", "reach solved state"), ("solve-problem", "study", "search", "utilize", "interact-environment"), ("attempts", "time", "hazard", "route"), F, 11, "SCENE-05", RUN),
    _s("camp-rest", "Camp, Watch, and Rest", "Party establishes safety, consumes supplies, assigns watches, and resolves recovery or interruption.", D.SURVIVAL, ("night", "resource pressure", "unsafe travel"), ("recover", "avoid surprise", "maintain supplies"), ("camp", "forage", "short-rest", "long-rest", "coordinate-party", "search"), ("recovery", "interruption", "supplies"), F, 12, "SCENE-08", ENG),
    _s("wilderness-survival", "Wilderness Survival", "Weather, food, water, navigation, shelter, tracking, and exhaustion pressure the party.", D.SURVIVAL, ("harsh environment", "lost route", "scarcity"), ("stay alive", "find route", "manage supplies"), ("forage", "navigate", "track", "camp", "ability-check", "saving-throw"), ("exhaustion", "supplies", "time", "damage"), F, 12, "SCENE-08", ENG),
    _s("commerce-services", "Commerce and Services", "Characters buy, sell, hire, repair, identify, lodge, travel, or obtain SRD-listed services.", D.WORLD, ("settlement", "merchant", "service need"), ("obtain resource", "pay fair cost", "avoid fraud"), ("trade", "negotiate", "manage-inventory", "spend-resource"), ("currency", "inventory", "reputation"), N, 12, "SCENE-07"),
    _s("downtime-project", "Downtime Project", "Characters invest time, tools, materials, instruction, and checks into declared long-form work.", D.DOWNTIME, ("safe time", "project goal"), ("craft", "train", "research", "earn"), ("craft", "train", "research", "work", "spend-resource"), ("time", "currency", "materials", "progress"), F, 12, "SCENE-07", ENG),
    _s("party-coordination", "Party Coordination", "Players organize roles, marching order, plans, shared assets, assistance, and group decisions.", D.PARTY, ("group task", "travel", "encounter setup"), ("coordinate", "share resources", "protect vulnerable members"), ("coordinate-party", "help", "manage-inventory", "communicate"), ("group cohesion", "shared resources", "position"), N, 10, "ENC-02"),
    _s("relationship-reputation", "Relationship and Reputation", "Runtime-authored trust, obligations, conflict, faction standing, and public consequences evolve.", D.WORLD, ("promise", "betrayal", "service", "public act"), ("build alliance", "repair harm", "manage obligation"), ("manage-relationship", "communicate", "negotiate", "pursue-objective"), ("trust", "access", "hostility", "obligation"), F, 12, "SCENE-09", RUN),
    _s("capture-restraint", "Capture and Restraint", "Character may be grappled, restrained, unconscious, disarmed, confined, searched, or transported.", D.NARRATIVE, ("defeat", "surrender", "trap", "lawful detention"), ("escape", "negotiate", "survive", "recover possessions"), ("contest", "ability-check", "communicate", "negotiate", "utilize", "pursue-objective"), ("freedom", "equipment", "time", "reputation"), F, 11, "SCENE-06", RUN),
    _s("objective-consequence", "Objective and Consequence", "Explicit goals advance or fail while consequences persist across scene transitions.", D.NARRATIVE, ("quest-like runtime objective", "deadline", "scene outcome"), ("make progress", "accept tradeoff", "complete goal"), ("pursue-objective", "transition-scene", "coordinate-party"), ("progress", "failure", "world state"), F, 10, "ENC-05", RUN),
    _s("rite-oath-omen", "Rite, Oath, and Omen", "Runtime-authored spiritual or ethical activities record intent, obligation, and consequence without invented lore.", D.WORLD, ("vow", "ceremony", "devotion", "omen"), ("express commitment", "seek meaning", "fulfill obligation"), ("perform-rite", "study", "communicate", "pursue-objective"), ("obligation", "relationship", "interpretation"), F, 12, "SCENE-10", RUN),
    _s("scene-transition", "Scene Transition", "Party carries actors, resources, clocks, effects, discoveries, and consequences into another scene.", D.NARRATIVE, ("exit", "travel complete", "objective change"), ("continue play", "preserve state"), ("transition-scene", "save-game", "coordinate-party"), ("state continuity", "time"), N, 10, "ENC-05"),
    _s("save-resume-replay", "Save, Resume, and Replay", "Player persists, migrates, resumes, and verifies deterministic game history.", D.SYSTEM, ("pause", "crash recovery", "debug", "regression"), ("preserve progress", "verify integrity"), ("save-game", "resume-game", "replay-game", "inspect-character"), ("data integrity", "determinism"), IMPL, 5, "KERN-04"),
)
