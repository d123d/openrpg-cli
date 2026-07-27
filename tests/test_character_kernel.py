from openrpg_cli.domain.codecs import decode_message, encode
from openrpg_cli.domain.messages import AdvanceCharacter, CharacterChanged
from openrpg_cli.domain.state import ActorState, GameState
from openrpg_cli.engine.reducer import reduce_command
from openrpg_cli.engine.rng import GameRNG


def test_character_command_roundtrip_is_atomic_and_rng_neutral():
    command = AdvanceCharacter("c1", "g", {"actor_id": "a", "target_level": 2})
    assert decode_message(encode(command)) == command
    state = GameState("g", actors=(ActorState("a"),))
    rng = GameRNG(7)
    result = reduce_command(state, command, rng)
    assert isinstance(result.events[0], CharacterChanged)
    assert result.rng == rng
    replay = reduce_command(state, command, GameRNG(7))
    assert encode(result.state) == encode(replay.state)


def test_unknown_actor_rejects_without_mutation():
    state = GameState("g")
    rng = GameRNG(1)
    result = reduce_command(state, AdvanceCharacter("c", "g", {"actor_id": "x"}), rng)
    assert result.state is state and result.rng == rng
