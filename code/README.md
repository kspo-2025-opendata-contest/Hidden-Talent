# 숨인재 (공공데이터 기반 청소년 스포츠 재능 발굴 플랫폼)

팀 이름: **숨어있는 재능을 찾아서**

2025년 국민체육진흥공단 공공데이터 활용 경진대회를 위해 제작된 프로젝트입니다.
국민체력·체력측정 데이터와 지역 체육 인프라·체육복지 데이터를 활용하여, 청소년 개개인의 종목별 잠재 재능을 계량화하고 실제 육성 경로까지 연결하는 웹 서비스입니다.

---

## 1. 프로젝트 개요

### 서비스 한 줄 정의

> 숨인재는 청소년의 체력측정 데이터를 기반으로
> "어떤 종목에 재능이 있을 가능성이 높은가?"를 점수화하고,
> 해당 재능을 키워줄 지도자·시설·프로그램·지원사업까지 한 번에 매칭해 주는 플랫폼입니다.

### 해결하고자 하는 문제

1. **재능 발굴의 편중**
   - 수도권, 체육 명문학교, 유명 클럽 중심으로 유망주 발굴이 이뤄지는 구조
   - 지방, 저소득층, 체육 비비중 학교 학생들은 운동을 잘해도 발굴되지 못하는 문제

2. **데이터 미활용**
   - 학교·체력인증센터 등에서 체력측정은 꾸준히 이루어지고 있으나
   - 이 데이터를 진로·재능 탐색, 종목 추천, 지원 연계에 활용하는 체계가 부재

3. **재능 → 육성으로 이어지는 파이프라인 부재**
   - "운동 잘하는 아이"를 알게 되어도
   - 어느 종목으로, 어떤 지도자에게, 어떤 시설과 지원사업으로 연결해야 할지 안내하는 시스템이 없음

---

## 2. 핵심 기능

### 2.1 종목별 재능 진단
- 학생의 체력측정 값(악력, 윗몸일으키기, 제자리멀리뛰기, 왕복달리기, 좌전굴 등)을 입력
- 연령·성별 기준으로 0~100점 정규화
- 축구, 농구, 배구, 단거리 육상, 수영, 테니스, 태권도, 유도 등 8개 종목별 재능 점수와 등급 산출
- Gemini API를 활용한 AI 기반 맞춤형 코멘트 생성

### 2.2 지도자·시설·프로그램 매칭
- 재능 상위 종목에 대해 지역 내 청소년 대상 체육 프로그램 추천
- 공공체육시설 위치 및 현황 정보 제공
- 지역별 체육지도자 자격 현황 조회

### 2.3 재능–지원 격차 분석 대시보드 (기관/정책용)
- 지역·계층별 재능 분포와 스포츠강좌이용권 수혜 현황 비교
- 재능은 많지만 지원이 부족한 지역·집단을 시각화
- 지자체·공단의 예산·프로그램 우선 배분 대상 도출

### 2.4 회원가입 및 마이페이지
- 사용자 유형: 학생, 학부모, 지도자, 지자체/기관 담당자
- 마이페이지에서 재능 진단 이력, 추천 프로그램, 북마크, 알림 등 관리

---

## 3. 사용 데이터셋

해커톤에서 제공된 약 140개 체육·스포츠 관련 공공데이터 중, 숨인재는 다음 핵심 그룹을 활용합니다.

| 데이터명 | 파일명 | 활용 목적 |
|---------|--------|----------|
| 체력측정 및 운동처방 종합 데이터 | `체력측정 및 운동처방 종합 데이터(202505).csv` | 연령별 체력 백분위 산출, 재능 스코어링 기초 지표 |
| 체육지도자 자격취득현황 | `체육지도자 연도별 자격취득현황 데이터(202508).csv` | 지역·종목별 지도자 풀 규모 파악 |
| 공공체육시설 보급현황 | `지역별공공체육시설보급현황정보(202507).csv` | 시·군·구별 시설 분포, 인프라 취약 지역 탐색 |
| 청소년·유아동 체육 프로그램 | `청소년 유아동 이용가능 체육시설 프로그램 정보(202510).csv` | 종목별, 지역별 훈련/클럽/교실 추천 |
| 스포츠강좌이용권 현황 | `지역별 스포츠강좌이용권 활용 정보(202505).csv` | 재능–지원 격차 분석 |

데이터 파일은 레포지토리의 `data/` 디렉터리에 저장하며, ETL 스크립트로 PostgreSQL DB에 적재합니다.

---

## 4. 시스템 아키텍처

### 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | Vite + HTML/CSS/JS + Tailwind CSS |
| 백엔드 | FastAPI (Python 3.11) |
| 데이터베이스 | PostgreSQL |
| ORM | SQLAlchemy 2.x |
| 마이그레이션 | Alembic |
| 인증 | JWT (python-jose + bcrypt) |
| AI 코멘트 | Google Gemini API |

### 주요 흐름

```
1. 사용자 → 회원가입/로그인
2. 체력측정 값 입력 → 재능 진단 요청
3. 백엔드 → 종목별 가중치 적용 스코어링 계산
4. Gemini API → AI 기반 맞춤 코멘트 생성
5. 같은 지역의 프로그램·시설 매칭 추천
6. 마이페이지에서 진단 이력 및 북마크 관리
7. 기관 담당자 → 대시보드에서 재능-지원 격차 분석
```

---

## 5. 재능 스코어링 알고리즘

### 5.1 체력 항목 점수화
- 악력, 윗몸일으키기, 제자리멀리뛰기, 20m 왕복달리기, 좌전굴 등을 0~100점으로 정규화
- 항목별 최소/최대값은 연령·성별 평균을 참고하여 설정

### 5.2 종목별 가중치 적용

```python
SPORT_WEIGHTS = {
    "soccer": {"grip_strength": 0.1, "sit_ups": 0.2, "standing_long_jump": 0.25, "shuttle_run_20m": 0.3, "sit_and_reach": 0.15},
    "basketball": {"grip_strength": 0.15, "sit_ups": 0.15, "standing_long_jump": 0.3, "shuttle_run_20m": 0.25, "sit_and_reach": 0.15},
    "volleyball": {"grip_strength": 0.15, "sit_ups": 0.15, "standing_long_jump": 0.35, "shuttle_run_20m": 0.2, "sit_and_reach": 0.15},
    "track_sprint": {"grip_strength": 0.05, "sit_ups": 0.15, "standing_long_jump": 0.35, "shuttle_run_20m": 0.35, "sit_and_reach": 0.1},
    # ... 8개 종목
}
```

### 5.3 점수 → 등급/백분위 변환
- 85점 이상: A등급 (상위 10%)
- 70점 이상: B등급 (상위 30%)
- 50점 이상: C등급 (상위 60%)
- 50점 미만: D등급

### 5.4 AI 코멘트 생성
- Gemini API를 통해 재능 결과에 대한 자연어 설명과 훈련 방향 코멘트 자동 생성

---

## 6. 디렉터리 구조

```bash
.
├── README.md
├── data/                              # 공공데이터 원본 파일(CSV)
│   ├── 체력측정 및 운동처방 종합 데이터(202505).csv
│   ├── 체육지도자 연도별 자격취득현황 데이터(202508).csv
│   ├── 지역별공공체육시설보급현황정보(202507).csv
│   ├── 청소년 유아동 이용가능 체육시설 프로그램 정보(202510).csv
│   └── 지역별 스포츠강좌이용권 활용 정보(202505).csv
│
└── code/
    ├── frontend/                      # 프론트엔드 (Vite)
    │   ├── index.html
    │   ├── index.css
    │   ├── logo.jpeg
    │   ├── package.json
    │   └── vite.config.ts
    │
    └── backend/                       # 백엔드 (FastAPI)
        ├── app/
        │   ├── main.py               # FastAPI 엔트리포인트
        │   ├── config.py             # 환경변수 설정
        │   ├── database.py           # SQLAlchemy 엔진/세션
        │   ├── dependencies.py       # JWT 인증 의존성
        │   ├── models/               # SQLAlchemy 모델
        │   │   ├── user.py
        │   │   ├── talent.py
        │   │   ├── program.py
        │   │   ├── facility.py
        │   │   ├── coach.py
        │   │   ├── support.py
        │   │   └── bookmark.py
        │   ├── schemas/              # Pydantic 스키마
        │   │   ├── auth.py
        │   │   ├── talent.py
        │   │   ├── program.py
        │   │   └── bookmark.py
        │   ├── routers/              # API 라우터
        │   │   ├── auth.py           # 회원가입/로그인
        │   │   ├── talent.py         # 재능 진단
        │   │   ├── programs.py       # 프로그램 검색
        │   │   ├── facilities.py     # 시설 현황
        │   │   ├── dashboard.py      # 대시보드 통계
        │   │   └── me.py             # 마이페이지
        │   ├── services/             # 비즈니스 로직
        │   │   ├── auth_service.py   # 인증 서비스
        │   │   ├── scoring_service.py # 재능 스코어링
        │   │   └── gemini_client.py  # Gemini API 연동
        │   └── scripts/              # ETL 스크립트
        │       ├── load_facility_stats.py
        │       ├── load_programs.py
        │       ├── load_coach_stats.py
        │       ├── load_support_stats.py
        │       └── load_all.py
        ├── alembic/                  # DB 마이그레이션
        ├── requirements.txt
        └── .env
```

---

## 7. 로컬 개발 환경 구성

### 7.1 사전 요구사항
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 7.2 데이터베이스 생성

```bash
createdb suminjae
```

### 7.3 백엔드 설정

```bash
cd code/backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정 (.env 파일 생성)
cat > .env << EOF
DATABASE_URL=postgresql+psycopg://사용자명@localhost:5432/suminjae
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your-gemini-api-key
DEBUG=true
EOF

# DB 마이그레이션
alembic upgrade head

# 데이터 적재 (ETL)
python -m app.scripts.load_all --programs-limit 5000

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

### 7.4 프론트엔드 설정

```bash
cd code/frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```

- 개발 서버: http://localhost:3000

---

## 8. API 엔드포인트

### 인증 API (`/api/auth`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/signup` | 회원가입 |
| POST | `/login` | 로그인 |
| GET | `/me` | 현재 사용자 정보 |

### 재능 진단 API (`/api/talent`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/score` | 체력 데이터 기반 재능 진단 |
| GET | `/tests` | 내 진단 이력 조회 |
| GET | `/tests/{id}` | 진단 결과 상세 조회 |

### 프로그램 API (`/api/programs`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 프로그램 목록 (필터/검색/페이지네이션) |
| GET | `/{id}` | 프로그램 상세 |
| GET | `/regions/list` | 지역 목록 |
| GET | `/types/list` | 프로그램 유형 목록 |

### 시설 API (`/api/facilities`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 시설 통계 목록 |
| GET | `/regions` | 지역 목록 |
| GET | `/summary` | 전국 요약 통계 |

### 대시보드 API (`/api/dashboard`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/summary` | 전체 현황 요약 |
| GET | `/regions` | 지역별 통계 |
| GET | `/coaches` | 체육지도자 통계 |

### 마이페이지 API (`/api/me`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/overview` | 마이페이지 개요 |
| GET | `/bookmarks` | 북마크 목록 |
| POST | `/bookmarks` | 북마크 추가 |
| DELETE | `/bookmarks/{id}` | 북마크 삭제 |
| GET | `/notifications` | 알림 목록 |
| POST | `/notifications/{id}/read` | 알림 읽음 처리 |

---

## 9. 향후 고도화 계획

1. **통계 기반 재능 스코어링 고도화**
   - 체력측정 종합 데이터를 활용하여 연령·성별별 실제 분포 계산
   - 표준점수, 백분위 기반 등급화 로직으로 교체

2. **종목 확장 및 세분화**
   - 수영, 양궁, 골프 등 점진적 확장
   - 종목별 요구 체력 모델을 전문가 의견 반영하여 보정

3. **지도자·프로그램 데이터 품질 개선**
   - 좌표 및 시·군·구 정규화
   - 프로그램 대상 연령, 난이도, 비용 등 파싱·정제 고도화

4. **권한 및 역할 기반 화면 분리**
   - 학생/학부모, 지도자, 기관 담당자별 접근 가능한 메뉴와 데이터 범위 세분화

5. **실서비스 전환**
   - 이메일 인증, 비밀번호 재설정
   - 로그·모니터링 추가
   - Render/Vercel 등 클라우드 배포

---

## 10. 팀 소개

- **팀 이름**: 숨어있는 재능을 찾아서
- **목표**:
  - 공공데이터를 활용해 지역·계층에 관계없이 숨은 스포츠 인재를 공정하게 발굴
  - 재능 발굴에서 끝나지 않고 실제 육성 경로까지 잇는 레퍼런스 모델 구축

---

## 라이선스

이 프로젝트는 2025년 국민체육진흥공단 공공데이터 활용 경진대회 출품작입니다.

제안, 이슈, 개선 아이디어는 언제든지 GitHub Issues로 남겨 주세요.
