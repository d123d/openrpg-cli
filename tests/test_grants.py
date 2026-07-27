import pytest
from srd_cli.rules.grants import ChoiceNode, Grant, project_grants, resolve_choices


def test_choice_projection_canonical_and_expertise_checked():
    nodes = (
        ChoiceNode("b", "src2", "expertise", 1, 1, ("arcana",), ("a",)),
        ChoiceNode("a", "src1", "skill", 1, 1, ("arcana",)),
    )
    grants = resolve_choices(nodes, {"a": ("arcana",), "b": ("arcana",)})
    assert project_grants(grants, 5).proficiency_bonus == 3
    with pytest.raises(ValueError):
        project_grants((Grant("expertise", "arcana", "x"),), 1)
