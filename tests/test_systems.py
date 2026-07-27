from typer.testing import CliRunner

from openrpg_cli.cli import app
from openrpg_cli.systems import SystemRegistry


def test_registry_keeps_system_packs_isolated() -> None:
    registry = SystemRegistry()
    packs = registry.packs()
    assert {pack.pack_id for pack in packs} == {
        "acks-core",
        "dungeon-world",
        "legacy-srd",
        "mothership",
        "pf2e-core",
        "srd521",
    }
    assert registry.select(["srd521", "dungeon-world"])[0].root != registry.select(
        ["srd521", "dungeon-world"]
    )[1].root


def test_quarantined_packs_cannot_be_selected() -> None:
    registry = SystemRegistry()
    for pack_id in ("acks-core", "mothership", "pf2e-core"):
        pack = registry.get(pack_id, allow_disabled=True)
        assert pack.manifest["quarantined"] is True
        try:
            registry.get(pack_id)
        except PermissionError:
            pass
        else:
            raise AssertionError(f"{pack_id} should be blocked")


def test_pack_audit_passes() -> None:
    assert all(not errors for errors in SystemRegistry().audit().values())


def test_systems_cli_list_info_audit() -> None:
    runner = CliRunner()
    listed = runner.invoke(app, ["systems", "list", "--json"])
    assert listed.exit_code == 0
    assert '"pack_id": "srd521"' in listed.stdout
    info = runner.invoke(app, ["systems", "info", "mothership", "--json"])
    assert info.exit_code == 0
    assert '"quarantined": true' in info.stdout
    audit = runner.invoke(app, ["systems", "audit"])
    assert audit.exit_code == 0
    assert "srd521: PASS" in audit.stdout
