#!/usr/bin/env python3
"""
Contact Finder — extracts leadership and team member contacts from company websites.
Usage: python3 contact_finder.py --url https://example.com [--output json]
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

TEAM_PATHS = [
    "/about", "/team", "/leadership", "/our-team", "/people",
    "/about-us", "/company/team", "/company/leadership", "/staff",
]

SENIORITY_MAP = {
    "c-suite": ["ceo", "cto", "cfo", "coo", "cpo", "cmo", "cso", "chief", "founder", "co-founder", "president"],
    "vp": ["vp", "vice president"],
    "director": ["director", "head of", "head,"],
    "manager": ["manager", "lead ", "principal"],
    "ic": ["engineer", "designer", "developer", "analyst", "specialist", "associate"],
}

DEPARTMENT_MAP = {
    "Engineering": ["engineer", "developer", "cto", "technical", "software", "infrastructure", "devops"],
    "Sales": ["sales", "account executive", "ae ", "business development", "revenue", "cro"],
    "Marketing": ["marketing", "cmo", "growth", "brand", "content", "demand gen"],
    "Product": ["product", "cpo", "ux", "design", "research"],
    "Operations": ["operations", "coo", "ops", "strategy"],
    "Finance": ["finance", "cfo", "accounting", "financial"],
    "HR": ["hr", "human resources", "people", "recruiting", "talent"],
    "Legal": ["legal", "counsel", "compliance", "attorney"],
    "Customer Success": ["customer success", "cs ", "support", "account manager", "implementation"],
}

BUYING_ROLES = {
    "Economic Buyer": ["ceo", "cfo", "coo", "president", "founder", "co-founder", "owner", "partner"],
    "Champion": ["vp of sales", "vp sales", "head of sales", "director of sales", "cro", "revenue"],
    "Evaluator": ["cto", "vp engineering", "director of engineering", "architect", "technical"],
    "End User": ["manager", "analyst", "specialist", "coordinator", "associate"],
    "Blocker": ["legal", "compliance", "procurement", "ciso", "security"],
}


class TeamPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.json_ld = []
        self.text_blocks = []
        self._in_script = False
        self._script_type = ""
        self._script_buffer = []
        self._text_buffer = []
        self._current_tags = []

    def handle_starttag(self, tag, attrs):
        self._current_tags.append(tag)
        attrs_dict = dict(attrs)
        if tag == "script":
            self._in_script = True
            self._script_type = attrs_dict.get("type", "")
            self._script_buffer = []

    def handle_endtag(self, tag):
        if self._current_tags and self._current_tags[-1] == tag:
            self._current_tags.pop()
        if tag == "script":
            self._in_script = False
            content = "".join(self._script_buffer)
            if self._script_type == "application/ld+json":
                try:
                    self.json_ld.append(json.loads(content))
                except json.JSONDecodeError:
                    pass
            self._script_buffer = []

        if tag in ("div", "section", "article", "li", "p"):
            if self._text_buffer:
                block = " ".join(self._text_buffer).strip()
                if block:
                    self.text_blocks.append(block)
                self._text_buffer = []

    def handle_data(self, data):
        if self._in_script:
            self._script_buffer.append(data)
        else:
            text = data.strip()
            if text:
                self._text_buffer.append(text)


def fetch_page(url, timeout=10):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; SalesIntel/1.0)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace"), str(resp.url)
    except Exception:
        return None, None


def classify_seniority(title_lower):
    for level, keywords in SENIORITY_MAP.items():
        if any(kw in title_lower for kw in keywords):
            return level
    return "unknown"


def classify_department(title_lower):
    for dept, keywords in DEPARTMENT_MAP.items():
        if any(kw in title_lower for kw in keywords):
            return dept
    return "Unknown"


def classify_buying_role(title_lower):
    for role, keywords in BUYING_ROLES.items():
        if any(kw in title_lower for kw in keywords):
            return role
    return "End User"


SENIORITY_ORDER = {"c-suite": 0, "vp": 1, "director": 2, "manager": 3, "ic": 4, "unknown": 5}

NOISE_NAMES = {
    "contact us", "about us", "our team", "team member", "meet the team",
    "join us", "get started", "learn more", "read more", "sign up",
}


def is_valid_name(name):
    parts = name.strip().split()
    if len(parts) < 2:
        return False
    if name.lower() in NOISE_NAMES:
        return False
    if any(char.isdigit() for char in name):
        return False
    if len(name) > 60:
        return False
    return True


def extract_from_json_ld(json_ld_list):
    contacts = []
    for ld in json_ld_list:
        if not isinstance(ld, dict):
            continue
        schema_type = ld.get("@type", "")

        persons = []
        if schema_type == "Person":
            persons = [ld]
        elif schema_type in ("Organization", "LocalBusiness"):
            employees = ld.get("employee", ld.get("member", []))
            if isinstance(employees, list):
                persons = employees
            elif isinstance(employees, dict):
                persons = [employees]

        for person in persons:
            if not isinstance(person, dict):
                continue
            name = person.get("name", "")
            title = person.get("jobTitle", "")
            if name and is_valid_name(name):
                contacts.append({
                    "name": name,
                    "title": title,
                    "linkedin": person.get("url", person.get("sameAs", [""])[0] if isinstance(person.get("sameAs"), list) else person.get("sameAs", "")),
                    "source": "json-ld",
                })
    return contacts


def extract_from_card_patterns(text_blocks):
    contacts = []
    # Look for Name followed by title pattern within a short block
    name_title_re = re.compile(
        r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})\s*\n?\s*"
        r"((?:CEO|CTO|CFO|COO|CPO|CMO|VP|Vice President|Director|Head of|Manager|"
        r"Engineer|Designer|Founder|Co-Founder|President|Partner)[^,\n]{0,60})"
    )
    for block in text_blocks:
        m = name_title_re.search(block)
        if m:
            name = m.group(1).strip()
            title = m.group(2).strip()
            if is_valid_name(name):
                contacts.append({"name": name, "title": title, "source": "card-pattern"})

    return contacts


def extract_from_list_patterns(text_blocks):
    contacts = []
    combined = "\n".join(text_blocks)

    # Pattern: "First Last — Title" or "First Last, Title"
    patterns = [
        r"([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*[—–\-,]\s*((?:CEO|CTO|CFO|COO|VP|Director|Head|Manager|Engineer|Founder|President|Lead|Principal)[^,\n\|]{0,50})",
        r"([A-Z][a-z]+ [A-Z][a-z]+)\s*\|\s*((?:CEO|CTO|CFO|VP|Director|Head|Manager|Engineer|Founder)[^|\n]{0,50})",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, combined):
            name = match.group(1).strip()
            title = match.group(2).strip()
            if is_valid_name(name) and title:
                contacts.append({"name": name, "title": title, "source": "list-pattern"})

    return contacts


def extract_linkedin_urls(html):
    pattern = r"href=[\"'](https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+))[\"']"
    matches = re.findall(pattern, html)
    return {slug: url for url, slug in matches}


def enrich_contact(contact, linkedin_map=None):
    title_lower = contact.get("title", "").lower()
    contact["seniority"] = classify_seniority(title_lower)
    contact["department"] = classify_department(title_lower)
    contact["buying_role"] = classify_buying_role(title_lower)

    if linkedin_map:
        name_slug = contact["name"].lower().replace(" ", "-")
        for slug, url in linkedin_map.items():
            if name_slug in slug or slug in name_slug:
                contact.setdefault("linkedin", url)
                break

    return contact


def find_contacts(base_url):
    parsed = urllib.parse.urlparse(base_url)
    domain_base = f"{parsed.scheme}://{parsed.netloc}"

    all_contacts = []
    pages_checked = []
    errors = []
    linkedin_map = {}

    for path in TEAM_PATHS:
        url = domain_base + path
        html, final_url = fetch_page(url)
        if not html:
            continue

        pages_checked.append(final_url or url)

        # Extract LinkedIn profile links from the page
        linkedin_map.update(extract_linkedin_urls(html))

        parser = TeamPageParser()
        parser.feed(html)
        if parser._text_buffer:
            parser.text_blocks.append(" ".join(parser._text_buffer))

        json_ld_contacts = extract_from_json_ld(parser.json_ld)
        card_contacts = extract_from_card_patterns(parser.text_blocks)
        list_contacts = extract_from_list_patterns(parser.text_blocks)

        for c in json_ld_contacts + card_contacts + list_contacts:
            c["found_at"] = final_url or url

        all_contacts.extend(json_ld_contacts + card_contacts + list_contacts)

    # Deduplicate by name
    seen = {}
    unique = []
    for c in all_contacts:
        name = c["name"]
        if name not in seen:
            seen[name] = True
            unique.append(c)

    # Enrich each contact
    enriched = [enrich_contact(c, linkedin_map) for c in unique]

    # Sort by seniority
    enriched.sort(key=lambda c: SENIORITY_ORDER.get(c.get("seniority", "unknown"), 5))

    return {
        "base_url": base_url,
        "contacts": enriched[:30],
        "total_found": len(enriched),
        "pages_checked": pages_checked,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Find contacts at a company website")
    parser.add_argument("--url", required=True, help="Company website URL")
    parser.add_argument("--output", choices=["json", "text"], default="json")
    args = parser.parse_args()

    url = args.url
    if not url.startswith("http"):
        url = "https://" + url

    result = find_contacts(url)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Contacts found at {result['base_url']}: {result['total_found']}")
        for c in result["contacts"]:
            print(f"  {c['name']} — {c.get('title', 'N/A')} [{c.get('seniority', '?')}] ({c.get('buying_role', '?')})")


if __name__ == "__main__":
    main()
