from __future__ import annotations

from collections import Counter


def summarize_emotional_signals(
    conflict: float,
    happiness: float,
    conf_kw: Counter[str],
    happy_kw: Counter[str],
) -> str:
    tension = float(conflict) - float(happiness)

    top_conf = [kw for kw, _ in conf_kw.most_common(3)]
    top_happy = [kw for kw, _ in happy_kw.most_common(3)]

    if tension > 5:
        mood = "전반적으로 갈등 신호가 우세한 하루입니다."
    elif tension < -5:
        mood = "긍정 신호가 갈등보다 강한 안정적인 하루입니다."
    else:
        mood = "긍정과 부정 신호가 균형을 이루는 중립적인 분위기입니다."

    conf_join = ", ".join(top_conf) if top_conf else "(해당 없음)"
    happy_join = ", ".join(top_happy) if top_happy else "(해당 없음)"

    summary = (
        f"{mood} "
        f"갈등을 유발한 주요 키워드는 {conf_join}이며, "
        f"긍정 흐름을 만든 키워드는 {happy_join}입니다. "
        f"오늘의 TEN EYES 정서 흐름은 "
        f"'행복 {happiness:.1f} vs 갈등 {conflict:.1f}'로 요약됩니다."
    )

    return summary
