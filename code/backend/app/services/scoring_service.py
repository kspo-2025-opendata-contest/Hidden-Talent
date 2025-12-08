"""
재능 스코어링 서비스
- 체력 항목을 0~100점으로 정규화
- 종목별 가중치 적용하여 점수 계산
- 백분위/등급 추정
"""

from typing import Dict, Tuple, Optional


# 체력 항목별 정규화 기준 (min, max) - 성별에 따라 분리
# 실제 체력측정 데이터 기반 (청소년 기준)
NORMALIZATION_RANGES_BY_GENDER = {
    "M": {  # 남성
        "grip_strength": (15.0, 50.0),      # 악력 (kg) - 남성 청소년 기준
        "sit_ups": (15, 65),                # 윗몸일으키기 (회/분)
        "standing_long_jump": (140.0, 280.0),  # 제자리멀리뛰기 (cm)
        "shuttle_run_20m": (20, 100),       # 왕복오래달리기 (회)
        "sit_and_reach": (-10.0, 25.0),     # 좌전굴 (cm) - 남성은 유연성이 낮음
    },
    "F": {  # 여성
        "grip_strength": (10.0, 35.0),      # 악력 (kg) - 여성 청소년 기준
        "sit_ups": (8, 45),                 # 윗몸일으키기 (회/분)
        "standing_long_jump": (100.0, 220.0),  # 제자리멀리뛰기 (cm)
        "shuttle_run_20m": (15, 80),        # 왕복오래달리기 (회)
        "sit_and_reach": (-5.0, 35.0),      # 좌전굴 (cm) - 여성은 유연성이 높음
    },
}

# 기본 정규화 기준 (성별 미지정시 사용)
NORMALIZATION_RANGES = {
    "grip_strength": (10.0, 45.0),      # 악력 (kg)
    "sit_ups": (10, 60),                # 윗몸일으키기 (회/분)
    "standing_long_jump": (100.0, 260.0),  # 제자리멀리뛰기 (cm)
    "shuttle_run_20m": (5, 100),        # 왕복오래달리기 (회)
    "sit_and_reach": (-5.0, 30.0),      # 좌전굴 (cm)
}


# 종목별 가중치
SPORT_WEIGHTS = {
    "soccer": {
        "grip_strength": 0.1,
        "sit_ups": 0.2,
        "standing_long_jump": 0.25,
        "shuttle_run_20m": 0.3,
        "sit_and_reach": 0.15,
    },
    "basketball": {
        "grip_strength": 0.15,
        "sit_ups": 0.15,
        "standing_long_jump": 0.3,
        "shuttle_run_20m": 0.25,
        "sit_and_reach": 0.15,
    },
    "volleyball": {
        "grip_strength": 0.15,
        "sit_ups": 0.15,
        "standing_long_jump": 0.35,
        "shuttle_run_20m": 0.2,
        "sit_and_reach": 0.15,
    },
    "sprint": {
        "grip_strength": 0.1,
        "sit_ups": 0.1,
        "standing_long_jump": 0.3,
        "shuttle_run_20m": 0.4,
        "sit_and_reach": 0.1,
    },
    "judo": {
        "grip_strength": 0.35,
        "sit_ups": 0.2,
        "standing_long_jump": 0.15,
        "shuttle_run_20m": 0.15,
        "sit_and_reach": 0.15,
    },
    "swimming": {
        "grip_strength": 0.15,
        "sit_ups": 0.2,
        "standing_long_jump": 0.2,
        "shuttle_run_20m": 0.3,
        "sit_and_reach": 0.15,
    },
    "baseball": {
        "grip_strength": 0.25,
        "sit_ups": 0.15,
        "standing_long_jump": 0.25,
        "shuttle_run_20m": 0.2,
        "sit_and_reach": 0.15,
    },
    "taekwondo": {
        "grip_strength": 0.1,
        "sit_ups": 0.2,
        "standing_long_jump": 0.25,
        "shuttle_run_20m": 0.2,
        "sit_and_reach": 0.25,
    },
}

# 종목 한글명 매핑
SPORT_NAMES_KO = {
    "soccer": "축구",
    "basketball": "농구",
    "volleyball": "배구",
    "sprint": "단거리 육상",
    "judo": "유도",
    "swimming": "수영",
    "baseball": "야구",
    "taekwondo": "태권도",
    # 패럴림픽 종목
    "para_swimming": "패럴림픽 수영",
    "para_athletics": "패럴림픽 육상",
    "boccia": "보치아",
    "goalball": "골볼",
    "sitting_volleyball": "좌식배구",
    "wheelchair_basketball": "휠체어 농구",
    "wheelchair_tennis": "휠체어 테니스",
    "para_table_tennis": "패럴림픽 탁구",
}

# 장애유형별 추천 종목
# physical: 지체장애, visual: 시각장애, hearing: 청각장애, intellectual: 지적장애
DISABILITY_SPORT_WEIGHTS = {
    "physical": {
        "para_swimming": {
            "grip_strength": 0.2,
            "sit_ups": 0.25,
            "standing_long_jump": 0.15,
            "shuttle_run_20m": 0.25,
            "sit_and_reach": 0.15,
        },
        "wheelchair_basketball": {
            "grip_strength": 0.3,
            "sit_ups": 0.25,
            "standing_long_jump": 0.15,
            "shuttle_run_20m": 0.15,
            "sit_and_reach": 0.15,
        },
        "wheelchair_tennis": {
            "grip_strength": 0.3,
            "sit_ups": 0.2,
            "standing_long_jump": 0.15,
            "shuttle_run_20m": 0.2,
            "sit_and_reach": 0.15,
        },
        "boccia": {
            "grip_strength": 0.35,
            "sit_ups": 0.15,
            "standing_long_jump": 0.1,
            "shuttle_run_20m": 0.1,
            "sit_and_reach": 0.3,
        },
        "para_table_tennis": {
            "grip_strength": 0.25,
            "sit_ups": 0.2,
            "standing_long_jump": 0.15,
            "shuttle_run_20m": 0.2,
            "sit_and_reach": 0.2,
        },
    },
    "visual": {
        "goalball": {
            "grip_strength": 0.2,
            "sit_ups": 0.2,
            "standing_long_jump": 0.2,
            "shuttle_run_20m": 0.2,
            "sit_and_reach": 0.2,
        },
        "para_swimming": {
            "grip_strength": 0.15,
            "sit_ups": 0.2,
            "standing_long_jump": 0.2,
            "shuttle_run_20m": 0.3,
            "sit_and_reach": 0.15,
        },
        "para_athletics": {
            "grip_strength": 0.1,
            "sit_ups": 0.15,
            "standing_long_jump": 0.3,
            "shuttle_run_20m": 0.35,
            "sit_and_reach": 0.1,
        },
        "judo": {
            "grip_strength": 0.35,
            "sit_ups": 0.2,
            "standing_long_jump": 0.15,
            "shuttle_run_20m": 0.15,
            "sit_and_reach": 0.15,
        },
    },
    "hearing": {
        "soccer": {
            "grip_strength": 0.1,
            "sit_ups": 0.2,
            "standing_long_jump": 0.25,
            "shuttle_run_20m": 0.3,
            "sit_and_reach": 0.15,
        },
        "basketball": {
            "grip_strength": 0.15,
            "sit_ups": 0.15,
            "standing_long_jump": 0.3,
            "shuttle_run_20m": 0.25,
            "sit_and_reach": 0.15,
        },
        "volleyball": {
            "grip_strength": 0.15,
            "sit_ups": 0.15,
            "standing_long_jump": 0.35,
            "shuttle_run_20m": 0.2,
            "sit_and_reach": 0.15,
        },
        "swimming": {
            "grip_strength": 0.15,
            "sit_ups": 0.2,
            "standing_long_jump": 0.2,
            "shuttle_run_20m": 0.3,
            "sit_and_reach": 0.15,
        },
        "para_table_tennis": {
            "grip_strength": 0.25,
            "sit_ups": 0.2,
            "standing_long_jump": 0.2,
            "shuttle_run_20m": 0.2,
            "sit_and_reach": 0.15,
        },
    },
    "intellectual": {
        "para_swimming": {
            "grip_strength": 0.15,
            "sit_ups": 0.2,
            "standing_long_jump": 0.2,
            "shuttle_run_20m": 0.3,
            "sit_and_reach": 0.15,
        },
        "para_athletics": {
            "grip_strength": 0.1,
            "sit_ups": 0.15,
            "standing_long_jump": 0.3,
            "shuttle_run_20m": 0.35,
            "sit_and_reach": 0.1,
        },
        "para_table_tennis": {
            "grip_strength": 0.2,
            "sit_ups": 0.2,
            "standing_long_jump": 0.2,
            "shuttle_run_20m": 0.2,
            "sit_and_reach": 0.2,
        },
        "boccia": {
            "grip_strength": 0.3,
            "sit_ups": 0.15,
            "standing_long_jump": 0.15,
            "shuttle_run_20m": 0.1,
            "sit_and_reach": 0.3,
        },
    },
}


def normalize_score(value: Optional[float], min_val: float, max_val: float) -> float:
    """체력 항목 값을 0~100점으로 정규화"""
    if value is None:
        return 0.0
    clamped = max(min_val, min(max_val, value))
    return (clamped - min_val) / (max_val - min_val) * 100.0


def normalize_all_metrics(
    grip_strength: Optional[float] = None,
    sit_ups: Optional[int] = None,
    standing_long_jump: Optional[float] = None,
    shuttle_run_20m: Optional[int] = None,
    sit_and_reach: Optional[float] = None,
    gender: Optional[str] = None,
) -> Dict[str, float]:
    """모든 체력 항목을 정규화 (성별에 따른 기준 적용)"""
    # 성별에 따른 정규화 기준 선택
    if gender and gender in NORMALIZATION_RANGES_BY_GENDER:
        ranges = NORMALIZATION_RANGES_BY_GENDER[gender]
    else:
        ranges = NORMALIZATION_RANGES

    return {
        "grip_strength": normalize_score(
            grip_strength,
            *ranges["grip_strength"]
        ),
        "sit_ups": normalize_score(
            float(sit_ups) if sit_ups is not None else None,
            *ranges["sit_ups"]
        ),
        "standing_long_jump": normalize_score(
            standing_long_jump,
            *ranges["standing_long_jump"]
        ),
        "shuttle_run_20m": normalize_score(
            float(shuttle_run_20m) if shuttle_run_20m is not None else None,
            *ranges["shuttle_run_20m"]
        ),
        "sit_and_reach": normalize_score(
            sit_and_reach,
            *ranges["sit_and_reach"]
        ),
    }


def compute_sport_score(norm_scores: Dict[str, float], sport: str) -> float:
    """종목별 재능 점수 계산"""
    if sport not in SPORT_WEIGHTS:
        return 0.0

    weights = SPORT_WEIGHTS[sport]
    total = 0.0
    for metric, weight in weights.items():
        total += norm_scores.get(metric, 0.0) * weight
    return round(total, 2)


def estimate_percentile_and_grade(score: float) -> Tuple[float, str]:
    """점수를 기반으로 백분위와 등급 추정 (5단계)"""
    if score >= 85:
        return (95.0, "excellent")  # 최우수 - 상위 5%
    elif score >= 70:
        return (85.0, "high")  # 우수 - 상위 15%
    elif score >= 55:
        return (65.0, "above_average")  # 평균 이상 - 상위 35%
    elif score >= 40:
        return (45.0, "average")  # 평균 - 상위 55%
    else:
        return (25.0, "below_average")  # 평균 이하 - 하위


def compute_sport_score_with_weights(norm_scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """가중치를 사용하여 종목 점수 계산"""
    total = 0.0
    for metric, weight in weights.items():
        total += norm_scores.get(metric, 0.0) * weight
    return round(total, 2)


def calculate_all_sport_scores(
    grip_strength: Optional[float] = None,
    sit_ups: Optional[int] = None,
    standing_long_jump: Optional[float] = None,
    shuttle_run_20m: Optional[int] = None,
    sit_and_reach: Optional[float] = None,
    disability_type: Optional[str] = None,
    gender: Optional[str] = None,
) -> list:
    """모든 종목에 대한 재능 점수 계산 (장애 유형 및 성별 지원)"""
    # 체력 항목 정규화 (성별에 따른 기준 적용)
    norm_scores = normalize_all_metrics(
        grip_strength=grip_strength,
        sit_ups=sit_ups,
        standing_long_jump=standing_long_jump,
        shuttle_run_20m=shuttle_run_20m,
        sit_and_reach=sit_and_reach,
        gender=gender,
    )

    results = []

    # 장애 유형이 있으면 패럴림픽 종목 사용
    if disability_type and disability_type in DISABILITY_SPORT_WEIGHTS:
        sport_weights = DISABILITY_SPORT_WEIGHTS[disability_type]
        for sport, weights in sport_weights.items():
            score = compute_sport_score_with_weights(norm_scores, weights)
            percentile, grade_level = estimate_percentile_and_grade(score)
            results.append({
                "sport": sport,
                "sport_name_ko": SPORT_NAMES_KO.get(sport, sport),
                "score": score,
                "percentile": percentile,
                "grade_level": grade_level,
            })
    else:
        # 일반 종목
        for sport in SPORT_WEIGHTS.keys():
            score = compute_sport_score(norm_scores, sport)
            percentile, grade_level = estimate_percentile_and_grade(score)
            results.append({
                "sport": sport,
                "sport_name_ko": SPORT_NAMES_KO.get(sport, sport),
                "score": score,
                "percentile": percentile,
                "grade_level": grade_level,
            })

    # 점수 높은 순으로 정렬
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
