# ruff: noqa: F403, F405
from openrpg_cli.domain.codecs import encode, decode_message
from openrpg_cli.domain.messages import *  # noqa: F403, F405
from openrpg_cli.domain.state import *  # noqa: F403, F405
from openrpg_cli.engine.reducer import reduce_command
from openrpg_cli.engine.rng import GameRNG


def state():
    return GameState(
        "g",
        actors=(ActorState("a", {"speed": 30}, team_id="x"), ActorState("b", {}, team_id="y")),
        teams=(TeamState("x", actor_ids=("a",)), TeamState("y", actor_ids=("b",))),
    )


def test_messages_roundtrip_and_replay():
    cmds = (StartEncounter("s", "g", {"encounter_id": "e", "actor_ids": ["a", "b"]}),)
    assert decode_message(encode(cmds[0])) == cmds[0]
    snapshots = []
    for _ in range(2):
        st = state()
        rng = GameRNG(7)
        for cmd in cmds:
            result = reduce_command(st, cmd, rng)
            st, rng = result.state, result.rng
        snapshots.append(encode(st))
    assert snapshots[0] == snapshots[1]
    current = dict(st.encounters[0].data)["order"][dict(st.encounters[0].data)["index"]]["actor_id"]
    q = QueryLegalCommands("q", "g", {"encounter_id": "e", "actor_id": current})
    out = reduce_command(st, q, rng)
    assert out.state == st and out.rng == rng and out.events[0].type_tag == "legal_commands_listed"


def test_spoof_rejects_atomically():
    start = reduce_command(
        state(),
        StartEncounter("s", "g", {"encounter_id": "e", "actor_ids": ["a", "b"]}),
        GameRNG(1),
    )
    out = reduce_command(
        start.state, EndTurn("e1", "g", {"encounter_id": "e", "actor_id": "nope"}), start.rng
    )
    assert (
        out.state == start.state
        and out.rng == start.rng
        and out.events[0].type_tag == "command_rejected"
    )
