"""
생성형 AI 클라이언트 (OpenAI)
- 재능 진단 결과에 대한 개인 맞춤 코칭 코멘트 생성
- OPENAI_API_KEY가 설정된 경우에만 동작 (미설정 시 None 반환하여 서비스 무영향)
- 존중·정직·성장 관점을 기반으로 한 가드레일 내장 프롬프트
"""

import httpx
from typing import Optional, Dict, List
from app.config import settings
from app.services.scoring_service import SPORT_NAMES_KO


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# 등급 → 한국어 표기
GRADE_KO = {
    "excellent": "최우수",
    "high": "우수",
    "above_average": "평균 이상",
    "average": "평균",
    "below_average": "평균 이하",
}

# 코칭 톤 결정을 위한 수준 분류
_HIGH = {"excellent", "high"}
_LOW = {"below_average"}

# 체력 항목 → (한글명, 대표 역량)
METRIC_KO = {
    "grip_strength": ("악력", "근력"),
    "sit_ups": ("윗몸일으키기", "근지구력"),
    "standing_long_jump": ("제자리멀리뛰기", "순발력"),
    "shuttle_run_20m": ("왕복오래달리기", "심폐지구력"),
    "sit_and_reach": ("좌전굴", "유연성"),
}


SYSTEM_PROMPT = """너는 청소년의 체력 측정 데이터를 해석해 따뜻하고 품격 있게 코칭하는 스포츠 과학 전문가야.
반드시 지킬 원칙:
1. 존중이 최우선 — 어떤 결과에도 학생의 노력과 가능성을 존중한다. 비하·동정·훈계는 절대 금지.
2. 정직 — 오직 제공된 측정 등급/백분위에 근거해 말한다. 데이터가 낮으면 '뛰어난 재능'이라 과장하지 않는다. 없는 재능을 지어내지 않는다.
3. 성장 관점 — 한 번의 측정이 학생의 전부가 아님을 전제로, 흥미와 꾸준함, 실천 가능한 '다음 한 걸음'을 제시한다.
4. 절제 — 엘리트 선수가 될 것이라 단정하지 않고, 의학·건강·체중 관련 조언은 하지 않는다. 진로를 강요하지 않는다.
5. 장애가 있는 경우 — 해당 종목(보치아·골볼·휠체어농구 등)과 학생의 역량을 그 자체로 진지하게 존중한다. '그럼에도 불구하고', '용기', 동정·시혜적 표현은 절대 쓰지 않는다.
6. 문체 — 상투어와 과장(예: '정말 감명받았어', '뛰어난 재능')을 피하고, 데이터에 근거한 구체적 관찰과 진심을 담아 자연스러운 반말로. 이모지·느낌표 남발 금지.
출력은 군더더기 없는 3~4문장의 한국어 코멘트 본문만."""


def _level(top_grade: str) -> str:
    if top_grade in _HIGH:
        return "high"
    if top_grade in _LOW:
        return "low"
    return "mid"


def _tone_instruction(level: str) -> str:
    if level == "high":
        return ("데이터가 실제로 뒷받침하는 강점을 구체적으로 짚어 진심으로 축하하고, "
                "그 강점을 더 키울 다음 한 걸음을 담백하게 제안해.")
    if level == "low":
        return ("절대 과장하거나 없는 재능을 칭찬하지 마. 대신 '이번 측정에서는 이 종목이 상대적으로 더 잘 맞는 편'이라고 "
                "솔직하되 따뜻하게 전하고, 지금부터 즐겁게 시작할 수 있는 작은 한 걸음을 제안해. "
                "한 번의 수치가 전부가 아님을 존중 있게 덧붙여.")
    return ("상대적으로 잘 맞는 종목과 두드러진 체력 요소를 알려주고, 흥미를 붙일 방법과 꾸준함을 담백하게 격려해. "
            "과장 없이 균형 있게.")


async def generate_talent_comment(
    scores: List[Dict],
    user_profile: Dict,
) -> Optional[str]:
    """
    재능 점수에 대한 개인 맞춤 코칭 코멘트 생성 (생성형 AI)

    scores: [{"sport","score","percentile","grade_level"}, ...] (내림차순 가정)
    user_profile: {"age","gender","disability_type"?,"metric_strengths"?:[한글역량,...]}
    """
    if not settings.OPENAI_API_KEY or not scores:
        return None

    try:
        top = scores[:3]
        top_lines = []
        for s in top:
            name = SPORT_NAMES_KO.get(s["sport"], s["sport"])
            grade = GRADE_KO.get(s.get("grade_level", ""), s.get("grade_level", ""))
            pct = s.get("percentile")
            pct_txt = f", 상위 {100 - pct:.0f}%" if isinstance(pct, (int, float)) else ""
            top_lines.append(f"- {name}: {grade}({s.get('score')}점{pct_txt})")

        level = _level(top[0].get("grade_level", ""))
        age = user_profile.get("age", "")
        gender = "남학생" if user_profile.get("gender") == "M" else "여학생"
        disability = user_profile.get("disability_type")
        dis_txt = ""
        if disability:
            dis_map = {"physical": "지체장애", "visual": "시각장애", "hearing": "청각장애", "intellectual": "지적장애"}
            dis_txt = f" · {dis_map.get(disability, '장애 유형 있음')} (장애인 스포츠 종목 기준으로 분석됨)"
        strengths = user_profile.get("metric_strengths") or []
        str_txt = f"\n상대적으로 두드러진 체력 요소: {', '.join(strengths)}" if strengths else ""

        user_prompt = (
            f"학생: {age}세 {gender}{dis_txt}\n"
            f"측정 기반 상위 종목(등급/점수/백분위):\n" + "\n".join(top_lines) + str_txt +
            f"\n\n지시: {_tone_instruction(level)}"
        )

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                OPENAI_API_URL,
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.6,
                    "max_tokens": 280,
                },
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
            else:
                print(f"OpenAI API error: {response.status_code} {response.text[:200]}")
            return None

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None
