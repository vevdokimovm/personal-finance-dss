# Survey — international (English) edition

English version of the FINPILOT audience survey ("How do you decide where to put
your money?"), for reaching English-speaking respondents.

## Files

- **`finpilot_survey_en.gs`** — Google Apps Script that builds the whole form in
  Google Forms. Data-driven: the `SURVEY` object holds the translated content; a
  builder loop applies the correct item type per question.

## How to generate the form

1. Open <https://script.google.com> → **New project**.
2. Paste the contents of `finpilot_survey_en.gs`, save.
3. Run `createFinpilotSurveyEN()` once and authorize when prompted.
4. Open **View → Logs** — the published + edit URLs are printed there.

## Fidelity to the source

- Mirrors the original RU form 1:1: **7 sections, 62 questions**
  (34 single-choice, 17 multi-select, 4 scales, 3 grids, 4 text/paragraph).
- Question types map faithfully: "one oval" → single choice, "select all" →
  multi-select, 1–N sliders → scales, matrices → grids, "Other:" → an editable
  "Other" option, `*` → required. Attention check (Q47, "select 7 stars") kept.
- Monetary amounts are left in **₽** on purpose, to keep the research context
  identical to the RU wave (do **not** silently convert to another currency —
  that would change what the numbers mean and break cross-wave comparison).

Source of the questionnaire: `../raw/survey_questionnaire_62q.pdf`.
