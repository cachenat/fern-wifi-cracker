---
name: sales-prospect
description: Full prospect analysis orchestrator for the AI Sales Team. Invoked via `/sales prospect <url>`. Launches 5 parallel subagents (sales-company, sales-contacts, sales-opportunity, sales-competitive, sales-strategy) to score a prospect 0-100 across Company Fit (25%), Contact Access (20%), Opportunity Quality (20%), Competitive Position (15%), and Outreach Readiness (20%). Saves complete analysis to PROSPECT-ANALYSIS.md.
metadata:
  version: 1.0.0
---

# Full Prospect Analysis Orchestrator

You are the prospect analysis orchestrator for `/sales prospect <url>`. Your job is to run a comprehensive, multi-dimensional analysis of a prospect company and produce an actionable sales intelligence report.

## When This Skill Is Invoked

The user runs `/sales prospect <url>` with a company website URL. This is the highest-value command in the AI Sales Team toolkit — it runs the full analysis pipeline and produces a complete prospect dossier.

---

## Phase 1: Discovery (Sequential)

Before launching parallel agents, perform initial discovery to provide shared context.

### 1.1 Fetch the Homepage

Use WebFetch to retrieve the company homepage. Extract:
- Company name
- Value proposition / tagline
- Target customer (who they serve)
- Primary product/service
- Company type: SaaS / Agency / E-commerce / Enterprise software / SMB / Startup / Other
- Industry vertical
- Any obvious signals (pricing visible, enterprise focus, etc.)

### 1.2 Detect Company Type

Based on the homepage, classify the company:

| Type | Signals |
|------|---------|
| **SaaS** | Subscription pricing, "platform", "software", trial/demo CTA |
| **Agency** | "We help clients", services listed, case studies |
| **E-commerce** | Product catalog, shopping cart, "shop now" |
| **Enterprise software** | "Contact Sales", no visible pricing, enterprise logos |
| **SMB** | Small team visible, local focus, founder-led |
| **Startup** | "We're building", early-stage language, small team |

### 1.3 Compile Discovery Briefing

Create a brief document containing:
- Company name, URL, type, industry
- Homepage value proposition (verbatim)
- Key pages found (which subpages exist)
- Pre-fetched page content to avoid redundant fetches by subagents
- Any ICP context from `IDEAL-CUSTOMER-PROFILE.md` if it exists

---

## Phase 2: Parallel Analysis (5 Agents)

Launch all 5 subagents simultaneously with the discovery briefing:

1. **sales-company** → Company Fit analysis (25% weight)
2. **sales-contacts** → Contact Access analysis (20% weight)
3. **sales-opportunity** → Opportunity Quality analysis (20% weight)
4. **sales-competitive** → Competitive Position analysis (15% weight)
5. **sales-strategy** → Outreach Readiness analysis (20% weight)

Each agent returns a structured analysis with a component score (0-100).

---

## Phase 3: Synthesis (Sequential)

After all 5 agents complete, synthesize results:

### 3.1 Calculate Prospect Score

```
Prospect Score = (
    Company Fit Score × 0.25 +
    Contact Access Score × 0.20 +
    Opportunity Quality Score × 0.20 +
    Competitive Position Score × 0.15 +
    Outreach Readiness Score × 0.20
)
```

### 3.2 Assign Grade

| Score | Grade | Label |
|-------|-------|-------|
| 90-100 | A+ | Hot Lead |
| 80-89 | A | Strong Fit |
| 70-79 | B+ | Good Fit |
| 60-69 | B | Moderate Fit |
| 50-59 | C+ | Weak Fit |
| 40-49 | C | Poor Fit |
| 0-39 | D | No Fit |

### 3.3 Generate Action Plan

Create prioritized actions across three timeframes:

**Immediate (Today):**
- Most important single action based on the highest-scoring opportunity
- The ready-to-send first email (from sales-strategy)
- The primary contact to reach out to

**This Week:**
- 3-5 follow-up actions to build momentum
- Secondary contacts to engage
- Content to prepare

**This Month:**
- Longer-term relationship building actions
- Research gaps to fill
- Events or triggers to monitor

### 3.4 Assess Confidence

Rate overall confidence in the analysis:
- **High:** Data found for most key dimensions; few assumptions made
- **Medium:** Some gaps filled with inferences; key facts confirmed
- **Low:** Significant data gaps; many assumptions required

---

## Output: PROSPECT-ANALYSIS.md

Save the complete analysis to `PROSPECT-ANALYSIS.md`:

```markdown
# Prospect Analysis: [Company Name]
**URL:** [url]
**Date:** [current date]
**Prospect Score: [X]/100 — Grade [X]: [Label]**
**Confidence:** [High/Medium/Low]

---

## Executive Summary

[3-5 sentence summary. What is this company? Why is it (or isn't it) a good prospect?
What's the single most important thing the sales rep needs to know?
What should they do first?]

---

## Prospect Score Breakdown

| Dimension | Score | Weight | Weighted Score |
|-----------|-------|--------|----------------|
| Company Fit | [X]/100 | 25% | [X] |
| Contact Access | [X]/100 | 20% | [X] |
| Opportunity Quality | [X]/100 | 20% | [X] |
| Competitive Position | [X]/100 | 15% | [X] |
| Outreach Readiness | [X]/100 | 20% | [X] |
| **TOTAL** | | **100%** | **[X]/100** |

**Grade: [X] — [Label]**

---

## Company Overview

[Insert Company Fit analysis from sales-company agent]

---

## Decision Maker Map

[Insert Contact Access analysis from sales-contacts agent]

---

## Opportunity Assessment

[Insert Opportunity Quality analysis from sales-opportunity agent]

---

## Competitive Intelligence

[Insert Competitive Position analysis from sales-competitive agent]

---

## Outreach Strategy

[Insert Outreach Readiness analysis from sales-strategy agent]

---

## Action Plan

### Immediate Actions (Today)

1. **[Primary action]** — [why and how]
2. **[Secondary action]** — [why and how]
3. **[Tertiary action]** — [why and how]

### This Week

1. [Action with specific detail]
2. [Action with specific detail]
3. [Action with specific detail]
4. [Action with specific detail]
5. [Action with specific detail]

### This Month

1. [Longer-term action]
2. [Longer-term action]
3. [Longer-term action]

---

## Ready-to-Send First Email

**To:** [Contact Name] ([Title])
**Subject:** [Email Subject]

[Complete email body ready to copy-paste]

---

## Analysis Confidence

**Overall Confidence:** [High/Medium/Low]

**Data Gaps:**
- [Gap 1: what's missing and how it affects the analysis]
- [Gap 2: what's missing and how it affects the analysis]

**Assumptions Made:**
- [Assumption 1 with reasoning]
- [Assumption 2 with reasoning]

---

*Generated by AI Sales Team — `/sales prospect`*
```

---

## Terminal Output

After saving the file, display a visual scorecard:

```
╔══════════════════════════════════════════════════════╗
║           PROSPECT ANALYSIS COMPLETE                 ║
╠══════════════════════════════════════════════════════╣
║ Company: [name]                                      ║
║ Grade:   [X] — [Label]                               ║
╠══════════════════════════════════════════════════════╣
║ PROSPECT SCORE: [XX]/100                             ║
║                                                      ║
║ Company Fit      [XX]/100  ████████░░  25%           ║
║ Contact Access   [XX]/100  ██████░░░░  20%           ║
║ Opportunity      [XX]/100  ███████░░░  20%           ║
║ Competitive      [XX]/100  █████░░░░░  15%           ║
║ Outreach Ready   [XX]/100  ████████░░  20%           ║
╠══════════════════════════════════════════════════════╣
║ Top Decision Maker: [Name], [Title]                  ║
║ Best Outreach Channel: [Channel]                     ║
║ Urgency: [High/Medium/Low]                           ║
╠══════════════════════════════════════════════════════╣
║ IMMEDIATE ACTION:                                    ║
║ [One sentence describing the single best next step]  ║
╚══════════════════════════════════════════════════════╝

Full report saved to: PROSPECT-ANALYSIS.md
```

---

## Error Handling

- **Unreachable URL:** Attempt alternate formats (www/no-www, http/https). If still unreachable, report error with suggestions.
- **Subagent failure:** Continue with remaining agents. Note which agent failed and proceed with partial data.
- **Authentication walls:** Note that the site requires authentication and analyze only publicly accessible content.
- **Minimal content site:** Reduce confidence to Low, rely more heavily on external search data, and flag data gaps explicitly.
- **Parked domain / not a real company:** Report this finding immediately and do not proceed with analysis.

## Cross-Skill Integration

- Reads `IDEAL-CUSTOMER-PROFILE.md` if it exists (provides ICP calibration to all agents)
- Writes `PROSPECT-ANALYSIS.md` (read by sales-report and sales-proposal)
- Suggests follow-up: `/sales outreach` for full email sequence, `/sales prep` for meeting brief
