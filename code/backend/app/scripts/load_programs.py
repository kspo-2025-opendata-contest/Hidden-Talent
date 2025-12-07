"""
청소년 유아동 이용가능 체육시설 프로그램 정보 적재 스크립트

데이터 파일: data/청소년_프로그램_part*.csv (분할된 파일들)
"""

import sys
import os
import glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from datetime import datetime
from app.database import SessionLocal
from app.models.program import Program


# 컬럼 매핑
COLUMN_MAP = {
    "FCLTY_NM": "facility_name",
    "FCLTY_SDIV_CD": "facility_type_code",
    "FCLTY_FLAG_NM": "facility_type_name",
    "INDUTY_CD": "industry_code",
    "INDUTY_NM": "industry_name",
    "CTPRVN_CD": "region_sido_code",
    "CTPRVN_NM": "region_sido",
    "SIGNGU_CD": "region_sigungu_code",
    "SIGNGU_NM": "region_sigungu",
    "EMD_NM": "emd_name",
    "FCLTY_ADDR": "address",
    "FCLTY_LA": "latitude",
    "FCLTY_LO": "longitude",
    "PROGRM_TY_NM": "program_type",
    "PROGRM_NM": "program_name",
    "PROGRM_TRGET_NM": "target_group",
    "PROGRM_BEGIN_DE": "start_date",
    "PROGRM_END_DE": "end_date",
    "PROGRM_ESTBL_WKDAY_NM": "schedule_weekdays",
    "PROGRM_ESTBL_TIZN_VALUE": "schedule_time",
    "PROGRM_RCRIT_NMPR_CO": "capacity",
    "PROGRM_PRC": "price",
    "PROGRM_PRC_TY_NM": "price_type",
    "HMPG_URL": "homepage_url",
}


def parse_date(date_str):
    """날짜 문자열 파싱"""
    if pd.isna(date_str) or not date_str:
        return None
    try:
        return datetime.strptime(str(date_str)[:8], "%Y%m%d").date()
    except Exception:
        return None


def load_programs(limit=None):
    """프로그램 데이터 적재"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    data_dir = os.path.join(project_root, "data")

    # 분할된 파일들 찾기
    data_files = sorted(glob.glob(os.path.join(data_dir, "청소년_프로그램_part*.csv")))

    if not data_files:
        print("No data files found!")
        return

    print(f"Found {len(data_files)} data files")

    # CSV 읽기 (대용량이므로 청크로 처리)
    chunk_size = 10000
    total_inserted = 0

    db = SessionLocal()

    try:
        # 기존 데이터 삭제
        deleted = db.query(Program).delete()
        db.commit()
        print(f"Deleted {deleted} existing records")

        # 각 분할 파일 처리
        for data_path in data_files:
            print(f"Loading data from: {data_path}")

            if limit and total_inserted >= limit:
                break

            # 청크 단위로 읽기
            for chunk_df in pd.read_csv(data_path, encoding="utf-8-sig", chunksize=chunk_size):
                if limit and total_inserted >= limit:
                    break

                records = []
                for _, row in chunk_df.iterrows():
                    if limit and total_inserted + len(records) >= limit:
                        break

                    record = Program(
                        facility_name=str(row["FCLTY_NM"])[:200] if pd.notna(row.get("FCLTY_NM")) else None,
                        facility_type_code=str(row["FCLTY_SDIV_CD"])[:20] if pd.notna(row.get("FCLTY_SDIV_CD")) else None,
                        facility_type_name=str(row["FCLTY_FLAG_NM"])[:100] if pd.notna(row.get("FCLTY_FLAG_NM")) else None,
                        industry_code=str(row["INDUTY_CD"])[:20] if pd.notna(row.get("INDUTY_CD")) else None,
                        industry_name=str(row["INDUTY_NM"])[:100] if pd.notna(row.get("INDUTY_NM")) else None,
                        region_sido_code=str(row["CTPRVN_CD"])[:20] if pd.notna(row.get("CTPRVN_CD")) else None,
                        region_sido=str(row["CTPRVN_NM"])[:50] if pd.notna(row.get("CTPRVN_NM")) else None,
                        region_sigungu_code=str(row["SIGNGU_CD"])[:20] if pd.notna(row.get("SIGNGU_CD")) else None,
                        region_sigungu=str(row["SIGNGU_NM"])[:50] if pd.notna(row.get("SIGNGU_NM")) else None,
                        emd_name=str(row["EMD_NM"])[:50] if pd.notna(row.get("EMD_NM")) else None,
                        address=str(row["FCLTY_ADDR"])[:500] if pd.notna(row.get("FCLTY_ADDR")) else None,
                        latitude=float(row["FCLTY_LA"]) if pd.notna(row.get("FCLTY_LA")) else None,
                        longitude=float(row["FCLTY_LO"]) if pd.notna(row.get("FCLTY_LO")) else None,
                        program_type=str(row["PROGRM_TY_NM"])[:100] if pd.notna(row.get("PROGRM_TY_NM")) else None,
                        program_name=str(row["PROGRM_NM"])[:200] if pd.notna(row.get("PROGRM_NM")) else None,
                        target_group=str(row["PROGRM_TRGET_NM"])[:100] if pd.notna(row.get("PROGRM_TRGET_NM")) else None,
                        start_date=parse_date(row.get("PROGRM_BEGIN_DE")),
                        end_date=parse_date(row.get("PROGRM_END_DE")),
                        schedule_weekdays=str(row["PROGRM_ESTBL_WKDAY_NM"])[:50] if pd.notna(row.get("PROGRM_ESTBL_WKDAY_NM")) else None,
                        schedule_time=str(row["PROGRM_ESTBL_TIZN_VALUE"])[:50] if pd.notna(row.get("PROGRM_ESTBL_TIZN_VALUE")) else None,
                        capacity=int(float(row["PROGRM_RCRIT_NMPR_CO"])) if pd.notna(row.get("PROGRM_RCRIT_NMPR_CO")) else None,
                        price=float(row["PROGRM_PRC"]) if pd.notna(row.get("PROGRM_PRC")) else None,
                        price_type=str(row["PROGRM_PRC_TY_NM"])[:50] if pd.notna(row.get("PROGRM_PRC_TY_NM")) else None,
                        homepage_url=str(row["HMPG_URL"])[:500] if pd.notna(row.get("HMPG_URL")) else None,
                    )
                    records.append(record)

                if records:
                    db.bulk_save_objects(records)
                    db.commit()
                    total_inserted += len(records)
                    print(f"Inserted {total_inserted} records...")

        print(f"Done! Total inserted: {total_inserted}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records to insert")
    args = parser.parse_args()
    load_programs(limit=args.limit)
