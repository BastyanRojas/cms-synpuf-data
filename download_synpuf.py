"""
Download CMS DE-SynPUF (Medicare Synthetic Public Use Files)
Source: https://www.cms.gov/data-research/statistics-trends-and-reports/
        medicare-claims-synthetic-public-use-files

Navigates the CMS index page to discover all sample pages and their real
download URLs, then downloads the ZIP files.

Data files per sample (8 total):
  - Beneficiary Summary  (2008, 2009, 2010) — demographics + chronic conditions
  - Carrier Claims A & B (2008-2010)         — physician / ambulatory claims
  - Inpatient Claims     (2008-2010)         — hospitalizations
  - Outpatient Claims    (2008-2010)         — outpatient facility claims
  - Prescription Drug Events (2008-2010)     — pharmacy (Part D)

Usage:
  python download_synpuf.py                  # all 20 samples
  python download_synpuf.py --samples 1 2 3  # specific samples
"""

import argparse
from html.parser import HTMLParser
from pathlib import Path

import requests
from tqdm import tqdm

CMS_BASE        = "https://www.cms.gov"
CMS_INDEX_URL   = (
    f"{CMS_BASE}/data-research/statistics-trends-and-reports/"
    "medicare-claims-synthetic-public-use-files/"
    "cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf"
)
OUTPUT_DIR = Path(__file__).parent / "data" / "raw"

DATA_KEYWORDS = [
    "beneficiary_summary",
    "carrier_claims",
    "inpatient_claims",
    "outpatient_claims",
    "prescription_drug_events",
]

SAS_KEYWORDS = ["_sas", "sas_code"]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            if "href" in attrs:
                self.links.append(attrs["href"])


def get_links(url: str) -> list[str]:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    parser = LinkParser()
    parser.feed(r.text)
    return parser.links


def normalize_url(href: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return CMS_BASE + href


def is_data_file(url: str) -> bool:
    lower = url.lower()
    if not lower.endswith(".zip"):
        return False
    if any(sas in lower for sas in SAS_KEYWORDS):
        return False
    return any(kw in lower for kw in DATA_KEYWORDS)


def get_sample_urls(index_url: str) -> dict[int, str]:
    links = get_links(index_url)
    samples = {}
    for link in links:
        for n in range(1, 21):
            if link.endswith(f"de10-sample-{n}") and n not in samples:
                samples[n] = normalize_url(link)
                break
    return dict(sorted(samples.items()))


def get_download_urls(sample_url: str) -> list[str]:
    links = get_links(sample_url)
    return [normalize_url(l) for l in links if is_data_file(l)]


def download_file(url: str, dest: Path) -> bool:
    if dest.exists():
        print(f"  [skip]  {dest.name}")
        return True

    try:
        r = requests.get(url, stream=True, timeout=120)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [error] {dest.name}: {e}")
        return False

    total = int(r.headers.get("content-length", 0))
    with open(dest, "wb") as f, tqdm(
        desc=dest.name,
        total=total,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        leave=False,
    ) as bar:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

    print(f"  [ok]    {dest.name} ({dest.stat().st_size / 1_048_576:.1f} MB)")
    return True


def process_sample(sample_num: int, sample_url: str) -> list[str]:
    print(f"\n{'='*60}")
    print(f"Sample {sample_num}: {sample_url}")

    sample_dir = OUTPUT_DIR / f"sample_{sample_num}"
    sample_dir.mkdir(parents=True, exist_ok=True)

    download_urls = get_download_urls(sample_url)
    if not download_urls:
        print("  [warn]  No data files found on this page.")
        return []

    failed = []
    for url in download_urls:
        filename = url.split("/")[-1]
        dest = sample_dir / filename
        print(f"  Downloading {filename}")
        ok = download_file(url, dest)
        if not ok:
            failed.append(filename)

    return failed


def main():
    parser = argparse.ArgumentParser(description="Download CMS DE-SynPUF data")
    parser.add_argument(
        "--samples", type=int, nargs="+", metavar="N",
        help="Sample numbers to download (default: all 20)"
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Destination : {OUTPUT_DIR.resolve()}")
    print(f"Fetching sample index from CMS...")

    all_samples = get_sample_urls(CMS_INDEX_URL)
    print(f"Found {len(all_samples)} samples.\n")

    target = sorted(args.samples) if args.samples else list(all_samples.keys())

    all_failed = {}
    for n in target:
        if n not in all_samples:
            print(f"Sample {n} not found in index, skipping.")
            continue
        failed = process_sample(n, all_samples[n])
        if failed:
            all_failed[n] = failed

    print(f"\n{'='*60}")
    print("DONE")
    if all_failed:
        print("\nFailed files:")
        for n, files in all_failed.items():
            for f in files:
                print(f"  Sample {n}: {f}")
    else:
        print("All files downloaded successfully.")


if __name__ == "__main__":
    main()
