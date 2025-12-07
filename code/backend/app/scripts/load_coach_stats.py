"""
체육지도자 연도별 자격취득현황 데이터 적재 스크립트

데이터 파일: data/체육지도자 연도별 자격취득현황 데이터(202508).csv
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from app.database import SessionLocal
from app.models.coach import CoachStats


# 컬럼 매핑
COLUMN_MAP = {
    "QUALF_YEAR": "qualification_year",
    "HEALTH_MVM_MNGER_CO": "health_exercise_manager",
    "SCLS1_SPCLTY_SPORTS_INSTOR_CO": "professional_sports_1",
    "SCLS2_SPCLTY_SPORTS_INSTOR_CO": "professional_sports_2",
    "SCLS1_LVLH_SPORTS_INSTOR_CO": "living_sports_1",
    "SCLS2_LVLH_SPORTS_INSTOR_CO": "living_sports_2",
    "YUTH_SPORTS_INSTOR_CO": "youth_sports",
    "SNCTZ_SPORTS_INSTOR_CO": "senior_sports",
    "SCLS1_DSPSN_SPORTS_INSTOR_CO": "disabled_sports_1",
    "SCLS2_DSPSN_SPORTS_INSTOR_CO": "disabled_sports_2",
}


def load_coach_stats():
    """체육지도자 통계 데이터 적재"""
    # backend 폴더 기준 (Docker에서는 /app)
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(
        backend_root,
        "data",
        "체육지도자 연도별 자격취득현황 데이터(202508).csv"
    )

    print(f"Loading data from: {data_path}")

    # CSV 읽기
    df = pd.read_csv(data_path, encoding="utf-8-sig")
    print(f"Loaded {len(df)} rows")

    # DB 세션
    db = SessionLocal()

    try:
        # 기존 데이터 삭제
        deleted = db.query(CoachStats).delete()
        db.commit()
        print(f"Deleted {deleted} existing records")

        # 배치 삽입
        records = []

        for _, row in df.iterrows():
            record = CoachStats(
                qualification_year=int(row["QUALF_YEAR"]) if pd.notna(row.get("QUALF_YEAR")) else 0,
                health_exercise_manager=int(row["HEALTH_MVM_MNGER_CO"]) if pd.notna(row.get("HEALTH_MVM_MNGER_CO")) else 0,
                professional_sports_1=int(row["SCLS1_SPCLTY_SPORTS_INSTOR_CO"]) if pd.notna(row.get("SCLS1_SPCLTY_SPORTS_INSTOR_CO")) else 0,
                professional_sports_2=int(row["SCLS2_SPCLTY_SPORTS_INSTOR_CO"]) if pd.notna(row.get("SCLS2_SPCLTY_SPORTS_INSTOR_CO")) else 0,
                living_sports_1=int(row["SCLS1_LVLH_SPORTS_INSTOR_CO"]) if pd.notna(row.get("SCLS1_LVLH_SPORTS_INSTOR_CO")) else 0,
                living_sports_2=int(row["SCLS2_LVLH_SPORTS_INSTOR_CO"]) if pd.notna(row.get("SCLS2_LVLH_SPORTS_INSTOR_CO")) else 0,
                youth_sports=int(row["YUTH_SPORTS_INSTOR_CO"]) if pd.notna(row.get("YUTH_SPORTS_INSTOR_CO")) else 0,
                senior_sports=int(row["SNCTZ_SPORTS_INSTOR_CO"]) if pd.notna(row.get("SNCTZ_SPORTS_INSTOR_CO")) else 0,
                disabled_sports_1=int(row["SCLS1_DSPSN_SPORTS_INSTOR_CO"]) if pd.notna(row.get("SCLS1_DSPSN_SPORTS_INSTOR_CO")) else 0,
                disabled_sports_2=int(row["SCLS2_DSPSN_SPORTS_INSTOR_CO"]) if pd.notna(row.get("SCLS2_DSPSN_SPORTS_INSTOR_CO")) else 0,
            )
            records.append(record)

        db.bulk_save_objects(records)
        db.commit()
        print(f"Inserted {len(records)} records")
        print("Done!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_coach_stats()
