from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict


@dataclass
class Stats:
    max_hp: float
    attack: float
    defense: float
    speed: float


class Character:
    """角色基类，包含基础属性与技能钩子。"""

    name: str = "Unnamed"

    def __init__(self, stats: Stats) -> None:
        self.stats = stats
        self.hp = float(stats.max_hp)
        self.status: Dict[str, float] = {}  # 用于记录持续状态或临时加成

    # 可以由子类覆写的方法
    def active_skill(self, target: "Character", context: "BattleContext") -> None:
        """主动技能默认执行普通攻击。"""
        self.basic_attack(target, context)

    def passive_skill(self, context: "BattleContext") -> None:
        """战斗开始或每回合触发的被动技能，占位实现。"""

    # 战斗行为
    def take_turn(self, target: "Character", context: "BattleContext") -> None:
        if not self.on_turn_start(context):
            return
        self.passive_skill(context)
        self.active_skill(target, context)

    def is_alive(self) -> bool:
        return self.hp > 0

    def get_effective_speed(self) -> float:
        bonus = float(self.status.get("speed_bonus", 0.0))
        penalty = float(self.status.get("speed_penalty", 0.0))
        return max(1.0, self.stats.speed + bonus - penalty)

    def basic_attack(self, target: "Character", context: "BattleContext") -> None:
        raw_damage = max(1.0, self.stats.attack - target.stats.defense)
        target.receive_damage(raw_damage)

    def receive_damage(self, amount: float) -> None:
        self.hp -= amount

    def on_turn_start(self, context: "BattleContext") -> bool:
        acted = True
        penalty = self.status.get("speed_penalty", 0.0)
        if penalty:
            penalty = max(0.0, penalty - 1.0)
            if penalty:
                self.status["speed_penalty"] = penalty
            else:
                self.status.pop("speed_penalty", None)
        stun = self.status.get("stunned_turns", 0.0)
        if stun:
            stun -= 1.0
            if stun > 0:
                self.status["stunned_turns"] = stun
            else:
                self.status.pop("stunned_turns", None)
            acted = False
        return acted

    def clone(self) -> "Character":
        """以初始状态复制角色，供新的战斗使用。"""
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
