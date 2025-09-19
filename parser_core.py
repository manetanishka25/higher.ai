# parser_core.py
import io
import re
import sys
from typing import List, Dict, Any, Tuple, Optional
from skill_sets import CANONICAL_SKILLS, SKILL_GROUPS, LANGUAGES

# Optional imports: handled gracefully if libs aren’t installed.
try:
    from pdfminer.high_level import extract_text as pdf_extract_text
except Exception:
    pdf_extract_text = None

try:
    import docx
except Exception:
    docx = None

URL_RE = re.compile(r'((?:https?://|www\.)[^\s)]+)', re.IGNORECASE)
EMAIL_RE = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', re.IGNORECASE)
PHONE_RE = re.compile(
    r'(\+?\d{1,3}[\s\-\.]?)?(\(?\d{3,4}\)?[\s\-\.]?)?\d{3,4}[\s\-\.]?\d{4}', re.IGNORECASE
)
YEAR_RE = r'(20\d{2}|19\d{2})'
DATE_RE = re.compile(
    fr'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s?\d{{0,2}},?\s?{YEAR_RE}|{YEAR_RE}\s?-\s?(Present|{YEAR_RE})|{YEAR_RE}\s?to\s?(Present|{YEAR_RE}))',
    re.IGNORECASE
)

DEGREE_WORDS = [
    "bachelor", "master", "phd", "b.tech", "btech", "m.tech", "mtech", "mba",
    "b.e", "m.e", "bsc", "msc", "ms", "bs", "ba", "ma", "mca", "bca", "bcom", "mcom",
]
EDU_SECTION_HINTS = ["education", "academics"]
EXP_SECTION_HINTS = ["experience", "work history", "employment"]
PROJ_SECTION_HINTS = ["projects", "personal projects"]
CERT_SECTION_HINTS = ["certifications", "licenses", "certs"]

def _clean_text(t: str) -> str:
    return re.sub(r'[ \t]+', ' ', t).replace('\r', '\n')

def extract_text_from_file(content: bytes, filename: str) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        if not pdf_extract_text:
            raise ValueError("pdfminer.six is not installed.")
        return _clean_text(pdf_extract_text(io.BytesIO(content)))
    elif name.endswith(".docx"):
        if not docx:
            raise ValueError("python-docx is not installed.")
        doc = docx.Document(io.BytesIO(content))
        return _clean_text("\n".join(p.text for p in doc.paragraphs))
    elif name.endswith(".txt"):
        # best-effort decode
        for enc in ("utf-8", "latin-1", "utf-16"):
            try:
                return _clean_text(content.decode(enc))
            except Exception:
                continue
        return _clean_text(content.decode(errors="ignore"))
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

def _top_lines(text: str, n=12) -> List[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[:n]

def _guess_name(text: str, email: Optional[str]) -> Optional[str]:
    # Heuristic: Look at the first lines for 2–4 capitalized tokens
    lines = _top_lines(text, n=8)
    for l in lines:
        tokens = [t for t in re.split(r'[\s|,]+', l) if t]
        caps = [t for t in tokens if re.match(r"^[A-Z][a-zA-Z'\-]+$", t)]
        if 2 <= len(caps) <= 4 and not re.search(EMAIL_RE, l):
            return " ".join(caps)
    # fallback: email local-part
    if email:
        local = email.split("@")[0]
        local = re.sub(r'[._-]+', ' ', local)
        parts = [p.capitalize() for p in local.split()]
        if len(parts) >= 2:
            return " ".join(parts[:3])
    return None

def _extract_links(text: str) -> List[Dict[str, str]]:
    urls = set(m.group(1) for m in URL_RE.finditer(text))
    links = []
    for u in urls:
        lu = u.lower()
        t = "other"
        if "linkedin.com" in lu:
            t = "linkedin"
        elif "github.com" in lu:
            t = "github"
        elif "leetcode.com" in lu or "hackerrank.com" in lu:
            t = "coding"
        elif "medium.com" in lu or "substack.com" in lu:
            t = "blog"
        elif "portfolio" in lu or "behance.net" in lu or "dribbble.com" in lu:
            t = "portfolio"
        links.append({"type": t, "url": u if u.startswith("http") else f"https://{u}"})
    return sorted(links, key=lambda x: x["type"])

def _detect_location(lines: List[str]) -> Optional[str]:
    # Naive: find line with city/state/country-like commas and no bullets
    for l in lines[:10]:
        if "@" in l or "http" in l.lower():
            continue
        if re.search(r'[A-Za-z]+,\s*[A-Za-z .-]+(,\s*[A-Za-z .-]+)?', l) and len(l) < 80:
            return l.strip("•- ")
    return None

def _split_sections(text: str) -> Dict[str, List[str]]:
    lines = [l.strip() for l in text.splitlines()]
    sections: Dict[str, List[str]] = {"_intro": []}
    current = "_intro"
    for l in lines:
        bare = l.lower().strip(":").strip()
        if bare in EDU_SECTION_HINTS:
            current = "education"
            sections.setdefault(current, [])
            continue
        if bare in EXP_SECTION_HINTS:
            current = "experience"
            sections.setdefault(current, [])
            continue
        if bare in PROJ_SECTION_HINTS:
            current = "projects"
            sections.setdefault(current, [])
            continue
        if bare in CERT_SECTION_HINTS:
            current = "certifications"
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(l)
    return sections

def _extract_summary(intro_lines: List[str]) -> Optional[str]:
    # first 3–6 lines that are not contact info
    body = []
    for l in intro_lines:
        if re.search(EMAIL_RE, l) or re.search(PHONE_RE, l) or re.search(URL_RE, l):
            continue
        if any(h in l.lower() for h in EDU_SECTION_HINTS + EXP_SECTION_HINTS + PROJ_SECTION_HINTS):
            break
        body.append(l.strip("•- "))
        if len(" ".join(body)) > 400:
            break
    t = " ".join(body).strip()
    return t or None

def _find_skill_hits(text: str) -> Tuple[List[str], Dict[str, List[str]]]:
    text_l = text.lower()
    hits = []
    for s in CANONICAL_SKILLS:
        if re.search(rf'\b{re.escape(s.lower())}\b', text_l):
            hits.append(s)
    buckets: Dict[str, List[str]] = {}
    for g, items in SKILL_GROUPS.items():
        buckets[g] = sorted([s for s in items if s in hits])
    return sorted(set(hits)), buckets

def _find_languages(text: str) -> List[str]:
    hits = []
    tl = text.lower()
    for lang in LANGUAGES:
        if re.search(rf'\b{re.escape(lang.lower())}\b', tl):
            hits.append(lang)
    return sorted(set(hits))

def _parse_timeline_line(l: str) -> Tuple[Optional[str], Optional[str]]:
    # Try "Jan 2020 - Mar 2022", "2021 - Present", "2019 to 2020"
    m = DATE_RE.search(l)
    if not m:
        return (None, None)
    # normalize roughly by pulling the first and last year-like tokens
    years = re.findall(r'(Present|20\d{2}|19\d{2})', m.group(0), re.I)
    if not years:
        return (None, None)
    start = years[0]
    end = years[-1] if len(years) > 1 else None
    return (start, end)

def _parse_bullets(lines: List[str], start_idx: int) -> List[str]:
    bullets = []
    for i in range(start_idx, min(start_idx + 12, len(lines))):
        l = lines[i].strip()
        if l.startswith(("-", "•", "*")) or l[:2] in ("- ", "• ", "* "):
            bullets.append(l.lstrip("-•* ").strip())
        else:
            # stop if we hit a blank or a new section-ish header
            if not l or l.isupper() or len(l) < 3:
                break
    return bullets

def _parse_education(section_lines: List[str]) -> List[Dict[str, Any]]:
    out = []
    for i, l in enumerate(section_lines):
        lower = l.lower()
        if any(dw in lower for dw in DEGREE_WORDS) or re.search(YEAR_RE, l):
            start, end = _parse_timeline_line(l)
            # attempt: Institution – Degree, Field
            inst = None
            deg = None
            field = None
            loc = None
            # institution often on same or next line
            inst_line = l
            if i + 1 < len(section_lines):
                nxt = section_lines[i + 1]
                if len(nxt) > len(inst_line):
                    inst_line = nxt + " " + inst_line
            # split on dash/pipe
            parts = re.split(r'\s[–\-|]\s', inst_line)
            if parts:
                if any(dw in parts[0].lower() for dw in DEGREE_WORDS):
                    # flipped
                    deg = parts[0]
                    inst = parts[1] if len(parts) > 1 else None
                else:
                    inst = parts[0]
                    deg = parts[1] if len(parts) > 1 else None
            # field guess
            m = re.search(r'in\s([A-Za-z& /]+)', l, re.I)
            if m:
                field = m.group(1).strip()
            # gpa
            gpa = None
            mg = re.search(r'GPA[:\s]+([0-9.]+/?[0-9.]*)', " ".join(section_lines[i:i+3]), re.I)
            if mg:
                gpa = mg.group(1)
            out.append({
                "institution": inst.strip() if inst else None,
                "degree": deg.strip() if deg else None,
                "field": field,
                "start_date": start,
                "end_date": end,
                "gpa": gpa,
                "location": loc,
                "highlights": _parse_bullets(section_lines, i+1),
            })
    # dedupe
    uniq = []
    seen = set()
    for e in out:
        key = (e.get("institution"), e.get("degree"), e.get("end_date"))
        if key not in seen:
            uniq.append(e); seen.add(key)
    return uniq

def _parse_experience(section_lines: List[str], text: str) -> List[Dict[str, Any]]:
    out = []
    for i, l in enumerate(section_lines):
        if not l.strip():
            continue
        # Look for Company — Title with dates on same/next line
        dates = _parse_timeline_line(l)
        if not any(dates):
            if i + 1 < len(section_lines):
                dates = _parse_timeline_line(section_lines[i + 1])
        if any(dates):
            # title/company heuristic
            parts = re.split(r'\s[–\-|]\s', l)
            title = None
            company = None
            if len(parts) >= 2:
                left, right = parts[0], parts[1]
                # Guess which is which by capitalization patterns
                if left.isupper() or left.istitle():
                    company, title = left, right
                else:
                    title, company = left, right
            else:
                # fallback: first token is title-ish
                title = l
            bullets = _parse_bullets(section_lines, i + 1)
            # tech mentions
            techs = []
            for s in CANONICAL_SKILLS:
                if re.search(rf'\b{re.escape(s)}\b', " ".join(bullets), re.I):
                    techs.append(s)
            out.append({
                "title": (title or "").strip("•- ").strip(),
                "company": (company or "").strip("•- ").strip(),
                "start_date": dates[0],
                "end_date": dates[1],
                "location": None,
                "bullets": bullets[:10],
                "technologies": sorted(set(techs))[:20],
            })
    # basic ordering: most recent first by end_date
    def _year_to_int(y):
        if not y or y.lower() == "present":
            return 9999
        try:
            return int(re.findall(r'(20\d{2}|19\d{2})', y)[0])
        except Exception:
            return 0
    out.sort(key=lambda e: _year_to_int(e.get("end_date") or "Present"), reverse=True)
    return out

def detect_language_simple(text: str) -> Optional[str]:
    # extremely naive: look for Devanagari or Latin
    if re.search(r'[\u0900-\u097F]', text):
        return "hi-Latn/Devanagari-mixed"
    return "en"  # default

def parse_resume(text: str) -> Dict[str, Any]:
    t = text.strip()
    lines = [l for l in t.splitlines() if l.strip()]
    head = "\n".join(lines[:20])

    email = (re.search(EMAIL_RE, t).group(0) if re.search(EMAIL_RE, t) else None)
    phone = (re.search(PHONE_RE, t).group(0) if re.search(PHONE_RE, t) else None)
    name = _guess_name(t, email)
    links = _extract_links(t)
    location = _detect_location(lines)
    sections = _split_sections(t)
    summary = _extract_summary(sections.get("_intro", []))
    skills, buckets = _find_skill_hits(t)
    languages = _find_languages(t)
    education = _parse_education(sections.get("education", []))
    experience = _parse_experience(sections.get("experience", []), t)

    projects = []
    for i, l in enumerate(sections.get("projects", [])):
        if len(l) < 2: continue
        # "ProjectName – short desc"
        parts = re.split(r'\s[–\-|]\s', l)
        if len(parts) >= 2 and len(parts[0]) < 80:
            bullets = _parse_bullets(sections.get("projects", []), i + 1)
            techs = [s for s in skills if re.search(rf'\b{re.escape(s)}\b', " ".join(bullets), re.I)]
            link = None
            m = re.search(URL_RE, l)
            if m: link = m.group(1)
            projects.append({
                "name": parts[0].strip(),
                "description": parts[1].strip(),
                "bullets": bullets[:8],
                "technologies": sorted(set(techs))[:15],
                "link": link,
            })

    certs = []
    for l in sections.get("certifications", []):
        if len(l) < 3: continue
        # "Name – Issuer (YYYY)" patterns
        parts = re.split(r'\s[–\-|]\s', l)
        name = parts[0].strip()
        issuer = parts[1].strip() if len(parts) > 1 else None
        yr = None
        m = re.search(YEAR_RE, l)
        if m: yr = m.group(1)
        url = None
        m2 = re.search(URL_RE, l)
        if m2: url = m2.group(1)
        certs.append({"name": name, "issuer": issuer, "date": yr, "license": None, "url": url})

    return {
        "detected_language": detect_language_simple(t),
        "candidate_name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "summary": summary,
        "links": links,
        "skills": skills,
        "skill_groups": buckets,
        "languages": languages,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certs,
    }
