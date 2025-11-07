from __future__ import annotations

from battle import BattleEngine
from characters import BlazingWarrior, FrostCaster

BATTLES = 10_000


def main() -> None:
    engine = BattleEngine(max_rounds=150, seed=2024)

    def warrior_factory() -> BlazingWarrior:
        return BlazingWarrior()

    def caster_factory() -> FrostCaster:
        return FrostCaster()

    results = engine.simulate(warrior_factory, caster_factory, BATTLES)

    name_a = BlazingWarrior().name
    name_b = FrostCaster().name
    wins_a = results.get(name_a, 0)
    wins_b = results.get(name_b, 0)
    draws = results.get("draw", 0)

    print(f"总对局: {BATTLES}")
    print(f"{name_a} 胜场: {wins_a}, 胜率: {wins_a / BATTLES:.2%}")
    print(f"{name_b} 胜场: {wins_b}, 胜率: {wins_b / BATTLES:.2%}")
    print(f"平局: {draws}, 占比: {draws / BATTLES:.2%}")


if __name__ == "__main__":
    main()
