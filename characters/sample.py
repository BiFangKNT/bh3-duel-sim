from __future__ import annotations

from characters.base import BattleContext, Character, Stats


class BlazingWarrior(Character):
    name = "灼炎战士"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=150.0, attack=28.0, defense=9.0, speed=14.0))

    def passive_skill(self, context: BattleContext) -> None:
        stacks = self.status.get("rage", 0.0)
        self.status["rage"] = min(5.0, stacks + 1.0)

    def active_skill(self, target: Character, context: BattleContext) -> None:
        rage = self.status.get("rage", 0.0)
        bonus = 3.0 * rage
        crit = 1.5 if context.rng.random() < 0.2 else 1.0
        raw_damage = max(1.0, (self.stats.attack + bonus) * crit - target.stats.defense)
        target.receive_damage(raw_damage)


class FrostCaster(Character):
    name = "霜寒术士"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=110.0, attack=22.0, defense=10.0, speed=18.0))
        self.status["ice_shield"] = 15.0

    def passive_skill(self, context: BattleContext) -> None:
        shield = self.status.get("ice_shield", 0.0)
        if shield < 10.0:
            self.status["ice_shield"] = shield + 5.0

    def active_skill(self, target: Character, context: BattleContext) -> None:
        damage = max(1.0, self.stats.attack + 5.0 - target.stats.defense * 0.5)
        target.receive_damage(damage)
        target.status["speed_penalty"] = min(5.0, target.status.get("speed_penalty", 0.0) + 1.0)
        if context.rng.random() < 0.15:
            target.status["stunned_turns"] = target.status.get("stunned_turns", 0.0) + 1.0

    def receive_damage(self, amount: float) -> None:
        shield = self.status.get("ice_shield", 0.0)
        if shield > 0:
            absorbed = min(shield, amount)
            amount -= absorbed
            self.status["ice_shield"] = shield - absorbed
        if amount > 0:
            super().receive_damage(amount)
