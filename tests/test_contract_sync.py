import json
from importlib.resources import files


def test_contract_sync_metadata_records_upstream_and_core_compatibility():
    metadata = json.loads(files("openrpg_cli").joinpath("contract_sync.json").read_text())
    assert metadata["upstream"]["through_commit"] == "5b89831"
    assert metadata["upstream"]["ports"] == {
        "deterministic_rng_boundaries": "51bc0b8",
        "command_router_handlers": "cbbb155",
        "presentation_cli_composition": "5b89831",
    }
    assert metadata["core_compatibility"]["version"] == "0.1.0"
    assert metadata["core_compatibility"]["verified_commit"] == "c178e59"
