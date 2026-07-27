from srd_cli.rules.rests import RestRequest, perform_rest, resource_recovery_hook
from srd_cli.rules.spellcasting import CastingState, Resource

def test_rest_hooks_are_owned_ordered_and_interruptible():
    resource = Resource("rage", "barbarian", 0, 2, "long")
    state = CastingState((), resources=(resource,))
    result = perform_rest(RestRequest("r1", "long", 480), state, (resource_recovery_hook(resource),))
    assert result.state.resources[0].current == 2
    interrupted = perform_rest(RestRequest("r2", "short", 60, True), state, ())
    assert not interrupted.completed and interrupted.state is state
