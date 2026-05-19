---
name: sales-research
description: Company research engine for the AI Sales Team. Use when invoked via `/sales research <url>`. Produces deep, structured intelligence on prospect companies across 8 research dimensions including company overview, business model, product/technology, leadership, funding, market position, culture, and recent developments. Saves full report to COMPANY-RESEARCH.md with a Company Fit Score (0-100).
metadata:
  version: 1.0.0
---

# Company Research & Firmographic Analysis

You are the company research engine for `/sales research <url>`. This system produces deep, structured intelligence on prospect companies across 8 research dimensions.

## When This Skill Is Invoked

- **Standalone:** User runs `/sales research <url>` for full research procedure outputting COMPANY-RESEARCH.md
- **As subagent:** Sales-prospect orchestrator launches this as sales-company subagent, receiving discovery briefing with pre-fetched content to skip redundant fetches, returning Company Fit Score (0-100) with structured data

---

## Phase 1: Website Analysis (Primary Source)

### 1.1 Fetch and Analyze Key Pages

Use `WebFetch` to retrieve these pages (skip any already provided):

| Page | Common URLs | Priority Data |
|------|-------------|--------------|
| **Homepage** | / | Company name, tagline, value proposition, product positioning, social proof |
| **About** | /about, /company, /about-us, /our-story | Founding story, mission, vision, values, team size, locations, history |
| **Team** | /team, /leadership, /about/team, /people | Executive names, titles, backgrounds, advisory board |
| **Pricing** | /pricing, /plans, /packages | Revenue model, price points, tier structure, enterprise tier |
| **Blog** | /blog, /resources, /insights | Content themes, posting frequency, thought leadership quality |
| **Careers** | /careers, /jobs, /join-us, /open-positions | Open roles, team sizes, growth rate, culture signals, tech stack |
| **Customers** | /customers, /case-studies | Customer logos, industries served, company sizes served |
| **Press** | /press, /news, /newsroom | Recent announcements, media coverage, partnerships |
| **Legal** | /privacy, /terms | Legal entity name, jurisdiction, compliance standards |

### 1.2 Technology Stack Detection

Identify technologies from these signals:

| Signal Source | What to Look For |
|---------------|-----------------|
| **Job postings** | Required skills and tools |
| **Website source** | Meta tags, script includes, framework signatures |
| **Integration pages** | Listed integrations and partners |
| **Developer docs** | API technology, SDKs offered |
| **Blog posts** | Technical blog content |

---

## Phase 2: Web Research (Secondary Sources)

### 2.1 Search-Based Research

Execute these searches:

```
Search 1: "[company name] company overview"
Search 2: "[company name] funding round"
Search 3: "[company name] revenue employees"
Search 4: "[company name] CEO founder"
Search 5: "[company name] news recent"
Search 6: "[company name] reviews Glassdoor"
Search 7: "[company name] competitors market"
```

### 2.2 Source Priority Hierarchy

1. Company website (highest authority for self-reported data)
2. SEC filings / public financial records
3. Crunchbase / PitchBook (funding, valuation, investors)
4. LinkedIn (employee count, team composition, growth)
5. Press releases (announcements, partnerships, milestones)
6. News articles (industry context, analyst perspectives)
7. Review sites (G2, Capterra, Glassdoor — customer and employee sentiment)
8. Social media (real-time signals, company culture, executive presence)

### 2.3 Data Freshness Requirements

- **Employee count:** Must be within 6 months. Flag if older.
- **Funding data:** Must include most recent round. Flag if last round was 18+ months ago.
- **Revenue estimates:** Must note methodology and confidence level.
- **News:** Focus on last 6 months.

---

## Phase 3: The 8 Research Dimensions

### Dimension 1: Company Overview

| Field | Description |
|-------|-------------|
| Company Name | Legal name and DBA |
| Founded | Year of incorporation |
| Founders | Founding team members |
| Headquarters | Primary office location |
| Employee Count | Current headcount |
| Stage | Startup / Growth / Mature / Public |
| Mission | Company mission statement |
| Company Structure | Public, Private, Subsidiary, Non-profit |

### Dimension 2: Business Model & Revenue

| Field | Description |
|-------|-------------|
| Revenue Model | Subscription, transactional, marketplace, advertising, licensing |
| Pricing Tiers | Free, starter, pro, enterprise with prices |
| Revenue Estimate | ARR or annual revenue range |
| Customer Count | Total customers or users |

**Revenue estimation methodology:**
- Employee-based: Median SaaS revenue per employee is $200K-$300K
- Funding-based: Series A = $1-3M ARR, Series B = $5-15M, Series C = $15-50M
- Customer-based: Average tier price × estimated customer count (when visible)
Always state estimation method and confidence level.

### Dimension 3: Product & Technology

| Field | Description |
|-------|-------------|
| Core Products | Primary product offerings |
| Tech Stack | Programming languages, frameworks, infrastructure |
| Differentiators | Unique product capabilities |
| Integrations | Third-party connections |
| API / Platform | Developer platform maturity |

### Dimension 4: Leadership & Team

| Field | Description |
|-------|-------------|
| CEO / Founder | Name, background, tenure |
| CTO / Technical Lead | Name, background, technical vision |
| Key Executives | VP/C-suite with titles and tenures |
| Recent Changes | New hires, departures, promotions (last 6 months) |

### Dimension 5: Funding & Financial Health

| Field | Description |
|-------|-------------|
| Total Funding | Sum of all funding raised |
| Latest Round | Most recent round details |
| Key Investors | Lead investors and notable participants |
| Valuation | Last known valuation |
| Burn Rate Signals | Hiring pace vs funding age, layoffs |

### Dimension 6: Market Position

| Field | Description |
|-------|-------------|
| Market Category | Primary market category |
| Primary Competitors | Top 3-5 direct competitors |
| Competitive Advantages | Key differentiators vs competitors |
| Analyst Coverage | Industry analyst mentions |

### Dimension 7: Culture & Employer Brand

| Field | Description |
|-------|-------------|
| Company Values | Stated values and culture principles |
| Glassdoor Rating | Employee satisfaction score |
| Hiring Pace | Number of open positions, growth rate |
| Work Model | Remote, hybrid, in-office |

### Dimension 8: Recent Developments (Last 6 Months)

| Category | What to Look For |
|----------|-----------------|
| Product Launches | New products, features, updates |
| Partnerships | New integrations, channel partners |
| Funding Events | New rounds, secondary sales |
| Leadership Changes | New hires, departures, reorganizations |
| Market Moves | Expansion into new markets |
| Customer Wins | New enterprise customers, notable logos |

---

## Phase 4: Synthesis and Scoring

### Company Fit Score (0-100)

Calculate across 5 sub-dimensions (each 0-20):

**Size Fit (0-20):**
| Employee Range | Score |
|---------------|-------|
| 1-10 | 5-10 |
| 11-50 | 10-15 |
| 51-200 | 15-20 |
| 201-1000 | 12-18 |
| 1001-5000 | 8-15 |
| 5000+ | 5-12 |

**Industry Fit (0-20):** Score based on match to ICP (if defined) or general B2B SaaS criteria.

**Growth Trajectory (0-20):** Score based on hiring velocity, recent funding, product launches.

**Tech Sophistication (0-20):** Score based on modern stack, API-first culture, integration ecosystem.

**Budget Signals (0-20):** Score based on enterprise pricing, funding, hiring for tools.

---

## Output Format: COMPANY-RESEARCH.md

```markdown
# Company Research: [Company Name]
**URL:** [url]
**Date:** [current date]
**Company Type:** [type]
**Industry:** [vertical]
**Company Fit Score: [X]/100**

---

## Executive Summary

[2-3 paragraph summary covering who the company is, what they do,
their current trajectory, and why they are or are not a good fit.
Written for a sales rep who needs to get up to speed in 60 seconds.]

---

## Company Snapshot

| Field | Value |
|-------|-------|
| **Company Name** | [name] |
| **Founded** | [year] |
| **Founders** | [names] |
| **Headquarters** | [location] |
| **Employees** | [count] (source: [source]) |
| **Stage** | [Startup/Growth/Mature/Public] |
| **Total Funding** | [amount] |
| **Latest Round** | [round type, amount, date] |
| **Revenue Estimate** | [range] (confidence: [H/M/L]) |
| **Key Investors** | [names] |
| **Tech Stack** | [key technologies] |

---

## 1. Company Overview
[Full findings for Dimension 1]

## 2. Business Model & Revenue
[Full findings for Dimension 2, including pricing tier table]

## 3. Product & Technology
[Full findings for Dimension 3, including tech stack table]

## 4. Leadership & Team
[Full findings for Dimension 4, including key executive profiles]

## 5. Funding & Financial Health
[Full findings for Dimension 5, including round history table]

## 6. Market Position
[Full findings for Dimension 6, including competitor mentions]

## 7. Culture & Employer Brand
[Full findings for Dimension 7]

## 8. Recent Developments
[Full findings for Dimension 8, in reverse chronological order]

---

## Company Fit Score: [X]/100

| Sub-Dimension | Score | Evidence |
|--------------|-------|----------|
| Size Fit | [X]/20 | [key evidence] |
| Industry Fit | [X]/20 | [key evidence] |
| Growth Trajectory | [X]/20 | [key evidence] |
| Tech Sophistication | [X]/20 | [key evidence] |
| Budget Signals | [X]/20 | [key evidence] |
| **Total** | **[X]/100** | |

---

## Strengths
1. **[Strength]** — [Evidence]. *Sales implication: [how to use this]*
2. **[Strength]** — [Evidence]. *Sales implication: [how to use this]*
3. **[Strength]** — [Evidence]. *Sales implication: [how to use this]*

## Risks
1. **[Risk]** — [Evidence]. *Mitigation: [how to address this]*
2. **[Risk]** — [Evidence]. *Mitigation: [how to address this]*

## Key Insights for Sales
1. **[Insight]** — [Evidence]. *Action: [what to do with this]*
2. **[Insight]** — [Evidence]. *Action: [what to do with this]*
3. **[Insight]** — [Evidence]. *Action: [what to do with this]*

---

*Generated by AI Sales Team — `/sales research`*
```

---

## Terminal Output

```
=== COMPANY RESEARCH COMPLETE ===

Company: [name] ([type])
Industry: [vertical]
Stage: [Startup/Growth/Mature/Public]
Employees: [count]
Funding: [total]
Revenue Est.: [range]

Company Fit Score: [X]/100
  Size Fit:           [XX]/20 ████████░░
  Industry Fit:       [XX]/20 ██████░░░░
  Growth Trajectory:  [XX]/20 ███████░░░
  Tech Sophistication:[XX]/20 █████░░░░░
  Budget Signals:     [XX]/20 ████████░░

Full report saved to: COMPANY-RESEARCH.md
```

## Cross-Skill Integration

- If `PROSPECT-ANALYSIS.md` exists, reference overall prospect context
- If `DECISION-MAKERS.md` exists, cross-reference leadership findings
- Suggest follow-up: `/sales contacts` for decision maker deep dive, `/sales qualify` for opportunity assessment
