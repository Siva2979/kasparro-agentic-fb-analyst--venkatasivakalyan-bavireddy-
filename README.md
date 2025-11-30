📊 Kasparro Agentic Facebook Analyst

This repository implements a fully autonomous Agentic AI System designed to analyze Facebook Ads performance, diagnose ROAS fluctuations, and generate data-driven creative recommendations.
The solution follows Kasparro’s required multi-agent architecture with structured prompts, validation workflows, and reproducible outputs.

🚀 1. Project Overview

The goal of this system is to automatically explain why ROAS changed over time and recommend new creative directions for low-performing ads.

Given a natural-language query (e.g., "Analyze ROAS drop"), the system:

Loads and analyzes the Facebook Ads dataset

Detects drivers of ROAS decline (CTR drop, CPM spike, creative fatigue, targeting issues)

Generates hypotheses and evaluates them with quantitative evidence

Suggests improved ad creatives (headline, CTA, hooks)

Outputs insights in both JSON and Markdown reports

🧠 2. Agent Architecture

The system uses a Planner → Worker → Evaluator pattern, as required by Kasparro.

User Query
     ↓
Planner Agent
     ↓
Data Agent → (summaries)
     ↓
Insight Agent → (hypotheses)
     ↓
Evaluator Agent → (validated insights)
     ↓
Creative Generator → (new creatives)
     ↓
Final Report (JSON + Markdown)

Agent Responsibilities
✅ Planner Agent

Breaks down the user query into subtasks

Determines which agents should be called and in what order

✅ Data Agent

Loads the CSV dataset

Cleans, validates, and aggregates:

ROAS trends

CTR patterns

Audience performance

Creative effectiveness

✅ Insight Agent

Creates data-backed hypotheses explaining ROAS changes

Example: “CTR dropped 22% while spend stayed constant → possible creative fatigue”

✅ Evaluator Agent

Quantitatively validates each hypothesis

Computes a confidence score (0–1)

Outputs evidence used for validation

✅ Creative Generator Agent

Identifies low-CTR campaigns

Uses dataset’s messaging to generate:

New headlines

New CTAs

Variant copy based on past winners

📁 3. Project Structure
├── run.py                        # Main orchestrator
├── requirements.txt              # Dependencies
├── README.md                     # Documentation

├── config/
│   └── config.yaml               # Thresholds, paths, seed

├── prompts/
│   ├── planner.md
│   ├── data_agent.md
│   ├── insight_agent.md
│   ├── evaluator.md
│   └── creative_generator.md

├── src/
│   ├── agents/
│   │   ├── planner.py
│   │   ├── data_agent.py
│   │   ├── insight_agent.py
│   │   ├── evaluator.py
│   │   └── creative_generator.py
│   ├── orchestrator/
│   │   └── __init__.py
│   └── utils/
│       ├── logger.py
│       └── helpers.py

├── data/
│   ├── synthetic_fb_ads.csv
│   └── README.md

├── reports/
│   ├── insights.json
│   ├── creatives.json
│   └── report.md

└── logs/                         # JSON execution logs

⚙️ 4. Setup Instructions
Install Dependencies
pip install -r requirements.txt

Run Full Analysis
python run.py "Analyze ROAS drop"

Outputs Generated In
reports/insights.json
reports/creatives.json
reports/report.md

📊 5. Data Instructions

The dataset is stored in:

data/synthetic_fb_ads.csv


Expected columns:

campaign_name

adset_name

date

spend

impressions

clicks

ctr

purchases

revenue

roas

creative_type

creative_message

audience_type

platform

country

You may replace the dataset with any CSV following the same fields.

📈 6. Validation Logic (Evaluator Agent)

The evaluator performs quantitative checks such as:

ROAS before vs after a date range

CTR relative to threshold

CPM or CPC spikes

Creative_type performance drop

Audience overlap or fatigue indicators

Confidence score logic (0–1):

0.8–1.0 → Strong evidence

0.5–0.79 → Moderate evidence

<0.5 → Weak or inconclusive

📑 7. Example Outputs
insights.json (sample)
{
  "hypothesis": "Creative fatigue detected",
  "confidence": 0.81,
  "evidence": "CTR dropped 26% week-over-week while spend remained stable."
}

creatives.json (sample)
{
  "campaign": "Winter Sale",
  "new_headlines": [
    "🔥 Limited-Time Winter Deals!",
    "Upgrade Your Winter Style Today"
  ],
  "new_ctas": ["Shop Now", "Grab the Offer"],
  "rationale": "Generated from top-performing creative themes in dataset."
}

📦 8. Reproducibility

All randomness controlled through:

random_seed: 42


Thresholds for evaluation stored in config.yaml

Deterministic agent outputs ensured by structured prompts

📝 9. Observability & Logging

All agent steps log JSON traces to:

/logs/


Each log includes:

timestamp

agent name

step name

inputs & outputs

confidence metrics

This supports auditability and debugging.

📬 10. Submission Information (Kasparro Requirements)

Repository name: kasparro-agentic-fb-analyst-firstname-lastname

At least 3 commits

Release tag: v1.0

Self-review PR describing design choices

Outputs included:

reports/insights.json

reports/creatives.json

reports/report.md

logs/

Example metadata:

Command used: python run.py "Analyze ROAS drop"
Release tag: v1.0
Commit hash: <your_commit>

