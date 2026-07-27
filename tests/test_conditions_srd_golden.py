import json
from pathlib import Path
from openrpg_cli.rules.effects import CONDITION_REGISTRY, Condition


def test_all_condition_keys_match_corpus() -> None:
    rows = json.loads(Path("openrpg_cli/data/srd521/ConditionDescription.json").read_text(encoding="utf-8"))
    assert {row["pk"] for row in rows} == {definition.srd_key for definition in CONDITION_REGISTRY.values()}
    assert all(CONDITION_REGISTRY[c].implemented_hooks and CONDITION_REGISTRY[c].unsupported_clauses for c in Condition)
