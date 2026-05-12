"""
Extract CMS DE-SynPUF ZIP files from raw/ into extracted/

Reads ZIPs from:   data/raw/sample_{N}/
Extracts CSVs to:  data/extracted/sample_{N}/

Usage:
  python extract_synpuf.py                  # all samples found in raw/
  python extract_synpuf.py --samples 1 2 3  # specific samples
"""

import argparse
import zipfile
from pathlib import Path

RAW_DIR       = Path(__file__).parent / "data" / "raw"
EXTRACTED_DIR = Path(__file__).parent / "data" / "extracted"


def extract_sample(sample_num: int) -> list[str]:
    raw_sample_dir       = RAW_DIR / f"sample_{sample_num}"
    extracted_sample_dir = EXTRACTED_DIR / f"sample_{sample_num}"

    if not raw_sample_dir.exists():
        print(f"  [warn]  raw/sample_{sample_num}/ not found, skipping.")
        return []

    extracted_sample_dir.mkdir(parents=True, exist_ok=True)

    zip_files = sorted(raw_sample_dir.glob("*.zip"))
    if not zip_files:
        print(f"  [warn]  No ZIP files found in raw/sample_{sample_num}/")
        return []

    failed = []
    for zip_path in zip_files:
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                members = zf.namelist()
                already_extracted = all(
                    (extracted_sample_dir / m).exists() for m in members
                )
                if already_extracted:
                    print(f"  [skip]  {zip_path.name}")
                    continue

                print(f"  [unzip] {zip_path.name} → {len(members)} file(s)")
                zf.extractall(extracted_sample_dir)
        except zipfile.BadZipFile as e:
            print(f"  [error] {zip_path.name}: {e}")
            failed.append(zip_path.name)

    return failed


def main():
    parser = argparse.ArgumentParser(description="Extract DE-SynPUF ZIPs to CSV")
    parser.add_argument(
        "--samples", type=int, nargs="+", metavar="N",
        help="Sample numbers to extract (default: all found in raw/)"
    )
    args = parser.parse_args()

    if args.samples:
        targets = sorted(args.samples)
    else:
        targets = sorted(
            int(p.name.split("_")[1])
            for p in RAW_DIR.iterdir()
            if p.is_dir() and p.name.startswith("sample_")
        )

    if not targets:
        print("No samples found in data/raw/. Run download_synpuf.py first.")
        return

    print(f"Extracting samples: {targets}")
    print(f"From : {RAW_DIR.resolve()}")
    print(f"To   : {EXTRACTED_DIR.resolve()}\n")

    all_failed = {}
    for n in targets:
        print(f"\n{'='*60}")
        print(f"Sample {n}")
        failed = extract_sample(n)
        if failed:
            all_failed[n] = failed

    print(f"\n{'='*60}")
    print("DONE")
    if all_failed:
        print("\nFailed:")
        for n, files in all_failed.items():
            for f in files:
                print(f"  Sample {n}: {f}")
    else:
        print("All files extracted successfully.")
        print(f"CSVs available at: {EXTRACTED_DIR.resolve()}")


if __name__ == "__main__":
    main()
