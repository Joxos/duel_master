from affairon import Dispatcher
from duel_core.affairs import (
    Attack,
    AvailableActions,
    Draw,
    DuelInit,
    EnterPhase,
    Forbid,
    NormalSummon,
    TurnCleanup,
)
from duel_core.models import RuntimeCard, REPRESENTATION
from duel_core.phase import Phase

TURN_DRAW_NUM = 1
INITIAL_DRAW_NUM = 5

PHASE_GRAPH: dict[Phase, tuple[Phase, ...]] = {
    Phase.DRAW: (Phase.STANDBY,),
    Phase.STANDBY: (Phase.MAIN_1,),
    Phase.MAIN_1: (Phase.BATTLE, Phase.END),
    Phase.BATTLE: (Phase.MAIN_2,),
    Phase.MAIN_2: (Phase.END,),
}


def can_normal_summon(card: RuntimeCard) -> bool:
    return card.card.level is not None and card.card.level <= 4


def setup(dispatcher: Dispatcher) -> None:
    @dispatcher.on(EnterPhase)
    def turn_draw(affair: EnterPhase) -> None:
        if affair.phase is not Phase.DRAW:
            return
        affair.duel.emit(
            Draw(
                duel=affair.duel,
                player=affair.duel.state.current_player,
                num=TURN_DRAW_NUM,
                requester=turn_draw,
            )
        )

    @dispatcher.on(DuelInit)
    def initial_draw(affair: DuelInit) -> None:
        for player in affair.duel.state.players:
            affair.duel.emit(
                Draw(
                    duel=affair.duel,
                    player=player,
                    num=INITIAL_DRAW_NUM,
                    requester=initial_draw,
                )
            )

    @dispatcher.on(DuelInit)
    def forbid_initial_turn_draw(affair: DuelInit) -> None:
        draw_action = Draw(
            duel=affair.duel,
            player=affair.duel.state.current_player,
            num=TURN_DRAW_NUM,
            requester=turn_draw,
        )
        affair.duel.emit(
            Forbid(
                duel=affair.duel,
                target=draw_action,
                outdated_when=TurnCleanup(
                    duel=affair.duel, turn=affair.duel.state.current_turn + 1
                ),
            )
        )

    @dispatcher.on(DuelInit)
    def forbid_first_turn_battle(affair: DuelInit) -> None:
        battle_action = EnterPhase(
            duel=affair.duel,
            phase=Phase.BATTLE,
            source_phase=Phase.MAIN_1,
            requester=phase_actions,
        )
        affair.duel.emit(
            Forbid(
                duel=affair.duel,
                target=battle_action,
                outdated_when=TurnCleanup(
                    duel=affair.duel, turn=affair.duel.state.current_turn + 1
                ),
            )
        )

    @dispatcher.on(AvailableActions)
    def phase_actions(affair: AvailableActions) -> None:
        for target_phase in PHASE_GRAPH.get(affair.duel.state.phase, ()):
            action = EnterPhase(
                duel=affair.duel,
                phase=target_phase,
                source_phase=affair.duel.state.phase,
                requester=phase_actions,
            )
            if affair.duel.kernel.is_forbidden(action):
                continue
            affair.actions.append(action)

    @dispatcher.on(AvailableActions)
    def normal_summon_actions(affair: AvailableActions) -> None:
        if affair.duel.state.phase not in (Phase.MAIN_1, Phase.MAIN_2):
            return
        if affair.duel.state.normal_summon_used:
            return
        if None not in affair.duel.state.current_player.monster_zones:
            return
        for card in affair.duel.state.current_player.hand:
            if not can_normal_summon(card):
                continue
            affair.actions.append(
                NormalSummon(
                    duel=affair.duel,
                    player=affair.duel.state.current_player,
                    card=card,
                    requester=normal_summon_actions,
                )
            )

    @dispatcher.on(AvailableActions)
    def battle_actions(affair: AvailableActions) -> None:
        if affair.duel.state.phase is not Phase.BATTLE:
            return
        attacker = affair.duel.state.current_player
        defender = affair.duel.state.opponent
        for attacker_card in attacker.monster_zones:
            if attacker_card is None:
                continue
            if attacker_card.representation is not REPRESENTATION.ATTACK:
                continue
            if all(d is None for d in defender.monster_zones):
                affair.actions.append(
                    Attack(
                        duel=affair.duel,
                        player=attacker,
                        attacker=attacker_card,
                        requester=battle_actions,
                    )
                )
                continue
            for defender_card in defender.monster_zones:
                if defender_card is None:
                    continue
                affair.actions.append(
                    Attack(
                        duel=affair.duel,
                        player=attacker,
                        attacker=attacker_card,
                        defender=defender_card,
                        requester=battle_actions,
                    )
                )
