from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass
class Stats:
    max_hp: float
    attack: float
    defense: float
    speed: float


class Character:
    """角色基类，包含基础属性与技能钩子。"""

    COMMON_STATE_KEYS = (
        "speed_bonus",
        "speed_penalty",
        "stunned_turns",
        "confused_turns",
        "damage_reduction_value",
        "damage_reduction_turns",
    )

    name: str = "Unnamed"

    def __init__(self, stats: Stats) -> None:
        self.stats = stats
        self.hp = float(stats.max_hp)
        self.common_status: Dict[str, float] = {key: 0.0 for key in self.COMMON_STATE_KEYS}
        self.unique_status: Dict[str, Any] = {}
        self._turn_hooks: Dict[str, list[Callable[["Character", "BattleContext"], None]]] = {
            "start": [],
            "end": [],
        }

    # 可以由子类覆写的方法
    def active_skill(self, target: "Character", context: "BattleContext") -> None:
        """主动技能默认无特殊效果。"""

    def can_use_active_skill(self, target: "Character", context: "BattleContext") -> bool:
        """决定当前回合是否可以释放主动技能。"""
        return False

    def passive_skill(self, context: "BattleContext") -> None:
        """战斗开始或每回合触发的被动技能，占位实现。"""

    def perform_normal_attack(self, target: "Character", context: "BattleContext") -> None:
        """执行当前回合的普通攻击，默认调用 basic_attack。"""
        self.basic_attack(target, context)

    # 战斗行为
    def take_turn(self, target: "Character", context: "BattleContext") -> None:
        context.log(f"{self.name} 行动开始，HP {self.hp:.1f}")
        passive_blocked = self._consume_passive_disable_turn(context)
        if not self.on_turn_start(context):
            context.log(f"{self.name} 因异常状态而跳过回合")
            self.on_turn_end(context)
            return
        if self._abort_turn_if_dead(context):
            return
        if not passive_blocked:
            self.passive_skill(context)
            if self._abort_turn_if_dead(context):
                return
        if self.can_use_active_skill(target, context):
            context.log(f"{self.name} 释放主动技能")
            self.active_skill(target, context)
            if self._abort_turn_if_dead(context):
                return
        normal_target = self.get_normal_attack_target(target, context)
        self.perform_normal_attack(normal_target, context)
        if self._abort_turn_if_dead(context):
            return
        self.on_turn_end(context)

    def is_alive(self) -> bool:
        return self.hp > 0

    def get_effective_speed(self) -> float:
        bonus = float(self.common_status.get("speed_bonus", 0.0))
        penalty = float(self.common_status.get("speed_penalty", 0.0))
        return max(1.0, self.stats.speed + bonus - penalty)

    def get_normal_attack_target(self, intended_target: "Character", context: "BattleContext") -> "Character":
        confusion = self.common_status.get("confused_turns", 0.0)
        if confusion > 0:
            context.log(f"{self.name} 处于混乱，普通攻击改为自己")
            return self
        return intended_target

    def basic_attack(
        self,
        target: "Character",
        context: "BattleContext",
        *,
        base_damage: float | None = None,
        multiplier: float = 1.0,
        flat_bonus: float = 0.0,
        ignore_defense: bool = False,
        ignore_reduction: bool = False,
    ) -> float:
        attack_value = base_damage if base_damage is not None else self.stats.attack * multiplier + flat_bonus
        defense = 0.0 if ignore_defense else target.stats.defense
        raw_damage = max(1.0, attack_value - defense)
        dealt = target.receive_damage(raw_damage, ignore_reduction=ignore_reduction)
        context.log(f"{self.name} 对 {target.name} 造成 {dealt:.1f} 点伤害，{target.name} 当前 HP {max(target.hp, 0):.1f}")
        return dealt

    def receive_damage(self, amount: float, *, ignore_reduction: bool = False, pure_damage: bool = False) -> float:
        if amount <= 0:
            return 0.0
        if pure_damage:
            self.hp -= amount
            return amount
        reduction = 0.0 if ignore_reduction else float(self.common_status.get("damage_reduction_value", 0.0))
        actual = max(0.0, amount - reduction)
        self.hp -= actual
        return actual

    def heal(self, amount: float, context: "BattleContext" | None = None) -> float:
        if amount <= 0:
            return 0.0
        before = self.hp
        self.hp = min(self.stats.max_hp, self.hp + amount)
        recovered = self.hp - before
        if recovered > 0 and context:
            context.log(f"{self.name} 回复 {recovered:.1f} 点生命")
        return recovered

    def on_turn_start(self, context: "BattleContext") -> bool:
        self._run_turn_hooks("start", context)
        acted = True
        penalty_before = self.common_status.get("speed_penalty", 0.0)
        if penalty_before > 0:
            remaining = self._decay_common_status("speed_penalty")
            context.log(f"{self.name} 的减速效果剩余 {remaining:.1f} 回合")
        stun_before = self.common_status.get("stunned_turns", 0.0)
        if stun_before > 0:
            remaining = self._decay_common_status("stunned_turns")
            context.log(f"{self.name} 被控制，剩余 {remaining:.1f} 回合无法行动")
            acted = False
        dr_turns = self.common_status.get("damage_reduction_turns", 0.0)
        if dr_turns > 0:
            remaining = self._decay_common_status("damage_reduction_turns")
            if remaining == 0.0:
                self.common_status["damage_reduction_value"] = 0.0
                context.log(f"{self.name} 的减伤效果结束")
        return acted

    def on_turn_end(self, context: "BattleContext") -> None:
        confusion = self.common_status.get("confused_turns", 0.0)
        if confusion > 0:
            remaining = self._decay_common_status("confused_turns")
            if remaining > 0:
                context.log(f"{self.name} 仍处于混乱，剩余 {remaining:.1f} 回合")
            else:
                context.log(f"{self.name} 恢复了清醒")
        self._run_turn_hooks("end", context)

    def apply_confusion(self, turns: float, context: "BattleContext" | None = None) -> None:
        new_turns = max(self.common_status.get("confused_turns", 0.0), max(0.0, turns))
        self.common_status["confused_turns"] = new_turns
        if context:
            context.log(f"{self.name} 陷入混乱 {new_turns:.1f} 回合")
        self.on_negative_state("confusion", context)

    def apply_damage_reduction(self, value: float, turns: float, context: "BattleContext" | None = None) -> None:
        self.common_status["damage_reduction_value"] = max(0.0, value)
        self.common_status["damage_reduction_turns"] = max(0.0, turns)
        if context:
            context.log(f"{self.name} 获得减伤 {value:.1f}，持续 {turns:.1f} 回合")

    def disable_passive(self, turns: float, context: "BattleContext" | None = None) -> None:
        if turns <= 0:
            return
        current = float(self.unique_status.get("passive_disabled_turns", 0.0))
        updated = max(current, float(turns))
        self.unique_status["passive_disabled_turns"] = updated
        if context:
            context.log(f"{self.name} 的被动被封锁 {updated:.1f} 回合")

    def get_passive_disabled_turns(self) -> float:
        """返回被动被封锁的剩余回合数，0 表示未被封锁。"""
        return float(self.unique_status.get("passive_disabled_turns", 0.0))

    def can_trigger_passive_effect(
        self, context: "BattleContext" | None = None, *, announce: bool = True
    ) -> bool:
        """供子类在自定义被动逻辑中统一判定封锁状态。"""
        remaining = self.get_passive_disabled_turns()
        if remaining <= 0:
            return True
        if context and announce:
            context.log(f"{self.name} 的被动被封锁，剩余 {remaining:.1f} 回合")
        return False


    def on_negative_state(self, state: str, context: "BattleContext" | None = None) -> None:
        """子类可覆写：受到控制或属性降低时触发。"""

    def _decay_common_status(self, key: str, amount: float = 1.0) -> float:
        value = self.common_status.get(key, 0.0)
        if value <= 0:
            return 0.0
        value = max(0.0, value - amount)
        self.common_status[key] = value
        return value

    def add_turn_hook(self, when: str, hook: Callable[["Character", "BattleContext"], None]) -> None:
        hooks = self._turn_hooks.setdefault(when, [])
        if hook not in hooks:
            hooks.append(hook)

    def remove_turn_hook(self, when: str, hook: Callable[["Character", "BattleContext"], None]) -> None:
        hooks = self._turn_hooks.get(when)
        if not hooks:
            return
        if hook in hooks:
            hooks.remove(hook)

    def _run_turn_hooks(self, when: str, context: "BattleContext") -> None:
        for hook in list(self._turn_hooks.get(when, [])):
            hook(self, context)

    def _consume_passive_disable_turn(self, context: "BattleContext") -> bool:
        remaining = float(self.unique_status.get("passive_disabled_turns", 0.0))
        if remaining <= 0:
            return False
        remaining = max(0.0, remaining - 1.0)
        self.unique_status["passive_disabled_turns"] = remaining
        context.log(f"{self.name} 的被动被封锁，剩余 {remaining:.1f} 回合")
        return True

    def _abort_turn_if_dead(self, context: "BattleContext") -> bool:
        if self.is_alive():
            return False
        context.log(f"{self.name} 无法继续行动，已经倒下")
        return True

    def clone(self) -> "Character":
        """以初始状态复制角色，供新的战斗使用。"""
        try:
            return self.__class__()  # type: ignore[call-arg]
        except TypeError:
            cloned = self.__class__(Stats(
                float(self.stats.max_hp),
                float(self.stats.attack),
                float(self.stats.defense),
                float(self.stats.speed),
            ))
            return cloned


class BattleContext:
    """为技能提供额外信息。"""

    def __init__(self, rng: random.Random | None = None) -> None:
        self.turn_index = 0
        self.rng = rng or random.Random()
        self.logging_enabled = False
        self.turn_log: list[str] = []

    def set_logging(self, enabled: bool) -> None:
        self.logging_enabled = enabled

    def log(self, message: str) -> None:
        if self.logging_enabled:
            self.turn_log.append(message)

    def consume_turn_log(self) -> list[str]:
        if not self.turn_log:
            return []
        logs = self.turn_log[:]
        self.turn_log.clear()
        return logs
