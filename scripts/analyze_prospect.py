#!/usr/bin/env python3
"""
Prospect Analyzer — extracts structured business intelligence from company websites.
Usage: python3 analyze_prospect.py --url https://example.com [--output json]
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

SUBPAGES = [
    "/about", "/team", "/pricing", "/careers", "/blog",
    "/contact", "/about-us", "/our-team", "/leadership", "/jobs",
]

TECH_SIGNATURES = {
    "WordPress": ["wp-content", "wp-includes", "wordpress"],
    "React": ["react.js", "react.min.js", "_next/", "__next"],
    "Next.js": ["_next/static", "__NEXT_DATA__"],
    "Vue.js": ["vue.js", "vue.min.js", "vuejs"],
    "Angular": ["angular.js", "ng-version"],
    "Shopify": ["cdn.shopify.com", "Shopify.theme"],
    "Stripe": ["stripe.com/v3", "stripe.js"],
    "Intercom": ["intercomSettings", "intercom.io"],
    "HubSpot": ["hs-scripts", "hubspot.com"],
    "Salesforce": ["salesforce.com", "force.com"],
    "Segment": ["analytics.js", "segment.com"],
    "Google Analytics": ["gtag(", "ga(", "google-analytics.com"],
    "Zendesk": ["zendesk.com", "zopim"],
    "Marketo": ["marketo.com", "munchkin"],
    "Drift": ["drift.com", "driftt.com"],
    "Wistia": ["wistia.com", "wistia.net"],
    "AWS": ["amazonaws.com", "aws-"],
    "Cloudflare": ["cloudflare.com", "cfcdn"],
    "Heroku": ["herokussl.com", "herokuapp.com"],
    "Gatsby": ["gatsby-", "__gatsby"],
}

INDUSTRY_KEYWORDS = {
    "SaaS": ["software", "platform", "saas", "cloud", "subscription", "api"],
    "E-commerce": ["shop", "store", "buy", "cart", "checkout", "product"],
    "FinTech": ["finance", "payment", "banking", "fintech", "investment", "trading"],
    "HealthTech": ["health", "medical", "healthcare", "clinical", "patient", "hipaa"],
    "EdTech": ["education", "learning", "course", "training", "edtech", "school"],
    "MarTech": ["marketing", "advertising", "martech", "campaign", "analytics"],
    "DevTools": ["developer", "devtools", "api", "sdk", "open source", "github"],
    "HR Tech": ["hr", "recruiting", "talent", "hiring", "workforce", "employee"],
    "Legal Tech": ["legal", "law", "compliance", "contract", "attorney"],
    "Real Estate": ["real estate", "property", "mortgage", "realty", "housing"],
}

SOCIAL_PATTERNS = {
    "linkedin": r"linkedin\.com/(?:company|in)/([a-zA-Z0-9\-_]+)",
    "twitter": r"twitter\.com/([a-zA-Z0-9_]+)",
    "github": r"github\.com/([a-zA-Z0-9\-_]+)",
    "facebook": r"facebook\.com/([a-zA-Z0-9\-_.]+)",
    "youtube": r"youtube\.com/(?:c/|channel/|user/)?([a-zA-Z0-9\-_]+)",
}

EMPLOYEE_SIGNALS = {
    (1, 10): ["small team", "founding team", "we're a team of"],
    (11, 50): ["growing team", "startup", "series a"],
    (51, 200): ["mid-size", "series b", "growing company"],
    (201, 1000): ["enterprise", "series c", "series d", "scale"],
    (1001, 10000): ["large company", "publicly traded", "fortune 500"],
}


class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.text_blocks = []
        self.links = []
        self.scripts = []
        self.meta = {}
        self.json_ld = []
        self._current_tag = None
        self._in_script = False
        self._script_type = ""
        self._script_content = []
        self._in_title = False
        self._text_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self._current_tag = tag

        if tag == "title":
            self._in_title = True

        elif tag == "meta":
            name = attrs_dict.get("name", attrs_dict.get("property", ""))
            content = attrs_dict.get("content", "")
            if name and content:
                self.meta[name.lower()] = content
            if name.lower() == "description":
                self.description = content

        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                self.links.append(href)

        elif tag == "script":
            self._in_script = True
            self._script_type = attrs_dict.get("type", "")
            src = attrs_dict.get("src", "")
            if src:
                self.scripts.append(src)
            self._script_content = []

        elif tag == "img":
            alt = attrs_dict.get("alt", "")
            if alt:
                self._text_buffer.append(alt)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            self._in_script = False
            content = "".join(self._script_content)
            if self._script_type == "application/ld+json":
                try:
                    self.json_ld.append(json.loads(content))
                except json.JSONDecodeError:
                    pass
            self.scripts.append(content[:500])
            self._script_content = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_script:
            self._script_content.append(data)
        else:
            text = data.strip()
            if text and len(text) > 10:
                self._text_buffer.append(text)
                if len(self._text_buffer) >= 20:
                    self.text_blocks.append(" ".join(self._text_buffer))
                    self._text_buffer = []

    def finalize(self):
        if self._text_buffer:
            self.text_blocks.append(" ".join(self._text_buffer))


def fetch_page(url, timeout=10):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; SalesIntel/1.0)",
                "Accept": "text/html,application/xhtml+xml,*/*",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/" not in content_type:
                return None
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def detect_tech_stack(html_sources):
    detected = []
    combined = " ".join(html_sources).lower()
    for tech, signals in TECH_SIGNATURES.items():
        for signal in signals:
            if signal.lower() in combined:
                detected.append(tech)
                break
    return list(set(detected))


def detect_industry(text):
    text_lower = text.lower()
    scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[industry] = score
    if not scores:
        return "Unknown"
    return max(scores, key=scores.get)


def extract_social_links(html_sources):
    combined = " ".join(html_sources)
    socials = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = re.findall(pattern, combined)
        if matches:
            socials[platform] = matches[0]
    return socials


def extract_emails(text):
    pattern = r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
    emails = re.findall(pattern, text)
    filtered = [e for e in emails if not any(x in e.lower() for x in ["example", "test", "noreply", "no-reply"])]
    return list(set(filtered))[:5]


def extract_phones(text):
    pattern = r"(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    return list(set(re.findall(pattern, text)))[:3]


def extract_team_members(parser, page_text):
    members = []
    title_patterns = [
        r"([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*[,\-–]\s*((?:CEO|CTO|CFO|COO|VP|Director|Head|Manager|Engineer|Designer|Founder|President)[^,\n]{0,40})",
    ]
    for pattern in title_patterns:
        matches = re.findall(pattern, page_text)
        for name, title in matches:
            if len(name.split()) >= 2:
                members.append({"name": name.strip(), "title": title.strip()})

    for ld in parser.json_ld:
        if isinstance(ld, dict):
            items = [ld] if ld.get("@type") == "Person" else ld.get("employee", [])
            for person in items if isinstance(items, list) else [items]:
                if isinstance(person, dict) and person.get("name"):
                    members.append({
                        "name": person["name"],
                        "title": person.get("jobTitle", ""),
                    })

    seen = set()
    unique = []
    for m in members:
        if m["name"] not in seen:
            seen.add(m["name"])
            unique.append(m)
    return unique[:10]


def extract_pricing_tiers(text):
    tiers = []
    price_pattern = r"\$[\d,]+(?:\.\d{2})?(?:/(?:mo|month|yr|year|user))?"
    prices = re.findall(price_pattern, text)
    if prices:
        tiers = list(set(prices))[:5]
    tier_words = ["free", "starter", "basic", "pro", "professional", "enterprise", "business"]
    detected_tiers = [w for w in tier_words if w in text.lower()]
    return {"prices": tiers, "tier_names": detected_tiers}


def estimate_company_size(text, json_ld_data):
    text_lower = text.lower()

    for ld in json_ld_data:
        if isinstance(ld, dict):
            count = ld.get("numberOfEmployees")
            if count:
                return str(count)

    employee_pattern = r"(\d+)\+?\s*(?:employees|team members|people|staff)"
    matches = re.findall(employee_pattern, text_lower)
    if matches:
        return f"~{matches[0]} employees"

    for (low, high), signals in EMPLOYEE_SIGNALS.items():
        for signal in signals:
            if signal in text_lower:
                return f"{low}-{high} employees"

    return "Unknown"


def detect_hiring(links, text):
    hiring_signals = ["we're hiring", "join our team", "open positions", "job openings", "careers"]
    has_hiring_page = any("/careers" in l or "/jobs" in l for l in links)
    has_hiring_text = any(signal in text.lower() for signal in hiring_signals)
    return has_hiring_page or has_hiring_text


def extract_funding_signals(text):
    signals = []
    rounds = re.findall(r"(?:Series [A-F]|Seed|Pre-seed|IPO|raised \$[\d,.]+[MBK]?)", text, re.IGNORECASE)
    if rounds:
        signals.extend(list(set(rounds))[:3])
    return signals


def analyze_url(url):
    parsed = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    result = {
        "url": url,
        "base_url": base_url,
        "company_name": "",
        "description": "",
        "industry": "Unknown",
        "tech_stack": [],
        "team_members": [],
        "pricing": {},
        "emails": [],
        "phones": [],
        "social_links": {},
        "estimated_employees": "Unknown",
        "is_hiring": False,
        "funding_signals": [],
        "pages_analyzed": [],
        "errors": [],
    }

    all_html = []
    all_text = []

    # Fetch homepage
    homepage_html = fetch_page(url)
    if not homepage_html:
        homepage_html = fetch_page(base_url)

    if homepage_html:
        parser = TagCollector()
        parser.feed(homepage_html)
        parser.finalize()
        all_html.append(homepage_html)
        text = " ".join(parser.text_blocks)
        all_text.append(text)
        result["pages_analyzed"].append(url)
        result["company_name"] = parser.title.strip().split("|")[0].split("–")[0].strip()
        result["description"] = parser.description or (parser.meta.get("og:description", ""))

        if not result["description"] and parser.text_blocks:
            result["description"] = parser.text_blocks[0][:200]

        result["social_links"] = extract_social_links([homepage_html])
        result["team_members"] = extract_team_members(parser, text)
        result["funding_signals"] = extract_funding_signals(text)
        result["is_hiring"] = detect_hiring(parser.links, text)
    else:
        result["errors"].append(f"Failed to fetch homepage: {url}")

    # Fetch subpages
    for subpage in SUBPAGES[:6]:
        subpage_url = base_url + subpage
        html = fetch_page(subpage_url)
        if html:
            result["pages_analyzed"].append(subpage_url)
            all_html.append(html)
            sub_parser = TagCollector()
            sub_parser.feed(html)
            sub_parser.finalize()
            sub_text = " ".join(sub_parser.text_blocks)
            all_text.append(sub_text)

            new_members = extract_team_members(sub_parser, sub_text)
            existing_names = {m["name"] for m in result["team_members"]}
            for m in new_members:
                if m["name"] not in existing_names:
                    result["team_members"].append(m)
                    existing_names.add(m["name"])

    combined_text = " ".join(all_text)

    result["tech_stack"] = detect_tech_stack(all_html)
    result["industry"] = detect_industry(combined_text)
    result["emails"] = extract_emails(combined_text)
    result["phones"] = extract_phones(combined_text)
    result["pricing"] = extract_pricing_tiers(combined_text)
    result["estimated_employees"] = estimate_company_size(combined_text, [])

    if not result["is_hiring"]:
        result["is_hiring"] = detect_hiring([], combined_text)

    return result


def main():
    parser = argparse.ArgumentParser(description="Analyze a company website for sales intelligence")
    parser.add_argument("--url", required=True, help="Company website URL")
    parser.add_argument("--output", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()

    url = args.url
    if not url.startswith("http"):
        url = "https://" + url

    result = analyze_url(url)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Company: {result['company_name']}")
        print(f"URL: {result['url']}")
        print(f"Industry: {result['industry']}")
        print(f"Description: {result['description'][:200]}")
        print(f"Employees: {result['estimated_employees']}")
        print(f"Tech Stack: {', '.join(result['tech_stack'])}")
        print(f"Team Members: {len(result['team_members'])}")
        print(f"Hiring: {result['is_hiring']}")
        print(f"Funding: {', '.join(result['funding_signals'])}")
        print(f"Social: {result['social_links']}")


if __name__ == "__main__":
    main()
