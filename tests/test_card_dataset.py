from duel_engine.cards import MALISS_CORE6_CARDS, get_maliss_core6_cards


EXPECTED_MALISS_CORE6_NAMES = {
    "M∀LICE＜P＞White Rabbit",
    "M∀LICE＜P＞Cheshire Cat",
    "M∀LICE＜P＞March Hare",
    "M∀LICE＜P＞Dormouse",
    "M∀LICE IN UNDERGROUND",
    "M∀LICE＜C＞MTP－０７",
}


def test_maliss_core6_dataset_has_expected_cards():
    cards = get_maliss_core6_cards()

    assert cards == MALISS_CORE6_CARDS
    assert len(cards) == 6
    assert {card["name"] for card in cards} == EXPECTED_MALISS_CORE6_NAMES


def test_maliss_core6_cards_have_required_fields():
    cards = get_maliss_core6_cards()

    ids = [card["id"] for card in cards]
    assert len(ids) == len(set(ids))

    for card in cards:
        assert set(card.keys()).issuperset({"id", "name", "type", "effect_text"})
        assert isinstance(card["id"], str) and card["id"]
        assert isinstance(card["name"], str) and card["name"]
        assert isinstance(card["type"], str) and card["type"]
        assert isinstance(card["effect_text"], str) and card["effect_text"]


def test_spell_speed_is_present_for_spell_and_trap():
    cards = get_maliss_core6_cards()
    by_name = {card["name"]: card for card in cards}

    assert by_name["M∀LICE IN UNDERGROUND"].get("spell_speed") == 1
    assert by_name["M∀LICE＜C＞MTP－０７"].get("spell_speed") == 2

    for name in {
        "M∀LICE＜P＞White Rabbit",
        "M∀LICE＜P＞Cheshire Cat",
        "M∀LICE＜P＞March Hare",
        "M∀LICE＜P＞Dormouse",
    }:
        assert "spell_speed" not in by_name[name]
