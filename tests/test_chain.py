import pytest

from duel_engine.chain import ChainBuilder, ChainResolver
from duel_engine.timing import SpellSpeed


def test_chain_builder_add_link_assigns_incrementing_chain_id():
    builder = ChainBuilder()

    first = builder.add_link(
        effect_id="e1",
        source_card_id="c1",
        targets=["t1"],
        controller="p1",
        spell_speed=SpellSpeed.SS1,
    )
    second = builder.add_link(
        effect_id="e2",
        source_card_id="c2",
        targets=["t2"],
        controller="p2",
        spell_speed=SpellSpeed.SS2,
    )

    assert first.chain_id == 1
    assert second.chain_id == 2


def test_chain_builder_build_chain_returns_lifo_order():
    builder = ChainBuilder()
    builder.add_link(
        effect_id="e1",
        source_card_id="c1",
        targets=[],
        controller="p1",
        spell_speed=SpellSpeed.SS1,
    )
    builder.add_link(
        effect_id="e2",
        source_card_id="c2",
        targets=[],
        controller="p2",
        spell_speed=SpellSpeed.SS2,
    )
    builder.add_link(
        effect_id="e3",
        source_card_id="c3",
        targets=[],
        controller="p1",
        spell_speed=SpellSpeed.SS3,
    )

    chain = builder.build_chain()

    assert [link.effect_id for link in chain] == ["e3", "e2", "e1"]
    assert [link.chain_id for link in chain] == [3, 2, 1]


def test_chain_builder_close_chain_blocks_new_links():
    builder = ChainBuilder()
    builder.add_link(
        effect_id="e1",
        source_card_id="c1",
        targets=[],
        controller="p1",
        spell_speed=SpellSpeed.SS1,
    )
    builder.close_chain()

    with pytest.raises(ValueError):
        builder.add_link(
            effect_id="e2",
            source_card_id="c2",
            targets=[],
            controller="p2",
            spell_speed=SpellSpeed.SS2,
        )


def test_chain_resolver_resolves_chain_reverse_order_with_negation_layer():
    builder = ChainBuilder()
    first = builder.add_link(
        effect_id="e1",
        source_card_id="c1",
        targets=["t1"],
        controller="p1",
        spell_speed=SpellSpeed.SS1,
    )
    _second = builder.add_link(
        effect_id="e2",
        source_card_id="c2",
        targets=["t2"],
        controller="p2",
        spell_speed=SpellSpeed.SS2,
    )
    third = builder.add_link(
        effect_id="e3",
        source_card_id="c3",
        targets=["t3"],
        controller="p1",
        spell_speed=SpellSpeed.SS3,
    )
    builder.close_chain()

    resolver = ChainResolver()
    resolver.negate(third)
    resolver.negate(first)

    result = resolver.resolve(builder.build_chain())

    assert [entry["effect_id"] for entry in result] == ["e3", "e2", "e1"]
    assert [entry["status"] for entry in result] == ["negated", "applied", "negated"]


def test_chain_resolver_apply_effects_is_placeholder_state_output():
    builder = ChainBuilder()
    builder.add_link(
        effect_id="draw_1",
        source_card_id="spell_1",
        targets=["p1"],
        controller="p1",
        spell_speed=SpellSpeed.SS1,
    )

    resolver = ChainResolver()
    result = resolver.apply_effects(builder.build_chain())

    assert result == [
        {
            "chain_id": 1,
            "effect_id": "draw_1",
            "controller": "p1",
            "source_card_id": "spell_1",
            "targets": ["p1"],
            "status": "applied",
        }
    ]
