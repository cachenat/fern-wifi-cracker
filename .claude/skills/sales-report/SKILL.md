---
name: sales-report
description: Sales pipeline report generator for the AI Sales Team. Use when invoked via `/sales report`. Synthesizes individual prospect analysis files into an executive-ready pipeline report. Reads all prospect files from the current directory and produces SALES-REPORT.md with pipeline dashboard, score distribution, top prospects, action items, and health metrics.
metadata:
  version: 1.0.0
---

# Sales Pipeline Report Generator

You are the pipeline report generator for `/sales report`. Your job is to synthesize all prospect analysis data in the current directory into a clear, executive-ready pipeline report.

## When This Skill Is Invoked

The user runs `/sales report` with no arguments. Scan the current directory for prospect files and generate a comprehensive pipeline report.

---

## Phase 1: File Discovery

Search for these prospect file patterns in the current directory and subdirectories:

- `**/PROSPECT-ANALYSIS.md`
- `**/COMPANY-RESEARCH.md`
- `**/LEAD-QUALIFICATION.md`
- `**/DECISION-MAKERS.md`
- `**/OUTREACH-SEQUENCE.md`

**If no files are found:** Generate guidance on how to start prospecting, with example workflows.

**If files are found:** Proceed to data extraction.

---

## Phase 2: Data Extraction

From each prospect file, extract:

| Field | Source | Priority |
|-------|--------|---------|
| Company name | File header or content | High |
| Company URL | File header or content | High |
| Prospect Score (0-100) | PROSPECT-ANALYSIS.md | High |
| Letter grade (A/B/C/D) | PROSPECT-ANALYSIS.md | High |
| Component scores | PROSPECT-ANALYSIS.md | Medium |
| Key pain points | Any analysis file | Medium |
| Primary decision maker | DECISION-MAKERS.md | Medium |
| Recommended action | Any analysis file | High |
| Outreach status | OUTREACH-SEQUENCE.md | Medium |
| Deal value estimate | Any analysis file | Low |
| Pipeline stage | Any analysis file | Medium |

**Stage classification based on available files:**

| Files Present | Stage |
|-------------|-------|
| PROSPECT-ANALYSIS.md only | Research |
| + OUTREACH-SEQUENCE.md | Outreach Started |
| + MEETING-PREP.md | Meeting Scheduled |
| + FOLLOWUP-SEQUENCE.md | In Follow-Up |
| + CLIENT-PROPOSAL.md | Proposal Sent |

---

## Phase 3: Build the 8-Section Report

### Section 1: Executive Summary

One-page overview covering:
- Total pipeline health (overall assessment)
- Score distribution trends
- Top opportunity highlight
- Critical risks requiring attention
- Focus recommendation (where to spend time this week)

### Section 2: Pipeline Dashboard

Comprehensive sorted table of all prospects:

| # | Company | Score | Grade | Stage | Key Pain | Next Action | Est. Value |
|---|---------|-------|-------|-------|----------|-------------|------------|
| 1 | [A-grade prospects first] | [X]/100 | A | [stage] | [pain] | [action] | $[X] |
| 2 | [B-grade prospects] | [X]/100 | B | [stage] | [pain] | [action] | $[X] |
[Continue for all prospects, sorted by score]

### Section 3: Score Distribution

Breakdown by grade with pipeline health assessment:

| Grade | Score Range | Count | % of Pipeline | Assessment |
|-------|-----------|-------|--------------|------------|
| A+ | 90-100 | [X] | [X]% | Hot leads — immediate action |
| A | 80-89 | [X] | [X]% | Strong fits — priority outreach |
| B+ | 70-79 | [X] | [X]% | Good fits — active nurturing |
| B | 60-69 | [X] | [X]% | Moderate — regular touchpoints |
| C+ | 50-59 | [X] | [X]% | Weak — research needed |
| C | 40-49 | [X] | [X]% | Poor fit — minimal time investment |
| D | 0-39 | [X] | [X]% | No fit — remove from active pipeline |

**Pipeline health assessment:**
- % of pipeline in A/B grades: [X]% (target: 60%+)
- Average score: [X] (target: 60+)
- Pipeline depth: [assessment]

### Section 4: Top 5 Prospects

Detailed snapshots of the 5 highest-scoring companies:

For each:
- Company name, score, grade
- Component score breakdown (Company Fit / Contact Access / Opportunity / Competitive / Outreach)
- Key contacts identified (names and titles)
- Top pain points (2-3 bullets)
- Recommended approach (1 paragraph)
- Immediate next action (specific, actionable)
- Risk factors (1-2 bullets)

### Section 5: Action Items

Prioritized, numbered list organized by timeframe:

**Immediate (Today):**
1. [Specific action for highest-priority prospect]
2. [Second action]
3. [Third action]

**This Week:**
1. [Medium-priority actions]
2. [Continue outreach on started sequences]
3. [Research gaps to fill]
[4-6 total]

**Pipeline Building:**
1. [Longer-term actions]
2. [New prospects to add]
3. [Content or resources to create]
[3-5 total]

### Section 6: Outreach Status

Matrix showing which prospects have sequences created:

| Company | Grade | Research | Outreach | Meeting | Follow-Up | Proposal |
|---------|-------|----------|---------|---------|-----------|---------|
| [Company] | A | ✅ | ✅ | ⬜ | ⬜ | ⬜ |
| [Company] | A | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |
| [Company] | B | ✅ | ✅ | ✅ | ⬜ | ⬜ |

**Gaps identified:**
- [X] A-grade prospects without outreach sequences
- [X] B-grade prospects without research completed
- [X] prospects with no follow-up after initial outreach

### Section 7: Pipeline Health Metrics

Dashboard display:

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Prospects | [X] | — | — |
| Average Score | [X] | 60+ | ✅/⚠️/❌ |
| A-Grade % | [X]% | 20%+ | ✅/⚠️/❌ |
| A+B Grade Coverage | [X]% | 60%+ | ✅/⚠️/❌ |
| With Outreach Sequence | [X]% | 80%+ | ✅/⚠️/❌ |
| Contacted This Week | [X] | — | — |
| In Active Follow-Up | [X] | — | — |
| Score Std. Deviation | [X] | — | Pipeline diversity |

**Overall Pipeline Health:** [Strong/Adequate/Needs Attention/Critical]

**Health narrative:** [2-3 sentence assessment of what the numbers mean and what needs to change]

### Section 8: Weekly Focus

Top 3 prospects for focused attention this week, with day-by-day activities:

**Priority 1: [Company Name] — Grade [X], Score [X]**

Urgency reason: [why this prospect needs attention now]

| Day | Action |
|-----|--------|
| Monday | [Specific action] |
| Tuesday | [Specific action] |
| Wednesday | [Specific action] |
| Thursday | [Specific action] |
| Friday | [Follow-up or review] |

**Priority 2: [Company Name]**
[same structure]

**Priority 3: [Company Name]**
[same structure]

---

## Output Format: SALES-REPORT.md

```markdown
# Sales Pipeline Report
**Date:** [current date]
**Prospects Analyzed:** [X]
**Overall Pipeline Health:** [Strong/Adequate/Needs Attention/Critical]

---

## Executive Summary

[Section 1 content]

---

## Pipeline Dashboard

[Section 2 — full sorted table]

---

## Score Distribution

[Section 3 — grade breakdown table + health assessment]

---

## Top Prospects

[Section 4 — top 5 detailed snapshots]

---

## Action Items

[Section 5 — prioritized action list]

---

## Outreach Status

[Section 6 — outreach matrix]

---

## Pipeline Health Metrics

[Section 7 — health dashboard]

---

## Weekly Focus

[Section 8 — top 3 with daily plans]

---

*Generated by AI Sales Team — `/sales report`*
*Next: Run `/sales report-pdf` to generate a PDF version for sharing*
```

---

## Terminal Output

```
=== SALES PIPELINE REPORT COMPLETE ===

Date: [date]
Prospects Analyzed: [X]

Score Distribution:
  A+ (90-100): [X] prospects
  A  (80-89):  [X] prospects
  B  (60-79):  [X] prospects
  C  (40-59):  [X] prospects
  D  (0-39):   [X] prospects

Pipeline Health: [Strong/Adequate/Needs Attention/Critical]
Average Score: [X]/100

Top Prospect: [Company Name] — Grade [X], Score [X]/100

Immediate Actions:
  1. [Action]
  2. [Action]
  3. [Action]

Full report saved to: SALES-REPORT.md
Run `/sales report-pdf` to generate a shareable PDF.
```

---

## Quality Standards

- **Data-driven and honest.** Avoid inflating scores or sugarcoating weak prospects.
- **Specific and actionable.** Every recommendation must answer "what exactly should I do and why?"
- **Complete coverage.** Every discovered prospect must appear in the report. No silent exclusions.
- **Forward-looking.** The report should tell the sales rep what to do next week, not just what happened.

## Cross-Skill Integration

- Reads all `PROSPECT-ANALYSIS.md`, `COMPANY-RESEARCH.md`, `LEAD-QUALIFICATION.md`, `DECISION-MAKERS.md`, `OUTREACH-SEQUENCE.md` files found in directory
- Output read by: `sales-report-pdf`
- Suggest follow-up: `/sales report-pdf` to generate shareable PDF
