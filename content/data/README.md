# Dashboard data

CSV files read by the charts in `app/charts/`. Every file is copied from a captured
source in the brain repo (`madviking/junction2026`, folder `sources/`); cite that
file in the chart's `source` line.

| File | From | Notes |
| --- | --- | --- |
| `screening_by_language.csv` | `sources/2026-11-14-cancerregistry-screening-by-language.md` | Finnish Cancer Registry, attendance by native language, 2020–2024 (every year, from `sources/data/2026-11-14-screening-equity-by-language.json`). "Other" = native language not Finnish, Swedish or Sámi, or unknown. |
| `screening_by_birth_region_2024.csv` | same | Attendance by region of birth, 2024. |
| `county_language_screening.csv` | `sources/2026-11-13-hva-languages.md` | Statistics Finland 11rm (2025) aggregated to wellbeing services counties + Sotkanet screening 2024. English county names are ours; `county_fi` is the official name. |
| `digital_clinic_use_by_group.csv` | `sources/2026-11-14-aalto-digital-clinic-users-register-study.md` | Kujansivu et al., Scand J Prim Health Care 2026 (register study, 8 wellbeing services counties, 9–12 months after each public chat clinic launched, data 2022–2025). Public digital-clinic contacts per person and digital share of all public primary-care contacts, as stated in the article text (Figure 3). An empty share means the article gives no number ("almost equal" to the total for non-native speakers). Helsinki and Vantaa–Kerava are not in the study. |
| `pathway.json` | `sources/2026-11-14-cancerregistry-screening-by-language.md`, `sources/2026-11-14-europepmc-unmet-need-and-access-by-origin.md`, `sources/2026-11-14-espoo-equity-talk-kuitunen.md`, `sources/2026-11-13-web-research-minorities-screening.md`, `notes/2026-11-14-0145-silta-deep-data-analysis.md` | The pathway slide (`/presentation#/pathway`): map nodes, Silta bands, and per step the evidence level (`lang` / `other` / `none`), text, popup tables and notes, charts and source. The symptom-to-treatment days (Kuitunen et al., DLBCL, by first provider, not by language) are in the `fork` step's table, read from the slide's data labels. |

Do not put personal data or made-up numbers here. Sample or synthetic data must say so in the file name (`sample_*.csv`) and in the chart subtitle.
