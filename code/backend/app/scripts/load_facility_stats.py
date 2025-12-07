"""
지역별공공체육시설보급현황정보 데이터 적재 스크립트

데이터 파일: data/지역별공공체육시설보급현황정보(202507).csv
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from app.database import SessionLocal
from app.models.facility import FacilityStats


# 컬럼 매핑
COLUMN_MAP = {
    "BASE_YM": "base_ym",
    "CTPRVN_CD": "region_sido_code",
    "CTPRVN_NM": "region_sido",
    "SIGNGU_CD": "region_sigungu_code",
    "SIGNGU_NM": "region_sigungu",
    "SIGNGU_ACCTO_FCLTY_CO": "facility_count",
    "SIGNGU_ACCTO_POPLTN_CO": "population",
    "PSNBY_FCLTY_CO": "facility_per_person",
    "PSNBY_FCL_CO_RANK_CO": "rank",
}


def load_facility_stats():
    """시설 통계 데이터 적재"""
    # backend 폴더 기준 (Docker에서는 /app)
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(
        backend_root,
        "data",
        "지역별공공체육시설보급현황정보(202507).csv"
    )

    print(f"Loading data from: {data_path}")

    # CSV 읽기
    df = pd.read_csv(data_path, encoding="utf-8-sig")
    print(f"Loaded {len(df)} rows")

    # 컬럼 이름 변경
    df = df.rename(columns=COLUMN_MAP)

    # NaN 처리
    df = df.fillna({
        "facility_count": 0,
        "population": 0,
        "facility_per_person": 0.0,
        "rank": 0,
    })

    # DB 세션
    db = SessionLocal()

    try:
        # 기존 데이터 삭제 (선택적)
        deleted = db.query(FacilityStats).delete()
        print(f"Deleted {deleted} existing records")

        # 배치 삽입
        batch_size = 1000
        records = []

        for _, row in df.iterrows():
            record = FacilityStats(
                base_ym=str(row["base_ym"]),
                region_sido_code=str(row["region_sido_code"]) if pd.notna(row.get("region_sido_code")) else None,
                region_sido=str(row["region_sido"]) if pd.notna(row.get("region_sido")) else None,
                region_sigungu_code=str(row["region_sigungu_code"]) if pd.notna(row.get("region_sigungu_code")) else None,
                region_sigungu=str(row["region_sigungu"]) if pd.notna(row.get("region_sigungu")) else None,
                facility_count=int(row["facility_count"]) if pd.notna(row.get("facility_count")) else 0,
                population=int(row["population"]) if pd.notna(row.get("population")) else 0,
                facility_per_person=float(row["facility_per_person"]) if pd.notna(row.get("facility_per_person")) else 0.0,
                rank=int(row["rank"]) if pd.notna(row.get("rank")) else 0,
            )
            records.append(record)

            if len(records) >= batch_size:
                db.bulk_save_objects(records)
                db.commit()
                print(f"Inserted {len(records)} records...")
                records = []

        # 남은 레코드 삽입
        if records:
            db.bulk_save_objects(records)
            db.commit()
            print(f"Inserted {len(records)} remaining records")

        print("Done!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_facility_stats()
