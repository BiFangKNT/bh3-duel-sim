from __future__ import annotations

from typing import Tuple, Type

from battle import BattleEngine
from characters import Bronya, BronyaTest, Character, Kiana, LiSushang, ChenXue, Theresa, DreamSeeker, ChenXueCopy

BATTLES = 10_000
MATCHUPS: Tuple[Tuple[Type[Character], Type[Character]], ...] = (
    # (Bronya, Kiana),
    # (LiSushang, Kiana),
    # (Bronya, LiSushang),
    # (ChenXue, Theresa),
    (ChenXue, DreamSeeker),
)


def main() -> None:
    engine = BattleEngine(max_rounds=150, seed=None)

    for cls_a, cls_b in MATCHUPS:
        results = engine.simulate(cls_a, cls_b, BATTLES)
        name_a = cls_a().name
        name_b = cls_b().name
        wins_a = results.get(name_a, 0)
        wins_b = results.get(name_b, 0)
        draws = results.get("draw", 0)

        print(f"{name_a} vs {name_b}")
        print(f"总对局: {BATTLES}")
        print(f"{name_a} 胜场: {wins_a}, 胜率: {wins_a / BATTLES:.2%}")
        print(f"{name_b} 胜场: {wins_b}, 胜率: {wins_b / BATTLES:.2%}")
        print(f"平局: {draws}, 占比: {draws / BATTLES:.2%}")
        print("-" * 40)

    for cls_a, cls_b in MATCHUPS:
        name_a = cls_a().name
        name_b = cls_b().name
        print(f"=== 单局行动详情（{name_a} vs {name_b}） ===")
        engine.fight(cls_a, cls_b, verbose=True)


if __name__ == "__main__":
    main()
