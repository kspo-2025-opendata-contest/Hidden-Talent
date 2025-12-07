"""
지역별 스포츠강좌이용권 활용정보 적재 스크립트

데이터 파일: data/지역별스포츠강좌이용권활용정보(202507).csv
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from app.database import SessionLocal
from app.models.support import SupportStats


# 컬럼 매핑
COLUMN_MAP = {
    "BASE_YEAR": "base_year",
    "CTPRVN_CD": "region_sido_code",
    "CTPRVN_NM": "region_sido",
    "SIGNGU_CD": "region_sigungu_code",
    "SIGNGU_NM": "region_sigungu",
    "SIGNGU_ACCTO_POPLTN_CO": "population",
    "SIGNGU_ACCTO_FCLTY_CO": "facility_count",
    "RECIPT_FLAG_CD": "recipient_type_code",
    "RECIPT_FLAG_NM": "recipient_type_name",
    "CRRSPND_FLAG_TRGET_NMPR_CO": "target_count",
    "CRRSPND_FLAG_RECIPT_NMPR_CO": "recipient_count",
}


def load_support_stats():
    """스포츠강좌이용권 통계 데이터 적재"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    data_path = os.path.join(
        project_root,
        "data",
        "지역별스포츠강좌이용권활용정보(202507).csv"
    )

    print(f"Loading data from: {data_path}")

    # CSV 읽기
    df = pd.read_csv(data_path, encoding="utf-8-sig")
    print(f"Loaded {len(df)} rows")

    # DB 세션
    db = SessionLocal()

    try:
        # 기존 데이터 삭제
        deleted = db.query(SupportStats).delete()
        db.commit()
        print(f"Deleted {deleted} existing records")

        # 배치 삽입
        records = []

        for _, row in df.iterrows():
            record = SupportStats(
                base_year=int(row["BASE_YEAR"]) if pd.notna(row.get("BASE_YEAR")) else 2025,
                region_sido_code=str(row["CTPRVN_CD"])[:20] if pd.notna(row.get("CTPRVN_CD")) else None,
                region_sido=str(row["CTPRVN_NM"])[:50] if pd.notna(row.get("CTPRVN_NM")) else None,
                region_sigungu_code=str(row["SIGNGU_CD"])[:20] if pd.notna(row.get("SIGNGU_CD")) else None,
                region_sigungu=str(row["SIGNGU_NM"])[:50] if pd.notna(row.get("SIGNGU_NM")) else None,
                population=int(row["SIGNGU_ACCTO_POPLTN_CO"]) if pd.notna(row.get("SIGNGU_ACCTO_POPLTN_CO")) else None,
                facility_count=int(row["SIGNGU_ACCTO_FCLTY_CO"]) if pd.notna(row.get("SIGNGU_ACCTO_FCLTY_CO")) else None,
                recipient_type_code=str(row["RECIPT_FLAG_CD"])[:10] if pd.notna(row.get("RECIPT_FLAG_CD")) else None,
                recipient_type_name=str(row["RECIPT_FLAG_NM"])[:100] if pd.notna(row.get("RECIPT_FLAG_NM")) else None,
                target_count=int(row["CRRSPND_FLAG_TRGET_NMPR_CO"]) if pd.notna(row.get("CRRSPND_FLAG_TRGET_NMPR_CO")) else None,
                recipient_count=int(row["CRRSPND_FLAG_RECIPT_NMPR_CO"]) if pd.notna(row.get("CRRSPND_FLAG_RECIPT_NMPR_CO")) else None,
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
    load_support_stats()
