Kasparro Agentic Facebook Analyst

This project implements an AI-powered multi-agent system that autonomously analyzes Facebook Ads performance, detects reasons for ROAS (Return on Ad Spend) fluctuations, and generates improved creative ideas for underperforming campaigns.

What the System Does

📌 Diagnoses ROAS drops using statistical trend analysis

📌 Identifies performance drivers such as creative fatigue, budget shifts, targeting issues, CTR decline, audience burnout

📌 Generates insights through structured hypothesis-driven reasoning

📌 Validates hypotheses with quantitative evidence and confidence scoring

📌 Produces new creative recommendations (headlines, CTAs, messages) based on existing ad copy

Agent Architecture

Planner Agent – Breaks down the user query into tasks

Data Agent – Loads dataset, cleans data, computes summaries

Insight Agent – Creates hypotheses about performance changes

Evaluator Agent – Tests and scores hypotheses using data

Creative Generator – Suggests improved creatives for low-CTR campaigns

Project Structure
├── run.py                 # Main entry point
├── config/config.yaml     # Settings & thresholds
├── prompts/               # Agent prompt templates
├── src/agents/            # All agent implementations
├── src/utils/             # Logging & helpers
├── data/                  # Sample dataset
├── reports/               # insights.json, creatives.json, report.md
└── logs/                  # Execution logs

How to Run
pip install -r requirements.txt
python run.py "Analyze ROAS drop"


Outputs are generated in the reports/ folder.
