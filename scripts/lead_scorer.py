#!/usr/bin/env python3
"""
Lead Scorer — BANT + MEDDIC qualification scoring system.
Usage: python3 lead_scorer.py <input.json>
       echo '{"signals": {...}}' | python3 lead_scorer.py
"""

import json
import sys


def score_budget(signals):
    """Score budget signals 0-25."""
    score = 0
    budget = signals.get("budget", {})
    company = signals.get("company", {})

    funding = budget.get("funding_amount_usd", 0)
    if funding >= 50_000_000:
        score += 15
    elif funding >= 10_000_000:
        score += 10
    elif funding >= 1_000_000:
        score += 6
    elif funding > 0:
        score += 3

    revenue = budget.get("annual_revenue_usd", 0)
    if revenue >= 10_000_000:
        score += 6
    elif revenue >= 1_000_000:
        score += 3

    employees = company.get("employee_count", 0)
    if employees >= 500:
        score += 4
    elif employees >= 100:
        score += 3
    elif employees >= 20:
        score += 2

    if budget.get("budget_confirmed"):
        score += 4
    if budget.get("has_budget_cycle"):
        score += 2

    return min(score, 25)


def score_authority(signals):
    """Score authority/decision-maker access 0-25."""
    score = 0
    contacts = signals.get("contacts", {})
    org = signals.get("org", {})

    if contacts.get("economic_buyer_identified"):
        score += 10
    if contacts.get("champion_identified"):
        score += 7
    if contacts.get("technical_evaluator_identified"):
        score += 3

    seniority = contacts.get("highest_seniority", "")
    if seniority in ("c-suite", "founder", "owner"):
        score += 5
    elif seniority in ("vp", "director"):
        score += 3
    elif seniority == "manager":
        score += 1

    if contacts.get("direct_email_found"):
        score += 3
    if contacts.get("linkedin_found"):
        score += 2
    if org.get("single_decision_maker"):
        score += 2

    return min(score, 25)


def score_need(signals):
    """Score need/pain severity 0-25."""
    score = 0
    pain = signals.get("pain", {})
    engagement = signals.get("engagement", {})

    pain_count = pain.get("pain_points_identified", 0)
    if pain_count >= 4:
        score += 8
    elif pain_count >= 2:
        score += 5
    elif pain_count >= 1:
        score += 2

    severity = pain.get("severity", "low")
    if severity == "critical":
        score += 8
    elif severity == "high":
        score += 5
    elif severity == "medium":
        score += 2

    if pain.get("quantified_pain"):
        score += 5
    if engagement.get("inbound_inquiry"):
        score += 4
    if engagement.get("multiple_stakeholders_engaged"):
        score += 3
    if pain.get("active_search_for_solution"):
        score += 4

    return min(score, 25)


def score_timeline(signals):
    """Score timeline/urgency 0-25."""
    score = 0
    timeline = signals.get("timeline", {})
    triggers = signals.get("triggers", {})

    decision_weeks = timeline.get("decision_weeks", 999)
    if decision_weeks <= 4:
        score += 12
    elif decision_weeks <= 12:
        score += 8
    elif decision_weeks <= 26:
        score += 4
    elif decision_weeks <= 52:
        score += 2

    if triggers.get("contract_renewal_upcoming"):
        score += 5
    if triggers.get("new_executive_hire"):
        score += 4
    if triggers.get("recent_funding"):
        score += 4
    if triggers.get("regulatory_deadline"):
        score += 5
    if triggers.get("competitor_threat"):
        score += 3

    if timeline.get("evaluation_started"):
        score += 4

    return min(score, 25)


def assess_meddic(signals):
    """Assess MEDDIC completeness (0-100% per dimension)."""
    meddic = {}

    pain = signals.get("pain", {})
    metrics = pain.get("quantified_pain", False)
    meddic["Metrics"] = 100 if metrics else (50 if pain.get("pain_points_identified", 0) > 0 else 0)

    contacts = signals.get("contacts", {})
    if contacts.get("economic_buyer_identified") and contacts.get("direct_email_found"):
        meddic["Economic Buyer"] = 100
    elif contacts.get("economic_buyer_identified"):
        meddic["Economic Buyer"] = 60
    else:
        meddic["Economic Buyer"] = 0

    sales = signals.get("sales_process", {})
    if sales.get("decision_criteria_confirmed"):
        meddic["Decision Criteria"] = 100
    elif sales.get("evaluation_criteria_known"):
        meddic["Decision Criteria"] = 50
    else:
        meddic["Decision Criteria"] = 20

    if sales.get("decision_process_mapped"):
        meddic["Decision Process"] = 100
    elif sales.get("stakeholders_known"):
        meddic["Decision Process"] = 60
    else:
        meddic["Decision Process"] = 20

    pain_count = pain.get("pain_points_identified", 0)
    severity = pain.get("severity", "low")
    if pain_count >= 2 and severity in ("high", "critical"):
        meddic["Identify Pain"] = 100
    elif pain_count >= 1:
        meddic["Identify Pain"] = 60
    else:
        meddic["Identify Pain"] = 10

    if contacts.get("champion_identified") and contacts.get("champion_active"):
        meddic["Champion"] = 100
    elif contacts.get("champion_identified"):
        meddic["Champion"] = 60
    else:
        meddic["Champion"] = 10

    return meddic


def compute_grade(bant_score):
    if bant_score >= 75:
        return "A"
    elif bant_score >= 50:
        return "B"
    elif bant_score >= 25:
        return "C"
    else:
        return "D"


def compute_confidence(signals):
    total_fields = 0
    filled_fields = 0

    def count_fields(d):
        nonlocal total_fields, filled_fields
        for v in d.values():
            if isinstance(v, dict):
                count_fields(v)
            else:
                total_fields += 1
                if v not in (None, "", 0, False, [], {}):
                    filled_fields += 1

    count_fields(signals)
    if total_fields == 0:
        return "low"
    ratio = filled_fields / total_fields
    if ratio >= 0.7:
        return "high"
    elif ratio >= 0.4:
        return "medium"
    else:
        return "low"


def recommend_action(grade, meddic):
    weakest = min(meddic, key=meddic.get)
    weakest_score = meddic[weakest]

    if grade == "A":
        if weakest_score < 50:
            return f"High priority — schedule discovery call. Strengthen {weakest} data."
        return "Hot lead — schedule discovery call immediately."
    elif grade == "B":
        return f"Good fit — nurture and qualify further. Focus on improving {weakest}."
    elif grade == "C":
        return f"Weak fit — needs research. Address gaps in {weakest} before prioritizing."
    else:
        return "Low priority — add to long-term nurture list."


def score_lead(data):
    signals = data.get("signals", data)

    budget_score = score_budget(signals)
    authority_score = score_authority(signals)
    need_score = score_need(signals)
    timeline_score = score_timeline(signals)

    bant_score = budget_score + authority_score + need_score + timeline_score

    meddic = assess_meddic(signals)
    meddic_avg = sum(meddic.values()) / len(meddic)

    grade = compute_grade(bant_score)
    confidence = compute_confidence(signals)
    recommendation = recommend_action(grade, meddic)

    return {
        "bant_score": bant_score,
        "grade": grade,
        "confidence": confidence,
        "breakdown": {
            "budget": budget_score,
            "authority": authority_score,
            "need": need_score,
            "timeline": timeline_score,
        },
        "meddic": meddic,
        "meddic_completeness_pct": round(meddic_avg, 1),
        "recommendation": recommendation,
    }


def main():
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1]) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

    result = score_lead(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
