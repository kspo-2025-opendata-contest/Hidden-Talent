"""
Gemini API 클라이언트
- 재능 점수에 대한 설명/코멘트 생성
- GEMINI_API_KEY가 설정된 경우에만 동작
"""

import httpx
from typing import Optional, Dict, List
from app.config import settings
from app.services.scoring_service import SPORT_NAMES_KO


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent"


async def generate_talent_comment(
    scores: List[Dict],
    user_profile: Dict,
) -> Optional[str]:
    """
    재능 점수에 대한 설명 생성

    Args:
        scores: 종목별 점수 리스트 [{"sport": "soccer", "score": 85, "grade_level": "high"}, ...]
        user_profile: {"age": 15, "gender": "M", "region_sido": "서울특별시"}

    Returns:
        생성된 코멘트 문자열 또는 None
    """
    if not settings.GEMINI_API_KEY:
        return None

    try:
        # 상위 3개 종목 추출
        top_scores = scores[:3]
        top_sports_text = ", ".join([
            f"{SPORT_NAMES_KO.get(s['sport'], s['sport'])}({s['score']:.1f}점)"
            for s in top_scores
        ])

        age = user_profile.get("age", "")
        gender = "남학생" if user_profile.get("gender") == "M" else "여학생"

        prompt = f"""당신은 청소년 체육 전문가입니다. 아래 체력 측정 결과를 바탕으로 학생에게 격려와 조언을 담은 짧은 코멘트를 작성해주세요.

학생 정보: {age}세 {gender}
상위 재능 종목: {top_sports_text}

다음 형식으로 3-4문장의 한국어 코멘트를 작성해주세요:
1. 상위 종목에서 보이는 재능을 칭찬
2. 해당 종목에서 성장하기 위한 간단한 조언
3. 생활체육 또는 엘리트 경로에 대한 부드러운 안내

코멘트:"""

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 300,
                    }
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            return None

    except Exception as e:
        # 실패해도 서비스 전체에 영향 없도록
        print(f"Gemini API error: {e}")
        return None
