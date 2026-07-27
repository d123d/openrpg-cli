from typer.testing import CliRunner

from openrpg_cli.cli import app
from openrpg_cli.systems import SystemRegistry


def test_registry_keeps_system_packs_isolated() -> None:
    registry = SystemRegistry()
    packs = registry.packs()
    assert {pack.pack_id for pack in packs} == {
        "acks-core",
        "cairn-first-edition",
        "dungeon-world",
        "fate-accelerated",
        "fate-condensed",
        "fate-core",
        "forged-in-the-dark-srd",
        "legacy-srd",
        "mothership",
        "pf2e-core",
        "questworlds-srd",
        "srd521",
    }
    assert registry.select(["srd521", "dungeon-world"])[0].root != registry.select(
        ["srd521", "dungeon-world"]
    )[1].root


def test_quarantined_packs_cannot_be_selected() -> None:
    registry = SystemRegistry()
    # questworlds-srd remains quarantined (reserved logo, no redistribution)
    pack = registry.get("questworlds-srd", allow_disabled=True)
    assert pack.manifest["quarantined"] is True
    try:
        registry.get("questworlds-srd")
    except PermissionError:
        pass
    else:
        raise AssertionError("questworlds-srd should be blocked")
    assert not pack.manifest["declared_files"]
    assert pack.manifest["disabled_reason"]


def test_new_open_systems_have_pinned_primary_sources_and_legal_files() -> None:
    registry = SystemRegistry()
    ids = {
        "fate-core",
        "fate-accelerated",
        "fate-condensed",
        "dungeon-world",
        "forged-in-the-dark-srd",
        "cairn-first-edition",
    }
    for pack_id in ids:
        pack = registry.get(pack_id)
        assert len(pack.manifest["source_commit"]) == 40
        assert pack.manifest["source_files"]
        assert pack.manifest["license"]["verified"] is True
        for key in ("license_file", "notice_file", "attribution_file"):
            assert (pack.root / pack.manifest[key]).is_file()

    questworlds = registry.get("questworlds-srd", allow_disabled=True)
    assert questworlds.manifest["quarantined"] is True
    assert not questworlds.manifest["declared_files"]
    assert "reserved logo" in questworlds.manifest["disabled_reason"]


def test_share_alike_content_stays_in_isolated_pack() -> None:
    cairn = SystemRegistry().get("cairn-first-edition")
    assert cairn.manifest["license"]["id"] == "CC-BY-SA-4.0"
    assert cairn.root.parent.name == "packs"
    assert cairn.root.parent.parent.name == "cairn"


def test_pack_audit_passes() -> None:
    assert all(not errors for errors in SystemRegistry().audit().values())


def test_systems_cli_list_info_audit() -> None:
    runner = CliRunner()
    listed = runner.invoke(app, ["systems", "list", "--json"])
    assert listed.exit_code == 0
    assert '"pack_id": "srd521"' in listed.stdout
    # mothership is now enabled (CC-BY-4.0 verified)
    info = runner.invoke(app, ["systems", "info", "mothership", "--json"])
    assert info.exit_code == 0
    assert '"quarantined": false' in info.stdout
    assert '"enabled": true' in info.stdout
    audit = runner.invoke(app, ["systems", "audit"])
    assert audit.exit_code == 0
    assert "srd521: PASS" in audit.stdout
