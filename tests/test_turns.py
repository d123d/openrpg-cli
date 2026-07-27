from srd_cli.engine.rng import GameRNG
from srd_cli.rules.turns import *


def test_initiative_turns_surprise_and_ties():
    actors=(("b","t",2),("a","t",2),("c","u",0))
    state,rng=roll_initiative(actors,(("t",("a","b")),("u",("c",))),GameRNG(1),frozenset({"a"}))
    assert rng.draws==3
    assert sorted(state.order.actor_ids)==["a","b","c"]
    before=state
    state2,event=end_turn(state,"wrong")
    assert state2==before and not event.accepted
    current=state.current_actor_id
    state,_=end_turn(state,current)
    assert state.current_actor_id!=current


def test_budget_atomic_and_reaction_trigger():
    budget=reset_budget(25)
    same,reason=spend_budget(budget,ActionCost(action=2))
    assert same==budget and reason=="insufficient_action"
    same,reason=spend_budget(budget,ActionCost(reaction=1))
    assert reason=="reaction_requires_trigger"
    spent,reason=spend_budget(budget,ActionCost(action=1,movement=5))
    assert reason is None and spent.action==0 and spent.movement==20
