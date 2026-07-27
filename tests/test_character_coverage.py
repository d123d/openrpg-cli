from openrpg_cli.rules.character_coverage import build_coverage, validate_coverage


def test_complete_explicit_coverage():
    rows = build_coverage()
    validate_coverage(rows)
    assert rows
    assert all(row.reason and row.source_key for row in rows)
