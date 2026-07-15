"""
생성형 AI 클라이언트 (OpenAI)
- 재능 진단 결과에 대한 개인 맞춤 코칭 코멘트 생성
- OPENAI_API_KEY가 설정된 경우에만 동작 (미설정 시 None 반환하여 서비스 무영향)
"""

import httpx
from typing import Optional, Dict, List
from app.config import settings
from app.services.scoring_service import SPORT_NAMES_KO


OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


async def generate_talent_comment(
    scores: List[Dict],
    user_profile: Dict,
) -> Optional[str]:
    """
    재능 점수에 대한 개인 맞춤 코칭 코멘트 생성 (생성형 AI)

    Args:
        scores: 종목별 점수 리스트 [{"sport": "soccer", "score": 85, "grade_level": "high"}, ...]
        user_profile: {"age": 15, "gender": "M", "region_sido": "서울특별시"}

    Returns:
        생성된 코멘트 문자열 또는 None
    """
    if not settings.OPENAI_API_KEY:
        return None

    try:
        top_scores = scores[:3]
        top_sports_text = ", ".join([
            f"{SPORT_NAMES_KO.get(s['sport'], s['sport'])}({s['score']:.1f}점)"
            for s in top_scores
        ])

        age = user_profile.get("age", "")
        gender = "남학생" if user_profile.get("gender") == "M" else "여학생"

        prompt = f"""아래 체력 측정 결과를 바탕으로 학생에게 격려와 조언을 담은 짧은 코멘트를 작성해주세요.

학생 정보: {age}세 {gender}
상위 재능 종목: {top_sports_text}

다음을 담아 3-4문장의 한국어 코멘트로 작성해주세요:
1. 상위 종목에서 보이는 재능을 칭찬
2. 해당 종목에서 성장하기 위한 간단한 조언
3. 생활체육 또는 엘리트 경로에 대한 부드러운 안내"""

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                OPENAI_API_URL,
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": "당신은 청소년 체육 전문가입니다."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 300,
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
        # 실패해도 서비스 전체에 영향 없도록
        print(f"OpenAI API error: {e}")
        return None
