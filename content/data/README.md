# Dashboard data

CSV files read by the charts in `app/charts/`. Every file is copied from a captured
source in the brain repo (`madviking/junction2026`, folder `sources/`); cite that
file in the chart's `source` line.

| File | From | Notes |
| --- | --- | --- |
| `screening_by_language.csv` | `sources/2026-11-14-cancerregistry-screening-by-language.md` | Finnish Cancer Registry, attendance by native language, 2020–2024 (every year, from `sources/data/2026-11-14-screening-equity-by-language.json`). "Other" = native language not Finnish, Swedish or Sámi, or unknown. |
| `screening_by_birth_region_2024.csv` | same | Attendance by region of birth, 2024. |
| `gap_by_step.csv` | same + `notes/2026-11-14-0145-silta-deep-data-analysis.md` §1 (95% CIs) + `sources/data/2026-11-14-screening-equity-by-language.json` (`followup_by_language`) | Gap (other minus domestic, pp) at each pathway step. Colorectal colonoscopy row is pooled 2022–2024 (n = 371 + 497 + 495 other-language positives). `verdict`: gap / none / unclear. |
| `county_language_screening.csv` | `sources/2026-11-13-hva-languages.md` | Statistics Finland 11rm (2025) aggregated to wellbeing services counties + Sotkanet screening 2024. English county names are ours; `county_fi` is the official name. |

Do not put personal data or made-up numbers here. Sample or synthetic data must say so in the file name (`sample_*.csv`) and in the chart subtitle.
