"""
모든 데이터 적재 스크립트 실행

usage: python -m app.scripts.load_all [--programs-limit N]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import argparse


def main():
    parser = argparse.ArgumentParser(description="Load all data into database")
    parser.add_argument("--programs-limit", type=int, default=10000,
                        help="Limit number of program records (default: 10000, full data is ~1.5M)")
    args = parser.parse_args()

    print("=" * 60)
    print("Starting data load...")
    print("=" * 60)

    # 1. 시설 통계
    print("\n[1/4] Loading Facility Stats...")
    from app.scripts.load_facility_stats import load_facility_stats
    load_facility_stats()

    # 2. 스포츠강좌이용권 통계
    print("\n[2/4] Loading Support Stats...")
    from app.scripts.load_support_stats import load_support_stats
    load_support_stats()

    # 3. 체육지도자 통계
    print("\n[3/4] Loading Coach Stats...")
    from app.scripts.load_coach_stats import load_coach_stats
    load_coach_stats()

    # 4. 프로그램 (대용량)
    print(f"\n[4/4] Loading Programs (limit: {args.programs_limit})...")
    from app.scripts.load_programs import load_programs
    load_programs(limit=args.programs_limit)

    print("\n" + "=" * 60)
    print("All data loaded successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
