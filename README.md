# CMS DE-SynPUF Data Pipeline

Download and extraction scripts for the CMS 2008–2010 Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF), a synthetic Medicare claims dataset published by the Centers for Medicare & Medicaid Services.

## Dataset

**Source:** [CMS DE-SynPUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf)

Synthetic dataset based on a 5% random sample of Medicare beneficiaries tracked over 3 years (2008–2010). Contains 20 non-overlapping samples (~116,000 beneficiaries each), all sharing the same structure and file format.

### Files per sample

| File | Description | Coverage |
|---|---|---|
| `Beneficiary_Summary` | Demographics, chronic conditions, annual reimbursements | 2008, 2009, 2010 |
| `Carrier_Claims A & B` | Physician / ambulatory claims | 2008–2010 |
| `Inpatient_Claims` | Hospital admissions | 2008–2010 |
| `Outpatient_Claims` | Outpatient facility claims | 2008–2010 |
| `Prescription_Drug_Events` | Pharmacy dispensing events (Part D) | 2008–2010 |

> **Known CMS issue:** The 2010 Beneficiary Summary for Sample 1 links to Sample 20 instead. See [OHDSI/ETL-CMS issue #62](https://github.com/OHDSI/ETL-CMS/issues/62).

## Project Structure

```
healthcare/
├── data/
│   ├── raw/                  # Downloaded ZIP files (source of truth)
│   │   └── sample_{N}/
│   ├── extracted/            # CSVs extracted from ZIPs
│   │   └── sample_{N}/
│   └── processed/            # Cleaned data in .parquet format
│       └── sample_{N}/
├── download_synpuf.py        # Download ZIPs from CMS
├── extract_synpuf.py         # Extract CSVs from raw/ into extracted/
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Download

```bash
python download_synpuf.py                  # all 20 samples
python download_synpuf.py --samples 1      # sample 1 only
python download_synpuf.py --samples 1 2 3  # specific samples
```

### Extract

```bash
python extract_synpuf.py                  # all samples found in raw/
python extract_synpuf.py --samples 1      # sample 1 only
python extract_synpuf.py --samples 1 2 3  # specific samples
```

Both scripts are idempotent — already downloaded or extracted files are skipped automatically.

## Key Variable

`DESYNPUF_ID` — unique beneficiary identifier linking all tables across all files.

## Documentation

- [CMS DE-SynPUF User Guide (PDF)](https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/Downloads/SynPUF_DUG.pdf)
- [CMS Codebook (PDF)](https://www.cms.gov/files/document/de-10-codebook.pdf-0)
