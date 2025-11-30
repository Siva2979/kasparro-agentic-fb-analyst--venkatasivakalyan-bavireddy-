import pandas as pd

from src.agents.evaluator import EvaluatorAgent


def test_evaluator_roas_drop_basic():
    # create simple dataset with clear ROAS drop
    data = {
        "date": pd.date_range("2024-01-01", periods=6, freq="D"),
        "roas": [4.0, 3.8, 3.5, 3.0, 2.5, 2.0],
        "ctr": [0.01, 0.011, 0.009, 0.008, 0.007, 0.006],
        "creative_type": ["image"] * 6,
    }
    df = pd.DataFrame(data)

    thresholds = {"roas_drop_pct": 0.15, "low_ctr": 0.007}
    evaluator = EvaluatorAgent(thresholds=thresholds)

    hypotheses = [
        {
            "id": "H1",
            "type": "roas_drop",
            "hypothesis": "ROAS dropped over time.",
        }
    ]

    evaluations = evaluator.evaluate(df, hypotheses)
    assert len(evaluations) == 1
    ev = evaluations[0]

    assert ev["hypothesis_id"] == "H1"
    assert 0.0 <= ev["confidence"] <= 1.0
    assert "ROAS" in ev["evidence"] or "roas" in ev["evidence"].lower()
