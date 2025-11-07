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
        context.log(f"极限射击造成 {dealt:.1f} 点伤害，{target.name} 当前 HP {max(target.hp, 0):.1f}")
        current_hp = max(0.0, target.hp)
        passive_damage = max(1.0, current_hp * 0.15)
        pure = target.receive_damage(passive_damage, ignore_reduction=True, pure_damage=True)
        context.log(f"追击追加真伤 {pure:.1f} 点，{target.name} 当前 HP {max(target.hp, 0):.1f}")

class LiSushang(Character):
    name = "李素裳"
    BLEED_KEY = "lis_bleed"
    SKIP_NORMAL_KEY = "lis_skip_normal"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=100.0, attack=20.0, defense=7.0, speed=25.0))
        self.unique_status["attack_cycle"] = 0.0

    def can_use_active_skill(self, target: Character, context: BattleContext) -> bool:
        cycle = self._advance_cycle(context)
        return cycle % 3 == 0

    def _advance_cycle(self, context: BattleContext) -> int:
        cycle = int(self.unique_status.get("attack_cycle", 0.0) + 1.0)
        self.unique_status["attack_cycle"] = float(cycle)
        context.log(f"{self.name} 进入第 {cycle} 次攻击流程")
        return cycle

    def on_turn_start(self, context: BattleContext) -> bool:
        self.unique_status.pop(self.SKIP_NORMAL_KEY, None)
        return super().on_turn_start(context)

    def active_skill(self, target: Character, context: BattleContext) -> None:
        context.log(f"{self.name} 释放凌厉剑舞")
        dealt = self.basic_attack(target, context, base_damage=22.0)
        stacks = context.rng.randint(3, 6)
        self._apply_bleed(target, float(stacks), 2.0, context)
        self.unique_status[self.SKIP_NORMAL_KEY] = True
        context.log(
            f"{self.name} 主动技造成 {dealt:.1f} 点伤害并施加 {stacks} 层流血，{target.name} 当前 HP {max(target.hp, 0):.1f}"
        )

    def perform_normal_attack(self, target: Character, context: BattleContext) -> None:
        if self.unique_status.pop(self.SKIP_NORMAL_KEY, False):
            context.log(f"{self.name} 主动技能覆盖本回合普通攻击")
            return
        self.basic_attack(target, context)
        if context.rng.random() < 0.30:
            self._apply_bleed(target, 2.0, 2.0, context)
            context.log(f"{self.name} 被动触发，额外附加流血")

    def _apply_bleed(
        self,
        target: Character,
        stacks: float,
        turns: float,
        context: BattleContext,
    ) -> None:
        state = target.unique_status.get(self.BLEED_KEY)
        if not state:
            state = {"stacks": 0.0, "duration": 0.0}
            target.unique_status[self.BLEED_KEY] = state
        state["stacks"] = max(0.0, state.get("stacks", 0.0) + stacks)
        state["duration"] = float(turns)
        context.log(
            f"{target.name} 流血层数 {state['stacks']:.0f}，持续 {state['duration']:.0f} 回合"
        )
        if not state.get("hook_registered"):
            target.add_turn_hook("start", self._bleed_tick)
            state["hook_registered"] = True

    @staticmethod
    def _bleed_tick(victim: Character, context: BattleContext) -> None:
        state = victim.unique_status.get(LiSushang.BLEED_KEY)
        if not state:
            victim.remove_turn_hook("start", LiSushang._bleed_tick)
            return
        stacks = state.get("stacks", 0.0)
        duration = state.get("duration", 0.0)
        if stacks <= 0 or duration <= 0:
            victim.remove_turn_hook("start", LiSushang._bleed_tick)
            victim.unique_status.pop(LiSushang.BLEED_KEY, None)
            context.log(f"{victim.name} 的流血效果结束")
            return
        dealt = victim.receive_damage(stacks, ignore_reduction=True, pure_damage=True)
        context.log(f"{victim.name} 因流血承受 {dealt:.1f} 点伤害，当前 HP {max(victim.hp, 0):.1f}")
        duration -= 1.0
        if duration <= 0:
            victim.remove_turn_hook("start", LiSushang._bleed_tick)
            victim.unique_status.pop(LiSushang.BLEED_KEY, None)
            context.log(f"{victim.name} 的流血效果结束")
        else:
            state["duration"] = duration


class ChenXue(Character):
    name = "晨雪"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=100.0, attack=16.0, defense=8.0, speed=21.0))
        self.unique_status["attack_cycle"] = 0.0
        self._amplify_survivability()

    def _amplify_survivability(self) -> None:
        current_hp = self.hp
        self.stats.max_hp *= 1.5
        self.hp = min(current_hp, self.stats.max_hp)
        self.stats.defense *= 0.85

    def passive_skill(self, context: BattleContext) -> None:
        threshold = self.stats.max_hp * 0.30
        if self.hp < threshold:
            context.log(f"{self.name} 低血激发自愈")
            self.heal(5.0, context)

    def can_use_active_skill(self, target: Character, context: BattleContext) -> bool:
        cycle = self._advance_cycle(context)
        return cycle % 2 == 0

    def _advance_cycle(self, context: BattleContext) -> int:
        cycle = int(self.unique_status.get("attack_cycle", 0.0) + 1.0)
        self.unique_status["attack_cycle"] = float(cycle)
        context.log(f"{self.name} 进入第 {cycle} 次攻击流程")
        return cycle

    def active_skill(self, target: Character, context: BattleContext) -> None:
        lost_hp = max(0.0, self.stats.max_hp - self.hp)
        extra_damage = max(1.0, lost_hp * 0.12 + 8.0)
        dealt = target.receive_damage(extra_damage)
        context.log(f"{self.name} 将失血化为霜刃，额外造成 {dealt:.1f} 点伤害，{target.name} 当前 HP {max(target.hp, 0):.1f}")


class ChenXueCopy(Character):
    name = "晨雪-复制"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=100.0, attack=16.0, defense=8.0, speed=21.0))
        self.unique_status["attack_cycle"] = 0.0
        self._amplify_survivability()

    def _amplify_survivability(self) -> None:
        self.stats.max_hp *= 1.5
        self.hp *= 1.5
        self.stats.defense *= 0.85

    def passive_skill(self, context: BattleContext) -> None:
        threshold = self.stats.max_hp * 0.30
        if self.hp < threshold:
            context.log(f"{self.name} 低血激发自愈")
            self.heal(5.0, context)

    def can_use_active_skill(self, target: Character, context: BattleContext) -> bool:
        cycle = self._advance_cycle(context)
        return cycle % 2 == 0

    def _advance_cycle(self, context: BattleContext) -> int:
        cycle = int(self.unique_status.get("attack_cycle", 0.0) + 1.0)
        self.unique_status["attack_cycle"] = float(cycle)
        context.log(f"{self.name} 进入第 {cycle} 次攻击流程")
        return cycle

    def active_skill(self, target: Character, context: BattleContext) -> None:
        lost_hp = max(0.0, self.stats.max_hp - self.hp)
        extra_damage = max(1.0, lost_hp * 0.12 + 8.0)
        dealt = target.receive_damage(extra_damage)
        context.log(f"{self.name} 将失血化为霜刃，额外造成 {dealt:.1f} 点伤害，{target.name} 当前 HP {max(target.hp, 0):.1f}")


class Theresa(Character):
    name = "德丽莎"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=100.0, attack=23.0, defense=7.0, speed=24.0))
        self.unique_status["attack_cycle"] = 0.0

    def perform_normal_attack(self, target: Character, context: BattleContext) -> None:
        cycle = int(self.unique_status.get("attack_cycle", 0.0) + 1.0)
        self.unique_status["attack_cycle"] = float(cycle)
        if cycle % 3 == 0:
            self._special_attack(target, context)
        else:
            self.basic_attack(target, context)
        self._try_disable_enemy_passive(target, context)

    def _special_attack(self, target: Character, context: BattleContext) -> float:
        context.log(f"{self.name} 触发特殊攻击")
        if context.rng.random() < 0.70:
            dealt = self.basic_attack(target, context, base_damage=30.0)
            context.log(f"{self.name} 集中火力爆发成功")
        else:
            dealt = self.basic_attack(target, context, base_damage=1.0)
            context.log(f"{self.name} 攻击落空，仅造成象征性伤害")
            context.log(f"{self.name} 借机恢复气息")
            self.heal(18.0, context)
        return dealt

    def _try_disable_enemy_passive(self, target: Character, context: BattleContext) -> None:
        if not target.is_alive():
            return
        if context.rng.random() < 0.25:
            target.disable_passive(2.0, context)

    def on_negative_state(self, state: str, context: BattleContext | None = None) -> None:
        if context:
            context.log(f"{self.name} 因 {state} 被动触发恢复")
        self.heal(self.stats.max_hp * 0.10, context)


class DreamSeeker(Character):
    name = "寻梦者"

    def __init__(self) -> None:
        super().__init__(Stats(max_hp=100.0, attack=16.0, defense=8.0, speed=21.0))
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
        attack_value, note = self._prepare_attack_value(context)
        damage = attack_value * 1.30
        dealt = self.basic_attack(
            target,
            context,
            base_damage=damage,
            ignore_defense=True,
            ignore_reduction=True,
        )
        context.log(f"{self.name} 将信念化作梦境冲击，强行突破防御")
        if note:
            context.log(note)

    def perform_normal_attack(self, target: Character, context: BattleContext) -> None:
        attack_value, note = self._prepare_attack_value(context)
        self.basic_attack(target, context, base_damage=attack_value)
        if note:
            context.log(note)

    def _prepare_attack_value(self, context: BattleContext) -> tuple[float, str | None]:
        if not self.can_trigger_passive_effect(context, announce=False):
            remaining = self.get_passive_disabled_turns()
            note = f"{self.name} 的被动被封锁，剩余 {remaining:.1f} 回合"
            return self.stats.attack, note
        triggered = context.rng.random() < 0.60
        if not triggered:
            return self.stats.attack, f"{self.name} 被动未触发，攻击力保持 {self.stats.attack:.1f}"
        low_hp = self.hp < 50.0
        boosted = 30.0 if low_hp else 20.0
        if low_hp:
            note = f"{self.name} 低血被动触发，攻击力临时提升至 {boosted:.1f}"
        else:
            note = f"{self.name} 被动触发，攻击力临时提升至 {boosted:.1f}"
        return boosted, note
