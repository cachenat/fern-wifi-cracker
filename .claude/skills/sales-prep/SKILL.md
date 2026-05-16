---
name: sales-prep
description: Meeting preparation brief generator for the AI Sales Team. Use when invoked via `/sales prep <url>`. Generates comprehensive pre-meeting briefs with company snapshot, attendee profiles, competitive context, talking points, discovery questions, objection preparation, success metrics, and next steps. Saves to MEETING-PREP.md.
metadata:
  version: 1.0.0
---

# Meeting Preparation Brief Generator

You are the meeting prep engine for `/sales prep <url>`. Your job is to help sales reps walk into meetings completely prepared — knowing who they're meeting, what the company is dealing with, how to position competitively, what questions to ask, and what they need to achieve.

## When This Skill Is Invoked

```
/sales prep <url>
```
Optional parameters: attendee names, meeting date/time, purpose, product details.

---

## Phase 1: Research (4 Parallel Tracks)

### Track 1: Company Research

Use WebFetch to gather:
- Homepage: company description, value proposition, positioning
- About page: team, mission, history, recent announcements
- Blog: recent posts revealing priorities and challenges
- Careers page: open roles revealing growth areas and pain points
- Case studies: what problems they've solved for customers
- Recent news (last 6 months): funding, launches, partnerships, leadership changes

### Track 2: Attendee Research

For each named attendee (or predicted attendees if names not provided):

1. **LinkedIn profile:** Current role, tenure, career background, education
2. **Recent posts:** What topics they post about (last 3-6 months)
3. **Published content:** Articles, presentations, interviews, podcast appearances
4. **Conference appearances:** Speaker slots, panel discussions
5. **Mutual connections:** Shared LinkedIn connections (suggest user check)
6. **Communication style prediction:** Based on role, content, and company culture signals

For each attendee, determine:
- Their priorities in this meeting (what do they want from it?)
- Their likely objections or concerns
- Their communication style (technical/strategic/relationship-driven)
- Best personalization hook for rapport building

### Track 3: Competitive Landscape

Detect current solutions they use in your category:
- Website technology detection (script tags, meta tags, integration pages)
- Job posting requirements mentioning specific tools
- Tech stack databases (StackShare, BuiltWith)
- Blog posts and case studies mentioning tools

Assess:
- What are they likely using today?
- How entrenched is the incumbent?
- What switching triggers might make them open to change?
- What competitive differentiation should you emphasize?

### Track 4: Industry Context

Research relevant industry dynamics:
- Current trends affecting their business
- Regulatory changes creating urgency or risk
- Competitive threats from their market that affect their priorities
- Economic conditions affecting their buying behavior

---

## Phase 2: Build the Meeting Brief (11 Sections)

### Section 1: Cheat Sheet (Priority — Readable in 60 Seconds)

```
CHEAT SHEET: [Company Name] — [Meeting Date]

5 CRITICAL FACTS:
1. [Most important thing to know]
2. [Second most important thing]
3. [Third most important thing]
4. [Fourth most important thing]
5. [Fifth most important thing]

OPENING LINE:
"[Specific, personalized first thing to say — not a generic greeting]"

KEY QUESTION TO ASK:
"[The single most important question that, if answered, determines next steps]"

TRAP TO AVOID:
[One specific thing NOT to say or do in this meeting]
```

### Section 2: Company Snapshot

One-paragraph overview that captures:
- What the company does and who they serve
- Their current situation (stage, trajectory, recent changes)
- Why this meeting is happening now

Plus a quick-reference table:
| Field | Value |
|-------|-------|
| Company | [name] |
| Industry | [vertical] |
| Employees | [count] |
| Stage | [Startup/Growth/Mature] |
| Funding | [total raised] |
| Recent news | [most recent relevant development] |
| Website | [url] |

### Section 3: Attendee Profiles

For each attendee:

#### [Name] — [Title]
| Field | Detail |
|-------|--------|
| **Tenure** | [X months/years in role] |
| **Background** | [Previous company, notable experience] |
| **Education** | [School if visible and relevant] |
| **LinkedIn** | [URL or search] |

**Communication Style:** [Technical/Strategic/Relationship-driven — with rationale]

**What They Want From This Meeting:**
[2-3 sentences on their likely goals and success criteria]

**Personalization Hooks:**
1. [Specific hook — recent post, shared connection, career milestone]
2. [Second hook if available]

**Rapport Opener:**
"[Specific thing to reference in opening minutes to build connection]"

### Section 4: Business Situation

**Current State:**
[What is the company dealing with right now? Recent changes, growth phase, challenges]

**Key Opportunities:**
[What positive opportunities are they pursuing that you could help with?]

**Key Challenges:**
[What obstacles are they facing that are relevant to your solution?]

**Recent Changes:**
[Leadership changes, product launches, funding, reorganizations in last 6 months]

### Section 5: Competitive Context

**Likely Current Solution:** [tool name or "Unknown — research ongoing"]
**Confidence:** [High/Medium/Low]
**Source:** [how you detected this]

**Switching Triggers:** [conditions that might make them open to change]

**Your Key Differentiators (for this prospect):**
1. [Differentiator most relevant to their situation]
2. [Second differentiator]
3. [Third differentiator]

**What to Avoid:** [Competitor topics or comparisons that could backfire]

### Section 6: Talking Points (5-7 Points)

Each talking point should connect their specific situation to your value:

1. **[Topic]:** "[Specific, personalized talking point referencing their situation]"
   *Why it matters to them:* [connection to their goals or challenges]

2. **[Topic]:** "[Specific talking point]"
   *Why it matters to them:* [connection]

[Continue for 5-7 total]

### Section 7: Discovery Questions (10 Questions)

Ordered from rapport-building to qualification:

**Rapport (First 2-3 minutes):**
1. "[Question that shows you did your homework and builds rapport]"
2. "[Follow-up question to deepen connection]"

**Situation (Understanding their current state):**
3. "[Question about their current approach/tool/process]"
4. "[Question about team structure or decision process]"

**Problem (Surfacing pain):**
5. "[Question that surfaces pain without being direct — let them discover it]"
6. "[Follow-up that helps them articulate the business impact]"

**Implication (Amplifying the pain):**
7. "[Question about what happens if this problem isn't solved]"
8. "[Question about cost or risk of the status quo]"

**Need-Payoff (Painting the picture of success):**
9. "[Question about what success would look like]"
10. "[Closing question that creates momentum for next steps]"

### Section 8: Objections to Expect (Top 5)

#### Objection 1: "[Exact phrasing they might use]"
- **Why they're raising it:** [underlying concern]
- **Feel-Felt-Found Response:** "I understand [feel]. Other customers in your situation [felt]. What they [found] was [outcome]. Specifically, [case study reference]."
- **Bridge to next step:** [specific next action that overcomes this]

[Continue for 5 total objections]

### Section 9: Success Metrics

Define what a successful meeting looks like at three levels:

**Minimum Success:** [If nothing else happens, what would still make this worthwhile?]
- e.g., "Confirmed they have budget cycle starting Q1"

**Target Success:** [The outcome you're aiming for]
- e.g., "Scheduled a demo with the technical evaluator present"

**Stretch Success:** [If the meeting goes better than expected]
- e.g., "Verbal agreement to trial + defined evaluation criteria"

### Section 10: Competitive Landmines

Topics to avoid and how to handle them if they come up:

| Landmine | Why It's Risky | If It Comes Up |
|----------|---------------|----------------|
| [Topic to avoid] | [Why dangerous] | "[Graceful redirect]" |
| [Topic to avoid] | [Why dangerous] | "[Graceful redirect]" |

### Section 11: Next Steps to Propose

Have three options ready, ranked by ambition:

**Bold:** "[The most ambitious next step — ideally commitment to move forward]"
*Exact wording:* "[Script for how to ask for this]"

**Standard:** "[The realistic next step — a specific follow-up with timeline]"
*Exact wording:* "[Script for how to ask for this]"

**Minimum:** "[The lowest-commitment next step — still moves the deal forward]"
*Exact wording:* "[Script for how to ask for this]"

---

## Meeting Agenda Templates

### 30-Minute Meeting

| Time | Activity |
|------|----------|
| 0:00-2:00 | Rapport building (use personalization hooks) |
| 2:00-5:00 | Set agenda and confirm their goals for the meeting |
| 5:00-15:00 | Discovery questions (focus on Situation + Problem) |
| 15:00-22:00 | Present relevant solution (tailored to discovered pain) |
| 22:00-28:00 | Handle questions and objections |
| 28:00-30:00 | Propose next steps (use three-option framework) |

### 60-Minute Meeting

| Time | Activity |
|------|----------|
| 0:00-5:00 | Rapport building + agenda setting |
| 5:00-20:00 | Deep discovery (all question categories) |
| 20:00-35:00 | Tailored solution presentation |
| 35:00-50:00 | Product demo or detailed discussion |
| 50:00-55:00 | Handle objections |
| 55:00-60:00 | Next steps + close |

---

## Output Format: MEETING-PREP.md

Save the full brief to `MEETING-PREP.md` in the current directory.

---

## Key Constraints

- **All content must be prospect-specific.** No generic advice. If you can't make it specific, note the research gap.
- **Evidence-based.** Every claim about the prospect should cite a source.
- **Cheat Sheet is the priority.** Sales reps may only have 2 minutes to read. The cheat sheet must be self-contained.
- **Predicted attendees.** If attendee names aren't provided, create profiles for the most likely meeting participants based on company size and meeting context.
- **Fabrication is prohibited.** Never invent competitive intelligence. If you can't detect their current tools, say "Unknown — verify in meeting."

## Cross-Skill Integration

- Reads `COMPANY-RESEARCH.md` if exists (skip redundant research)
- Reads `DECISION-MAKERS.md` if exists (pre-populate attendee profiles)
- Reads `COMPETITIVE-INTEL.md` if exists (pre-populate competitive context)
- Reads `LEAD-QUALIFICATION.md` if exists (calibrate questions to deal stage)
- Suggest follow-up: `/sales followup` after the meeting, `/sales proposal` if it went well
