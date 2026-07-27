from srd_cli.data import CATEGORY_TABLES, SRDRepository, category_name


def test_bundle_integrity() -> None:
    assert SRDRepository().verify() == []


def test_expected_core_counts() -> None:
    stats = SRDRepository().stats()
    assert stats["creatures"] == 331
    assert stats["spells"] == 339
    assert stats["backgrounds"] == 4
    assert stats["species"] == 9
    assert stats["weapons"] == 38


def test_find_exact_and_alias_category() -> None:
    repo = SRDRepository()
    goblin = repo.find("monster", "Goblin Warrior")
    assert goblin is not None
    assert goblin["name"] == "Goblin Warrior"
    assert category_name("race") == "species"


def test_search_stays_inside_public_categories() -> None:
    repo = SRDRepository()
    hits = repo.search("fireball")
    assert hits
    assert all(category in CATEGORY_TABLES for category, _ in hits)
