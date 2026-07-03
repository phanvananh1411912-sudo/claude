#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""enrich_cilin.py — Bổ sung mã trung/tiểu loại Cilin đầy đủ cho shuowen_radicals_vi.json.

Cách dùng:
    python3 enrich_cilin.py cilin.txt shuowen_radicals_vi.json [-o output.json]

- `cilin.txt`: 哈工大同义词词林扩展版 (mỗi dòng: "Aa01A01= 人 士 人物 ...";
  mã 8 ký tự ở đầu, các từ cách nhau bằng khoảng trắng).
- Với mỗi bộ thủ, tra `cilin.tu_khoa_tra` trong cilin.txt, lấy các mã dòng chứa
  từ đó và điền vào `cilin.ma_chi_tiet` (tối đa 5 mã, ưu tiên mã trùng đại loại).
- App chạy bình thường khi chưa có `ma_chi_tiet` — script này là tuỳ chọn.
"""
import argparse, json, sys, collections

def load_cilin(path):
    index = collections.defaultdict(list)  # từ -> [mã]
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            head, *words = line.split()
            code = head.rstrip("=#@")
            for w in words:
                index[w].append(code)
    return index

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cilin_txt")
    ap.add_argument("shuowen_json")
    ap.add_argument("-o", "--output", default=None, help="mặc định: ghi đè file shuowen")
    args = ap.parse_args()

    index = load_cilin(args.cilin_txt)
    with open(args.shuowen_json, encoding="utf-8") as f:
        data = json.load(f)

    filled = missing = 0
    for key, entry in data.get("radicals", {}).items():
        cilin = entry.get("cilin")
        if not cilin:
            continue
        kw = cilin.get("tu_khoa_tra") or key
        codes = index.get(kw, [])
        if not codes:  # thử từng chữ trong từ khoá
            for chx in kw:
                codes = index.get(chx, [])
                if codes:
                    break
        if codes:
            main_cat = cilin.get("dai_loai", "")
            codes = sorted(set(codes), key=lambda c: (0 if c[:1] == main_cat else 1, c))[:5]
            cilin["ma_chi_tiet"] = codes
            filled += 1
        else:
            missing += 1
            print(f"  ! không tìm thấy '{kw}' (bộ {key})", file=sys.stderr)

    out = args.output or args.shuowen_json
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"Đã điền ma_chi_tiet cho {filled} bộ, thiếu {missing}. Ghi ra: {out}")

if __name__ == "__main__":
    main()
