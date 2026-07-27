from openrpg_cli.domain.codecs import decode_message, encode
from openrpg_cli.domain.messages import ResolveTest
from openrpg_cli.domain.state import GameState
from openrpg_cli.engine.reducer import reduce_command
from openrpg_cli.engine.rng import GameRNG


def test_resolution_command_round_trip_and_replay() -> None:
    command = ResolveTest("r1", "g", {"kind": "check", "ability_modifier": 2, "target": 10})
    assert decode_message(encode(command)) == command
    left = reduce_command(GameState("g"), command, GameRNG(42))
    right = reduce_command(GameState("g"), command, GameRNG(42))
    assert encode(left.state) == encode(right.state)
    assert encode(left.events) == encode(right.events)
    assert left.rng == right.rng


def test_bad_resolution_is_atomic_rejection() -> None:
    state, rng = GameState("g"), GameRNG(2)
    result = reduce_command(state, ResolveTest("bad", "g", {"kind": "bogus"}), rng)
    assert result.state is state and result.rng is rng
    assert result.events[0].type_tag == "command_rejected"
