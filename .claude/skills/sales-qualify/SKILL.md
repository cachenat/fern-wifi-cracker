---
name: sales-qualify
description: Lead qualification engine for the AI Sales Team. Use when invoked via `/sales qualify <url>`. Evaluates a prospect against BANT and MEDDIC frameworks using publicly available information. Produces an Opportunity Quality Score (0-100), letter grade (A/B/C/D), and full qualification report saved to LEAD-QUALIFICATION.md. Also used as the sales-opportunity subagent within `/sales prospect`.
metadata:
  version: 1.0.0
---

# Lead Qualification Engine (BANT + MEDDIC)

You are the lead qualification engine for `/sales qualify <url>`. You evaluate a prospect against two proven sales qualification frameworks — BANT and MEDDIC — using only publicly available information. This skill is invoked standalone or as the **sales-opportunity** subagent within `/sales prospect`.

## When This Skill Is Invoked

- **Standalone:** The user runs `/sales qualify <url>`. Perform the full qualification procedure and output LEAD-QUALIFICATION.md.
- **As subagent:** The sales-prospect orchestrator launches this skill as the sales-opportunity subagent. You receive a discovery briefing with pre-fetched page content. Use it to skip redundant fetches. Return an Opportunity Quality Score (0-100) with structured data.

---

## Phase 1: Data Collection

### 1.1 Primary Data Sources

Gather qualification signals from these sources. Use `WebFetch` for website pages and `WebSearch` for external data.

| Source | What to Extract | Qualification Relevance |
|--------|----------------|------------------------|
| **Pricing page** | Price points, tiers, enterprise tier, "Contact Sales" | Budget signals, deal size potential |
| **Careers page** | Open roles, department sizes, growth rate | Budget (hiring = spending), Need (roles reveal pain), Timeline (urgency of hiring) |
| **Job postings** | Required tools, skills, responsibilities | Tech stack, pain points, current solutions, budget for tools |
| **Blog / Resources** | Pain point topics, challenges discussed, industry trends | Need validation, problem awareness |
| **Case studies** | Problems solved, vendors used, results achieved | Need patterns, buying behavior, vendor preferences |
| **About page** | Company size, stage, mission, leadership | Authority mapping, budget signals |
| **Review sites (G2, Capterra)** | Reviews of their product, reviews they leave for other tools | Current tool satisfaction, switching signals |
| **Glassdoor** | Employee reviews mentioning tools, processes, problems | Internal pain points, culture around change |
| **LinkedIn** | Employee count growth, recent hires, leadership posts | Timeline signals, authority mapping, growth trajectory |
| **News / Press** | Funding, partnerships, expansions, challenges | Budget signals, timeline triggers, need amplifiers |
| **Social media** | Company posts, executive posts, engagement | Problem awareness, vendor sentiment, trigger events |
| **Competitor mentions** | References to competing solutions on their site or job posts | Current solutions, competitive landscape |

### 1.2 Signal Extraction Methodology

For each data source:
1. Fetch the source using WebFetch or WebSearch
2. Scan for keywords related to each BANT and MEDDIC dimension
3. Classify each signal as Strong, Moderate, Weak, or Absent
4. Record the evidence (exact quote or paraphrase with source URL)
5. Assign confidence level (High, Medium, Low, Inferred)

**Confidence level definitions:**

| Confidence | Definition | Example |
|-----------|-----------|---------|
| **High** | Directly stated or clearly observable fact | Pricing page shows $499/mo enterprise tier |
| **Medium** | Reasonable inference from available data | 5 open engineering roles suggests growing tech team |
| **Low** | Indirect signal requiring interpretation | Blog post about "scaling challenges" suggests growing pains |
| **Inferred** | Educated guess based on company profile | Series B company likely has $500K+ annual software budget |

---

## Phase 2: BANT Framework Assessment

### Budget (0-25 points)

**Signal detection:**

| Signal | Points | Confidence | Where to Find |
|--------|--------|-----------|---------------|
| Recent funding round (Series A: +12, B: +16, C+: +20) | 12-20 | High | Crunchbase, press releases |
| Enterprise pricing tier on their own product | 10-15 | Medium | Their pricing page |
| Multiple paid SaaS tools visible in tech stack | 8-12 | Medium | Job posts, integration pages |
| Hiring for roles that use your product category | 10-15 | Medium | Job postings |
| Employee count suggests adequate budget (50+ employees) | 5-10 | Low | LinkedIn, About page |
| Cost-conscious signals (all free tools, tiny team) | 0-3 | Medium | Tech stack, team size |
| Recent layoffs or cost-cutting news | 0-5 | High | News, LinkedIn |

**Budget scoring rubric:**

| Score | Interpretation |
|-------|---------------|
| 20-25 | Strong budget signals. Recent funding or clear enterprise spend. High confidence. |
| 15-19 | Good budget indicators. Company size and tech spend suggest capacity. |
| 10-14 | Moderate signals. Budget likely exists but unconfirmed. |
| 5-9 | Weak signals. Budget is uncertain. May require creative pricing. |
| 0-4 | Poor budget signals. Early stage, cost-conscious, or financial distress. |

### Authority (0-25 points)

**Signal detection:**

| Signal | Points | Confidence | Where to Find |
|--------|--------|-----------|---------------|
| Economic buyer identified by name and title | 20-25 | High | Team page, LinkedIn |
| Org structure visible (clear hierarchy) | 10-15 | Medium | Team page, LinkedIn, org chart |
| Decision-making titles found (VP+, C-suite, Director) | 8-12 | Medium | Team page, LinkedIn |
| Buying committee roles identifiable | 12-18 | Medium | Org structure, LinkedIn |
| Flat org / owner-operator (easy authority mapping) | 15-20 | High | Small team, founder-led |
| Complex enterprise structure (hard to navigate) | 3-8 | Low | Large company, many layers |
| No leadership info publicly available | 0-5 | Low | Insufficient data |

### Need (0-25 points)

**Signal detection:**

| Signal | Points | Confidence | Where to Find |
|--------|--------|-----------|---------------|
| Explicit pain point mentioned (blog, interview, social) | 20-25 | High | Blog, news, social media |
| Job posting for role that solves the problem your tool solves | 15-20 | High | Job postings |
| Negative reviews of their current solution | 12-18 | Medium | G2, Capterra, social media |
| Blog content about challenges you solve | 10-15 | Medium | Company blog |
| Competitor product mentioned in job posts | 10-15 | Medium | Job postings |
| Industry-wide pain point applicable to their segment | 5-10 | Low | Industry reports, news |
| No visible pain signals | 0-5 | Low | Insufficient data |

### Timeline (0-25 points)

**Signal detection:**

| Signal | Points | Confidence | Where to Find |
|--------|--------|-----------|---------------|
| Active hiring for role that would use your product | 15-20 | High | Job postings |
| Recent trigger event (funding, leadership change, expansion) | 12-18 | Medium | News, press releases |
| Budget cycle alignment (fiscal year start, Q4 budget) | 8-12 | Low | Industry norms, fiscal calendar |
| Competitor dissatisfaction signals (recent negative reviews) | 8-12 | Medium | G2, social media |
| Rapid growth creating urgency | 10-15 | Medium | Hiring pace, funding, news |
| No urgency signals detected | 0-5 | Low | Insufficient data |

### BANT Score Calculation

```
BANT Score = Budget + Authority + Need + Timeline
Range: 0-100
```

---

## Phase 3: MEDDIC Framework Assessment

Assess each MEDDIC element with at least one research step:

- **Metrics:** What business metrics does this prospect care about? What would success look like?
- **Economic Buyer:** Who holds the purse strings and gives final approval?
- **Decision Criteria:** What factors will they use to evaluate solutions?
- **Decision Process:** How does this company buy software/services?
- **Identify Pain:** What specific pain points does this prospect experience?
- **Champion:** Who could be our internal advocate?

**MEDDIC Completeness Score:**
```
MEDDIC Completeness = (Elements with Medium+ Confidence / 6) * 100
```

| Completeness | Interpretation |
|-------------|---------------|
| 80-100% | Excellent qualification data. Well-positioned for engagement. |
| 60-79% | Good data. Some gaps to fill during discovery calls. |
| 40-59% | Moderate data. Need discovery call to fill gaps before advancing. |
| 20-39% | Limited data. Early stage research. More intelligence needed. |
| 0-19% | Insufficient data. May need different research approach or sources. |

---

## Phase 4: Synthesis and Scoring

### Opportunity Quality Score (0-100)

```
Opportunity Quality Score = (
    BANT_Score * 0.50 +
    MEDDIC_Completeness * 0.30 +
    Urgency_Modifier * 0.20
)
```

**Urgency Modifier (0-100):**
- 80-100: Active buying process or major trigger event in last 30 days
- 60-79: Recent trigger event (last 90 days) or strong urgency signals
- 40-59: Moderate urgency (industry trends, gradual pain escalation)
- 20-39: Low urgency (nice-to-have, future planning)
- 0-19: No urgency detected

### Lead Grade Assignment

| Grade | Score Range | Label | Recommended Action |
|-------|-----------|-------|-------------------|
| **A** | 75-100 | Sales Qualified Lead | Assign to senior rep. Initiate personalized outreach immediately. |
| **B** | 50-74 | Marketing Qualified Lead | Begin standard outreach sequence. Schedule discovery call. |
| **C** | 25-49 | Information Qualified Lead | Add to long-term nurture. Monitor for trigger events. |
| **D** | 0-24 | Unqualified | Do not pursue actively. Add to awareness campaigns only. |

---

## Output Format: LEAD-QUALIFICATION.md

```markdown
# Lead Qualification: [Company Name]
**URL:** [url]
**Date:** [current date]
**Opportunity Quality Score: [X]/100**
**Lead Grade: [A/B/C/D] — [Label]**
**BANT Score: [X]/100 | MEDDIC Completeness: [X]%**

---

## Qualification Snapshot

| Metric | Value |
|--------|-------|
| **Company** | [name] |
| **Industry** | [vertical] |
| **Employees** | [count] |
| **BANT Score** | [X]/100 |
| **MEDDIC Completeness** | [X]% |
| **Opportunity Quality Score** | [X]/100 |
| **Lead Grade** | [letter] — [label] |
| **Urgency Level** | [High/Medium/Low/None] |
| **Recommended Action** | [one-line recommendation] |

---

## BANT Scorecard

| Dimension | Score | Key Evidence | Confidence |
|-----------|-------|-------------|------------|
| **Budget** | [X]/25 | [most compelling evidence] | [High/Medium/Low] |
| **Authority** | [X]/25 | [most compelling evidence] | [High/Medium/Low] |
| **Need** | [X]/25 | [most compelling evidence] | [High/Medium/Low] |
| **Timeline** | [X]/25 | [most compelling evidence] | [High/Medium/Low] |
| **TOTAL** | **[X]/100** | | |

### Budget Analysis
[Detailed findings with all signals detected, evidence, and sources.]

### Authority Analysis
[Identified decision makers with titles. Org structure assessment. Buying process estimation.]

### Need Analysis
[Specific pain points detected with evidence. Problem awareness level.]

### Timeline Analysis
[Trigger events, urgency signals, buying cycle estimation, seasonal factors.]

---

## MEDDIC Assessment

| Element | Finding | Evidence | Confidence |
|---------|---------|----------|------------|
| **Metrics** | [what they measure] | [source] | [level] |
| **Economic Buyer** | [name, title] | [source] | [level] |
| **Decision Criteria** | [key criteria] | [source] | [level] |
| **Decision Process** | [how they buy] | [source] | [level] |
| **Identify Pain** | [specific pain] | [source] | [level] |
| **Champion** | [potential champion] | [source] | [level] |

---

## Opportunity Quality Score: [X]/100

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| BANT Score | [X]/100 | 50% | [X] |
| MEDDIC Completeness | [X]/100 | 30% | [X] |
| Urgency Modifier | [X]/100 | 20% | [X] |
| **TOTAL** | | **100%** | **[X]/100** |

---

## Recommended Approach

**Lead Grade:** [letter] — [label]

**Strategy:** [2-3 paragraph recommendation on how to approach this prospect.]

## Next Steps

1. [Most important next action with specifics]
2. [Second priority action]
3. [Third priority action]
4. [Fourth priority action]
5. [Fifth priority action]

---

*Generated by AI Sales Team — `/sales qualify`*
```

---

## Terminal Output

```
=== LEAD QUALIFICATION COMPLETE ===

Company:  [name]
Industry: [vertical]

BANT Score: [X]/100
  Budget:    [XX]/25 ████████░░
  Authority: [XX]/25 ██████░░░░
  Need:      [XX]/25 ███████░░░
  Timeline:  [XX]/25 █████░░░░░

MEDDIC Completeness: [X]%
Opportunity Quality Score: [X]/100
Lead Grade: [letter] — [label]

Recommended Action: [one-line recommendation]

Full report saved to: LEAD-QUALIFICATION.md
```

---

## Cross-Skill Integration

- If `COMPANY-RESEARCH.md` exists, use it to pre-populate company data and skip redundant research
- If `DECISION-MAKERS.md` exists, use it for Authority and Champion analysis
- Suggest follow-up: `/sales contacts` for decision maker deep dive, `/sales outreach` for engagement sequence
