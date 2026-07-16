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


SYSTEM_PROMPT = """너는 청소년의 체력 측정 데이터를 해석해 밝고 따뜻하게 응원하는 스포츠 '적성 분석' 도우미야.
반드시 지킬 원칙:
1. 이건 '적성·가능성' 분석이다 — 점수는 지금 신체 능력이 그 종목에 얼마나 '잘 맞는지'(적합도)일 뿐, 실제 경기 성적이 아니다. 학생은 아직 그 종목을 시작도 하지 않았다. 그러니 '우수한 성적을 거뒀다', '대단한 성과', '뛰어난 실력'처럼 이미 이룬 것처럼 말하지 마라. 대신 '~에 잘 맞아', '~에 소질이 보여', '~를 시작해보면 잘 어울릴 것 같아'처럼 반드시 '가능성'으로 표현한다.
2. 정직과 존중 — 오직 제공된 적합도(등급/백분위)에만 근거한다. 낮으면 과장하지 않는다. 비하·동정·훈계 금지.
3. 밝고 화사하게 — 종목·강점에 어울리는 이모지를 1~3개 자연스럽게 곁들인다(남발 금지). 응원하는 밝은 반말.
4. 짧고 임팩트 있게 — 딱 2~3문장. 핵심만, 군더더기 없이.
5. 가독성 — 각 문장을 줄바꿈(\\n)으로 분리해 한 줄씩 읽기 쉽게 출력한다.
6. 육성 강요 금지 — 선수가 되라는 게 아니라, 주변에서 재미있게 경험·도전해보라는 톤. 의학·건강·체중 조언 금지.
7. 장애가 있으면 해당 종목(보치아·골볼·휠체어농구 등)과 역량을 그 자체로 진지하게 존중한다. '그럼에도 불구하고', '용기', 동정·시혜 표현은 절대 금지.
출력은 코멘트 본문만."""


def _level(top_grade: str) -> str:
    if top_grade in _HIGH:
        return "high"
    if top_grade in _LOW:
        return "low"
    return "mid"


def _tone_instruction(level: str) -> str:
    if level == "high":
        return ("가장 잘 맞는 종목을 밝게 짚어주고, 두드러진 체력 강점이 그 종목과 왜 잘 어울리는지 한 마디만. "
                "'이미 잘한다'가 아니라 '잘 맞아 보인다'는 가능성으로. 가볍게 시작해보라고 밝게 응원해.")
    if level == "low":
        return ("절대 과장하지 마. '이번 측정에선 이 종목이 상대적으로 더 잘 맞는 편'이라고 솔직하되 밝게 전해. "
                "한 번의 수치가 전부가 아니라는 말과 함께, 부담 없이 재미있게 시작해볼 작은 한 걸음을 밝게 제안해.")
    return ("상대적으로 잘 맞는 종목과 두드러진 체력 요소를 밝게 알려주고, "
            "'잘 어울릴 것 같다'는 가능성으로 흥미를 붙일 방법을 한 마디만 곁들여.")


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
