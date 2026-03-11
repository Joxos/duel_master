from duel_engine.policy import DeterministicDefaultPolicy, StrictManualPolicy
from duel_engine.policy.base import ChoiceRequest


def test_strict_manual_policy_always_requires_external_input():
    policy = StrictManualPolicy()

    assert policy.choose(state=None, choice_request={"type": "pass_priority"}) is None
    assert (
        policy.choose(
            state={"turn": 1},
            choice_request={"type": "choose_targets", "options": ["c1", "c2"]},
        )
        is None
    )


def test_deterministic_default_policy_auto_passes_priority_and_records_choice():
    policy = DeterministicDefaultPolicy()

    choice = policy.choose(state=None, choice_request={"type": "pass_priority"})

    assert choice == "pass"
    assert policy.choice_log == [
        {
            "request_type": "pass_priority",
            "choice": "pass",
        }
    ]


def test_deterministic_default_policy_selects_first_target_by_default():
    policy = DeterministicDefaultPolicy()

    choice = policy.choose(
        state={"phase": "MAIN1"},
        choice_request={
            "type": "choose_targets",
            "options": ["target_a", "target_b", "target_c"],
        },
    )

    assert choice == ["target_a"]
    assert policy.choice_log[-1] == {
        "request_type": "choose_targets",
        "choice": ["target_a"],
    }


def test_deterministic_default_policy_uses_lifo_chain_resolution_default():
    policy = DeterministicDefaultPolicy()
    lifo_order_chain = ["chain_link_3", "chain_link_2", "chain_link_1"]

    choice = policy.choose(
        state={"chain_open": True},
        choice_request={"type": "resolve_chain", "options": lifo_order_chain},
    )

    assert choice == "chain_link_3"
    assert policy.choice_log[-1] == {
        "request_type": "resolve_chain",
        "choice": "chain_link_3",
    }


def test_deterministic_policy_replay_is_reproducible_for_same_sequence():
    sequence: list[ChoiceRequest] = [
        {"type": "pass_priority"},
        {"type": "choose_targets", "options": ["t1", "t2"]},
        {"type": "resolve_chain", "options": [2, 1]},
    ]
    first = DeterministicDefaultPolicy()
    second = DeterministicDefaultPolicy()

    first_choices = [first.choose(state=None, choice_request=req) for req in sequence]
    second_choices = [second.choose(state=None, choice_request=req) for req in sequence]

    assert first_choices == second_choices
    assert first.choice_log == second.choice_log
