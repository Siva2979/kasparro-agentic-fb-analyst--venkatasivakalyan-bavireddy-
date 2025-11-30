import os
import sys
from typing import List, Dict, Any

import pandas as pd

# Ensure src is on the path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from utils.helpers import load_config, save_json, save_markdown, set_seed  # type: ignore
from utils.logger import get_logger  # type: ignore
from agents.planner import PlannerAgent  # type: ignore
from agents.data_agent import DataAgent  # type: ignore
from agents.insight_agent import InsightAgent  # type: ignore
from agents.evaluator import EvaluatorAgent  # type: ignore
from agents.creative_generator import CreativeGeneratorAgent  # type: ignore


def build_report_markdown(
    user_query: str,
    plan_steps: List[Dict[str, Any]],
    evaluations: List[Dict[str, Any]],
    creative_recs: List[Dict[str, Any]],
) -> str:
    lines: List[str] = []
    lines.append(f"# Kasparro Agentic FB Analyst – Report\n")
    lines.append(f"## User Query\n`{user_query}`\n")

    lines.append("## Planner Steps\n")
    for step in plan_steps:
        lines.append(f"- **Step {step['step']} – {step['name']}**: {step['description']}")

    lines.append("\n## Validated Insights\n")
    if not evaluations:
        lines.append("_No hypotheses generated/evaluated._")
    else:
        for ev in evaluations:
            lines.append(f"### {ev['hypothesis_id']}: {ev['hypothesis']}")
            lines.append(f"- Type: `{ev['type']}`")
            lines.append(f"- Confidence: **{ev['confidence']:.2f}**")
            lines.append(f"- Evidence: {ev['evidence']}")
            lines.append("")

    lines.append("\n## Creative Recommendations (Low CTR)\n")
    if not creative_recs:
        lines.append("_No low-CTR campaigns detected under the configured threshold._")
    else:
        for rec in creative_recs:
            lines.append(f"### Campaign: {rec['campaign_name']} | Adset: {rec['adset_name']}")
            lines.append(
                f"- Original CTR: {rec['original_ctr']:.4f}, Original ROAS: {rec['original_roas']:.2f}"
            )
            lines.append(f"- Audience: {rec['audience_type']} | Platform: {rec['platform']}")
            lines.append(f"- Original Message: {rec['original_creative_message']}")
            lines.append(f"- Suggested Headlines:")
            for h in rec["suggested_headlines"]:
                lines.append(f"  - {h}")
            lines.append(f"- Suggested CTAs: {', '.join(rec['suggested_ctas'])}")
            lines.append(f"- Rationale: {rec['rationale']}")
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python run.py 'Analyze ROAS drop'")
        sys.exit(1)

    user_query = sys.argv[1]

    # Load config
    config_path = os.path.join(CURRENT_DIR, "config", "config.yaml")
    config = load_config(config_path)

    # Setup logging and seed
    log_dir = config["paths"]["logs"]
    logger = get_logger("agentic_fb_analyst", log_dir)
    set_seed(config.get("random_seed", 42))

    logger.info("Starting Agentic FB Analyst run", {"user_query": user_query})

    # Initialize agents
    planner = PlannerAgent()
    data_agent = DataAgent(dataset_path=config["paths"]["dataset"])
    insight_agent = InsightAgent(thresholds=config["thresholds"])
    evaluator_agent = EvaluatorAgent(thresholds=config["thresholds"])
    creative_agent = CreativeGeneratorAgent(thresholds=config["thresholds"])

    # 1. Planning
    plan_steps = planner.plan(user_query)
    logger.info("Planner produced steps", {"steps": plan_steps})

    # 2. Data load & summary
    df: pd.DataFrame = data_agent.load_data()
    summary = data_agent.summarize(df)
    logger.info("Data summary computed", {"summary_keys": list(summary.keys())})

    # 3. Generate hypotheses
    hypotheses = insight_agent.generate_hypotheses(summary)
    logger.info("Hypotheses generated", {"count": len(hypotheses)})

    # 4. Evaluate hypotheses
    evaluations = evaluator_agent.evaluate(df, hypotheses)
    logger.info("Hypotheses evaluated", {"count": len(evaluations)})

    # 5. Generate creative recommendations
    creative_recs = creative_agent.generate(df)
    logger.info("Creative recommendations generated", {"count": len(creative_recs)})

    # 6. Save outputs
    outputs_dir = config["paths"]["outputs"]
    insights_path = os.path.join(outputs_dir, "insights.json")
    creatives_path = os.path.join(outputs_dir, "creatives.json")
    report_path = os.path.join(outputs_dir, "report.md")

    save_json(evaluations, insights_path)
    save_json(creative_recs, creatives_path)

    report_md = build_report_markdown(user_query, plan_steps, evaluations, creative_recs)
    save_markdown(report_md, report_path)

    logger.info(
        "Run completed successfully",
        {
            "insights_path": insights_path,
            "creatives_path": creatives_path,
            "report_path": report_path,
        },
    )

    print(f"Analysis complete. Report saved to: {report_path}")


if __name__ == "__main__":
    main()
