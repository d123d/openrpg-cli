import json
from pathlib import Path


def test_resolution_rule_keys_exist() -> None:
    rows = json.loads(Path("openrpg_cli/data/srd521/Rule.json").read_text(encoding="utf-8"))
    keys = {row["pk"] for row in rows}
    expected = {
        "srd-2024_the-six-abilities_ability-modifiers",
        "srd-2024_d20-tests_ability-checks",
        "srd-2024_d20-tests_saving-throw",
        "srd-2024_d20-tests_attack-rolls",
        "srd-2024_d20-tests_advantage-disadvantage",
        "srd-2024_proficiency_bonus-dont-stack",
    }
    assert expected <= keys
