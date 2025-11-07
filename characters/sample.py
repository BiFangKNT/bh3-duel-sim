from __future__ import annotations

from characters.base import BattleContext, Character, Stats


class Bronya(Character):
    name = "布洛妮娅"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=100.0, attack=18.0, defense=6.0, speed=20.0))
        self.unique_status["attack_cycle"] = 0.0

    def can_use_active_skill(self, target: Character, context: BattleContext) -> bool:
        cycle = self._advance_cycle(context)
        return cycle % 3 == 0

    def _advance_cycle(self, context: BattleContext) -> int:
        cycle = int(self.unique_status.get("attack_cycle", 0.0) + 1.0)
        self.unique_status["attack_cycle"] = float(cycle)
        context.log(f"{self.name} 进入第 {cycle} 次攻击流程")
        return cycle

    def active_skill(self, target: Character, context: BattleContext) -> None:
        context.log(f"{self.name} 触发主动额外打击")
        combo_damage = 0.0
        for idx in range(1, 6):
            context.log(f"{self.name} 额外打击第 {idx} 次")
            combo_damage += self._strike(target, context, base_damage=15.0)
            if not target.is_alive():
                break
        context.log(f"{self.name} 额外打击总伤害 {combo_damage:.1f}")
        if context.rng.random() < 0.25:
            target.apply_confusion(1.0, context)

    def perform_normal_attack(self, target: Character, context: BattleContext) -> None:
        self._strike(target, context)

    def _strike(self, target: Character, context: BattleContext, *, base_damage: float | None = None) -> float:
        ignore = context.rng.random() < 0.15
        if ignore:
            context.log(f"{self.name} 的被动触发，忽视防御与减伤")
        return self.basic_attack(
            target,
            context,
            base_damage=base_damage,
            ignore_defense=ignore,
            ignore_reduction=ignore,
        )


class BronyaTest(Bronya):
    name = "布洛妮娅-测试"

    def active_skill(self, target: Character, context: BattleContext) -> None:
        context.log(f"{self.name} [测试] 主动必中混乱")
        self._strike(target, context, base_damage=75.0)
        target.apply_confusion(1.0, context)

    def _strike(self, target: Character, context: BattleContext, *, base_damage: float | None = None) -> float:
        context.log(f"{self.name} [测试] 被动必定触发")
        return self.basic_attack(
            target,
            context,
            base_damage=base_damage,
            ignore_defense=True,
            ignore_reduction=True,
        )


class Kiana(Character):
    name = "琪亚娜"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=100.0, attack=18.0, defense=7.0, speed=21.0))
        self.unique_status["attack_cycle"] = 0.0

    def can_use_active_skill(self, target: Character, context: BattleContext) -> bool:
        cycle = self._advance_cycle(context)
        return cycle % 2 == 0

    def _advance_cycle(self, context: BattleContext) -> int:
        cycle = int(self.unique_status.get("attack_cycle", 0.0) + 1.0)
        self.unique_status["attack_cycle"] = float(cycle)
        context.log(f"{self.name} 进入第 {cycle} 次攻击流程")
        return cycle

    def active_skill(self, target: Character, context: BattleContext) -> None:
        context.log(f"{self.name} 触发特殊攻击")
        self._special_attack(target, context)

    def _special_attack(self, target: Character, context: BattleContext) -> None:
        base_damage = max(1.0, 20.0 - target.stats.defense)
        dealt = target.receive_damage(base_damage)
        context.log(f"主动额外造成 {dealt:.1f} 点伤害")
        current_hp = max(0.0, target.hp)
        passive_damage = max(1.0, current_hp * 0.15)
        pure = target.receive_damage(passive_damage, ignore_reduction=True, pure_damage=True)
        context.log(f"被动追加真伤 {pure:.1f}")
