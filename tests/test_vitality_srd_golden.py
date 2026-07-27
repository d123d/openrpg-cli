import json
from pathlib import Path
from openrpg_cli.rules.vitality import DamageType


def test_damage_types_match_srd_corpus() -> None:
    rows = json.loads(Path("openrpg_cli/data/srd521/DamageTypeDescription.json").read_text(encoding="utf-8"))
    assert {row["fields"]["describes"] for row in rows} == {item.value for item in DamageType}
