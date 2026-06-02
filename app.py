"""
Purposeful — AI Mentor for Women in Tech
Streamlit Web App | Powered by Claude (Anthropic API)
"""

import os
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Purposeful — AI Mentor for Women in Tech",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Mobile responsiveness — let Streamlit handle the sidebar toggle natively
st.markdown("""
<style>
/* Hide ONLY the question-mark / main-menu help button in the top-right corner.
   (Does NOT touch the sidebar toggle arrow, the header, or anything else.) */
#MainMenu { display: none !important; }
button[data-testid="baseButton-header"] { display: none !important; }
[data-testid="stMainMenu"] { display: none !important; }

/* Keep the AI News heading + refresh button on the same row everywhere */
[data-testid="stHorizontalBlock"]:has(.news-refresh-marker) {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
}

@media (max-width: 768px) {
    /* Tighter page padding on small screens */
    .main .block-container,
    [data-testid="stMain"] .block-container {
        padding: 0.5rem !important;
        max-width: 100% !important;
    }
    /* Stack all column layouts (score cards, quick actions, panels) into a
       responsive single/auto-fit grid */
    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)) !important;
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        min-width: unset !important;
    }
    /* News heading row stays inline even on mobile (override the grid above) */
    [data-testid="stHorizontalBlock"]:has(.news-refresh-marker) {
        display: flex !important;
        justify-content: space-between !important;
    }
    /* Hero card: stack the cat on top, text below, full width */
    .hero-inner {
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
        gap: 0.75rem !important;
    }
    .luna-cat-emoji { font-size: 3.2rem !important; }
    /* Slightly smaller type on small screens */
    html, body, [data-testid="stAppViewContainer"] {
        font-size: 0.92rem !important;
    }
    .greeting-name { font-size: 1.15rem !important; }
    .hero-title { font-size: 1.1rem !important; }
    .sc-value { font-size: 1.4rem !important; }
    .top-bar { flex-wrap: wrap !important; gap: 0.5rem !important; }
    /* Do NOT hide or override the sidebar toggle button */
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────
PURPOSEFUL_BASE = """You are Purposeful, a warm, expert, and empowering AI mentor
specifically designed for women in tech. You combine deep technical and product knowledge
with a genuine understanding of the unique challenges women face in the technology industry.

Your tone is: professional yet warm, data-driven but human, direct and actionable.
You speak to your users as capable, intelligent professionals — you celebrate their wins
and give honest, practical guidance without sugarcoating.

Key facts about the user you may be talking to:
- She may be a QA Engineer, developer, PM, or someone transitioning into tech
- She is building real career skills, not just exploring hypothetically
- Her time is valuable — give clear, structured, actionable responses
- She is part of the "AI with Purpose" community of women in tech
"""

CAREER_PATH_PROMPT = PURPOSEFUL_BASE + """
You specialize in career path planning for women in tech, especially those moving into
AI/ML, Product Management, or AI PM hybrid roles.

When helping someone plan their career path:
1. First, ask about their current role, years of experience, key skills, and career goal
2. Offer 2-3 realistic trajectory options with realistic timelines (e.g., "6-12 months to X")
3. For each path: list required skills, how to get them, and where her current background shines
4. Be honest about challenges AND reframe her existing experience as strengths
5. End with a clear "your best next 3 actions" summary

Example paths worth knowing:
- QA Engineer → AI QA Specialist → AI PM
- QA Engineer → SDET → Technical PM → AI PM
- QA Engineer → Product Analyst → PM → AI PM
"""

RESUME_PROMPT = PURPOSEFUL_BASE + """
You are an expert resume writer specializing in AI Product Management roles.
You know exactly what hiring managers at top tech companies look for and how to
translate any background — especially QA and testing — into a compelling AI PM narrative.

When reviewing or creating a resume:
1. Ask the user to paste their resume or describe their experience
2. Identify which existing skills map directly to AI PM competencies:
   - QA → quality mindset, risk assessment, edge cases, user empathy
   - Testing → systematic thinking, documentation, stakeholder communication
   - PSPO certification → scrum, backlog management, product ownership
3. Rewrite bullet points using impact metrics and AI/PM language
4. Flag gaps and give quick wins to address each one
5. Give ATS optimization tips (keywords for AI PM job listings)
6. End with a "headline" and "summary statement" they can use

Key AI PM keywords to weave in: machine learning workflows, model evaluation,
data pipelines, product-led growth, AI/ML roadmaps, cross-functional alignment,
responsible AI, bias mitigation, LLM-powered features, AI product strategy.
"""

JOB_MATCHER_PROMPT = PURPOSEFUL_BASE + """
You are a job matching specialist who helps women in tech identify their best-fit roles
in AI and tech based on their unique background, skills, values, and goals.

When helping with job matching:
1. Ask about: current skills, years of experience, preferred industry, work style
   (IC vs. manager, startup vs. enterprise), salary expectations, and non-negotiables
2. Suggest 6-8 specific job titles she should be targeting RIGHT NOW
3. For each title: explain why it's a match, what companies hire for it, and a
   "readiness score" out of 10 with what would close the gap
4. Distinguish between: roles she can apply to today vs. in 6 months vs. in 1 year
5. Include less obvious roles that often get overlooked by women (e.g., AI Ops,
   Prompt Engineer, AI Solutions Architect, Technical Program Manager — AI)

Be specific with company names where relevant (e.g., Anthropic, Google DeepMind,
Microsoft, Salesforce, HubSpot, Notion, Linear, Cohere, etc.)
"""

LEARNING_PATH_PROMPT = PURPOSEFUL_BASE + """
You are a learning architect who creates focused, efficient learning plans for women
entering or advancing in AI/tech roles. You cut through the noise and recommend only
what actually moves the needle.

When creating a learning path:
1. Ask about: target role, current knowledge level (beginner/intermediate/advanced),
   hours available per week, learning style (video/reading/hands-on), and budget
2. Build a phased plan: 30 days (foundation) / 60 days (build) / 90 days (portfolio)
3. For each phase, list:
   - Specific resources (course name + platform + link if known)
   - Hands-on projects to build portfolio evidence
   - A milestone: "By the end of this phase you'll be able to..."
4. Prioritize free and low-cost resources; mention paid ones only if clearly worth it
5. Include community resources: newsletters, Discord servers, LinkedIn creators to follow

Great free resources to know:
- fast.ai (practical deep learning), deeplearning.ai (Andrew Ng courses),
- Google's ML Crash Course, Kaggle Learn, freeCodeCamp, CS50 (Harvard)
- For PM skills: Lenny's Newsletter, Shreyas Doshi on LinkedIn, Product School
- Communities: Women in AI, Learnprompting.org, AI with Purpose community
"""

INTERVIEW_PREP_PROMPT = PURPOSEFUL_BASE + """
You are an expert interview coach who conducts realistic mock interviews and gives
precise, actionable feedback. You specialize in tech and product management interviews
including behavioral, technical, case study, and PM-specific rounds.

How to run interview prep:
1. First ask: what role, what company (if known), what type of interview (behavioral,
   technical, case, general PM, or "mix")
2. Conduct a realistic mock interview — ask questions ONE AT A TIME, wait for the
   answer before moving to the next
3. After EACH answer: give specific feedback using this format:
   ✅ What worked: [specific praise]
   🔧 Improve this: [specific suggestion]
   💡 Try saying: [example of a stronger phrase]
4. Teach frameworks naturally when relevant:
   - STAR (Situation, Task, Action, Result) for behavioral
   - CIRCLES or RICE for PM case studies
   - "Why this company / why this role" coaching
5. At the end, give an overall assessment and top 3 things to practice

Be a realistic interviewer — push back, ask follow-up questions, simulate silence.
Don't make it too easy. Women deserve honest preparation.
"""

AI_NEWS_PROMPT = PURPOSEFUL_BASE + """
You are an AI industry analyst and curator helping women in tech stay sharp on AI
developments that matter for their careers — without the hype or overwhelm.

When discussing AI news and trends:
1. Share the most significant recent developments across: LLMs, AI products, AI regulation,
   AI in enterprise, and new AI job categories
2. For each development, explain: what it is in plain English + why it matters for
   someone building a career in AI/tech
3. Highlight which companies are leading vs. following in each area
4. Flag new job categories and skills becoming valuable because of these changes
5. Be upfront that your training data has a knowledge cutoff — always tell users:
   "For the most current news, check these sources daily:"
   - The Batch (deeplearning.ai) — deeplearning.ai/the-batch
   - MIT Technology Review — technologyreview.com
   - AI Tidbits — newsletter
   - Wired AI section — wired.com/tag/artificial-intelligence
   - Lenny's Newsletter (for AI in product) — lennysnewsletter.com

Start with a "Today's AI landscape in 3 bullets" summary if asked for a general briefing.
"""

ROLEPLAY_PROMPT = PURPOSEFUL_BASE + """
You are a roleplay facilitator and negotiation/communication coach who helps women in tech
practice high-stakes conversations in a safe space. You play realistic counterparts.

Available scenarios:
A) Salary Negotiation — you play the hiring manager or current manager
B) Difficult Workplace Conversation — managing up, addressing microaggressions,
   asking for promotion, pushing back on unfair feedback
C) Pitch Practice — pitching a product idea, a project, or yourself to leadership

How to run a roleplay:
1. Ask the user which scenario they want, and for relevant context
2. Set the scene: describe who you're playing and the context in 2-3 sentences
3. Start the roleplay — stay IN CHARACTER as the counterpart
   - Be realistic: ask hard questions, push back, use common deflections
4. When the user types "STOP" or "feedback" — break character immediately
5. Give structured coaching feedback:
   ✅ Strong moves: what she did well
   🔧 Missed opportunities: what she could have said
   💬 Power phrases: specific language to use next time
   🔁 Optional: offer to run the scenario again with improvements
"""

# ─────────────────────────────────────────────
# FEATURE REGISTRY
# ─────────────────────────────────────────────
FEATURES = {
    "career": {
        "label": "🗺️ Career Path Generator",
        "prompt": CAREER_PATH_PROMPT,
        "intro": (
            "Let's map out your career journey! 🗺️\n\n"
            "Tell me about yourself:\n"
            "- What's your current role and years of experience?\n"
            "- What's your big career goal? (e.g., AI PM, ML Engineer, Tech Lead)\n"
            "- Any timeline or constraints I should know about?"
        ),
    },
    "resume": {
        "label": "📄 Resume Optimizer",
        "prompt": RESUME_PROMPT,
        "intro": (
            "Let's make your resume irresistible for AI PM roles! 📄\n\n"
            "Paste your resume text, or describe your experience and I'll help you "
            "frame it powerfully."
        ),
    },
    "jobs": {
        "label": "🎯 Job Matcher",
        "prompt": JOB_MATCHER_PROMPT,
        "intro": (
            "Let's find your best-fit roles in AI and tech! 🎯\n\n"
            "Tell me about your skills, experience, preferred work environment, "
            "and salary range."
        ),
    },
    "learning": {
        "label": "📚 Learning Path Generator",
        "prompt": LEARNING_PATH_PROMPT,
        "intro": (
            "Let's build your personalized learning plan! 📚\n\n"
            "What role or skill are you working toward, and how many hours/week "
            "can you dedicate?"
        ),
    },
    "interview": {
        "label": "🎤 Interview Prep",
        "prompt": INTERVIEW_PREP_PROMPT,
        "intro": (
            "Time to practice! Let's run a mock interview. 🎤\n\n"
            "What role are you interviewing for, and what type? "
            "(behavioral / technical / PM case / mix)"
        ),
    },
    "news": {
        "label": "📰 AI News & Trends",
        "prompt": AI_NEWS_PROMPT,
        "intro": (
            "Let's get you up to speed on AI! 📰\n\n"
            "Ask about any topic, a company, or just say 'briefing' for a general "
            "AI landscape overview."
        ),
    },
    "roleplay": {
        "label": "🎭 Roleplay Scenarios",
        "prompt": ROLEPLAY_PROMPT,
        "intro": (
            "Let's practice a high-stakes conversation! 🎭\n\n"
            "Choose a scenario:\n"
            "**A)** 💰 Salary Negotiation\n"
            "**B)** 💬 Difficult Workplace Conversation\n"
            "**C)** 🚀 Pitch Practice\n\n"
            "Which one, and give me some context!"
        ),
    },
}

NAV_GROUPS = {
    "OVERVIEW":  ["home"],
    "CAREER":    ["career", "resume", "jobs"],
    "LEARNING":  ["learning"],
    "PRACTICE":  ["interview", "roleplay"],
}

# Course categories → colored dot (emoji to avoid HTML rendering issues)
COURSE_CATEGORIES = {
    "AI & ML":     "🔵",
    "Product":     "🟣",
    "Leadership":  "🟠",
    "Technical":   "🟢",
    "Other":       "⚪",
}

# Progress status → colored dot
COURSE_STATUSES = ["⚪ Not started", "🟡 In Progress", "🟢 Completed"]

NAV_LABELS = {
    "home":      "🏠 Dashboard",
    "career":    "🗺️ Career Path",
    "resume":    "📄 Resume Optimizer",
    "jobs":      "🎯 Job Matcher",
    "learning":  "📚 Learning Path",
    "interview": "🎤 Interview Prep",
    "roleplay":  "🎭 Roleplay Scenarios",
}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "active_feature" not in st.session_state:
    st.session_state.active_feature = "home"

for key in FEATURES:
    if f"history_{key}" not in st.session_state:
        st.session_state[f"history_{key}"] = []

if "user_resume" not in st.session_state:
    st.session_state.user_resume = ""

if "user_goal" not in st.session_state:
    st.session_state.user_goal = ""

if "notes" not in st.session_state:
    st.session_state.notes = [
        {"text": "Research AI PM roles at Anthropic 🎯", "color": "yellow"},
        {"text": "Complete fast.ai — week 3 📚",         "color": "pink"},
        {"text": "Salary range: $140k–$180k 💰",         "color": "blue"},
    ]

if "new_note_text" not in st.session_state:
    st.session_state.new_note_text = ""

if "ai_news" not in st.session_state:
    st.session_state.ai_news = []  # populated on first Refresh click

if "luna_picks" not in st.session_state:
    st.session_state.luna_picks = None  # None = not yet fetched

if "recent_features" not in st.session_state:
    st.session_state.recent_features = []

if "news_pending_prompt" not in st.session_state:
    st.session_state.news_pending_prompt = ""

if "news_detail_item" not in st.session_state:
    st.session_state.news_detail_item = None   # the news item dict currently being viewed

if "news_detail_content" not in st.session_state:
    st.session_state.news_detail_content = ""  # fetched article body

if "scores" not in st.session_state:
    st.session_state.scores = None          # None = no resume analyzed yet

if "score_reasons" not in st.session_state:
    st.session_state.score_reasons = {}

if "analyzing" not in st.session_state:
    st.session_state.analyzing = False

# Shared user profile — resume + goal available to every feature
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "career_goal" not in st.session_state:
    st.session_state.career_goal = ""

if "profile_ready" not in st.session_state:
    st.session_state.profile_ready = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "courses" not in st.session_state:
    st.session_state.courses = []  # list of {name, url, category, folder, status}

if "show_course_form" not in st.session_state:
    st.session_state.show_course_form = False

# ─────────────────────────────────────────────
# API CLIENT
# ─────────────────────────────────────────────
api_key = os.getenv("ANTHROPIC_API_KEY")


@st.cache_resource
def get_client(k: str) -> Anthropic:
    return Anthropic(api_key=k)


SCORE_PROMPT = """You are an expert career coach. Analyze the resume and career goal below, then return ONLY a valid JSON object — no explanation, no markdown fences, just raw JSON.

Scores are integers 0–100. Calibrate each score against the stated career goal.

{{
  "career_readiness": {{"score": 75, "reason": "one sentence why"}},
  "resume_score":     {{"score": 60, "reason": "one sentence why"}},
  "interview_ready":  {{"score": 50, "reason": "one sentence why"}},
  "ai_skill_score":   {{"score": 80, "reason": "one sentence why"}}
}}

Definitions (score relative to the career goal):
- career_readiness: How ready is this person for their stated goal given their current trajectory?
- resume_score: How well optimized is this resume for that goal (keywords, impact, ATS)?
- interview_ready: Based on experience depth, how prepared for interviews for that role?
- ai_skill_score: How strong are their AI/ML skills relative to what the goal demands?

CAREER GOAL: {goal}

RESUME:
{resume}"""


# Per-feature opening request sent automatically when the user's profile is ready,
# so Luna jumps straight to personalized output instead of asking intro questions.
AUTO_KICKOFF = {
    "career": (
        "Using my resume and career goal, generate a personalized career roadmap for me "
        "now. Skip the introductions — don't ask me to tell you about myself."
    ),
    "resume": (
        "Analyze my resume against my career goal now: give an optimized rewrite with "
        "improved bullet points, ATS keywords, and a headline. Don't ask me to paste it again."
    ),
    "interview": (
        "Start a mock interview for my target role now. Based on my career goal, ask me "
        "the first relevant interview question."
    ),
    "jobs": (
        "Based on my resume and career goal, recommend my best-fit roles right now."
    ),
    "learning": (
        "Based on my resume and career goal, build my personalized 30/60/90-day learning "
        "plan now."
    ),
}


def build_system_prompt(base_prompt: str) -> str:
    """Append the user's resume + goal to a feature's system prompt when known."""
    if st.session_state.get("profile_ready"):
        resume = (st.session_state.get("resume_text") or "").strip()
        goal = (st.session_state.get("career_goal") or "").strip()
        if resume or goal:
            return (
                base_prompt
                + "\n\n--- USER CONTEXT (already known — do NOT ask the user to repeat) ---\n"
                + f"User's resume: {resume or 'not provided'}. "
                + f"Career goal: {goal or 'not provided'}. "
                + "Use this context throughout. Do not ask the user to restate their "
                "background or goal."
            )
    return base_prompt


RSS_FEEDS = [
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("AI News",     "https://www.artificialintelligence-news.com/feed/"),
    ("TechCrunch",  "https://techcrunch.com/category/artificial-intelligence/feed/"),
]


def fetch_ai_news() -> list:
    import feedparser
    import html as html_mod
    import re
    import time
    import random

    cache_bust = int(time.time())
    all_items = []
    for source_name, feed_url in RSS_FEEDS:
        try:
            sep = "&" if "?" in feed_url else "?"
            feed = feedparser.parse(f"{feed_url}{sep}t={cache_bust}")
            for entry in feed.entries[:15]:
                raw = entry.get("summary", entry.get("description", ""))
                clean = re.sub(r"<[^>]+>", " ", raw)
                clean = re.sub(r"\s+", " ", html_mod.unescape(clean)).strip()
                if len(clean) > 160:
                    clean = clean[:157].rstrip() + "…"
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                all_items.append({
                    "headline": html_mod.unescape(entry.get("title", "Untitled")),
                    "summary":  clean or "Click to read the full article.",
                    "url":      entry.get("link", "#"),
                    "source":   source_name,
                    "published": published,
                })
        except Exception:
            continue

    # Sort newest-first, then randomly sample 5 from the recent pool so each
    # refresh surfaces a different mix (feeds rarely publish new items minute-to-minute).
    all_items.sort(key=lambda x: x["published"] or (0,) * 9, reverse=True)
    recent_pool = all_items[:20]
    if len(recent_pool) > 5:
        return random.sample(recent_pool, 5)
    return recent_pool


def analyze_resume(resume_text: str, goal: str) -> dict:
    import json
    client = get_client(api_key)
    prompt = SCORE_PROMPT.format(
        goal=goal.strip() if goal.strip() else "AI Product Manager",
        resume=resume_text,
    )
    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def get_greeting() -> str:
    from datetime import datetime
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good afternoon"
    if 17 <= hour < 21:
        return "Good evening"
    return "Good night"


def fetch_luna_picks() -> list:
    client = get_client(api_key)
    goal = (st.session_state.get("user_goal") or "").strip()
    resume = (st.session_state.get("user_resume") or "").strip()
    recent = st.session_state.get("recent_features", [])

    if goal or resume or recent:
        context = (
            f"Career goal: {goal or 'not specified'}\n"
            f"Resume on file: {'yes' if resume else 'no'}\n"
            f"Recently used features: {', '.join(recent) if recent else 'none'}"
        )
        ask = (
            "Based on this tech professional's activity below, give exactly 3 short, "
            "personalized, actionable next-step recommendations.\n\n" + context
        )
    else:
        ask = (
            "Give exactly 3 short, actionable starter recommendations for a tech "
            "professional building a career in AI."
        )

    prompt = (
        ask
        + "\n\nReturn ONLY a JSON array of 3 strings, each under 90 characters. "
        "No extra text. Example: [\"Do X\", \"Do Y\", \"Do Z\"]"
    )
    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    import json
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    picks = json.loads(raw.strip())
    return [str(p) for p in picks][:3]


# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ─────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stAppViewContainer"] {
    background: #f5f0ff;
}

[data-testid="stMain"] {
    background: #f5f0ff;
}

/* ── Sidebar shell — always visible ───────────── */
/* Sidebar — cosmetic only; let Streamlit control open/collapse natively */
[data-testid="stSidebar"] {
    background: #fdf5ff !important;
    border-right: 1px solid #e9d5ff;
}

[data-testid="stSidebar"] > div:first-child {
    background: #fdf5ff;
    padding-top: 0;
}

/* Always keep the reopen control visible when the sidebar is collapsed.
   Streamlit has used different test IDs across versions, so target all. */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="header"],
[data-testid="stExpandSidebarButton"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 9999 !important;
}
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 0.5rem !important;
    left: 0.5rem !important;
}

/* ── Sidebar logo ─────────────────────────────── */
.sb-logo {
    font-size: 1.25rem;
    font-weight: 900;
    color: #6d28d9;
    letter-spacing: -0.02em;
    padding: 1.4rem 1rem 0.15rem 1rem;
}

.sb-tagline {
    font-size: 0.7rem;
    color: #a78bfa;
    font-weight: 500;
    padding: 0 1rem 1rem 1rem;
    line-height: 1.4;
}

.sb-profile-badge {
    display: inline-block;
    margin: 0 1rem 0.6rem 1rem;
    padding: 0.2rem 0.6rem;
    font-size: 0.68rem;
    font-weight: 700;
    color: #15803d;
    background: #dcfce7;
    border: 1px solid #86efac;
    border-radius: 20px;
}

/* ── Nav section labels ───────────────────────── */
.nav-group-label {
    font-size: 0.6rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    color: #c4b5fd;
    text-transform: uppercase;
    padding: 0.9rem 1rem 0.35rem 1rem;
}

/* ── Course category sub-label ────────────────── */
.course-cat-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: #6d28d9;
    padding: 0.5rem 1rem 0.1rem 1rem;
}

/* ── Active nav pill ──────────────────────────── */
.nav-active {
    background: #7c3aed;
    color: #ffffff !important;
    padding: 0.45rem 0.75rem;
    border-radius: 9px;
    font-size: 0.82rem;
    font-weight: 700;
    margin: 2px 0;
    display: block;
    cursor: default;
    box-sizing: border-box;
}

/* ── Sidebar button wrapper — strip all default spacing ── */
[data-testid="stSidebar"] .stButton {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}

/* ── Sidebar plain buttons → nav items ───────── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-left: none !important;
    box-shadow: none !important;
    outline: none !important;
    color: #4c1d95 !important;
    text-align: left !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 0.75rem !important;
    border-radius: 9px !important;
    width: 100% !important;
    transition: background 0.13s, color 0.13s !important;
    margin: 2px 0 !important;
    display: flex !important;
    align-items: center !important;
}

/* Strip pseudo-element decorations and ALL list markers Streamlit injects */
[data-testid="stSidebar"] .stButton > button::before,
[data-testid="stSidebar"] .stButton > button::after {
    display: none !important;
    content: none !important;
}

[data-testid="stSidebar"] .stButton > button ul,
[data-testid="stSidebar"] .stButton > button ol {
    list-style: none !important;
    padding-left: 0 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] .stButton > button li {
    list-style: none !important;
    list-style-type: none !important;
    padding-left: 0 !important;
    margin-left: 0 !important;
}

[data-testid="stSidebar"] .stButton > button li::marker,
[data-testid="stSidebar"] .stButton > button li::before,
[data-testid="stSidebar"] .stButton > button li::after {
    display: none !important;
    content: none !important;
}

/* Ensure inner div/span from Streamlit button internals is left-flush */
[data-testid="stSidebar"] .stButton > button > div,
[data-testid="stSidebar"] .stButton > button > div > div {
    padding: 0 !important;
    margin: 0 !important;
    text-align: left !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #ede9fe !important;
    color: #6d28d9 !important;
}

[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:focus-visible,
[data-testid="stSidebar"] .stButton > button:active {
    outline: none !important;
    box-shadow: none !important;
    border: none !important;
}

/* Inner <p> tag — left-align and strip margin */
[data-testid="stSidebar"] .stButton > button p {
    text-align: left !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.4 !important;
}

/* ── Sticky notes ─────────────────────────────── */
.sticky {
    padding: 0.7rem 0.8rem;
    border-radius: 8px;
    font-size: 0.76rem;
    font-weight: 500;
    line-height: 1.45;
    margin: 0.35rem 0.5rem;
    box-shadow: 2px 3px 8px rgba(0,0,0,0.08);
    font-family: 'Patrick Hand', cursive, sans-serif;
}

.sticky-yellow { background: #fef9c3; color: #713f12; border-left: 3px solid #fbbf24; }
.sticky-pink   { background: #fce7f3; color: #831843; border-left: 3px solid #f472b6; }
.sticky-blue   { background: #dbeafe; color: #1e3a8a; border-left: 3px solid #60a5fa; }

/* × delete button in the narrow column beside each note */
[data-testid="stSidebar"] [data-testid="stColumn"]:last-child .stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #d1d5db !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    padding: 0 !important;
    min-height: unset !important;
    height: 1.6rem !important;
    width: 1.6rem !important;
    border-radius: 50% !important;
    line-height: 1 !important;
    transform: none !important;
    margin-top: 0.25rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stSidebar"] [data-testid="stColumn"]:last-child .stButton > button:hover {
    color: #ef4444 !important;
    background: rgba(239,68,68,0.1) !important;
    transform: none !important;
}

/* Add note text input in sidebar */
[data-testid="stSidebar"] .stTextInput input {
    font-size: 0.78rem !important;
    border-radius: 8px !important;
    border: 1.5px solid #e9d5ff !important;
    padding: 0.4rem 0.6rem !important;
    background: white !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.15) !important;
}

/* Add note button */
[data-testid="stSidebar"] .add-note-btn .stButton > button {
    background: #7c3aed !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    padding: 0.35rem 0.5rem !important;
    width: 100% !important;
    min-height: 0 !important;
    height: auto !important;
    margin-top: 0.3rem !important;
}

/* ── Sidebar divider ──────────────────────────── */
.sb-divider {
    height: 1px;
    background: #e9d5ff;
    margin: 0.6rem 0.8rem;
}

/* ── Top bar ──────────────────────────────────── */
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.4rem 0 1.2rem 0;
}

.greeting-name {
    font-size: 1.55rem;
    font-weight: 900;
    color: #1e1b4b;
    letter-spacing: -0.02em;
    display: block;
}

.greeting-sub {
    font-size: 0.83rem;
    color: #6b7280;
    display: block;
    margin-top: 0.15rem;
}

.top-bar-right {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.streak-badge {
    background: #fff7ed;
    border: 1.5px solid #fed7aa;
    color: #ea580c;
    font-weight: 800;
    font-size: 0.8rem;
    padding: 0.38rem 0.9rem;
    border-radius: 20px;
    white-space: nowrap;
}

.avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%);
    color: white;
    font-weight: 900;
    font-size: 1.05rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 10px rgba(124,58,237,0.35);
}

/* ── Hero card ────────────────────────────────── */
.hero-card {
    background: linear-gradient(135deg, #6d28d9 0%, #9333ea 55%, #c026d3 100%);
    border-radius: 22px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 10px 40px rgba(109,40,217,0.28);
    position: relative;
    overflow: hidden;
}

.hero-card::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}

.hero-inner {
    display: flex;
    align-items: center;
    gap: 1.4rem;
    position: relative;
    z-index: 1;
}

.luna-img {
    width: 90px;
    height: 90px;
    object-fit: contain;
    cursor: pointer;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.25));
    transition: transform 0.1s;
    flex-shrink: 0;
}

.luna-cat-emoji {
    font-size: 4.5rem;
    cursor: pointer;
    user-select: none;
    display: inline-block;
    flex-shrink: 0;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.2));
}

@keyframes bounce {
    0%   { transform: translateY(0) scale(1); }
    20%  { transform: translateY(-18px) scale(1.05); }
    40%  { transform: translateY(0) scale(0.97); }
    60%  { transform: translateY(-9px) scale(1.02); }
    80%  { transform: translateY(0) scale(0.99); }
    100% { transform: translateY(0) scale(1); }
}

.bouncing { animation: bounce 0.65s ease; }

.hero-text { flex: 1; }

.hero-title {
    font-size: 1.3rem;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 0.45rem;
    letter-spacing: -0.01em;
}

.hero-msg {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.88);
    line-height: 1.65;
}

/* ── Score cards ──────────────────────────────── */
.score-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.1rem 1rem 0.85rem;
    box-shadow: 0 2px 14px rgba(0,0,0,0.06);
    border-top: 3px solid transparent;
    height: 100%;
}

.score-card.pink   { border-top-color: #ec4899; }
.score-card.amber  { border-top-color: #f59e0b; }
.score-card.purple { border-top-color: #8b5cf6; }
.score-card.green  { border-top-color: #22c55e; }

.sc-emoji { font-size: 1.35rem; margin-bottom: 0.4rem; }

.sc-label {
    font-size: 0.67rem;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.25rem;
}

.sc-value {
    font-size: 1.7rem;
    font-weight: 900;
    color: #1e1b4b;
    letter-spacing: -0.03em;
    margin-bottom: 0.6rem;
    line-height: 1;
}

.prog-track {
    background: #f3f4f6;
    border-radius: 4px;
    height: 5px;
    overflow: hidden;
}

.prog-bar {
    height: 100%;
    border-radius: 4px;
}

.score-card.pink   .prog-bar { background: linear-gradient(90deg, #f472b6, #ec4899); }
.score-card.amber  .prog-bar { background: linear-gradient(90deg, #fcd34d, #f59e0b); }
.score-card.purple .prog-bar { background: linear-gradient(90deg, #a78bfa, #8b5cf6); }
.score-card.green  .prog-bar { background: linear-gradient(90deg, #4ade80, #22c55e); }

.sc-reason {
    font-size: 0.67rem;
    color: #9ca3af;
    line-height: 1.35;
    margin-top: 0.45rem;
    font-style: italic;
}

/* Analyze button must NOT inherit quick-action card styles */
[data-testid="stMain"] [data-testid="column"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    min-height: 40px !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    transform: none !important;
    box-shadow: 0 2px 10px rgba(124,58,237,0.3) !important;
}

/* ── Section headings ─────────────────────────── */
.section-head {
    font-size: 1.05rem;
    font-weight: 800;
    color: #1e1b4b;
    margin: 1.4rem 0 0.75rem 0;
    letter-spacing: -0.01em;
}

/* ── Quick action cards ───────────────────────── */
.qa-card {
    background: #ffffff;
    border: 1.5px solid #f3e8ff;
    border-radius: 14px;
    padding: 1rem 0.85rem 0.6rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 0;
    cursor: pointer;
    transition: box-shadow 0.15s, transform 0.15s, border-color 0.15s;
}

.qa-card:hover {
    border-color: #a78bfa;
    box-shadow: 0 6px 24px rgba(124,58,237,0.13);
    transform: translateY(-2px);
}

.qa-emoji { font-size: 1.55rem; margin-bottom: 0.35rem; }
.qa-title { font-size: 0.85rem; font-weight: 800; color: #1e1b4b; margin-bottom: 0.15rem; }
.qa-sub   { font-size: 0.72rem; color: #6b7280; line-height: 1.35; }

/* Main area quick-action open buttons */
.main-area .stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #7c3aed !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    padding: 0.3rem 0 0.5rem 0 !important;
    text-align: left !important;
    width: 100% !important;
    border-radius: 0 !important;
    margin: 0 !important;
}

.main-area .stButton > button:hover {
    color: #5b21b6 !important;
    background: transparent !important;
}

/* ── Luna right panel ─────────────────────────── */
/* ── Luna's Picks card ───────────────────────── */
.picks-card {
    background: #ffffff;
    border: 1px solid #e9d5ff;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.picks-header {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin-bottom: 0.75rem;
}

.picks-icon { font-size: 1.1rem; }

.picks-title {
    font-size: 0.85rem;
    font-weight: 800;
    color: #1e1b4b;
}

.pick-row {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.55rem 0;
}

.pick-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 4px;
}

.pick-dot-purple { background: #8b5cf6; }
.pick-dot-blue   { background: #3b82f6; }
.pick-dot-orange { background: #f97316; }

.pick-text {
    flex: 1;
    font-size: 0.78rem;
    color: #374151;
    line-height: 1.4;
}


.pick-divider {
    height: 1px;
    background: #f3e8ff;
    margin: 0;
}


/* ── AI News section ─────────────────────────── */
.news-section {
    margin-top: 0.85rem;
}

.news-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.6rem;
}

.news-section-title {
    font-size: 0.85rem;
    font-weight: 800;
    color: #1e1b4b;
}

/* Refresh button — small icon pill */
[data-testid="stMarkdownContainer"]:has(.news-refresh-marker) + [data-testid="stButton"] > button {
    background: #f3e8ff !important;
    border: none !important;
    box-shadow: none !important;
    color: #7c3aed !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    padding: 0.2rem 0.55rem !important;
    min-height: unset !important;
    height: auto !important;
    width: auto !important;
    border-radius: 20px !important;
    transform: none !important;
    line-height: 1.4 !important;
}
[data-testid="stMarkdownContainer"]:has(.news-refresh-marker) + [data-testid="stButton"] > button:hover {
    background: #ede9fe !important;
    transform: none !important;
}
/* Push the refresh button to the right edge of its column, inline with heading */
[data-testid="stColumn"]:has(.news-refresh-marker) [data-testid="stButton"] {
    display: flex !important;
    justify-content: flex-end !important;
}

/* News cards */
.nc {
    background: #ffffff;
    border: 1px solid #f3e8ff;
    border-left: 3px solid #a78bfa;
    border-radius: 10px;
    padding: 0.65rem 0.75rem 0.55rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.nc-top {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.25rem;
}

.nc-badge {
    display: inline-block;
    font-size: 0.58rem;
    font-weight: 700;
    padding: 0.08rem 0.4rem;
    border-radius: 20px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.badge-venturebeat { background: #fef3c7; color: #92400e; }
.badge-ainews      { background: #dbeafe; color: #1d4ed8; }
.badge-techcrunch  { background: #d1fae5; color: #065f46; }
.badge-fallback    { background: #fce7f3; color: #9d174d; }

.nc-headline {
    display: block;
    font-size: 0.8rem;
    font-weight: 700;
    color: #1e1b4b;
    text-decoration: none;
    line-height: 1.35;
    margin-bottom: 0.3rem;
}
.nc-headline:hover { color: #7c3aed; text-decoration: underline; }

.nc-summary {
    font-size: 0.7rem;
    color: #6b7280;
    line-height: 1.4;
    margin-bottom: 0.4rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.nc-footer {
    display: flex;
    justify-content: flex-end;
}

.nc-read {
    font-size: 0.68rem;
    font-weight: 700;
    color: #7c3aed;
    text-decoration: none;
}
.nc-read:hover { text-decoration: underline; }

/* ── News detail back button ─────────────────── */
/* Targets the first stButton in the main area when NOT in home (no card CSS injected) */
.news-detail-back .stButton > button {
    background: #ede9fe !important;
    border: none !important;
    box-shadow: none !important;
    color: #6d28d9 !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.8rem !important;
    min-height: unset !important;
    width: auto !important;
    transform: none !important;
}

/* ── Chat feature view ────────────────────────── */
.feature-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 0 1.2rem 0;
    border-bottom: 2px solid #e9d5ff;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.4rem;
    font-weight: 900;
    color: #1e1b4b;
    letter-spacing: -0.02em;
    margin: 0;
}

/* Back button in chat view */
.chat-view .stButton > button {
    background: #ede9fe !important;
    border: none !important;
    box-shadow: none !important;
    color: #6d28d9 !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.8rem !important;
}

.chat-view .stButton > button:hover {
    background: #ddd6fe !important;
}

/* Clear button in chat view */
.chat-view .clear-btn .stButton > button {
    background: #fff1f2 !important;
    color: #e11d48 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    margin-bottom: 0.5rem;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo">Purposeful</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-tagline">Your AI Career Mentor</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("profile_ready"):
        st.markdown(
            '<div class="sb-profile-badge">✓ Resume loaded</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    active = st.session_state.active_feature

    for group, keys in NAV_GROUPS.items():
        st.markdown(f'<div class="nav-group-label">{group}</div>', unsafe_allow_html=True)
        for k in keys:
            label = NAV_LABELS[k]
            if k == active:
                st.markdown(f'<div class="nav-active">{label}</div>', unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{k}", use_container_width=True):
                    st.session_state.active_feature = k
                    st.rerun()

    # NOTES section — interactive sticky notes
    st.markdown('<div class="nav-group-label">NOTES</div>', unsafe_allow_html=True)

    for idx, note in enumerate(st.session_state.notes):
        color = note["color"]
        col_note, col_del = st.columns([9, 1])
        with col_note:
            st.markdown(
                f'<div class="sticky sticky-{color}">📌 {note["text"]}</div>',
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("×", key=f"del_note_{idx}", help="Delete note"):
                st.session_state.notes.pop(idx)
                st.rerun()

    # Add new note
    st.markdown('<div style="margin-top:0.5rem"></div>', unsafe_allow_html=True)
    new_text = st.text_input(
        label="new_note",
        label_visibility="collapsed",
        placeholder="Add a note…",
        key="new_note_input",
    )
    color_choice = st.radio(
        label="color",
        label_visibility="collapsed",
        options=["🟡 Yellow", "🩷 Pink", "🔵 Blue"],
        horizontal=True,
        key="note_color_radio",
    )
    st.markdown('<div class="add-note-btn">', unsafe_allow_html=True)
    if st.button("+ Add Note", key="add_note_btn", use_container_width=True):
        if new_text.strip():
            color_map = {"🟡 Yellow": "yellow", "🩷 Pink": "pink", "🔵 Blue": "blue"}
            chosen = color_map[color_choice]
            st.session_state.notes.append({"text": new_text.strip(), "color": chosen})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── MY COURSES — bookmarked courses with progress tracking ──
    course_count = len(st.session_state.courses)
    st.markdown(
        f'<div class="nav-group-label">MY COURSES ({course_count})</div>',
        unsafe_allow_html=True,
    )

    # Group courses by category, keeping original index for edits/deletion
    grouped = {}
    for idx, course in enumerate(st.session_state.courses):
        cat = course.get("category", "Other")
        grouped.setdefault(cat, []).append((idx, course))

    for cat in COURSE_CATEGORIES:
        items = grouped.get(cat, [])
        if not items:
            continue
        dot = COURSE_CATEGORIES[cat]
        st.markdown(f'<div class="course-cat-label">{dot} {cat}</div>', unsafe_allow_html=True)
        for idx, course in items:
            folder = course.get("folder", "").strip()
            label = course["name"] + (f"  ·  {folder}" if folder else "")
            url = course.get("url", "").strip()
            c_name, c_del = st.columns([8, 1])
            with c_name:
                if url:
                    st.markdown(f'[{label}]({url})')
                else:
                    st.markdown(label)
            with c_del:
                if st.button("×", key=f"del_course_{idx}", help="Remove course"):
                    st.session_state.courses.pop(idx)
                    st.rerun()
            current = course.get("status", COURSE_STATUSES[0])
            new_status = st.selectbox(
                label="status",
                label_visibility="collapsed",
                options=COURSE_STATUSES,
                index=COURSE_STATUSES.index(current) if current in COURSE_STATUSES else 0,
                key=f"course_status_{idx}",
            )
            if new_status != current:
                st.session_state.courses[idx]["status"] = new_status
                st.rerun()

    # Add-course toggle + form
    if st.button("+ Add Course", key="toggle_course_form", use_container_width=True):
        st.session_state.show_course_form = not st.session_state.show_course_form
        st.rerun()

    if st.session_state.show_course_form:
        with st.form("add_course_form", clear_on_submit=True):
            course_name = st.text_input("Course name", key="course_name_input")
            course_url = st.text_input("URL", key="course_url_input")
            course_cat = st.selectbox(
                "Category",
                options=list(COURSE_CATEGORIES.keys()),
                key="course_cat_input",
            )
            course_folder = st.text_input("Folder / tag (optional)", key="course_folder_input")
            submitted = st.form_submit_button("Save", use_container_width=True)
            if submitted:
                if course_name.strip():
                    st.session_state.courses.append({
                        "name": course_name.strip(),
                        "url": course_url.strip(),
                        "category": course_cat,
                        "folder": course_folder.strip(),
                        "status": COURSE_STATUSES[0],
                    })
                    st.session_state.show_course_form = False
                    st.rerun()
                else:
                    st.warning("Please enter a course name.")

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
active = st.session_state.active_feature

if active == "home":
    # Auto-load news on first render
    if not st.session_state.ai_news and api_key and not api_key.startswith("sk-ant-api03-your-key"):
        try:
            st.session_state.ai_news = fetch_ai_news()
        except Exception:
            pass  # silently skip — user can hit ↻ manually

    # ── Top bar ──────────────────────────────
    name = st.session_state.user_name.strip()
    greeting_text = f"{get_greeting()}, {name}! 👋" if name else f"{get_greeting()}! 👋"
    # Only show the avatar once a name is set (otherwise it's a meaningless "?")
    avatar_html = f'<div class="avatar">{name[:1].upper()}</div>' if name else ""
    # Built as a single line (no blank lines / indentation) so an empty avatar
    # doesn't break the HTML block into literal text.
    st.markdown(
        '<div class="top-bar">'
        '<div>'
        f'<span class="greeting-name">{greeting_text}</span>'
        '<span class="greeting-sub">Ready to build your future in AI?</span>'
        '</div>'
        '<div class="top-bar-right">'
        '<div class="streak-badge">🔥 7 day streak</div>'
        f'{avatar_html}'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Name capture — always visible so each user can set/update their own name.
    # Stored ONLY in st.session_state (per-session, per-user; never shared globally).
    name_col, save_col, _spacer = st.columns([2, 1, 3])
    with name_col:
        name_input = st.text_input(
            "What's your name?",
            value=st.session_state.user_name,
            placeholder="Enter your first name…",
            key="name_input",
            label_visibility="collapsed",
        )
    with save_col:
        if st.button("Save name", use_container_width=True):
            st.session_state.user_name = name_input.strip()
            st.rerun()

    # ── Two-column layout ─────────────────────
    col_main, col_right = st.columns([1.85, 1], gap="large")

    # Inject card-style CSS scoped to the home view buttons only
    st.markdown("""<style>
    [data-testid="stMain"] [data-testid="column"] .stButton > button {
        background: #ffffff !important;
        border: 1.5px solid #f3e8ff !important;
        border-radius: 14px !important;
        padding: 1.2rem 1rem 1rem !important;
        text-align: left !important;
        height: auto !important;
        min-height: 115px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        color: #1e1b4b !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        line-height: 1.5 !important;
        transition: box-shadow 0.15s, transform 0.15s, border-color 0.15s !important;
        white-space: pre-line !important;
    }
    [data-testid="stMain"] [data-testid="column"] .stButton > button:hover {
        border-color: #a78bfa !important;
        box-shadow: 0 6px 24px rgba(124,58,237,0.14) !important;
        transform: translateY(-2px) !important;
        background: #ffffff !important;
        color: #1e1b4b !important;
    }
    [data-testid="stMain"] [data-testid="column"] .stButton > button p {
        text-align: left !important;
        white-space: pre-line !important;
        margin: 0 !important;
        font-size: 0.88rem !important;
    }
    </style>""", unsafe_allow_html=True)

    with col_main:
        # ── Hero card ─────────────────────────
        luna_html = '<span class="luna-cat-emoji" onclick="this.classList.add(\'bouncing\'); setTimeout(()=>this.classList.remove(\'bouncing\'),700)" title="Click me!">🐱</span>'

        # Dynamic Luna message: prompt for resume first, then personalize once analyzed
        if st.session_state.scores:
            if name:
                hero_msg = (
                    f"Hi {name}! ✨ Here's what I picked for you today — your scores are "
                    "ready below. Click a card to keep building your future in AI!"
                )
            else:
                hero_msg = (
                    "Here's what I picked for you today — your scores are ready below. "
                    "Click a card to keep building your future in AI!"
                )
        else:
            hero_msg = "Start by uploading your resume below — I'll calculate all 4 scores instantly!"

        st.markdown(f"""
        <div class="hero-card">
            <div class="hero-inner">
                {luna_html}
                <div class="hero-text">
                    <div class="hero-title">Hi! I'm Luna ✨</div>
                    <div class="hero-msg">{hero_msg}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Score cards ───────────────────────
        s = st.session_state.scores
        DEFAULT_SCORES = {
            "career_readiness": {"score": 0, "reason": "Add your resume below to calculate"},
            "resume_score":     {"score": 0, "reason": "Add your resume below to calculate"},
            "interview_ready":  {"score": 0, "reason": "Add your resume below to calculate"},
            "ai_skill_score":   {"score": 0, "reason": "Add your resume below to calculate"},
        }
        score_data = [
            ("Career Readiness", "pink",   "🗺️", "career_readiness"),
            ("Resume Score",     "amber",  "📄", "resume_score"),
            ("Interview Ready",  "purple", "🎤", "interview_ready"),
            ("AI Skill Score",   "green",  "🤖", "ai_skill_score"),
        ]

        has_scores = bool(s)
        s_cols = st.columns(4, gap="small")
        for i, (lbl, color, emoji, key) in enumerate(score_data):
            with s_cols[i]:
                src = (s or {}).get(key) or DEFAULT_SCORES[key]
                val = src["score"]
                if has_scores:
                    value_display = f"{val}%"
                    bar_width = val
                    reason_html = f'<div class="sc-reason">{src["reason"]}</div>'
                else:
                    # Locked empty state before any resume is analyzed
                    value_display = "🔒"
                    bar_width = 0
                    reason_html = '<div class="sc-reason">Upload resume to unlock</div>'
                st.markdown(f"""
                <div class="score-card {color}">
                    <div class="sc-emoji">{emoji}</div>
                    <div class="sc-label">{lbl}</div>
                    <div class="sc-value">{value_display}</div>
                    <div class="prog-track">
                        <div class="prog-bar" style="width:{bar_width}%"></div>
                    </div>
                    {reason_html}
                </div>
                """, unsafe_allow_html=True)

        # ── Resume + Goal input section ───────
        st.markdown('<div class="section-head">📋 Resume & Career Goal</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:0.82rem;color:#6b7280;margin:-0.5rem 0 0.75rem 0">'
            'Add your resume and career goal — Luna will use both to calculate your scores accurately.</p>',
            unsafe_allow_html=True,
        )

        input_col, goal_col = st.columns([2, 1], gap="medium")

        with input_col:
            st.markdown(
                '<p style="font-size:0.78rem;font-weight:700;color:#4c1d95;margin-bottom:0.3rem">📄 Your Resume</p>',
                unsafe_allow_html=True,
            )
            resume_text = st.text_area(
                label="resume_input",
                label_visibility="collapsed",
                value=st.session_state.user_resume,
                placeholder="Paste your resume here — the more detail, the better Luna can analyze you.",
                height=180,
                key="resume_textarea",
            )

        with goal_col:
            st.markdown(
                '<p style="font-size:0.78rem;font-weight:700;color:#4c1d95;margin-bottom:0.3rem">🎯 Career Goal</p>',
                unsafe_allow_html=True,
            )
            goal_text = st.text_area(
                label="goal_input",
                label_visibility="collapsed",
                value=st.session_state.user_goal,
                placeholder="e.g. AI Product Manager at a tech company, or ML Engineer at a startup…",
                height=180,
                key="goal_textarea",
            )

        analyze_col, status_col = st.columns([1, 3])
        with analyze_col:
            analyze_clicked = st.button(
                "✨ Analyze",
                key="analyze_btn",
                use_container_width=True,
                type="primary",
                disabled=not resume_text.strip(),
            )
        with status_col:
            if st.session_state.scores:
                goal_label = st.session_state.user_goal or "AI PM"
                st.markdown(
                    f'<p style="font-size:0.8rem;color:#22c55e;padding-top:0.6rem">✅ Scores based on your resume · Goal: <em>{goal_label}</em></p>',
                    unsafe_allow_html=True,
                )

        if analyze_clicked:
            if not resume_text.strip():
                st.warning("Please paste your resume text first.")
            elif not api_key or api_key.startswith("sk-ant-api03-your-key"):
                st.error("API key not configured.")
            else:
                st.session_state.user_resume = resume_text
                st.session_state.user_goal = goal_text
                # Save profile as global context for every feature
                st.session_state.resume_text = resume_text
                st.session_state.career_goal = goal_text
                st.session_state.profile_ready = True
                # New profile → regenerate personalized picks next render
                st.session_state.luna_picks = None
                with st.spinner("Luna is reading your resume…"):
                    try:
                        result = analyze_resume(resume_text, goal_text)
                        st.session_state.scores = result
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

        # ── Quick actions ─────────────────────
        st.markdown('<div class="section-head">Quick Actions</div>', unsafe_allow_html=True)

        actions = [
            ("career",    "🗺️", "Career Path",      "Map your AI PM journey"),
            ("resume",    "📄", "Resume Optimizer",  "Rewrite for AI PM roles"),
            ("jobs",      "🎯", "Job Matcher",       "Find your best-fit roles"),
            ("learning",  "📚", "Learning Path",     "30 / 60 / 90 day plan"),
            ("interview", "🎤", "Interview Prep",    "Mock interview simulation"),
            ("roleplay",  "🎭", "Roleplay",          "Salary & pitch practice"),
        ]

        for row_start in range(0, len(actions), 3):
            row_actions = actions[row_start:row_start + 3]
            qa_cols = st.columns(3, gap="small")
            for ci, (feat_key, emoji, title, sub) in enumerate(row_actions):
                with qa_cols[ci]:
                    if st.button(
                        f"{emoji}  {title}\n{sub}",
                        key=f"qa_{feat_key}",
                        use_container_width=True,
                    ):
                        st.session_state.active_feature = feat_key
                        st.rerun()

    # ── Right panel ──────────────────────────────
    with col_right:
        # ── Luna's Picks — dynamic, personalized via Claude ──
        if st.session_state.luna_picks is None and api_key and not api_key.startswith("sk-ant-api03-your-key"):
            try:
                st.session_state.luna_picks = fetch_luna_picks()
            except Exception:
                st.session_state.luna_picks = [
                    "Update LinkedIn with AI PM keywords before applying",
                    "Complete deeplearning.ai Prompt Engineering course",
                    "Practice behavioral questions for your next interview",
                ]

        picks = st.session_state.luna_picks or [
            "Update LinkedIn with AI PM keywords before applying",
            "Complete deeplearning.ai Prompt Engineering course",
            "Practice behavioral questions for your next interview",
        ]
        dot_colors = ["purple", "blue", "orange"]
        rows_html = ""
        for i, pick in enumerate(picks):
            if i > 0:
                rows_html += '<div class="pick-divider"></div>'
            color = dot_colors[i % len(dot_colors)]
            rows_html += (
                '<div class="pick-row">'
                f'<div class="pick-dot pick-dot-{color}"></div>'
                f'<div class="pick-text">{pick}</div>'
                '</div>'
            )

        st.markdown(
            '<div class="picks-card">'
            '<div class="picks-header">'
            '<span class="picks-icon">🐱</span>'
            '<span class="picks-title">Luna\'s Picks for You</span>'
            '</div>'
            + rows_html +
            '</div>',
            unsafe_allow_html=True,
        )

        # ── AI News & Trends ──────────────────────────────
        st.markdown('<div class="news-section">', unsafe_allow_html=True)
        _nh, _nr = st.columns([4, 1], vertical_alignment="center")
        with _nh:
            st.markdown('<div class="news-section-title">📰 AI News &amp; Trends</div>', unsafe_allow_html=True)
        with _nr:
            st.markdown('<span class="news-refresh-marker"></span>', unsafe_allow_html=True)
            if st.button("↻", key="refresh_news", help="Refresh headlines"):
                with st.spinner("Fetching…"):
                    try:
                        st.session_state.ai_news = fetch_ai_news()
                    except Exception as e:
                        st.error(f"Could not fetch news: {e}")
                st.rerun()

        if not st.session_state.ai_news:
            st.markdown(
                '<p style="font-size:0.75rem;color:#9ca3af;margin:0.4rem 0">Loading headlines…</p>',
                unsafe_allow_html=True,
            )
        else:
            SOURCE_BADGE = {
                "VentureBeat": "badge-venturebeat",
                "AI News":     "badge-ainews",
                "TechCrunch":  "badge-techcrunch",
            }
            cards_html = ""
            for item in st.session_state.ai_news:
                src = item.get("source", "")
                badge_cls = SOURCE_BADGE.get(src, "badge-fallback")
                url = item.get("url", "#")
                headline = item["headline"]
                summary = item["summary"]
                cards_html += (
                    f'<div class="nc">'
                    f'<div class="nc-top"><span class="nc-badge {badge_cls}">{src}</span></div>'
                    f'<a class="nc-headline" href="{url}" target="_blank" rel="noopener">{headline}</a>'
                    f'<div class="nc-summary">{summary}</div>'
                    f'<div class="nc-footer">'
                    f'<a class="nc-read" href="{url}" target="_blank" rel="noopener">Read more &#x2192;</a>'
                    f'</div>'
                    f'</div>'
                )
            st.markdown(cards_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close news-section

elif active == "news_detail":
    # ─────────────────────────────────────────
    # NEWS DETAIL VIEW
    # ─────────────────────────────────────────
    item = st.session_state.news_detail_item
    if item is None:
        st.session_state.active_feature = "home"
        st.rerun()

    BADGE_CLASS_DETAIL = {
        "Tools": "badge-tools", "Research": "badge-research",
        "Industry": "badge-industry", "Careers": "badge-careers",
    }
    cat = item.get("category", "Industry")

    # Back button
    if st.button("← Back to Dashboard", key="news_detail_back"):
        st.session_state.active_feature = "home"
        st.rerun()

    st.markdown(
        f'<span class="news-badge {BADGE_CLASS_DETAIL.get(cat, "badge-industry")}" '
        f'style="margin:0.5rem 0 0.75rem 0;display:inline-block">{cat}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h2 style="font-size:1.6rem;font-weight:900;color:#1e1b4b;'
        f'letter-spacing:-0.02em;margin:0 0 0.5rem 0;line-height:1.3">'
        f'{item["headline"]}</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="font-size:0.9rem;color:#6b7280;margin:0 0 1.5rem 0">'
        f'{item["summary"]}</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="border:none;border-top:1.5px solid #e9d5ff;margin:0 0 1.5rem 0">', unsafe_allow_html=True)

    # Fetch and cache the full article body
    if not st.session_state.news_detail_content:
        if not api_key or api_key.startswith("sk-ant-api03-your-key"):
            st.error("API key not configured.")
            st.stop()
        with st.spinner("Luna is writing the full story…"):
            try:
                client = get_client(api_key)
                article_prompt = (
                    f'You are an AI industry analyst writing for women building careers in tech. '
                    f'Using your knowledge of AI industry trends and developments, write a clear, '
                    f'engaging 4-6 paragraph deep-dive on this topic: "{item["headline"]}"\n\n'
                    f'Structure:\n'
                    f'1. What this is about — context and what happened (2-3 sentences, plain English)\n'
                    f'2. Why it matters for the AI industry overall\n'
                    f'3. What it means specifically for someone building an AI/PM career\n'
                    f'4. Key skills or opportunities this development opens up\n'
                    f'5. One concrete action the reader can take this week to stay ahead\n\n'
                    f'Tone: professional, warm, direct. Be specific — name real tools, companies, skills. '
                    f'No hype. No bullet lists — flowing paragraphs only.'
                )
                resp = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": article_prompt}],
                )
                st.session_state.news_detail_content = resp.content[0].text.strip()
            except Exception as e:
                st.error(f"Could not load article: {e}")
                st.stop()

    st.markdown(st.session_state.news_detail_content)

    st.markdown('<hr style="border:none;border-top:1.5px solid #e9d5ff;margin:1.5rem 0">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.78rem;color:#a78bfa">✨ Powered by Luna · Purposeful AI Mentor</p>',
        unsafe_allow_html=True,
    )

elif active in FEATURES:
    # ─────────────────────────────────────────
    # CHAT VIEW
    # ─────────────────────────────────────────
    feature = FEATURES[active]
    history_key = f"history_{active}"

    st.markdown('<div class="chat-view">', unsafe_allow_html=True)

    # Header row: back button + title + clear button
    h_back, h_title, h_clear = st.columns([1, 6, 1.5])
    with h_back:
        if st.button("← Back", key="back_btn"):
            st.session_state.active_feature = "home"
            st.rerun()
    with h_title:
        st.markdown(
            f'<div class="feature-title">{feature["label"]}</div>',
            unsafe_allow_html=True,
        )
    with h_clear:
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear", key="clear_btn"):
            st.session_state[history_key] = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1.5px solid #e9d5ff;margin:0 0 1rem 0">', unsafe_allow_html=True)

    # API key guard
    if not api_key or api_key.startswith("sk-ant-api03-your-key"):
        st.error(
            "**API key not found.** Create a `.env` file in this folder with:\n\n"
            "```\nANTHROPIC_API_KEY=your_key_here\n```"
        )
        st.stop()

    # Auto-send a pending news prompt when navigating from a headline
    if active == "news" and st.session_state.get("news_pending_prompt") and not st.session_state[history_key]:
        pending = st.session_state.news_pending_prompt
        st.session_state.news_pending_prompt = ""
        st.session_state[history_key].append({"role": "user", "content": pending})
        with st.chat_message("user"):
            st.markdown(pending)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                client = get_client(api_key)
                with client.messages.stream(
                    model="claude-opus-4-6",
                    max_tokens=2048,
                    system=build_system_prompt(feature["prompt"]),
                    messages=st.session_state[history_key],
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"❌ Error: {e}"
                placeholder.markdown(full_response)
            st.session_state[history_key].append({"role": "assistant", "content": full_response})
        st.rerun()

    # Auto-kickoff a personalized first response when the profile is ready —
    # skips the generic "tell me about yourself" intro for relevant features.
    if (
        st.session_state.get("profile_ready")
        and active in AUTO_KICKOFF
        and not st.session_state[history_key]
    ):
        kickoff = AUTO_KICKOFF[active]
        st.session_state[history_key].append({"role": "user", "content": kickoff})
        with st.chat_message("user"):
            st.markdown(kickoff)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                client = get_client(api_key)
                with client.messages.stream(
                    model="claude-opus-4-6",
                    max_tokens=2048,
                    system=build_system_prompt(feature["prompt"]),
                    messages=st.session_state[history_key],
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"❌ Error: {e}"
                placeholder.markdown(full_response)
            st.session_state[history_key].append({"role": "assistant", "content": full_response})
        st.rerun()

    # Show intro if no history yet
    if not st.session_state[history_key]:
        with st.chat_message("assistant"):
            st.markdown(feature["intro"])

    # Render conversation history
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your message…")

    if user_input:
        st.session_state[history_key].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                client = get_client(api_key)
                with client.messages.stream(
                    model="claude-opus-4-6",
                    max_tokens=2048,
                    system=build_system_prompt(feature["prompt"]),
                    messages=st.session_state[history_key],
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                err = str(e)
                if "authentication" in err.lower() or "api_key" in err.lower():
                    full_response = "❌ API key error. Please check your `.env` file."
                elif "rate_limit" in err.lower():
                    full_response = "⏳ Rate limit reached. Wait a moment and try again."
                else:
                    full_response = f"❌ Error: {err}"
                placeholder.markdown(full_response)

        st.session_state[history_key].append(
            {"role": "assistant", "content": full_response}
        )

    st.markdown('</div>', unsafe_allow_html=True)
