#!/usr/bin/env python3
"""
Purposeful — AI Mentor for Women in Tech
MVP v1.0 | Command Line Interface
Built with the Claude API (Anthropic)

How it works:
- Each feature has a "system prompt" that shapes how Claude responds
- The main loop keeps conversation history so Claude remembers context
- Type 'back' at any time to return to the main menu
- Type 'quit' to exit
"""

import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv

# Load your API key from the .env file
load_dotenv()

# ============================================================
# INITIALIZE THE CLAUDE CLIENT
# This is your connection to the Claude API
# ============================================================
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# The Claude model we'll use — claude-opus-4-6 is the most capable
MODEL = "claude-opus-4-6"

# ============================================================
# SYSTEM PROMPTS
# These are the instructions that shape Purposeful's personality
# for each feature. Think of them as the "role" Claude plays.
# ============================================================

# Base personality shared by all features
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

# ============================================================
# CORE CHAT FUNCTION
# ============================================================

def chat_with_claude(conversation_history, system_prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=conversation_history
    )
    return response.content[0].text


# ============================================================
# FEATURE RUNNER
# ============================================================

def run_feature(feature_name, system_prompt, intro_message):
    print(f"\n{'=' * 62}")
    print(f"  {feature_name}")
    print(f"{'=' * 62}")
    print(f"\n{intro_message}")
    print("\n  Type 'back' to return to the main menu")
    print("  Type 'quit' to exit Purposeful\n")
    print("-" * 62)

    conversation_history = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n✨ Keep building! You've got this. — Purposeful\n")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ["back", "menu", "b"]:
            print("\n  → Returning to main menu...\n")
            break
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n✨ Keep building! You've got this. — Purposeful 💜\n")
            sys.exit(0)

        conversation_history.append({"role": "user", "content": user_input})
        print("\nPurposeful: ", end="", flush=True)

        try:
            response = chat_with_claude(conversation_history, system_prompt)
            print(response)
            conversation_history.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                print("❌ API key error. Please check your .env file.")
            elif "rate_limit" in error_msg.lower():
                print("⏳ Rate limit reached. Wait a moment and try again.")
            else:
                print(f"❌ Error: {error_msg}")


# ============================================================
# MAIN MENU
# ============================================================

def show_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        ✨  PURPOSEFUL — AI Mentor for Women in Tech  ✨      ║
║              Powered by Claude (Anthropic API)               ║
╚══════════════════════════════════════════════════════════════╝""")


def show_menu():
    print("""
  What would you like to work on today?
  ──────────────────────────────────────
  1.  🗺️   Career Path Generator
  2.  📄  Resume Optimizer       (for AI PM roles)
  3.  🎯  Job Matcher
  4.  📚  Learning Path Generator
  5.  🎤  Interview Prep         (mock interview simulation)
  6.  📰  AI News & Trends Digest
  7.  🎭  Roleplay Scenarios     (salary negotiation · pitches · tough convos)
  ──────────────────────────────────────
  0.  👋  Exit
""")


FEATURES = {
    "1": {
        "name": "🗺️  Career Path Generator",
        "prompt": CAREER_PATH_PROMPT,
        "intro": "Let's map out your career journey! 🗺️\n\n  Tell me about yourself:\n  • What's your current role and how many years of experience do you have?\n  • What's your big career goal? (e.g., AI PM, ML Engineer, Tech Lead)\n  • Any specific timeline or constraints I should know about?"
    },
    "2": {
        "name": "📄  Resume Optimizer",
        "prompt": RESUME_PROMPT,
        "intro": "Let's make your resume irresistible for AI PM roles! 📄\n\n  Paste your resume text, or describe your experience and I'll help you frame it powerfully."
    },
    "3": {
        "name": "🎯  Job Matcher",
        "prompt": JOB_MATCHER_PROMPT,
        "intro": "Let's find your best-fit roles in AI and tech! 🎯\n\n  Tell me about your skills, experience, preferred work environment, and salary range."
    },
    "4": {
        "name": "📚  Learning Path Generator",
        "prompt": LEARNING_PATH_PROMPT,
        "intro": "Let's build your personalized learning plan! 📚\n\n  What role or skill are you working toward, and how many hours/week can you dedicate?"
    },
    "5": {
        "name": "🎤  Interview Prep",
        "prompt": INTERVIEW_PREP_PROMPT,
        "intro": "Time to practice! Let's run a mock interview. 🎤\n\n  What role are you interviewing for, and what type? (behavioral / technical / PM case / mix)"
    },
    "6": {
        "name": "📰  AI News & Trends",
        "prompt": AI_NEWS_PROMPT,
        "intro": "Let's get you up to speed on AI! 📰\n\n  Ask about any topic, a company, or just say 'briefing' for a general AI landscape overview."
    },
    "7": {
        "name": "🎭  Roleplay Scenarios",
        "prompt": ROLEPLAY_PROMPT,
        "intro": "Let's practice a high-stakes conversation! 🎭\n\n  Choose:\n  A) 💰 Salary Negotiation\n  B) 💬 Difficult Conversation\n  C) 🚀 Pitch Practice\n\n  Which one, and give me some context!"
    }
}


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ API key not found!")
        print("\n  Create a .env file in this folder with:")
        print("  ANTHROPIC_API_KEY=your_key_here\n")
        sys.exit(1)

    show_banner()
    print("\n  Welcome! Ready to build your future in AI? 💜")

    while True:
        show_menu()
        try:
            choice = input("  Enter your choice (0-7): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n✨ Keep building! You've got this. — Purposeful\n")
            sys.exit(0)

        if choice == "0":
            print("\n✨ Keep building! You've got this. — Purposeful 💜\n")
            break
        elif choice in FEATURES:
            f = FEATURES[choice]
            run_feature(f["name"], f["prompt"], f["intro"])
        else:
            print("\n  ⚠️  Please enter a number between 0 and 7.\n")


if __name__ == "__main__":
    main()
