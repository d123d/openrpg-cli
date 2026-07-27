"""SRD CLI."""

__version__ = "0.1.0"

from srd_cli.api import RulesAPI, get_rules_api

__all__ = ("RulesAPI", "__version__", "get_rules_api")
