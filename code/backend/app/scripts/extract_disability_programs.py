#!/usr/bin/env python3
"""
장애인 체육 프로그램 정제 추출 스크립트

배경:
  원본 프로그램 분할 CSV(data/청소년_프로그램_aa~ad.csv)는 일부 파일에 따옴표가
  닫히지 않은 손상 행이 있어 pandas 전체 파싱이 실패한다(기존 로더는 aa 앞부분
  5,000행만 읽어 문제를 우회했음). 이 때문에 뒤쪽 파일에 있는 장애인 체육 프로그램이
  DB에 적재되지 못해, 장애 학생에게 맞춤 추천이 불가능했다.

방법:
  각 물리적 라인을 독립적으로 csv 파싱하여(손상 따옴표가 해당 라인에만 영향)
  프로그램명/시설명/대상에 장애 관련 키워드가 있는 행만 안전하게 추출,
  중복 제거 후 표준 CSV로 저장한다.

사용:  python -m app.scripts.extract_disability_programs
출력:  data/장애인_체육_프로그램.csv  (load_programs.py 1패스에서 우선 적재)
"""
import csv
import glob
import os

import pandas as pd

DIS_KEYWORDS = ["장애", "파라", "휠체어", "보치아", "골볼"]


def main():
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
    )
    files = sorted(glob.glob(os.path.join(data_dir, "청소년_프로그램_*.csv")))
    if not files:
        raise SystemExit("원본 분할 CSV 없음")

    header = None
    rows = []
    skipped = 0
    for f in files:
        with open(f, encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh)
            h = [c.replace("﻿", "").strip() for c in next(reader)]
            if header is None:
                header = h
            idx = {c: i for i, c in enumerate(h)}
            cols = [idx.get("PROGRM_NM"), idx.get("FCLTY_NM"), idx.get("PROGRM_TRGET_NM")]
            for line in fh:
                try:
                    row = next(csv.reader([line]))
                except Exception:
                    skipped += 1
                    continue
                if len(row) != len(h):  # 손상 행(컬럼 수 불일치) 스킵
                    skipped += 1
                    continue
                blob = "|".join(row[i] for i in cols if i is not None)
                if any(k in blob for k in DIS_KEYWORDS):
                    rows.append(row)

    df = pd.DataFrame(rows, columns=header)
    df = df.drop_duplicates(subset=["FCLTY_NM", "PROGRM_NM", "CTPRVN_NM", "SIGNGU_NM"])
    out = os.path.join(data_dir, "장애인_체육_프로그램.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    print(f"손상 스킵 {skipped}행 / 장애인 프로그램 {len(df)}건 저장 → {out}")
    print("시도 분포:", df["CTPRVN_NM"].value_counts().to_dict())


if __name__ == "__main__":
    main()
