---
name: sales-report-pdf
description: PDF pipeline report generator for the AI Sales Team. Use when invoked via `/sales report-pdf`. Converts SALES-REPORT.md into a professional, visually polished PDF suitable for leadership and investor distribution. Uses Python reportlab library via scripts/generate_pdf_report.py. Produces SALES-REPORT-{YYYY-MM-DD}.pdf.
metadata:
  version: 1.0.0
---

# Professional Sales Report PDF Generator

You are the PDF report generator for `/sales report-pdf`. Your job is to convert the markdown pipeline report into a professional PDF ready for leadership or investor distribution.

## When This Skill Is Invoked

The user runs `/sales report-pdf`. Generate a professional PDF from the existing `SALES-REPORT.md` file.

---

## Phase 1: Prerequisites Check

Before generating the PDF, verify:

1. **SALES-REPORT.md exists** in the current directory
   - If not found: "No SALES-REPORT.md found. Run `/sales report` first to generate the pipeline report."

2. **Python 3 is available:** `python3 --version`
   - If not found: Provide installation instructions

3. **reportlab is installed:** `python3 -c "import reportlab"`
   - If not installed: Run `pip install reportlab>=4.0`

4. **generate_pdf_report.py exists** at `scripts/generate_pdf_report.py`
   - If not found: "Script not found. Ensure scripts/generate_pdf_report.py is present."

---

## Phase 2: Data Extraction

Parse `SALES-REPORT.md` and any linked prospect files to build the JSON input for the PDF generator.

Extract:
- Report date
- Overall pipeline score (calculated from all prospect scores)
- Executive summary text
- All prospects with: name, URL, score, grade, stage, next action
- Category/dimension scores if available
- Action items (quick wins, this week, this month)
- Pipeline health metrics

Also read individual prospect files for richer data:
- Component scores from `PROSPECT-ANALYSIS.md` files
- Decision maker names from `DECISION-MAKERS.md` files
- Key contacts and pain points

---

## Phase 3: Build JSON Input

Create `_pdf_input.json` in the current directory with this structure:

```json
{
  "date": "Month DD, YYYY",
  "overall_pipeline_score": 72,
  "executive_summary": "...",
  "prospects": [
    {
      "name": "Company Name",
      "url": "https://example.com",
      "score": 85,
      "grade": "A",
      "stage": "Discovery Call",
      "next_action": "Schedule demo with VP Engineering"
    }
  ],
  "categories": {
    "Company Fit": {"score": 75},
    "Contact Access": {"score": 68},
    "Opportunity Quality": {"score": 82},
    "Competitive Position": {"score": 63},
    "Outreach Readiness": {"score": 70}
  },
  "action_items": {
    "quick_wins": [
      "Action item 1",
      "Action item 2"
    ],
    "this_week": [
      "Action item 1",
      "Action item 2"
    ],
    "this_month": [
      "Action item 1",
      "Action item 2"
    ]
  },
  "pipeline_health": {
    "total_prospects": 12,
    "avg_score": 65,
    "a_grade": 3,
    "b_grade": 5,
    "c_grade": 3,
    "d_grade": 1
  }
}
```

---

## Phase 4: Generate the PDF

Run the generation script:

```bash
python3 scripts/generate_pdf_report.py _pdf_input.json SALES-REPORT-$(date +%Y-%m-%d).pdf
```

---

## Phase 5: Verify and Clean Up

After generation:

1. **Verify the PDF was created** and has a reasonable file size (>10KB)
2. **Report the output:** File path, file size, estimated page count
3. **Clean up:** Delete `_pdf_input.json` on success (retain for debugging if generation failed)

---

## PDF Document Specifications

**Format:**
- Page size: Letter (8.5" × 11")
- Orientation: Portrait
- Margins: 0.75" all sides

**Design:**
- Color scheme: Professional blues and grays (sales-focused)
- Scoring colors: Green (80+), Blue (60-79), Amber (40-59), Red (<40)
- Grade colors: Green (A), Blue (B), Amber (C), Red (D)

**Expected structure (4-8 pages):**
1. Cover page with pipeline score gauge and executive summary
2. Score breakdown with horizontal bar chart
3. Top prospects (5 detailed cards)
4. Pipeline summary table (all prospects)
5. Action plan (quick wins, this week, this month)
6. Scoring methodology

---

## Output Confirmation

After successful generation, display:

```
=== PDF REPORT GENERATED ===

File: SALES-REPORT-[YYYY-MM-DD].pdf
Size: [X] KB
Pages: ~[X] pages
Location: [full path]

Ready to share with leadership or investors.
```

---

## Error Handling

**If reportlab fails to install:**
```
pip3 install reportlab>=4.0
# or
pip install reportlab --user
```

**If PDF generation script fails:**
- Print the Python error message
- Suggest checking the JSON input format
- Offer to regenerate the markdown report first

**If output PDF is empty or too small:**
- Suggests the markdown report may have minimal data
- Recommend running additional prospect analyses first

---

## Critical Rules

1. **Never generate PDF without SALES-REPORT.md** — require the markdown report first
2. **Always verify dependencies before execution** — clear error messages if missing
3. **Delete `_pdf_input.json` on success** — don't leave temp files in the working directory
4. **Mark incomplete data as N/A** — don't fail if some prospect data is missing
5. **Provide exact file path** — confirm where the PDF was saved

## Cross-Skill Integration

- Requires `SALES-REPORT.md` to exist (run `/sales report` first)
- Also reads individual prospect files for richer data
- The script `scripts/generate_pdf_report.py` must be present (included with this installation)
- Dependencies: `pip install -r requirements.txt`
