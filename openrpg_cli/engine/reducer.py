"""Pure allowlisted command reducer composition root."""

from __future__ import annotations

from openrpg_cli.domain.messages import (
    Act, AdvanceCharacter, AdvanceEffects, ApplyDamage, ApplyEffect, ChooseGrant,
    Command, CreateGame, EndTurn, EquipItem, Heal, MakeDeathSave, Move,
    PrepareSpell, PutEntity, QueryLegalCommands, React, RecordLegacy, Recover,
    RemoveEffect, ResolveTest, RestCharacter, RollDie, SetConcentration,
    SpendResource, Stabilize, StartEncounter, UpdateInventory,
)
from openrpg_cli.domain.state import GameState
from openrpg_cli.engine.handlers import (
    handle_character, handle_create, handle_damage, handle_death_operation,
    handle_effect, handle_heal, handle_legacy, handle_phase7, handle_put,
    handle_resolve, handle_roll,
)
from openrpg_cli.engine.rng import DeterministicRNG
from openrpg_cli.engine.router import CommandRouter, Handler
from openrpg_cli.engine.types import ReductionResult

HANDLERS: dict[type[Command], Handler] = {
    CreateGame: handle_create, PutEntity: handle_put, RollDie: handle_roll,
    RecordLegacy: handle_legacy, ResolveTest: handle_resolve,
    ApplyDamage: handle_damage, Heal: handle_heal,
    MakeDeathSave: handle_death_operation, Stabilize: handle_death_operation,
    Recover: handle_death_operation, ApplyEffect: handle_effect,
    RemoveEffect: handle_effect, AdvanceEffects: handle_effect,
    StartEncounter: handle_phase7, QueryLegalCommands: handle_phase7,
    Act: handle_phase7, Move: handle_phase7, React: handle_phase7, EndTurn: handle_phase7,
    AdvanceCharacter: handle_character, ChooseGrant: handle_character,
    UpdateInventory: handle_character, EquipItem: handle_character,
    PrepareSpell: handle_character, SpendResource: handle_character,
    SetConcentration: handle_character, RestCharacter: handle_character,
}

DEFAULT_ROUTER = CommandRouter(HANDLERS)


def reduce_command(
    state: GameState, command: Command, rng: DeterministicRNG
) -> ReductionResult:
    return DEFAULT_ROUTER.reduce(state, command, rng)
