from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple

from characters.base import BattleContext, Character

CharacterFactory = Callable[[], Character]


class BattleEngine:
    def __init__(self, max_rounds: int = 200, seed: int | None = None) -> None:
        self.max_rounds = max_rounds
        self._rng = random.Random(seed)

    def fight(self, factory_a: CharacterFactory, factory_b: CharacterFactory) -> str:
        fighter_a = factory_a()
        fighter_b = factory_b()
        context = BattleContext(self._rng)
        rounds = 0

        while fighter_a.is_alive() and fighter_b.is_alive() and rounds < self.max_rounds:
            turn_order = self._decide_order(fighter_a, fighter_b)
            for attacker, defender in turn_order:
                context.turn_index += 1
                attacker.take_turn(defender, context)
                if not defender.is_alive():
                    return attacker.name
            rounds += 1

        if fighter_a.hp == fighter_b.hp:
            return "draw"
        return fighter_a.name if fighter_a.hp > fighter_b.hp else fighter_b.name

    def simulate(self, factory_a: CharacterFactory, factory_b: CharacterFactory, battles: int) -> Dict[str, int]:
        name_a = factory_a().name
        name_b = factory_b().name
        results = {name_a: 0, name_b: 0, "draw": 0}
        for _ in range(battles):
            outcome = self.fight(factory_a, factory_b)
            if outcome not in results:
                results[outcome] = 0
            results[outcome] += 1
        return results

    def _decide_order(self, fighter_a: Character, fighter_b: Character) -> List[Tuple[Character, Character]]:
        speed_a = fighter_a.get_effective_speed()
        speed_b = fighter_b.get_effective_speed()
        if speed_a == speed_b:
            if self._rng.random() < 0.5:
                return [(fighter_a, fighter_b), (fighter_b, fighter_a)]
            return [(fighter_b, fighter_a), (fighter_a, fighter_b)]
        if speed_a > speed_b:
            return [(fighter_a, fighter_b), (fighter_b, fighter_a)]
        return [(fighter_b, fighter_a), (fighter_a, fighter_b)]
