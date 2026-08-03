#!/usr/bin/env python3
"""
ARSC site generator.

Emits the whole static site from the course data below. Re-run it any time
content changes:

    python3 build.py

Why a generator instead of 19 hand-written files: the header, footer, nav and
disclaimers appear on every page. Editing them by hand in 19 places is how
sites drift out of sync. Change it once here, rebuild, and every page matches.

Nothing is minified or obfuscated — the output is plain, readable HTML you can
edit directly if you prefer. If you do hand-edit, note that re-running this
script overwrites the generated pages.
"""

import hashlib
import json
import os
import re
import shutil
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://arscollegecanada.ca"
TODAY = date.today().isoformat()
EMAIL = "info@arscollegecanada.ca"

DISCLOSURE = (
    "ARSC provides non-degree professional development, continuing education and "
    "skills-upgrading courses. Certificates issued by ARSC confirm successful "
    "completion of private professional development training and do not represent "
    "an academic degree, government licence, regulated professional designation or "
    "provincially recognized career-training diploma."
)

DISCLOSURE_2 = (
    "ARSC courses are not a substitute for regulated accounting, CPA, legal or human "
    "resources professional designations. Legal advice, immigration advice and "
    "regulated accounting opinions are referred to appropriately licensed professionals."
)

# ---------------------------------------------------------------------------
# Course catalogue. Lesson lists come from the project's own topic lists.
# `yt` is the YouTube video ID for each lesson — left empty until recorded.
# ---------------------------------------------------------------------------

SCHOOLS = [
    ("Artificial Intelligence", "School of Artificial Intelligence"),
    ("Taxation and Accounting", "School of Taxation and Accounting"),
    ("Business and Entrepreneurship", "School of Business and Entrepreneurship"),
    ("Human Resources", "School of Human Resources"),
]

COURSES = [
    dict(
        code="AI-01", slug="ai-for-business-professionals",
        school="Artificial Intelligence",
        title="AI for Business Professionals",
        hours=24, low=699, high=999,
        blurb="Generative AI fundamentals, prompt writing, workflow automation and responsible AI use.",
        summary=(
            "A practical grounding in generative AI for people who already have a job to do. "
            "You will learn how these tools actually behave, how to write prompts that produce "
            "usable work, where to automate safely, and where a human must stay in the loop."
        ),
        prereq="None. Comfort with everyday office software is enough.",
        outcomes=[
            "Write prompts that produce consistent, reviewable output",
            "Identify which parts of your own workflow are safe to automate",
            "Recognise where AI output must not be trusted without review",
            "Apply a responsible-use standard to client and employer data",
        ],
        lessons=[
            "Generative AI fundamentals", "Prompt writing", "AI-assisted research",
            "Business communications", "Workflow automation", "AI risks and privacy",
            "Responsible AI use",
        ],
    ),
    dict(
        code="AI-02", slug="ai-for-accounting-and-bookkeeping",
        school="Artificial Intelligence",
        title="AI for Accounting and Bookkeeping",
        hours=20, low=599, high=899,
        blurb="AI-assisted categorization, document processing, spreadsheet automation and error detection.",
        summary=(
            "How AI tools fit into a real bookkeeping cycle — and where they do not belong. "
            "Built around the tasks that consume the most hours: categorising transactions, "
            "pulling data out of documents, and finding the errors before a client does."
        ),
        prereq="Working knowledge of debits and credits, or Bookkeeping Fundamentals.",
        outcomes=[
            "Use AI assistance for transaction categorisation without losing accuracy",
            "Extract data from invoices and statements reliably",
            "Build spreadsheet automations that a reviewer can follow",
            "Apply confidentiality safeguards to client financial records",
        ],
        lessons=[
            "AI-assisted transaction categorization", "Document processing",
            "Invoice extraction", "Financial report summaries", "Spreadsheet automation",
            "Error detection", "Privacy and confidentiality",
        ],
    ),
    dict(
        code="AI-03", slug="ai-for-tax-professionals",
        school="Artificial Intelligence",
        title="AI for Tax Professionals",
        hours=16, low=599, high=899,
        blurb="Tax research support, client intake automation, and the limits of AI tax advice.",
        summary=(
            "A short, focused course on using AI around tax work without letting it near the "
            "conclusions. Covers research support, intake and document handling, and spends "
            "real time on where these tools are wrong and what review is mandatory."
        ),
        prereq="Familiarity with Canadian personal tax, or Canadian Personal Tax Fundamentals.",
        outcomes=[
            "Use AI for research support while verifying every source",
            "Automate client intake and document organisation",
            "Draft client communications for supervisor review",
            "State clearly where AI tax output cannot be relied upon",
        ],
        lessons=[
            "Tax research support", "Client intake automation", "Document organization",
            "Drafting client communications", "Tax checklist generation",
            "Limitations of AI tax advice", "Human review requirements",
        ],
    ),
    dict(
        code="TAX-01", slug="canadian-personal-tax-fundamentals",
        school="Taxation and Accounting",
        title="Canadian Personal Tax Fundamentals",
        hours=30, low=899, high=1299,
        blurb="The Canadian personal income tax system, from slips and income types through to T1 preparation.",
        summary=(
            "The full personal tax picture, worked through rather than lectured. Employment "
            "income, self-employment, the common deductions and credits, and how a T1 is "
            "actually assembled — using simulated client files throughout."
        ),
        prereq="None. Built to be a genuine starting point.",
        outcomes=[
            "Read and apply T4 and T4A slips correctly",
            "Handle employment and self-employment income",
            "Prepare a basic T1 return from a client document set",
            "Respond appropriately to CRA notices",
        ],
        lessons=[
            "Canadian personal income tax system", "T4 and T4A slips", "Employment income",
            "Self-employment income", "Common deductions and credits", "Basic T1 preparation",
            "CRA notices", "Client document collection", "Ethical tax preparation",
        ],
    ),
    dict(
        code="ACC-01", slug="bookkeeping-fundamentals",
        school="Taxation and Accounting",
        title="Bookkeeping Fundamentals",
        hours=30, low=899, high=1299,
        blurb="Chart of accounts, debits and credits, reconciliations and month-end procedures.",
        summary=(
            "Full-cycle bookkeeping from a blank set of books to a month-end close. The "
            "emphasis is on producing records that somebody else can review — which is the "
            "difference between doing your own books and being employable."
        ),
        prereq="None.",
        outcomes=[
            "Build and maintain a chart of accounts",
            "Reconcile bank and credit card accounts confidently",
            "Manage receivables and payables through a full cycle",
            "Close a month and produce basic financial statements",
        ],
        lessons=[
            "Chart of accounts", "Debits and credits", "Bank reconciliations",
            "Accounts receivable", "Accounts payable", "Expense categorization",
            "Financial statements", "Month-end procedures",
        ],
    ),
    dict(
        code="PAY-01", slug="payroll-administration-fundamentals",
        school="Taxation and Accounting",
        title="Payroll Administration Fundamentals",
        hours=20, low=699, high=999,
        blurb="Payroll cycles, statutory deductions, remittances, T4 preparation and reconciliation.",
        summary=(
            "Canadian payroll end to end. Source deductions, vacation pay, the remittance "
            "calendar, and year-end T4s — the areas where mistakes are both common and "
            "expensive."
        ),
        prereq="None, though bookkeeping familiarity helps.",
        outcomes=[
            "Run a payroll cycle from timesheets to net pay",
            "Calculate and remit statutory deductions on schedule",
            "Prepare and file T4s",
            "Reconcile payroll to the general ledger",
        ],
        lessons=[
            "Payroll cycles", "Employee records", "Statutory deductions", "Vacation pay",
            "Payroll remittances", "T4 preparation", "Payroll reconciliation",
            "Record retention",
        ],
    ),
    dict(
        code="ACC-02", slug="small-business-accounting-essentials",
        school="Taxation and Accounting",
        title="Small Business Accounting Essentials",
        hours=24, low=799, high=1099,
        blurb="Business income and expenses, structures, GST/HST and PST, cash flow and year-end.",
        summary=(
            "Accounting from the owner's side of the desk. How structure changes the numbers, "
            "how sales tax actually works in practice, and what a clean year-end handover to "
            "an accountant looks like."
        ),
        prereq="Bookkeeping Fundamentals, or equivalent experience.",
        outcomes=[
            "Distinguish sole proprietorship from corporate treatment",
            "Handle GST/HST and PST correctly through a year",
            "Build a working cash-flow view of a small business",
            "Prepare a year-end file an accountant can work from",
        ],
        lessons=[
            "Business income and expenses", "Sole proprietorships", "Corporations",
            "GST/HST", "PST", "Cash flow", "Financial controls", "Year-end preparation",
        ],
    ),
    dict(
        code="BUS-01", slug="starting-a-small-business-in-canada",
        school="Business and Entrepreneurship",
        title="Starting a Small Business in Canada",
        hours=20, low=699, high=999,
        blurb="Structures, registration, business numbers, banking, insurance, contracts and planning.",
        summary=(
            "The practical sequence of actually starting a Canadian business, in order, with "
            "the paperwork explained. Written particularly for newcomers navigating Canadian "
            "registration and tax accounts for the first time."
        ),
        prereq="None.",
        outcomes=[
            "Choose a business structure for your situation",
            "Register a business and obtain the accounts you need",
            "Set up banking, insurance and basic contracts",
            "Write a business plan and a first-year budget",
        ],
        lessons=[
            "Business structures", "Business registration", "Business numbers",
            "GST/HST registration", "Business banking", "Insurance", "Contracts",
            "Pricing", "Marketing", "Business planning",
        ],
    ),
    dict(
        code="BUS-02", slug="business-management-fundamentals",
        school="Business and Entrepreneurship",
        title="Business Management Fundamentals",
        hours=30, low=899, high=1299,
        blurb="Operations, leadership, financial management, strategy, risk and performance measurement.",
        summary=(
            "A broad management grounding for people moving from doing the work to running "
            "the work. Operations, money, people and risk — with performance measurement "
            "treated as a discipline rather than a dashboard."
        ),
        prereq="None. Some workplace experience is assumed.",
        outcomes=[
            "Structure operations around measurable outcomes",
            "Read and act on the financial position of a business",
            "Build a strategic plan with real constraints in it",
            "Identify and mitigate operational risk",
        ],
        lessons=[
            "Business operations", "Leadership", "Financial management",
            "Strategic planning", "Risk management", "Customer service",
            "Performance measurement", "Business growth",
        ],
    ),
    dict(
        code="BUS-03", slug="small-business-financial-management",
        school="Business and Entrepreneurship",
        title="Small Business Financial Management",
        hours=20, low=699, high=999,
        blurb="Budgeting, cash-flow forecasting, pricing, margins and cost management.",
        summary=(
            "The financial half of running a small business. Budgets that survive contact "
            "with reality, cash-flow forecasting, and pricing that actually covers cost — "
            "the three places small businesses most often fail."
        ),
        prereq="Basic bookkeeping familiarity.",
        outcomes=[
            "Build a budget and track variance against it",
            "Forecast cash flow well enough to see trouble early",
            "Price work to a target margin",
            "Manage costs without cutting the wrong things",
        ],
        lessons=[
            "Budgeting", "Cash-flow forecasting", "Pricing", "Profit margins",
            "Cost management", "Financial statements", "Business performance indicators",
        ],
    ),
    dict(
        code="HR-01", slug="hr-administration-fundamentals",
        school="Human Resources",
        title="HR Administration Fundamentals",
        hours=24, low=799, high=1099,
        blurb="Employee files, onboarding, agreements, workplace policies and performance documentation.",
        summary=(
            "The administrative backbone of an HR function. Files, onboarding, agreements, "
            "policies and the documentation that protects both employer and employee — with "
            "privacy treated as a first-order concern, not a footnote."
        ),
        prereq="None.",
        outcomes=[
            "Set up and maintain compliant employee files",
            "Run an onboarding process end to end",
            "Document performance and attendance defensibly",
            "Apply privacy and confidentiality standards to HR records",
        ],
        lessons=[
            "Employee files", "Onboarding", "Employment agreements", "Workplace policies",
            "Attendance records", "Performance documentation", "Termination administration",
            "Privacy and confidentiality",
        ],
    ),
    dict(
        code="HR-02", slug="recruitment-and-interviewing-skills",
        school="Human Resources",
        title="Recruitment and Interviewing Skills",
        hours=16, low=499, high=799,
        blurb="Job descriptions, screening, interview technique, evaluation and hiring documentation.",
        summary=(
            "A short course on hiring well. Writing a description that attracts the right "
            "people, screening without bias, asking questions that actually predict "
            "performance, and documenting the decision."
        ),
        prereq="None.",
        outcomes=[
            "Write job descriptions and advertisements that work",
            "Screen resumes consistently and fairly",
            "Run a structured interview and evaluate against criteria",
            "Complete reference checks and hiring documentation",
        ],
        lessons=[
            "Job descriptions", "Job advertisements", "Resume screening",
            "Interview preparation", "Interview questions", "Candidate evaluation",
            "Reference checking", "Hiring documentation",
        ],
    ),
]

LAUNCH = ["AI-01", "ACC-01", "TAX-01", "BUS-01"]

NAV = [
    ("College", "college/"),
    ("Faculty", "faculty/"),
    ("Advisory", "advisory/"),
    ("Resources", "resources/"),
    ("About", "about/"),
    ("Contact", "contact/"),
]

# Secondary destinations: drawer + footer only, to keep the top nav to six.
SECONDARY = [
    ("How it works", "how-it-works/"),
    ("Employer training", "employers/"),
    ("Policies", "policies/"),
]

# Software named on course pages. Every competitor leads with QuickBooks and
# Sage; "is_planned" marks tools not yet in the written curriculum, so nothing
# here claims to teach something that has not been built.
TOOLS = {
    "ACC-01": [("Excel", False), ("QuickBooks Online", True), ("Sage 50", True)],
    "ACC-02": [("Excel", False), ("QuickBooks Online", True)],
    "PAY-01": [("Excel", False), ("Payroll software", True)],
    "TAX-01": [("CRA forms", False), ("Tax software", True)],
    "BUS-03": [("Excel", False)],
    "AI-01":  [("Generative AI tools", False)],
    "AI-02":  [("Generative AI tools", False), ("Spreadsheet automation", False)],
    "AI-03":  [("Generative AI tools", False)],
}

# ---------------------------------------------------------------------------
# Fragments
# ---------------------------------------------------------------------------

ARROW = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M5 12h14M13 6l6 6-6 6"/></svg>')

ARROW_UR = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M7 17 17 7M9 7h8v8"/></svg>')

ARROW_DOWN = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M12 5v14M6 13l6 6 6-6"/></svg>')

CREST = ('<span class="brand-mark"><img src="{root}assets/arsc-logo-128.jpg" alt="" '
         'width="44" height="44" decoding="async"></span>')


# Google truncates titles past ~60 characters and descriptions past ~160.
# Anything outside those bounds is a real defect, not a style preference, so
# the build fails loudly rather than shipping a truncated search result.
def _check_meta(path, title, desc):
    if not 30 <= len(title) <= 62:
        raise SystemExit(f"TITLE {len(title)}ch (need 30-62) on {path}: {title}")
    if not 110 <= len(desc) <= 160:
        raise SystemExit(f"DESC {len(desc)}ch (need 110-160) on {path}: {desc}")


def head(root, title, desc, canon, extra="", keywords=""):
    kw = f'<meta name="keywords" content="{keywords}">\n' if keywords else ""
    return f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{kw}<meta name="theme-color" content="#0B1B3F">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="ARSC Professional Development College">
<meta name="geo.region" content="CA-BC">
<meta name="geo.placename" content="British Columbia, Canada">

<link rel="canonical" href="{SITE}{canon}">
<link rel="icon" href="{root}assets/favicon-180.png" sizes="any">
<link rel="apple-touch-icon" href="{root}assets/favicon-180.png">

<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}{canon}">
<meta property="og:site_name" content="ARSC Professional Development College">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:locale" content="en_CA">
<meta property="og:image" content="{SITE}/assets/arsc-logo-400.jpg">
<meta property="og:image:alt" content="Academy of Research and Sciences of Canada Inc. crest">
<meta name="twitter:card" content="summary_large_image">

<link rel="preload" as="image" href="{root}assets/arsc-logo-128.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Karla:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/site.css?v={CSS_V}">
{extra}</head>
<body>

<a class="skip" href="#main">Skip to main content</a>
<div class="topline"></div>
"""


def header(root, active):
    links, drawer = [], []
    for label, href in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append(f'<li><a href="{root}{href}"{cur}>{label}</a></li>')
        drawer.append(f'<li><a href="{root}{href}"{cur}>{label} {ARROW}</a></li>')

    cur_e = ' aria-current="page"' if active == "enroll/" else ""
    drawer.append(f'<li><a href="{root}enroll/"{cur_e}>Enrol {ARROW}</a></li>')

    sec = "".join(
        f'<li><a href="{root}{href}">{label} {ARROW}</a></li>' for label, href in SECONDARY
    )

    return f"""
<header class="site-header">
  <div class="shell">
    <nav class="nav" aria-label="Primary">

      <a class="brand" href="{root}index.html" aria-label="ARSC Professional Development College — home">
        {CREST.format(root=root)}
        <span class="brand-text">ARSC<span>Professional Development College</span></span>
      </a>

      <ul class="nav-links">
        {''.join(links)}
      </ul>

      <div class="nav-end">
        <a class="btn btn-gold" href="{root}enroll/">Enrol {ARROW}</a>
      </div>

      <button class="nav-toggle" aria-expanded="false" aria-controls="navDrawer">
        Menu <span class="nav-toggle-bars" aria-hidden="true"></span>
      </button>

    </nav>
  </div>

  <div class="nav-drawer" id="navDrawer">
    <div><div class="shell"><ul>{''.join(drawer)}{sec}</ul></div></div>
  </div>
</header>
"""


def footer(root):
    school_links = "".join(
        f'<li><a href="{root}college/#school-{slugify(name)}">{name}</a></li>'
        for name, _ in SCHOOLS
    )
    return f"""
<footer class="site-footer">
  <div class="shell">

    <div class="footer-top">
      <div>
        <img class="footer-logo" src="{root}assets/arsc-logo-200.jpg" width="95" height="95"
             loading="lazy" decoding="async"
             alt="Crest of the Academy of Research and Sciences of Canada Inc. — Académie de Recherche et des Sciences du Canada Inc.">
        <p class="footer-blurb">
          The AI era begins here. ARSC Professional Development College is the
          education division of Academy of Research and Sciences of Canada Inc.
        </p>
      </div>

      <div class="footer-cols">
        <div>
          <h2>Schools</h2>
          <ul>{school_links}</ul>
        </div>
        <div>
          <h2>Organization</h2>
          <ul>
            <li><a href="{root}college/">The College</a></li>
            <li><a href="{root}advisory/">Advisory Services</a></li>
            <li><a href="{root}about/">About ARSC</a></li>
            <li><a href="{root}how-it-works/">How it works</a></li>
            <li><a href="{root}employers/">Employer training</a></li>
            <li><a href="{root}faculty/">Faculty</a></li>
            <li><a href="{root}resources/">Resources</a></li>
            <li><a href="{root}policies/">Policies</a></li>
          </ul>
        </div>
        <div>
          <h2>Contact</h2>
          <ul>
            <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
            <li><a href="{SITE}">arscollegecanada.ca</a></li>
            <li><a href="{root}enroll/">Enrol in a course</a></li>
            <li>British Columbia, Canada</li>
          </ul>
        </div>
      </div>
    </div>

    <div style="padding-bottom:var(--sp-2xl)">
      <h2>Stay informed</h2>
      <p style="max-width:52ch;margin-bottom:var(--sp-md)">
        Occasional notes on Canadian tax changes, AI in practice, and new course
        intakes. No more than monthly.
      </p>
      <form class="signup" id="signupForm" novalidate>
        <div class="field">
          <label for="nl-email">Email address</label>
          <input id="nl-email" name="email" type="email" autocomplete="email" required>
        </div>
        <button class="btn btn-gold" type="submit">Subscribe {ARROW}</button>
      </form>
    </div>

    <p class="disclaimer">{DISCLOSURE}</p>
    <p class="disclaimer">{DISCLOSURE_2}</p>

    <p class="land">
      ARSC operates from the territories of the x&#695;m&#601;&#952;k&#695;&#601;y&#769;&#601;m (Musqueam),
      S&#7317;&#7369;x&#817;w&#250;7mesh (Squamish) and s&#601;lilw&#601;ta&#623; (Tsleil-Waututh) Nations.
    </p>

    <div class="footer-legal">
      <span>British Columbia, Canada</span>
      <span>© {date.today().year} ARSC</span>
      <a href="#">Back to top <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg></a>
    </div>

  </div>
</footer>

<script src="{root}assets/site.js?v={JS_V}" defer></script>
</body>
</html>
"""


def course_title(c):
    """<=62 chars. Hours and "Online" are what people actually search for."""
    t = f"{c['title']} — {c['hours']}h Online Course | ARSC"
    if len(t) > 62:
        t = f"{c['title']} — {c['hours']}h Course | ARSC"
    return t


def course_desc(c):
    """110-160 chars. Starts with the blurb, then pads with the facts a
    searcher wants: hours, delivery, credential."""
    tails = [
        f" {c['hours']} instructional hours, online and self-paced, certificate on completion.",
        f" {c['hours']} hours, online and self-paced, with a certificate of completion.",
        f" {c['hours']} hours online, self-paced. Certificate of completion.",
        f" {c['hours']} hours, online, self-paced.",
        "",
    ]
    base = c["blurb"].rstrip()
    for t in tails:
        d = base + t
        if 110 <= len(d) <= 160:
            return d
    d = (base + tails[0])[:157].rsplit(" ", 1)[0] + "."
    return d


def course_keywords(c):
    school = c["school"].lower()
    return (f"{c['title'].lower()}, online {school} course canada, "
            f"{c['code'].lower()} arsc, professional development certificate bc, "
            "self paced online course")


# Cache busting. The host serves assets with max-age=31536000 (one year), so a
# returning visitor keeps the old stylesheet long after a deploy — which is
# exactly what "I can't see the update" looks like. Appending a hash of the
# file's own contents means a changed file is a changed URL, so the browser
# is obliged to fetch it, while an unchanged file still caches for the full
# year. Best of both.
def asset_v(relpath):
    full = os.path.join(HERE, relpath)
    try:
        with open(full, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:8]
    except FileNotFoundError:
        return "0"


CSS_V = None   # filled in by main() once the CSS is final
JS_V = None


def slugify(s):
    return s.lower().replace(" ", "-").replace("&", "and")

def money(n):
    """Thousands separators. $1299 reads as a typo; $1,299 reads as a price."""
    return f"{n:,}"


def rings(n=4):
    return '<div class="rings" aria-hidden="true">' + "<span></span>" * n + "</div>"


def crumbs(root, trail):
    """trail: list of (label, href or None). Last item is the current page."""
    out = [f'<li><a href="{root}index.html">Home</a></li>']
    for i, (label, href) in enumerate(trail):
        last = i == len(trail) - 1
        if last or href is None:
            out.append(f'<li><span aria-current="page">{label}</span></li>')
        else:
            out.append(f'<li><a href="{root}{href}">{label}</a></li>')
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs">{"".join(out)}</ol></nav>'


def course_card(root, c, prefix="college/"):
    lis = "".join(f"<li>{l}</li>" for l in c["lessons"][:4])
    price = f'${money(c["low"])}&ndash;${money(c["high"])}'
    return f"""
      <a class="course" href="{root}{prefix}{c['slug']}.html">
        <span class="course-top">
          <span class="course-code">{c['code'].replace('-', '&mdash;')}</span>
          <span class="course-arrow">{ARROW_UR}</span>
        </span>
        <span class="course-cat">{c['school']}</span>
        <h3>{c['title']}</h3>
        <span class="course-meta"><span>{c['hours']} hours</span><span>Online</span><span>{price}</span></span>
        <ul>{lis}</ul>
        <span class="course-foot">View course {ARROW}</span>
      </a>"""


def write(path, content):
    # Validate meta lengths on the finished HTML so every page is checked,
    # including any added later.
    m_t = re.search(r"<title>(.*?)</title>", content, re.S)
    m_d = re.search(r'name="description" content="(.*?)"', content, re.S)
    if m_t and m_d:
        _check_meta(path, m_t.group(1).strip(), m_d.group(1).strip())

    full = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# Structured data
# ---------------------------------------------------------------------------

def org_node():
    return {
        "@type": "EducationalOrganization",
        "@id": f"{SITE}/#org",
        "name": "ARSC Professional Development College",
        "alternateName": "ARSC",
        "url": f"{SITE}/",
        "logo": f"{SITE}/assets/arsc-logo-400.jpg",
        "email": EMAIL,
        "slogan": "The AI Era Begins Here",
        "description": ("Non-degree professional development, continuing education and "
                        "skills-upgrading courses in artificial intelligence, Canadian "
                        "taxation, accounting, bookkeeping, business and human resources."),
        "parentOrganization": {
            "@type": "Organization",
            "name": "Academy of Research and Sciences of Canada Inc.",
            "alternateName": "Académie de Recherche et des Sciences du Canada Inc.",
        },
        "address": {"@type": "PostalAddress", "addressRegion": "BC", "addressCountry": "CA"},
        "areaServed": {"@type": "Country", "name": "Canada"},
    }


def ldjson(nodes):
    """No aggregateRating or review markup anywhere: there are no students and
    no reviews yet. Fabricated review markup is a misrepresentation risk and a
    Google manual-action risk. Add it only when real reviews exist."""
    payload = {"@context": "https://schema.org", "@graph": nodes}
    return ('<script type="application/ld+json">\n'
            + json.dumps(payload, indent=2, ensure_ascii=False)
            + "\n</script>\n")


def course_node(c):
    return {
        "@type": "Course",
        "@id": f"{SITE}/college/{c['slug']}.html#course",
        "name": c["title"],
        "description": c["summary"],
        "courseCode": c["code"],
        "url": f"{SITE}/college/{c['slug']}.html",
        "provider": {"@id": f"{SITE}/#org"},
        "educationalCredentialAwarded": "Certificate of Completion",
        "timeRequired": f"PT{c['hours']}H",
        "inLanguage": "en-CA",
        "numberOfCredits": 0,
        "hasCourseInstance": {
            "@type": "CourseInstance",
            "courseMode": "online",
            "courseWorkload": f"PT{c['hours']}H",
        },
        "offers": {
            "@type": "AggregateOffer",
            "priceCurrency": "CAD",
            "lowPrice": str(c["low"]),
            "highPrice": str(c["high"]),
            "availability": "https://schema.org/PreOrder",
        },
        "syllabusSections": [
            {"@type": "Syllabus", "name": l, "position": i + 1}
            for i, l in enumerate(c["lessons"])
        ],
    }


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def page_home():
    root = ""
    launch = [c for c in COURSES if c["code"] in LAUNCH]
    cards = "".join(course_card(root, c) for c in launch)

    ld = ldjson([
        org_node(),
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/",
         "name": "ARSC Professional Development College", "inLanguage": "en-CA",
         "publisher": {"@id": f"{SITE}/#org"}},
        {"@type": "ItemList", "name": "ARSC course catalogue",
         "itemListElement": [
             {"@type": "ListItem", "position": i + 1,
              "url": f"{SITE}/college/{c['slug']}.html", "name": c["title"]}
             for i, c in enumerate(COURSES)]},
    ])

    body = f"""
<main id="main">

<section class="hero">

  <!-- Responsive: a phone downloads 60 KB, not the 181 KB desktop frame.
       fetchpriority=high because this is the Largest Contentful Paint
       element — the one image that must not be lazy. -->
  <div class="hero-photo" aria-hidden="true">
    <img src="assets/hero-1376.jpg"
         srcset="assets/hero-640.jpg 640w,
                 assets/hero-1000.jpg 1000w,
                 assets/hero-1376.jpg 1376w"
         sizes="100vw"
         width="1376" height="768"
         alt="" decoding="async" fetchpriority="high">
  </div>

  {rings()}
  <div class="shell">
    <div class="hero-grid">
      <div>
        <p class="eyebrow" data-reveal="fade">Education for the AI era</p>
        <h1 data-reveal style="--d:70ms">Yesterday&rsquo;s education won&rsquo;t build <span class="em">tomorrow.</span></h1>
        <p class="lede" data-reveal style="--d:150ms">
          Practical, AI-integrated professional education for people ready to
          adapt, lead and transform.
        </p>
        <div class="hero-actions" data-reveal style="--d:230ms">
          <a class="btn btn-gold" href="college/">Explore programs {ARROW}</a>
          <a class="link-rule" href="about/">Discover our mission {ARROW_DOWN}</a>
        </div>
      </div>

    </div>
  </div>
</section>

<div class="ticker" aria-hidden="true">
  <div class="ticker-track">
    <div class="ticker-run"><span>Adapt.</span><i>&#10022;</i><span>Lead.</span><i>&#10022;</i><span>Transform.</span><i>&#10022;</i><span>Build the future.</span><i>&#10022;</i></div>
    <div class="ticker-run"><span>Adapt.</span><i>&#10022;</i><span>Lead.</span><i>&#10022;</i><span>Transform.</span><i>&#10022;</i><span>Build the future.</span><i>&#10022;</i></div>
  </div>
</div>

<section class="on-light">
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">01 / Mission</p>
        <h2 data-reveal style="--d:70ms">We don&rsquo;t teach the past.<br><span class="em">We build the future.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        We are building the bridge between traditional education and the future
        of artificial intelligence.
      </p>
    </div>
    <div class="steps">
      <div class="step" data-reveal><p class="step-no">01</p><div class="step-rule"></div>
        <h3>Learn what matters now</h3>
        <p>Curriculum shaped around today&rsquo;s tools, standards and workplace realities &mdash; reviewed every year, because tax legislation, CRA procedures and AI tooling all change quickly.</p></div>
      <div class="step" data-reveal style="--d:120ms"><p class="step-no">02</p><div class="step-rule"></div>
        <h3>Practice before it counts</h3>
        <p>Realistic scenarios turn knowledge into repeatable professional skill. Coursework uses simulated client files, so you practise on real problems without real exposure.</p></div>
      <div class="step" data-reveal style="--d:240ms"><p class="step-no">03</p><div class="step-rule"></div>
        <h3>Lead the change</h3>
        <p>Use AI responsibly &mdash; not as a shortcut, but as a professional advantage. Every AI course covers privacy, limitations, and where human review is mandatory.</p></div>
    </div>
    <div class="hero-actions" style="margin-top:var(--sp-2xl)" data-reveal="fade">
      <a class="btn btn-line" href="about/">Read our mission and vision {ARROW}</a>
    </div>
  </div>
</section>

<section>
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">02 / Programs</p>
        <h2 data-reveal style="--d:70ms">Skills for the<br><span class="em">world ahead.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        Short, focused professional-development courses for working professionals,
        newcomers and business owners. Twelve courses across four schools.
      </p>
    </div>
    <div class="courses is-four" data-reveal="fade">{cards}</div>
    <div class="hero-actions" style="margin-top:var(--sp-lg)" data-reveal="fade">
      <a class="btn btn-line" href="college/">See all 12 courses {ARROW}</a>
    </div>
  </div>
</section>

<div class="split" aria-hidden="true">
  <div class="a">Professional education</div><div class="b"></div><div class="c">Real-world practice</div>
</div>

<section>
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">03 / One organization, two divisions</p>
        <h2 data-reveal style="--d:70ms">From education<br><span class="em">to innovation.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        ARSC operates an education division and a professional services division,
        run separately, under one corporate structure.
      </p>
    </div>
    <div class="divisions">
      <article class="division" data-reveal>
        <span class="division-tag">Division One</span>
        <h3>ARSC Professional Development College</h3>
        <p>Practical education for modern business. Online professional development across four schools.</p>
        <ul><li>Artificial intelligence and AI applications</li><li>Canadian taxation and accounting</li><li>Bookkeeping and payroll administration</li><li>Business management and startup</li><li>Human resources and administration</li></ul>
        <a class="btn btn-line" href="college/">Visit the College {ARROW}</a>
      </article>
      <article class="division" data-reveal style="--d:110ms">
        <span class="division-tag">Division Two</span>
        <h3>ARSC Accounting, Tax &amp; Business Advisory</h3>
        <p>Professional support for individuals and growing businesses, delivered separately from the college.</p>
        <ul><li>Personal and business tax preparation</li><li>Monthly bookkeeping and payroll</li><li>GST/HST and PST assistance</li><li>Business registration and startup support</li><li>HR administration and recruitment</li><li>AI implementation and automation</li></ul>
        <a class="btn btn-line" href="advisory/">Visit Advisory Services {ARROW}</a>
      </article>
    </div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">Your next chapter</p>
    <h2 data-reveal style="--d:70ms">Ready to build<br><span class="em">what&rsquo;s next?</span></h2>
    <p class="lede" data-reveal style="--d:150ms">
      Join the first community of professionals learning to lead in an AI-shaped world.
    </p>
    <a class="btn btn-gold" href="enroll/" data-reveal style="--d:230ms">Start a conversation {ARROW_UR}</a>
  </div>
</section>

</main>
"""
    return write("index.html",
                 head(root, "ARSC Professional Development College | British Columbia",
                      "Online professional development in AI, Canadian taxation, accounting, bookkeeping, payroll, business and HR. Non-degree certificates, British Columbia.",
                      "/", ld,
                      "professional development courses BC, online accounting course Canada, "
                      "Canadian tax course online, bookkeeping course Vancouver, AI training for professionals, "
                      "payroll course Canada, continuing education British Columbia")
                 + header(root, "") + body + footer(root))


def page_college():
    root = "../"
    blocks = []
    for name, full in SCHOOLS:
        cs = [c for c in COURSES if c["school"] == name]
        lis = "".join(
            f'<li><a href="{c["slug"]}.html"><span>{c["title"]}</span><em>{c["hours"]} hrs</em></a></li>'
            for c in cs)
        blocks.append(f'<div class="school" id="school-{slugify(name)}" data-reveal>'
                      f'<h3>{full}</h3><ul>{lis}</ul></div>')

    # This page already lives in /college/, so course links are siblings:
    # no root prefix, no directory prefix.
    cards = "".join(course_card("", c, prefix="") for c in COURSES)

    ld = ldjson([org_node(), {
        "@type": "ItemList", "name": "ARSC course catalogue",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": course_node(c)}
            for i, c in enumerate(COURSES)]}])

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("The College", None)])}
    <p class="eyebrow" data-reveal="fade">Division One</p>
    <h1 data-reveal style="--d:70ms">ARSC Professional<br><span class="em">Development College</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Twelve online courses across four schools. Every course is non-degree
      professional development, delivered online, with a certificate of
      completion on finishing.
    </p>
  </div>
</section>

<section class="tight">
  <div class="shell">
    <h2 class="visually-hidden">Schools and courses</h2>
    <div class="schools">{''.join(blocks)}</div>
  </div>
</section>

<section class="on-light">
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">Full catalogue</p>
        <h2 data-reveal style="--d:70ms">Every course,<br><span class="em">with what&rsquo;s inside it.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        Each course page lists every lesson, the hours, the price, and what you
        should be able to do at the end.
      </p>
    </div>
    <div class="courses is-three" data-reveal="fade">{cards}</div>
  </div>
</section>

<section>
  <div class="shell">
    <div class="head solo">
      <div>
        <p class="marker" data-reveal="fade">Before you enrol</p>
        <h2 data-reveal style="--d:70ms">What ARSC is &mdash;<br><span class="em">and what it is not.</span></h2>
      </div>
    </div>
    <div class="on-dark faq" data-reveal="fade">
      {faq_items([
        ("What kind of certificate do I receive?",
         "Depending on the program: a Certificate of Completion, a Professional Development Certificate, a Continuing Education Certificate, or a Record of Training. These confirm successful completion of private professional development training. They are not academic degrees, government licences, regulated professional designations, or provincially recognised career-training diplomas."),
        ("Will these courses make me a CPA or a licensed bookkeeper?",
         "No. ARSC courses are professional development and skills upgrading. They are not a substitute for regulated accounting, CPA, legal or human resources professional designations. The CPA designation is granted solely by the applicable provincial body."),
        ("Who are these courses designed for?",
         "Working professionals adding AI and technical skills, newcomers to Canada building familiarity with Canadian tax and business practice, and small business owners who want to understand their own books, payroll and obligations."),
        ("How are courses delivered?",
         "Online, as recorded video lessons you work through at your own pace, with downloadable notes and worksheets. Each course page lists its full lesson sequence."),
        ("Is there practical training?",
         "Coursework uses simulated tax, payroll and bookkeeping files. Selected graduates may be invited into the ARSC Professional Practice Program — supervised, paid trainee placements within the advisory division. Trainees never independently provide services to clients."),
      ])}
    </div>
    <div class="notice on-dark" data-reveal="fade">
      <strong>Regulatory disclosure</strong>
      {DISCLOSURE}
    </div>
  </div>
</section>

</main>
"""
    return write("college/index.html",
                 head(root, "Course Catalogue — 12 Online Courses | ARSC College",
                      "Twelve online professional development courses in artificial intelligence, Canadian taxation and accounting, business, entrepreneurship and human resources.",
                      "/college/", ld,
                      "online bookkeeping course Canada, Canadian personal tax course, "
                      "payroll administration course, small business accounting course, AI for accountants")
                 + header(root, "college/") + body + footer(root))


def faq_items(pairs):
    out = []
    for i, (q, a) in enumerate(pairs, 1):
        out.append(f"""
      <div class="qa">
        <h3><button class="qa-btn" aria-expanded="false" aria-controls="qa{i}" id="qa{i}-btn">
          {q}<span class="qa-icon" aria-hidden="true"></span>
        </button></h3>
        <div class="qa-panel" id="qa{i}" role="region" aria-labelledby="qa{i}-btn"><div>
          <p>{a}</p>
        </div></div>
      </div>""")
    return "".join(out)


def page_course(c):
    root = "../"

    lessons = []
    for i, l in enumerate(c["lessons"], 1):
        cur = ' aria-current="true"' if i == 1 else ""
        lessons.append(
            f'<li><button class="lesson"{cur} data-yt-id="" data-lesson-no="{i:02d}" '
            f'data-lesson-title="{l}">'
            f'<span class="lesson-no">{i:02d}</span>'
            f'<span class="lesson-name">{l}</span>'
            f'<span class="lesson-time"></span></button></li>')

    outcomes = "".join(f"<li>{o}</li>" for o in c["outcomes"])

    tools = TOOLS.get(c["code"], [])
    tools_block = ""
    if tools:
        chips = "".join(
            f'<span class="tool{" is-planned" if planned else ""}">{name}'
            f'{" &middot; planned" if planned else ""}</span>'
            for name, planned in tools)
        tools_block = (
            '<h2 style="margin-top:var(--sp-xl);font-size:clamp(1.5rem,1.3rem+0.8vw,1.9rem)" data-reveal="fade">Tools covered</h2>'
            f'<div class="tools" style="margin-top:var(--sp-md)" data-reveal="fade">{chips}</div>'
            '<p style="margin-top:12px;font-size:13.5px;opacity:.75">'
            'Items marked <em>planned</em> are scheduled for a future revision of this '
            'course and are not part of the current syllabus.</p>')

    RELEVANCE = {
        "Artificial Intelligence": [
            ("Where these skills are used",
             "Administrative and analyst roles where routine drafting, research and document handling consume the day."),
            ("Who tends to take it",
             "Working professionals adding AI capability, and practice staff who want to speed up without cutting corners."),
        ],
        "Taxation and Accounting": [
            ("Where these skills are used",
             "Bookkeeping and accounting support work, seasonal tax preparation support, and owner-operators handling their own records."),
            ("Who tends to take it",
             "Career changers, newcomers building Canadian practice familiarity, and small business owners."),
        ],
        "Business and Entrepreneurship": [
            ("Where these skills are used",
             "Running or managing a small business — operations, budgets, pricing and planning."),
            ("Who tends to take it",
             "New and prospective business owners, and staff stepping into management."),
        ],
        "Human Resources": [
            ("Where these skills are used",
             "HR and office administration, employee records, onboarding and hiring coordination."),
            ("Who tends to take it",
             "Administrators taking on HR duties, and small employers with no HR department."),
        ],
    }
    rel = RELEVANCE.get(c["school"], [])
    relevance_block = ""
    if rel:
        cells = "".join(f"<div><h3>{t}</h3><p>{b}</p></div>" for t, b in rel)
        relevance_block = (
            '<h2 style="margin-top:var(--sp-xl);font-size:clamp(1.5rem,1.3rem+0.8vw,1.9rem)" data-reveal="fade">Context</h2>'
            f'<div class="relevance" style="margin-top:var(--sp-md)" data-reveal="fade">{cells}</div>'
            '<p style="margin-top:14px;font-size:13.5px;opacity:.75">'
            'This describes where the subject matter is applied. It is not a '
            'statement about employment outcomes, and ARSC does not guarantee '
            'employment or provide job placement.</p>')
    others = [x for x in COURSES if x["school"] == c["school"] and x["code"] != c["code"]]
    # Sibling pages inside /college/ — no root prefix.
    related = "".join(course_card("", x, prefix="") for x in others[:3])

    ld = ldjson([org_node(), course_node(c), {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "The College", "item": f"{SITE}/college/"},
            {"@type": "ListItem", "position": 3, "name": c["title"],
             "item": f"{SITE}/college/{c['slug']}.html"},
        ]}])

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("The College", "college/"), (c["title"], None)])}

    <div class="course-hero-grid">
      <div>
        <p class="eyebrow" data-reveal="fade">{c['code']} &nbsp;&middot;&nbsp; School of {c['school']}</p>
        <h1 data-reveal style="--d:70ms">{c['title']}</h1>
        <p class="lede" data-reveal style="--d:150ms">{c['summary']}</p>

        <h2 style="margin-top:var(--sp-xl);font-size:clamp(1.5rem,1.3rem+0.8vw,1.9rem)" data-reveal="fade">What you will be able to do</h2>
        <ul class="division" style="border:0;padding:var(--sp-md) 0 0;list-style:none;margin:0;display:grid;gap:9px" data-reveal="fade">
          {outcomes}
        </ul>

        {tools_block}
        {relevance_block}
      </div>

      <aside class="buy-card" data-reveal="right" aria-labelledby="enrol-heading">
        <h2 id="enrol-heading" class="visually-hidden">Enrolment</h2>
        <div class="buy-price">
          <span class="amount">${money(c['low'])}</span>
          <span class="unit">&ndash; ${money(c['high'])} CAD</span>
        </div>
        <p class="buy-note">Final price depends on cohort and materials. Instalment plans available.</p>

        <ul class="buy-specs">
          <li><span class="k">Course code</span><span class="v">{c['code']}</span></li>
          <li><span class="k">Instructional hours</span><span class="v">{c['hours']}</span></li>
          <li><span class="k">Lessons</span><span class="v">{len(c['lessons'])}</span></li>
          <li><span class="k">Delivery</span><span class="v">Online, self-paced</span></li>
          <li><span class="k">Credential</span><span class="v">Certificate of Completion</span></li>
          <li><span class="k">Prerequisites</span><span class="v">{c['prereq']}</span></li>
          <li><span class="k">Intake</span><span class="v">Rolling &mdash; start any time</span></li>
          <li><span class="k">Access</span><span class="v">12 months from enrolment</span></li>
        </ul>

        <a class="btn btn-gold btn-block" href="{root}enroll/?course={c['slug']}">Request enrolment {ARROW}</a>
        <a class="btn btn-line btn-block" style="margin-top:12px" href="{root}contact/">Ask a question {ARROW}</a>
      </aside>
    </div>
  </div>
</section>

<section class="tight">
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">Syllabus</p>
        <h2 data-reveal style="--d:70ms">All {len(c['lessons'])} lessons,<br><span class="em">in order.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        Select a lesson to open its video. Lessons still in production are marked
        &ldquo;soon&rdquo; &mdash; the rest play in place.
      </p>
    </div>

    <div class="player-grid" data-reveal="fade">
      <div class="video-wrap">
        <button class="lite-yt" id="ytPlayer" data-yt-id="" data-yt-title="{c['lessons'][0]}"
                aria-label="Play the selected lesson">
          <span class="lite-yt-face">
            <span class="lite-yt-play"><svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.14v13.72L19 12 8 5.14Z"/></svg></span>
            <span class="lite-yt-label">Play lesson</span>
          </span>
        </button>
        <p class="now-playing" id="nowPlaying" aria-live="polite">
          <b>Lesson 01</b> <span>{c['lessons'][0]}</span>
        </p>
      </div>

      <div>
        <p class="lesson-head"><span>{c['title']}</span><span>{c['hours']} hrs</span></p>
        <ol class="lesson-list">{''.join(lessons)}</ol>
      </div>
    </div>
  </div>
</section>

<section class="on-light">
  <div class="shell">
    <div class="head solo">
      <div>
        <p class="marker" data-reveal="fade">Also in this school</p>
        <h2 data-reveal style="--d:70ms">School of <span class="em">{c['school']}</span></h2>
      </div>
    </div>
    <div class="courses is-three" data-reveal="fade">{related}</div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">{c['code']}</p>
    <h2 data-reveal style="--d:70ms">Enrol in<br><span class="em">{c['title']}</span></h2>
    <p class="lede" data-reveal style="--d:150ms">
      Submit an enrolment request and an advisor will confirm the next intake,
      the final price, and whether this is the right course for you.
    </p>
    <a class="btn btn-gold" href="{root}enroll/?course={c['slug']}" data-reveal style="--d:230ms">Request enrolment {ARROW}</a>
  </div>
</section>

</main>
"""
    return write(f"college/{c['slug']}.html",
                 head(root, course_title(c), course_desc(c), f"/college/{c['slug']}.html", ld,
                      course_keywords(c))
                 + header(root, "college/") + body + footer(root))


def page_advisory():
    root = "../"
    ld = ldjson([org_node(), {
        "@type": "Organization",
        "name": "ARSC Accounting, Tax & Business Advisory",
        "parentOrganization": {"@id": f"{SITE}/#org"},
        "url": f"{SITE}/advisory/",
        "areaServed": {"@type": "Country", "name": "Canada"},
    }])

    groups = [
        ("Accounting &amp; Bookkeeping", [
            "Monthly bookkeeping", "Bank and credit card reconciliations",
            "Accounts payable and receivable support", "Expense categorization",
            "Year-end bookkeeping packages", "QuickBooks setup and support",
            "Management reports"]),
        ("Taxation", [
            "Personal income tax preparation", "Self-employment tax returns",
            "GST/HST return preparation", "T4 and T4A preparation",
            "CRA correspondence support", "Notice of Assessment review",
            "Tax document organization"]),
        ("Payroll", [
            "Payroll administration", "Statutory deduction processing",
            "Remittance coordination", "T4 preparation and filing",
            "Payroll reconciliation", "Record management"]),
        ("Business Startup", [
            "Business registration administration", "Business number applications",
            "GST/HST and payroll account setup", "Business planning and budgeting",
            "Record-keeping systems", "Accounting software implementation"]),
        ("Human Resources", [
            "Job descriptions", "Recruitment coordination", "Resume screening",
            "Onboarding documentation", "Employee file setup",
            "Workplace policy templates", "Performance review administration"]),
        ("AI &amp; Automation", [
            "AI workflow review", "Prompt library development",
            "Automated intake forms", "Document processing workflows",
            "AI training for staff", "Responsible AI implementation"]),
    ]

    cards = "".join(
        f'<article class="division" data-reveal style="--d:{i*80}ms">'
        f'<span class="division-tag">{i+1:02d}</span><h3>{name}</h3>'
        f'<ul>{"".join(f"<li>{s}</li>" for s in items)}</ul>'
        f'<a class="btn btn-line" href="{root}contact/">Enquire {ARROW}</a></article>'
        for i, (name, items) in enumerate(groups))

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("Advisory Services", None)])}
    <p class="eyebrow" data-reveal="fade">Division Two</p>
    <h1 data-reveal style="--d:70ms">ARSC Accounting, Tax<br>&amp; <span class="em">Business Advisory</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Professional support for individuals and growing businesses. Operated
      separately from the College, with its own contracts, client records and
      compliance procedures.
    </p>
  </div>
</section>

<section class="tight">
  <div class="shell">
    <h2 class="visually-hidden">Services offered</h2>
    <div class="divisions" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">{cards}</div>

    <div class="notice on-dark" data-reveal="fade">
      <strong>How the two divisions are separated</strong>
      The College and the Advisory division maintain separate service descriptions,
      contracts, student and client records, revenue categories, and compliance
      procedures. Student learning-platform access never grants access to client
      systems. Legal advice, immigration advice and regulated accounting opinions
      are referred to appropriately licensed professionals.
    </div>
  </div>
</section>

<section class="on-light">
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">Professional Practice Program</p>
        <h2 data-reveal style="--d:70ms">Where graduates<br><span class="em">meet real work.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        Selected College graduates may be invited into supervised, paid trainee
        placements inside the Advisory division.
      </p>
    </div>

    <div class="steps">
      <div class="step" data-reveal><p class="step-no">01</p><div class="step-rule"></div>
        <h3>Simulation first</h3>
        <p>Trainees begin on simulated tax, payroll and bookkeeping files. No real client data is touched until confidentiality training is complete and access is granted individually.</p></div>
      <div class="step" data-reveal style="--d:120ms"><p class="step-no">02</p><div class="step-rule"></div>
        <h3>Always supervised</h3>
        <p>Every trainee is assigned a qualified supervisor who assigns work, reviews all of it, and approves anything that reaches a client or the CRA. Trainees never independently provide services.</p></div>
      <div class="step" data-reveal style="--d:240ms"><p class="step-no">03</p><div class="step-rule"></div>
        <h3>Paid, and documented</h3>
        <p>Placements are paid trainee contracts with logged hours, written evaluations, and a completion certificate that states plainly what it is and is not.</p></div>
    </div>

    <div class="notice" data-reveal="fade">
      <strong>What the practical training certificate is not</strong>
      A Certificate of Practical Training Completion confirms supervised practical
      training only. It does not represent a professional licence, CPA designation,
      regulated credential, or authorization to independently provide accounting or
      taxation services. Clients are informed when a supervised trainee may assist
      on their file, and may decline trainee involvement.
    </div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">Advisory Services</p>
    <h2 data-reveal style="--d:70ms">Let&rsquo;s talk about<br><span class="em">what you need.</span></h2>
    <p class="lede" data-reveal style="--d:150ms">
      Tell us the service and the timeline. We will tell you honestly whether we
      are the right fit, and refer you on where we are not.
    </p>
    <a class="btn btn-gold" href="{root}contact/" data-reveal style="--d:230ms">Contact the Advisory team {ARROW}</a>
  </div>
</section>

</main>
"""
    return write("advisory/index.html",
                 head(root, "Accounting, Tax and Business Advisory | ARSC",
                      "Bookkeeping, personal and business tax preparation, payroll, GST/HST, business registration and HR administration for growing Canadian businesses.",
                      "/advisory/", ld,
                      "bookkeeping services BC, personal tax preparation Canada, GST HST filing, "
                      "payroll services British Columbia, business registration BC, CRA correspondence support")
                 + header(root, "advisory/") + body + footer(root))


def page_about():
    root = "../"
    ld = ldjson([org_node(), {
        "@type": "AboutPage", "url": f"{SITE}/about/",
        "name": "About ARSC", "publisher": {"@id": f"{SITE}/#org"}}])

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("About", None)])}
    <p class="eyebrow" data-reveal="fade">About ARSC</p>
    <h1 data-reveal style="--d:70ms">Educating the leaders<br><span class="em">of the AI era.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Artificial intelligence is reshaping every profession, every industry and
      every workplace. Our mission is to ensure that individuals, businesses and
      communities are prepared not merely to adapt to this change, but to lead it.
    </p>
  </div>
</section>

<section class="on-light tight">
  <div class="shell">
    <h2 class="visually-hidden">Mission, vision and philosophy</h2>
    <div class="steps" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">
      <div class="step" data-reveal><p class="step-no">Mission</p><div class="step-rule"></div>
        <h3>What we are here to do</h3>
        <p>To transform education and professional development by integrating artificial intelligence into every aspect of learning, business and workforce development. We believe the future belongs to people who know how to lead, innovate and work alongside AI, rather than compete with it.</p></div>
      <div class="step" data-reveal style="--d:110ms"><p class="step-no">Vision</p><div class="step-rule"></div>
        <h3>Where we are going</h3>
        <p>To become Canada&rsquo;s leading AI-driven professional development institution and business services organization, preparing individuals and businesses for the future of work.</p></div>
      <div class="step" data-reveal style="--d:220ms"><p class="step-no">Philosophy</p><div class="step-rule"></div>
        <h3>AI Works. Humans Lead.</h3>
        <p>The traditional model of education no longer reflects the realities of the modern world. We are building a new generation of AI-driven professionals, entrepreneurs and leaders &mdash; with human judgement kept firmly in charge.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">Structure</p>
        <h2 data-reveal style="--d:70ms">One corporation,<br><span class="em">two divisions.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        ARSC operates as an integrated model with deliberately separated
        operations.
      </p>
    </div>

    <div class="table-wrap on-dark" data-reveal="fade">
      <table>
        <caption class="visually-hidden">ARSC corporate structure</caption>
        <thead><tr><th scope="col">Entity</th><th scope="col">Role</th><th scope="col">Public name</th></tr></thead>
        <tbody>
          <tr><td><strong>Parent corporation</strong></td><td>British Columbia corporation</td><td>Academy of Research and Sciences of Canada Inc.</td></tr>
          <tr><td><strong>Division one</strong></td><td>Education and continuing education</td><td>ARSC Professional Development College</td></tr>
          <tr><td><strong>Division two</strong></td><td>Professional services</td><td>ARSC Accounting, Tax &amp; Business Advisory</td></tr>
          <tr><td><strong>Training program</strong></td><td>Supervised practical experience</td><td>ARSC Professional Practice Program</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="on-light">
  <div class="shell">
    <div class="prose" data-reveal="fade">
      <p class="marker">Regulatory position</p>
      <h2>Honest about what we are.</h2>

      <p style="margin-top:var(--sp-md)">
        ARSC provides short professional development and continuing education
        courses. We are deliberately explicit about the limits of what that means,
        because the alternative misleads the people we are trying to help.
      </p>

      <h3>What ARSC issues</h3>
      <ul>
        <li>Certificate of Completion</li>
        <li>Professional Development Certificate</li>
        <li>Continuing Education Certificate</li>
        <li>Record of Training</li>
        <li>Certificate of Practical Training Completion</li>
      </ul>

      <h3>What ARSC does not issue</h3>
      <ul>
        <li>Academic degrees</li>
        <li>Government-recognized diplomas</li>
        <li>Regulated professional licences</li>
        <li>CPA designations</li>
        <li>Government accreditation</li>
        <li>Immigration-related educational credentials</li>
      </ul>

      <p>
        The CPA designation is granted solely by the applicable provincial body.
        ARSC is not affiliated with, endorsed by, or accredited by CPA Canada or
        CPA British Columbia.
      </p>
    </div>

    <div class="notice" data-reveal="fade">
      <strong>Required disclosure</strong>
      {DISCLOSURE}
    </div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">ARSC</p>
    <h2 data-reveal style="--d:70ms">The AI era<br><span class="em">begins here.</span></h2>
    <a class="btn btn-gold" href="{root}college/" data-reveal style="--d:150ms">Explore the courses {ARROW}</a>
  </div>
</section>

</main>
"""
    return write("about/index.html",
                 head(root, "About ARSC — Mission, Vision and Regulatory Position",
                      "Our mission, vision and corporate structure, plus a plain statement of what ARSC certificates are and are not. Non-degree training in British Columbia.",
                      "/about/", ld,
                      "ARSC College, professional development college BC, "
                      "non-degree certificate Canada, Academy of Research and Sciences of Canada")
                 + header(root, "about/") + body + footer(root))


def page_enroll():
    root = "../"
    opts = "".join(
        f'<option value="{c["slug"]}">{c["code"]} — {c["title"]} ({c["hours"]} hrs)</option>'
        for c in COURSES)

    ld = ldjson([org_node()])

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("Enrol", None)])}
    <p class="eyebrow" data-reveal="fade">Enrolment</p>
    <h1 data-reveal style="--d:70ms">Request your<br><span class="em">place on a course.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Tell us which course you want and an advisor will confirm the next intake,
      the final price, and whether it is genuinely the right fit for you.
    </p>
  </div>
</section>

<section class="on-light tight">
  <div class="shell">
    <div class="form-grid">

      <form id="enrolForm" data-reveal="fade" novalidate>
        <div class="field">
          <label for="course">Course</label>
          <select id="course" name="course" required>
            <option value="">Select a course&hellip;</option>
            {opts}
          </select>
        </div>

        <div class="field">
          <label for="name">Full name</label>
          <input id="name" name="name" type="text" autocomplete="name" required>
        </div>

        <div class="field">
          <label for="email">Email</label>
          <input id="email" name="email" type="email" autocomplete="email" required>
          <span class="hint">We reply within two business days.</span>
        </div>

        <div class="field">
          <label for="phone">Phone <span style="text-transform:none;letter-spacing:0">(optional)</span></label>
          <input id="phone" name="phone" type="tel" autocomplete="tel">
        </div>

        <div class="field">
          <label for="background">Your background</label>
          <textarea id="background" name="background" placeholder="What are you trying to reach? Any relevant experience?"></textarea>
          <span class="hint">This helps the advisor tell you honestly whether the course fits.</span>
        </div>

        <button class="btn btn-gold btn-block" type="submit">Send enrolment request {ARROW}</button>

        <div class="form-note">
          <strong>Note:</strong> online payment is not connected yet. This form
          opens an email addressed to admissions with your details filled in, so
          nothing is transmitted to a third party. Once a payment gateway is
          live, this becomes a direct checkout.
        </div>
      </form>

      <div data-reveal="right">
        <h2 style="font-size:clamp(1.4rem,1.2rem+0.7vw,1.8rem)">What happens next</h2>
        <ol class="prose" style="margin-top:var(--sp-md)">
          <li>An advisor reviews your request and replies within two business days.</li>
          <li>You get a short, honest conversation about fit &mdash; including being told if a cheaper or different option would serve you better.</li>
          <li>If you go ahead, you receive the enrolment agreement, the refund policy, and a payment link.</li>
          <li>Access opens at the start of your intake, and your certificate is issued on completion.</li>
        </ol>

        <div class="notice">
          <strong>Before you pay anything</strong>
          Read the enrolment agreement and refund policy in full. Both are linked
          from the <a href="{root}policies/">policies page</a>. If any claim made
          to you verbally is not written there, ask for it in writing.
        </div>
      </div>

    </div>
  </div>
</section>

</main>

<script>
/* Pre-select the course from ?course=slug so the buttons on each course page
   land here with the right option already chosen. */
(function () {{
  var params = new URLSearchParams(location.search);
  var slug = params.get("course");
  var select = document.getElementById("course");
  if (slug && select) {{
    var match = select.querySelector('option[value="' + slug.replace(/"/g, "") + '"]');
    if (match) select.value = slug;
  }}

  /* No backend yet: compose a mailto so the request still reaches a human and
     nothing is posted to a third-party endpoint. */
  var form = document.getElementById("enrolForm");
  if (!form) return;

  form.addEventListener("submit", function (e) {{
    e.preventDefault();
    if (!form.checkValidity()) {{ form.reportValidity(); return; }}

    var get = function (id) {{ return (document.getElementById(id) || {{}}).value || ""; }};
    var sel = document.getElementById("course");
    var courseLabel = sel.options[sel.selectedIndex].text;

    var body = [
      "Course: " + courseLabel,
      "Name: " + get("name"),
      "Email: " + get("email"),
      "Phone: " + get("phone"),
      "",
      "Background:",
      get("background")
    ].join("\\n");

    location.href = "mailto:{EMAIL}"
      + "?subject=" + encodeURIComponent("Enrolment request — " + courseLabel)
      + "&body=" + encodeURIComponent(body);
  }});
}})();
</script>
"""
    return write("enroll/index.html",
                 head(root, "Enrol in a Course | ARSC College",
                      "Request enrolment in an ARSC professional development course. An advisor confirms the next intake, the price and whether the course genuinely fits you.",
                      "/enroll/", ld,
                      "enrol online course Canada, professional development enrolment, "
                      "accounting course registration BC")
                 + header(root, "enroll/") + body + footer(root))


def page_contact():
    root = "../"
    ld = ldjson([org_node(), {
        "@type": "ContactPage", "url": f"{SITE}/contact/",
        "name": "Contact ARSC", "publisher": {"@id": f"{SITE}/#org"}}])

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("Contact", None)])}
    <p class="eyebrow" data-reveal="fade">Contact</p>
    <h1 data-reveal style="--d:70ms">Talk to<br><span class="em">a real person.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Whether it is a course question or an advisory enquiry, tell us what you
      need and we will point you to the right side of the organization.
    </p>
  </div>
</section>

<section class="on-light tight">
  <div class="shell">
    <div class="form-grid">

      <form id="contactForm" data-reveal="fade" novalidate>
        <div class="field">
          <label for="topic">What is this about?</label>
          <select id="topic" name="topic" required>
            <option value="">Select&hellip;</option>
            <option value="Course enquiry">A course (the College)</option>
            <option value="Advisory enquiry">Accounting, tax or HR services (Advisory)</option>
            <option value="Employer training">Employer or group training</option>
            <option value="Practical training">The Professional Practice Program</option>
            <option value="Privacy request">A privacy or records request</option>
            <option value="Other">Something else</option>
          </select>
        </div>

        <div class="field">
          <label for="cname">Full name</label>
          <input id="cname" name="name" type="text" autocomplete="name" required>
        </div>

        <div class="field">
          <label for="cemail">Email</label>
          <input id="cemail" name="email" type="email" autocomplete="email" required>
        </div>

        <div class="field">
          <label for="message">Message</label>
          <textarea id="message" name="message" required></textarea>
          <span class="hint">Please do not include SINs, banking details, or tax documents in this form.</span>
        </div>

        <button class="btn btn-gold btn-block" type="submit">Send message {ARROW}</button>

        <div class="form-note">
          <strong>Note:</strong> this form opens an email in your own mail app with
          the details filled in. Nothing is transmitted to a third-party form
          service, which is deliberate while secure intake is being set up.
        </div>
      </form>

      <div data-reveal="right">
        <h2 style="font-size:clamp(1.4rem,1.2rem+0.7vw,1.8rem)">Direct</h2>
        <ul class="buy-specs" style="margin-top:var(--sp-md)">
          <li><span class="k">Email</span><span class="v"><a href="mailto:{EMAIL}" style="color:var(--gold-deep)">{EMAIL}</a></span></li>
          <li><span class="k">Website</span><span class="v">arscollegecanada.ca</span></li>
          <li><span class="k">Location</span><span class="v">British Columbia, Canada</span></li>
          <li><span class="k">Delivery</span><span class="v">Online</span></li>
        </ul>

        <div class="notice">
          <strong>Never send sensitive documents by email</strong>
          Social insurance numbers, tax returns, Notices of Assessment, banking
          information and identification documents must not be sent through
          ordinary email. Advisory clients receive access to a secure document
          portal for exactly this reason. If you are unsure, ask first.
        </div>

        <div class="notice">
          <strong>Privacy requests</strong>
          To ask what personal information we hold, request a correction, or make
          a privacy complaint, choose &ldquo;a privacy or records request&rdquo;
          above. Our handling of personal information is described on the
          <a href="{root}policies/">policies page</a>.
        </div>
      </div>

    </div>
  </div>
</section>

</main>

<script>
(function () {{
  var form = document.getElementById("contactForm");
  if (!form) return;
  form.addEventListener("submit", function (e) {{
    e.preventDefault();
    if (!form.checkValidity()) {{ form.reportValidity(); return; }}
    var get = function (id) {{ return (document.getElementById(id) || {{}}).value || ""; }};
    var sel = document.getElementById("topic");
    var topic = sel.options[sel.selectedIndex].text;
    var body = ["Topic: " + topic, "Name: " + get("cname"), "Email: " + get("cemail"), "", get("message")].join("\\n");
    location.href = "mailto:{EMAIL}?subject=" + encodeURIComponent("Website enquiry — " + topic)
      + "&body=" + encodeURIComponent(body);
  }});
}})();
</script>
"""
    return write("contact/index.html",
                 head(root, "Contact ARSC College and Advisory Services",
                      "Contact ARSC about a course, accounting and tax services, employer training, the Professional Practice Program, or a privacy request. Based in BC, Canada.",
                      "/contact/", ld,
                      "contact ARSC, accounting services enquiry BC, course advisor Canada")
                 + header(root, "contact/") + body + footer(root))


def page_policies():
    root = "../"
    ld = ldjson([org_node()])

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("Policies", None)])}
    <p class="eyebrow" data-reveal="fade">Policies</p>
    <h1 data-reveal style="--d:70ms">The rules,<br><span class="em">written down.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Everything a student or client is entitled to know before paying us
      anything. If a claim was made to you verbally and is not written here,
      ask for it in writing.
    </p>
  </div>
</section>

<section class="on-light">
  <div class="shell">
    <h2 class="visually-hidden">Policy summaries</h2>
    <div class="prose" data-reveal="fade">

      <div class="notice" style="margin-top:0">
        <strong>Drafting status</strong>
        The summaries below describe the policies ARSC is required to publish and
        maintain. Each one must be reviewed by legal counsel and finalised before
        courses are sold. Placeholder text is marked as such &mdash; do not treat
        an unmarked summary as a completed legal document.
      </div>

      <h3>Regulatory disclosure</h3>
      <p>{DISCLOSURE}</p>
      <p>{DISCLOSURE_2}</p>

      <h3>Enrolment agreement</h3>
      <p>
        Before payment, every student receives a written enrolment agreement
        covering terms of enrolment, payment terms, the refund policy, access
        duration, technology requirements, acceptable use, academic integrity,
        and the complaint resolution procedure.
      </p>
      <h4>To be confirmed before launch</h4>
      <ul>
        <li>Access duration per course &mdash; a fixed, renewable term rather than an open-ended promise</li>
        <li>Instalment schedule and any administration fee</li>
        <li>Whether course materials may be downloaded and retained</li>
      </ul>

      <h3>Refund policy</h3>
      <p>
        The refund policy must state the cancellation window, the basis for
        proration after that window, how refunds are issued, and the timeline.
        It must be provided in writing before payment and must not be less
        favourable than any applicable statutory minimum.
      </p>

      <h3>Complaint resolution</h3>
      <p>
        Students and clients may raise a complaint in writing and receive a
        written response. The procedure must name who reviews complaints, the
        response timeline, the escalation path, and the external avenues
        available if the outcome is unsatisfactory.
      </p>

      <h3>Academic integrity and AI use</h3>
      <p>
        Assessed work must be a student&rsquo;s own. Because ARSC teaches AI
        tools, the AI use policy states explicitly where AI assistance is
        expected, where it must be disclosed, and where it is not permitted in
        assessment.
      </p>

      <h3>Accessibility</h3>
      <p>
        ARSC works toward WCAG 2.1 AA. This website is built to that standard:
        colour contrast is verified, all functionality is keyboard reachable,
        focus states are visible, motion respects the operating-system
        reduced-motion setting, and touch targets meet minimum sizes.
      </p>
      <h4>Committed for course content</h4>
      <ul>
        <li>Captions on every video lesson</li>
        <li>Downloadable transcripts</li>
        <li>An accommodation request process with a named contact</li>
      </ul>

      <h3>Privacy</h3>
      <p>
        ARSC is a private organization in British Columbia and handles personal
        information under the province&rsquo;s Personal Information Protection
        Act. The published privacy policy must describe what is collected, how
        it is used, when it is disclosed, how long it is retained, how to
        request access or correction, and how a breach is handled.
      </p>
      <h4>Required before any client data is collected</h4>
      <ul>
        <li>A named Privacy Officer with published contact details</li>
        <li>Written retention periods per record type</li>
        <li>A breach response plan</li>
        <li>Confirmation of where data is stored, and disclosure if stored outside Canada</li>
      </ul>

      <div class="notice">
        <strong>Sensitive information</strong>
        Social insurance numbers, tax returns, Notices of Assessment, banking
        information and identification documents must never be sent by ordinary
        email. Advisory clients are given access to a secure document portal.
      </div>

      <h3>Student records</h3>
      <p>
        ARSC retains enrolment history, completion status, assessment results,
        certificate issuance records and access logs for the periods set out in
        the records retention policy.
      </p>

      <h3>Certificates</h3>
      <p>
        Every certificate carries the student&rsquo;s name, the course title and
        duration, the completion date, a unique certificate number, and this
        statement:
      </p>
      <p>
        <em>&ldquo;This certificate confirms successful completion of private
        professional development training and does not represent an academic
        degree, government licence, regulated professional designation or
        provincially recognized diploma.&rdquo;</em>
      </p>

    </div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">Questions</p>
    <h2 data-reveal style="--d:70ms">Ask before<br><span class="em">you commit.</span></h2>
    <a class="btn btn-gold" href="{root}contact/" data-reveal style="--d:150ms">Contact us {ARROW}</a>
  </div>
</section>

</main>
"""
    return write("policies/index.html",
                 head(root, "Policies — Enrolment, Refunds and Privacy | ARSC",
                      "Regulatory disclosure, enrolment agreements, refunds, complaint resolution, academic integrity, accessibility, privacy and student records at ARSC College.",
                      "/policies/", ld,
                      "refund policy online course, PIPA privacy BC, enrolment agreement, "
                      "student records retention Canada")
                 + header(root, "") + body + footer(root))


def page_faculty():
    root = "../"
    ld = ldjson([org_node()])

    # Deliberately empty slots. No invented instructors, no invented
    # credentials — a fabricated faculty page is a misrepresentation, and
    # instructor qualifications are a documented PTIRU requirement.
    slots = "".join(f'''
      <article class="person is-vacant" data-reveal style="--d:{i*70}ms">
        <div class="person-seal" aria-hidden="true">&mdash;</div>
        <h3>{title}</h3>
        <p class="role">Position open</p>
        <p>{blurb}</p>
      </article>''' for i, (title, blurb) in enumerate([
        ("Director of Education", "Curriculum development, instructor recruitment, course quality, assessment and certificate approval."),
        ("Director of Accounting and Taxation", "Tax and bookkeeping standards, CRA compliance, EFILE, quality control and trainee supervision."),
        ("Director of Artificial Intelligence and Technology", "AI curriculum, learning platform, cybersecurity, automation and AI risk management."),
        ("Director of Human Resources and Operations", "HR services, internal policy, staffing and placement administration."),
        ("Instructor — Taxation", "Practising professional teaching the taxation sequence."),
        ("Instructor — Bookkeeping and Payroll", "Practising professional teaching full-cycle bookkeeping and Canadian payroll."),
    ]))

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("Faculty", None)])}
    <p class="eyebrow" data-reveal="fade">Faculty</p>
    <h1 data-reveal style="--d:70ms">Taught by people who<br><span class="em">still do the work.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      ARSC recruits instructors who maintain active professional practice. It is
      a hiring condition, and it is the reason the material stays current as tax
      legislation, CRA procedures and AI tooling change.
    </p>
  </div>
</section>

<section class="on-light tight">
  <div class="shell">
    <div class="notice" style="margin-top:0" data-reveal="fade">
      <strong>Faculty appointments in progress</strong>
      The positions below are being filled ahead of the first intake. Instructor
      names, credentials and photographs will be published here as appointments
      are confirmed. We would rather show you an honest blank than invent a
      faculty roster.
    </div>

    <h2 class="visually-hidden">Faculty positions</h2>
    <div class="people" style="margin-top:var(--sp-xl)">{slots}</div>
  </div>
</section>

<section>
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">Standards</p>
        <h2 data-reveal style="--d:70ms">How instructors<br><span class="em">are qualified.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        Instructor qualification is documented, not assumed. Every appointment is
        recorded against a written standard.
      </p>
    </div>

    <div class="steps">
      <div class="step" data-reveal><p class="step-no">01</p><div class="step-rule"></div>
        <h3>Active practice</h3>
        <p>Instructors in taxation, accounting and payroll maintain current professional practice. Teaching is not their only occupation.</p></div>
      <div class="step" data-reveal style="--d:120ms"><p class="step-no">02</p><div class="step-rule"></div>
        <h3>Documented credentials</h3>
        <p>Qualifications are verified and recorded before appointment, and held on file against the instructor qualification standard.</p></div>
      <div class="step" data-reveal style="--d:240ms"><p class="step-no">03</p><div class="step-rule"></div>
        <h3>Annual course review</h3>
        <p>Taxation and payroll courses are reviewed every year because legislation and CRA forms change. AI courses are reviewed at least as often.</p></div>
    </div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">Teach with us</p>
    <h2 data-reveal style="--d:70ms">Practising professional?<br><span class="em">We are hiring.</span></h2>
    <p class="lede" data-reveal style="--d:150ms">
      If you hold a current designation and want to teach one block a term, we
      would like to hear from you.
    </p>
    <a class="btn btn-gold" href="{root}contact/" data-reveal style="--d:230ms">Enquire about teaching {ARROW}</a>
  </div>
</section>

</main>
"""
    return write("faculty/index.html",
                 head(root, "Faculty and Instructor Standards | ARSC College",
                      "ARSC instructors maintain active professional practice. Faculty appointments, qualification standards and the annual course review cycle, explained plainly.",
                      "/faculty/", ld,
                      "accounting instructor Canada, tax instructor BC, teach professional development, "
                      "instructor qualifications, practising professional educator")
                 + header(root, "faculty/") + body + footer(root))


def page_how():
    root = "../"
    ld = ldjson([org_node()])
    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("How it works", None)])}
    <p class="eyebrow" data-reveal="fade">Student experience</p>
    <h1 data-reveal style="--d:70ms">What studying here<br><span class="em">actually looks like.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      No jargon, no vague promises. Here is the format, the technology you need,
      the support you get, and what is expected of you.
    </p>
  </div>
</section>

<section class="tight">
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">Format</p>
        <h2 data-reveal style="--d:70ms">Asynchronous,<br><span class="em">by design.</span></h2>
      </div>
      <p class="lede" data-reveal style="--d:150ms">
        Courses are delivered as recorded video lessons you work through at your
        own pace, because most of our students already have jobs.
      </p>
    </div>

    <div class="table-wrap on-dark" data-reveal="fade">
      <table>
        <caption class="visually-hidden">Delivery format comparison</caption>
        <thead><tr><th scope="col"></th><th scope="col">Asynchronous (ARSC)</th><th scope="col">Live scheduled classes</th></tr></thead>
        <tbody>
          <tr><td><strong>When you study</strong></td><td>Any time</td><td>Fixed times</td></tr>
          <tr><td><strong>Timezone</strong></td><td>Irrelevant</td><td>Must match the class</td></tr>
          <tr><td><strong>Pace</strong></td><td>Yours</td><td>The cohort&rsquo;s</td></tr>
          <tr><td><strong>Rewatching</strong></td><td>Unlimited, 12 months</td><td>If recorded</td></tr>
          <tr><td><strong>Questions</strong></td><td>Written, answered by faculty</td><td>Live in session</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="on-light">
  <div class="shell">
    <div class="steps" style="grid-template-columns:repeat(auto-fit,minmax(270px,1fr))">
      <div class="step" data-reveal><p class="step-no">01</p><div class="step-rule"></div>
        <h3>Enrol</h3>
        <p>Submit a request, speak to an advisor, receive the enrolment agreement and refund policy in writing, then pay.</p></div>
      <div class="step" data-reveal style="--d:100ms"><p class="step-no">02</p><div class="step-rule"></div>
        <h3>Work through the lessons</h3>
        <p>Video lessons in sequence, with downloadable notes and worksheets. Your progress is saved so you can stop and resume.</p></div>
      <div class="step" data-reveal style="--d:200ms"><p class="step-no">03</p><div class="step-rule"></div>
        <h3>Practise on simulated files</h3>
        <p>Exercises use realistic but fictional client files. You make mistakes on invented data, never on someone&rsquo;s real return.</p></div>
      <div class="step" data-reveal style="--d:300ms"><p class="step-no">04</p><div class="step-rule"></div>
        <h3>Complete and be certified</h3>
        <p>Finish the assessments and your certificate is issued to your account with a unique certificate number.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="shell">
    <div class="head">
      <div>
        <p class="marker" data-reveal="fade">Requirements</p>
        <h2 data-reveal style="--d:70ms">What you need<br><span class="em">to take part.</span></h2>
      </div>
    </div>

    <div class="relevance" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr))" data-reveal="fade">
      <div><h3>Device</h3><p>Any laptop or desktop from the last several years. A tablet works for watching, but spreadsheet exercises need a real keyboard.</p></div>
      <div><h3>Connection</h3><p>A standard home broadband connection. Video quality adjusts automatically to what your connection can carry.</p></div>
      <div><h3>Software</h3><p>A spreadsheet application for the accounting and finance courses. Requirements are listed on each course page.</p></div>
      <div><h3>Time</h3><p>Instructional hours are listed per course. Most students spread a 24-hour course across six to eight weeks.</p></div>
    </div>

    <div class="notice on-dark" data-reveal="fade">
      <strong>Accessibility</strong>
      This site is built to WCAG 2.1 AA: verified colour contrast, full keyboard
      operation, visible focus states, and motion that respects your operating
      system&rsquo;s reduced-motion setting. Captions and downloadable transcripts
      are committed for every video lesson. To request an accommodation, contact
      us and name what would help.
    </div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">Still deciding?</p>
    <h2 data-reveal style="--d:70ms">Ask before<br><span class="em">you enrol.</span></h2>
    <a class="btn btn-gold" href="{root}contact/" data-reveal style="--d:150ms">Talk to an advisor {ARROW}</a>
  </div>
</section>

</main>
"""
    return write("how-it-works/index.html",
                 head(root, "How Online Learning Works | ARSC College",
                      "Delivery format, technology requirements, student support and accessibility. What to expect from a self-paced ARSC online professional development course today.",
                      "/how-it-works/", ld,
                      "self paced online course Canada, asynchronous learning, "
                      "online course requirements, accessible online learning")
                 + header(root, "") + body + footer(root))


def page_employers():
    root = "../"
    ld = ldjson([org_node()])
    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("Employer training", None)])}
    <p class="eyebrow" data-reveal="fade">For employers</p>
    <h1 data-reveal style="--d:70ms">Train your team<br><span class="em">on your schedule.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Group delivery for firms and businesses that need several staff brought to
      the same standard &mdash; scheduled around your close, not ours.
    </p>
  </div>
</section>

<section class="tight">
  <div class="shell">
    <h2 class="visually-hidden">Training options</h2>
    <div class="divisions" style="grid-template-columns:repeat(auto-fit,minmax(290px,1fr))">
      <article class="division" data-reveal>
        <span class="division-tag">Group seats</span>
        <h3>Six or more staff</h3>
        <p>Per-seat pricing on any published course, with a single invoice and consolidated completion reporting.</p>
        <ul><li>Any course in the catalogue</li><li>One invoice, one contact</li><li>Completion reporting for HR</li><li>Certificates issued per participant</li></ul>
        <a class="btn btn-line" href="{root}contact/">Request a quote {ARROW}</a>
      </article>
      <article class="division" data-reveal style="--d:90ms">
        <span class="division-tag">Private cohort</span>
        <h3>Delivered for your firm</h3>
        <p>A private run of a course, scheduled around your busy season and mapped to the way your firm actually works.</p>
        <ul><li>Scheduled around your close</li><li>Examples drawn from your sector</li><li>Your file conventions used</li><li>Dedicated point of contact</li></ul>
        <a class="btn btn-line" href="{root}contact/">Discuss a private cohort {ARROW}</a>
      </article>
      <article class="division" data-reveal style="--d:180ms">
        <span class="division-tag">Workshops</span>
        <h3>Half and full day</h3>
        <p>Focused sessions for teams that need one capability quickly &mdash; most often AI workflow and responsible AI use.</p>
        <ul><li>AI for business teams</li><li>Responsible AI and privacy</li><li>Spreadsheet and workflow automation</li><li>Delivered online</li></ul>
        <a class="btn btn-line" href="{root}contact/">Enquire about workshops {ARROW}</a>
      </article>
    </div>

    <div class="notice on-dark" data-reveal="fade">
      <strong>What group training is not</strong>
      Group and workshop delivery is professional development. It does not confer
      an academic credential, a regulated designation, or any form of
      accreditation on participants or on your organization.
    </div>
  </div>
</section>

<section class="on-light">
  <div class="shell">
    <div class="head solo">
      <div>
        <p class="marker" data-reveal="fade">Getting a quote</p>
        <h2 data-reveal style="--d:70ms">Tell us four things<br><span class="em">and we can price it.</span></h2>
      </div>
    </div>
    <div class="relevance" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))" data-reveal="fade">
      <div><h3>How many people</h3><p>Headcount, and whether they are all at the same level.</p></div>
      <div><h3>Which subject</h3><p>A published course, or the capability gap you are trying to close.</p></div>
      <div><h3>When</h3><p>Your target window, and any period to avoid &mdash; tax season, month end, year end.</p></div>
      <div><h3>Format</h3><p>Self-paced seats, or a private cohort with scheduled sessions.</p></div>
    </div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">Employer training</p>
    <h2 data-reveal style="--d:70ms">Get a quote<br><span class="em">this week.</span></h2>
    <a class="btn btn-gold" href="{root}contact/" data-reveal style="--d:150ms">Request a proposal {ARROW}</a>
  </div>
</section>

</main>
"""
    return write("employers/index.html",
                 head(root, "Employer and Group Training | ARSC College",
                      "Group seats, private cohorts and workshops for firms training staff in accounting, taxation, payroll, HR or AI. Scheduled around your busy season.",
                      "/employers/", ld,
                      "corporate training Canada, group training accounting, staff upskilling BC, "
                      "employer training program, private cohort training")
                 + header(root, "") + body + footer(root))


def page_resources():
    root = "../"
    ld = ldjson([org_node(), {
        "@type": "CollectionPage", "url": f"{SITE}/resources/",
        "name": "Resources", "publisher": {"@id": f"{SITE}/#org"}}])

    planned = [
        ("Canadian tax", "What changes for personal tax this filing season",
         "A plain-language summary of the changes that actually affect ordinary returns, published each year before filing opens."),
        ("Bookkeeping", "The month-end close, in the order you should do it",
         "A practical sequence for closing a month cleanly, and the checks that catch errors before a client sees them."),
        ("Artificial intelligence", "Where AI should not touch a client file",
         "The specific points in accounting and tax work where AI output must be verified by a person, and why."),
        ("Payroll", "The Canadian payroll calendar, explained",
         "Remittance deadlines, T4 season and the year-end sequence, laid out as a calendar rather than a regulation."),
        ("Starting a business", "Registering a business in British Columbia, step by step",
         "The actual order of operations, the accounts you need, and the ones you do not."),
        ("Newcomers", "Canadian accounting practice for internationally trained professionals",
         "What transfers from experience gained abroad, what does not, and where the gaps usually are."),
    ]

    posts = "".join(f'''
      <article class="post is-planned" data-reveal style="--d:{i*60}ms">
        <p class="kicker">{kicker}</p>
        <h3>{title}</h3>
        <p>{blurb}</p>
        <p style="margin-top:var(--sp-md);font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;opacity:.6">In preparation</p>
      </article>''' for i, (kicker, title, blurb) in enumerate(planned))

    body = f"""
<main id="main">

<section class="page-hero">
  {rings(3)}
  <div class="shell">
    {crumbs(root, [("Resources", None)])}
    <p class="eyebrow" data-reveal="fade">Resources</p>
    <h1 data-reveal style="--d:70ms">Useful things,<br><span class="em">written plainly.</span></h1>
    <p class="lede" data-reveal style="--d:150ms">
      Practical notes on Canadian tax, bookkeeping, payroll and AI in
      professional practice &mdash; free to read, no enrolment required.
    </p>
  </div>
</section>

<section class="on-light tight">
  <div class="shell">
    <div class="notice" style="margin-top:0" data-reveal="fade">
      <strong>Editorial calendar</strong>
      These are the first six articles in preparation. Titles are planned, not
      published &mdash; nothing below is live yet, and none of it is presented as
      if it were.
    </div>
    <h2 class="visually-hidden">Articles in preparation</h2>
    <div class="posts" style="margin-top:var(--sp-xl)">{posts}</div>
  </div>
</section>

<section class="closer">
  {rings(3)}
  <div class="shell">
    <p class="eyebrow" data-reveal="fade">Get them when they land</p>
    <h2 data-reveal style="--d:70ms">Monthly at most.<br><span class="em">Nothing else.</span></h2>
    <p class="lede" data-reveal style="--d:150ms">
      Subscribe at the bottom of any page and you will hear from us when an
      article or a new intake is actually ready.
    </p>
  </div>
</section>

</main>
"""
    return write("resources/index.html",
                 head(root, "Resources — Canadian Tax and Bookkeeping Notes | ARSC",
                      "Plain-language notes on Canadian taxation, bookkeeping, payroll and the responsible use of AI in professional practice. Free to read, no enrolment needed.",
                      "/resources/", ld,
                      "Canadian tax guide, bookkeeping tips Canada, payroll calendar Canada, "
                      "AI in accounting, starting a business in BC")
                 + header(root, "resources/") + body + footer(root))


def page_404():
    root = ""
    body = f"""
<main id="main">
<section class="notfound">
  <div class="shell">
    <p class="code" aria-hidden="true">404</p>
    <p class="eyebrow" style="justify-content:center">Page not found</p>
    <h1>That page<br><span class="em">isn&rsquo;t here.</span></h1>
    <p class="lede" style="margin:var(--sp-md) auto 0">
      The link may be out of date, or the page may have moved. The course
      catalogue is the best place to pick things back up.
    </p>
    <div class="hero-actions" style="justify-content:center;margin-top:var(--sp-xl)">
      <a class="btn btn-gold" href="college/">Browse all courses {ARROW}</a>
      <a class="btn btn-line" href="index.html">Back to home {ARROW}</a>
    </div>
  </div>
</section>
</main>
"""
    return write("404.html",
                 head(root, "Page Not Found | ARSC Professional Development",
                      "The page you requested could not be found. Browse the ARSC catalogue of twelve online professional development courses in accounting, tax, business and AI.",
                      "/404.html", "")
                 + header(root, "") + body + footer(root))


def page_sitemap(paths):
    urls = []
    for p in paths:
        if not p.endswith(".html"):
            continue
        loc = "/" if p == "index.html" else "/" + p.replace("index.html", "")
        prio = "1.0" if p == "index.html" else ("0.9" if p.endswith("college/index.html") else "0.7")
        urls.append(f"""  <url>
    <loc>{SITE}{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{prio}</priority>
  </url>""")

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    return write("sitemap.xml", xml)


def main():
    global CSS_V, JS_V
    CSS_V = asset_v("assets/site.css")
    JS_V = asset_v("assets/site.js")

    built = []

    # Remove the previous single-page build so nothing stale is served.
    stale = os.path.join(HERE, "index.html")
    if os.path.exists(stale):
        os.remove(stale)

    built.append(page_home())
    built.append(page_college())
    for c in COURSES:
        built.append(page_course(c))
    built.append(page_advisory())
    built.append(page_faculty())
    built.append(page_how())
    built.append(page_employers())
    built.append(page_resources())
    built.append(page_about())
    built.append(page_enroll())
    built.append(page_contact())
    built.append(page_policies())

    # 404 is intentionally excluded from the sitemap.
    page_404()

    page_sitemap(built)

    with open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    print(f"built {len(built)} pages + sitemap.xml + robots.txt")
    print(f"asset versions: site.css?v={CSS_V}  site.js?v={JS_V}")
    for p in built:
        print("  " + p)
    total = sum(len(c["lessons"]) for c in COURSES)
    print(f"\n{len(COURSES)} courses, {total} lessons, all data-yt-id empty and ready to fill")


if __name__ == "__main__":
    main()
