#!/usr/bin/env python3
"""
재능진단 정규화 기준값(NORMALIZATION_RANGES) 재산출 스크립트

출처: 국민체력100 「체력측정 및 운동처방 종합 데이터」 (문화빅데이터플랫폼)
      월별 원본 CSV: data/국민체력100_202506-202603/KS_NFA_FTNESS_..._YYYYMM.csv
      공식 컬럼정의서: 같은 폴더의 _컬럼정의서.xls

방법:
  1. 청소년(AGRDE_FLAG_NM='청소년') 표본만 필터
  2. 공식 컬럼정의서 기준 5개 체력항목 추출
       - 악력            = max(IEM_007 악력_좌, IEM_008 악력_우)
       - 윗몸일으키기    = IEM_009 (윗몸말아올리기)
       - 제자리멀리뛰기  = IEM_022
       - 20m왕복오래달리기 = IEM_020 (왕복오래달리기)
       - 좌전굴          = IEM_012 (앉아윗몸앞으로굽히기)
  3. 성별 x 항목 p5~p95를 정규화 min/max로 사용
  4. 실제 점수 분포로 등급 임계값 검증

사용법:  python -m app.scripts.recompute_norms
결과는 app/services/scoring_service.py의 값과 일치해야 함(재현성 검증).
"""
import os
import glob
import warnings
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "data", "국민체력100_202506-202603")

ITEM = {  # 재능진단 입력 → 공식 IEM 컬럼
    "grip_strength": ("MESURE_IEM_007_VALUE", "MESURE_IEM_008_VALUE"),  # 악력 좌/우 최대
    "sit_ups": ("MESURE_IEM_009_VALUE",),          # 윗몸말아올리기
    "standing_long_jump": ("MESURE_IEM_022_VALUE",),  # 제자리멀리뛰기
    "shuttle_run_20m": ("MESURE_IEM_020_VALUE",),  # 왕복오래달리기
    "sit_and_reach": ("MESURE_IEM_012_VALUE",),    # 앉아윗몸앞으로굽히기(좌전굴)
}


def load_youth() -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(DATA_DIR, "KS_NFA_FTNESS_*.csv")))
    if not files:
        raise SystemExit(f"원본 CSV 없음: {DATA_DIR} (문화빅데이터플랫폼에서 다운로드 필요)")
    df = pd.concat([pd.read_csv(f, encoding="utf-8-sig", low_memory=False) for f in files],
                   ignore_index=True)
    you = df[df["AGRDE_FLAG_NM"] == "청소년"].copy()
    for name, cols in ITEM.items():
        arr = np.vstack([pd.to_numeric(you[c], errors="coerce") for c in cols])
        with np.errstate(all="ignore"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                you[name] = np.nanmax(arr, axis=0)
    print(f"원본 {len(df):,}건 → 청소년 {len(you):,}건 "
          f"(남 {(you['SEXDSTN_FLAG_CD']=='M').sum():,} / 여 {(you['SEXDSTN_FLAG_CD']=='F').sum():,})")
    return you


def compute_ranges(you: pd.DataFrame):
    print("\n=== 성별 정규화 기준 (p5~p95) ===")
    for sex in ["M", "F"]:
        sub = you[you["SEXDSTN_FLAG_CD"] == sex]
        print(f'    "{sex}": {{')
        for name in ITEM:
            s = sub[name].dropna()
            print(f'        "{name}": ({round(s.quantile(.05))}, {round(s.quantile(.95))}),'
                  f'  # n={len(s):,}')
        print("    },")
    print("\n=== 기본(성별통합) ===")
    for name in ITEM:
        s = you[name].dropna()
        print(f'    "{name}": ({round(s.quantile(.05))}, {round(s.quantile(.95))}),')


if __name__ == "__main__":
    compute_ranges(load_youth())
