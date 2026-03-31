"""Gemini prompt templates for each export format."""

BLOG_PROMPT = """\
You are a financial content writer. Given this trading analysis report, write a \
polished blog post for retail investors.

Requirements:
- Title and subtitle
- 1,200-1,500 words
- Engaging narrative style with section headers (##)
- Include key metrics, analyst ratings, and the final recommendation
- Write in accessible language — avoid jargon, explain technical terms
- End with a clear takeaway and disclaimer
- Return valid JSON matching the schema exactly

Report:
"""

SOCIAL_PROMPT = """\
You are a financial social media strategist. Given this trading analysis report, \
generate social media posts for three platforms.

Requirements:
1. **Twitter/X thread**: 5 tweets, each under 280 characters. First tweet is the hook. \
Use $TICKER format. Include key metrics.
2. **LinkedIn post**: 200-300 words, professional tone. Focus on the investment thesis \
and risk assessment. Include a call to action.
3. **Instagram caption**: 150-200 words with relevant hashtags (10-15). Visual storytelling \
tone, highlight the most compelling data point.

Return valid JSON matching the schema exactly.

Report:
"""

PPTX_PROMPT = """\
You are a financial presentation designer. Given this trading analysis report, \
generate content for a 10-slide executive presentation.

Slide structure:
1. Title slide (company name, date, recommendation)
2. Executive Summary (3 bullet points)
3. Company Overview (business description, key stats)
4. Financial Snapshot (revenue, margins, EPS, dividend)
5. Technical Analysis (key indicators, support/resistance levels)
6. News & Sentiment (recent events, sentiment score)
7. Bull vs Bear Case (key arguments from each side)
8. Risk Assessment (top 3 risks with mitigations)
9. Trade Plan (entry, targets, stop-loss)
10. Final Recommendation (decision + rationale)

Each slide needs: title, 3-4 bullet points, and speaker notes (2-3 sentences).
Return valid JSON as a list of slide objects matching the schema exactly.

Report:
"""

PDF_PROMPT = """\
You are a financial report writer. Given this trading analysis report, generate a \
structured PDF report suitable for institutional investors.

Requirements:
- Professional title and subtitle
- Executive summary (3-4 sentences)
- Sections: Company Profile, Financial Analysis, Technical Outlook, \
Sentiment & News, Risk Assessment, Investment Thesis
- Each section has a heading and body text (use markdown-style formatting)
- Include a table_data field (list of [column, value] pairs) where relevant
- End with a standard investment disclaimer
- Return valid JSON matching the schema exactly

Report:
"""

AUDIO_SCRIPT_PROMPT = """\
You are a podcast script writer for a financial analysis show. Given this trading \
analysis report, write a 5-minute two-person conversation.

Characters:
- **Alex**: The analyst who presents the findings. Knowledgeable, uses data.
- **Sam**: The host who asks questions. Curious, represents the listener.

Requirements:
- Natural spoken dialogue, not formal language
- Cover: company overview, key financials, the bull/bear debate, risk factors, \
and the final recommendation
- Start with a brief intro, end with a clear takeaway
- 20-30 exchanges total
- Each line should be 1-3 sentences max
- Return valid JSON with title and dialogue array

Report:
"""
